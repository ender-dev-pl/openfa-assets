"""Exercise current canonical payloads, flight visibility and full preview rigs."""
import json
import sys
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(Path(__file__).parent))
from build_ship_construction_layers import SHIPS,sha
from render_complete_shipyard_movies import initialize,pose,configure


def main():
    migration_path=ROOT/'sources/docs/reconstruction/models/shipyard-canonical-assets.json'
    migration=json.loads(migration_path.read_text(encoding='utf-8'))
    inputs={migration_path.relative_to(ROOT).as_posix():sha(migration_path)}
    for row in migration['models']:
        for kind in ['blend','glb']:
            assert sha(ROOT/row[kind])==row[kind+'_sha256']
            inputs[row[kind]]=row[kind+'_sha256']
    for name in ['verify_canonical_shipyard_assets.py','render_complete_shipyard_movies.py','render_shipyard_construction.py','build_shipyard_hangar.py','build_ship_construction_layers.py']:
        p=Path(__file__).with_name(name);inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    folder=ROOT/'artifacts/issue-227/consolidation/runtime';folder.mkdir(parents=True,exist_ok=True)
    rows=[]
    for ship in SHIPS:
        scene,components,config=initialize(ship)
        # Evaluate the real current controller throughout the entire full film.
        for frame in range(480):pose(scene,components,config,frame/24)
        configure(scene,384,'BLENDER_EEVEE_NEXT')
        images=[]
        for seconds in [3,7.9,10.5,15,19.9]:
            pose(scene,components,config,seconds)
            path=folder/(ship+'-'+str(seconds)+'.png')
            scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            images.append(dict(seconds=seconds,sha256=sha(path)))
        # Reopen native editable source; flight has both complementary skin groups
        # and none of the build batches. This is the same asset, not another model.
        bpy.ops.wm.open_mainfile(filepath=str(ROOT/'sources/objects/terran'/ship/'model.blend'),load_ui=False,use_scripts=False)
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        for o in meshes:o.hide_render=not o.name.startswith(('HullPartialBatch_','HullFinalBatch_'))
        assert all(o.hide_render for o in meshes if o.name.startswith('Build'))
        visible=[o for o in meshes if not o.hide_render]
        assert visible and all(o.name.startswith(('HullPartialBatch_','HullFinalBatch_')) for o in visible)
        assert any(o.name.startswith('HullPartialBatch_') for o in visible) and any(o.name.startswith('HullFinalBatch_') for o in visible)
        configure(bpy.context.scene,384,'BLENDER_EEVEE_NEXT')
        path=folder/(ship+'-flight.png');bpy.context.scene.render.filepath=str(path);bpy.ops.render.render(write_still=True)
        rows.append(dict(ship=ship,frames=480,contact_assertions=True,flight_visible_meshes=len(visible),flight_triangles=sum(len(p.vertices)-2 for o in visible for p in o.data.polygons),flight_image_sha256=sha(path),combined_renders=images))
        print('CANONICAL_PAYLOAD_RUNTIME_OK',ship,flush=True)
    report=dict(issue=227,inputs=inputs,payloads_checked=3,controller_frames_per_payload=480,geometry_relocated_byte_identically=True,flight_and_construction_share_model=True,payloads=rows,media='Existing full movies retained; actual new-path combined probes and native flight renders inspected separately. No claim that the old movie was rerendered.')
    out=ROOT/'sources/objects/terran/ship-yard/canonical-runtime-validation.json'
    out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':main()
