"""Compose real building/scaffold states for the OpenFA GPU studio renderer."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile

import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene,material
from build_refined_rigellian_scaffold import box,export_glb_to
from catalogue_rendering import evaluated_points,fit_camera

REPO=Path(__file__).resolve().parents[2]
ASSETS=REPO.parent
SELECTED=[('terran','terran:living-quarters'),('rigellian','openfa:building/legacy/041'),
          ('braccatian','openfa:building/legacy/074'),('mikotaj','openfa:building/legacy/088'),
          ('artemian','openfa:building/legacy/111'),('mauna','openfa:building/legacy/138'),
          ('achaean','openfa:building/legacy/156')]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def imported(path):
    before=set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return set(bpy.context.scene.objects)-before


def parent_group(objects,name):
    root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root)
    for obj in objects:
        if obj.parent not in objects:obj.parent=root
    return root


def bounds(objects):
    points=evaluated_points([o for o in objects if o.type=='MESH'])
    return [min(p[k] for p in points) for k in range(3)]+[max(p[k] for p in points) for k in range(3)]


def timeline(ceiling):
    entries=[dict(key='empty',phase='ready',stage=0,duration=.8)]
    entries += [dict(key=f'erection-{stage:02}',phase='erection',stage=stage,duration=5/ceiling) for stage in range(1,ceiling+1)]
    entries += [dict(key=f'reveal-{ceiling:02}',phase='reveal',stage=ceiling,duration=1.2)]
    entries += [dict(key=f'reveal-{stage:02}',phase='dismantling',stage=stage,duration=5/ceiling) for stage in range(ceiling,0,-1)]
    entries += [dict(key='complete',phase='complete',stage=0,duration=3)]
    return entries


def prepare(culture,identity,output):
    integration=json.loads((ASSETS/'sources/docs/assets/reconstruction/scaffolds/culture-kits/integration.json').read_text())
    catalogue=json.loads((ASSETS/'gallery/catalogue.json').read_text(encoding='utf-8'))
    definition=next(d for d in integration['definitions'] if d['id']==identity)
    family=next(f for f in integration['families'] if f['family']==definition['family'])
    row=next(r for r in catalogue if r['id']==identity)
    building=ASSETS/row['studies'][-1]['glb'];ceiling=definition['ceiling']
    family_meta=json.loads((ASSETS/family['manifest']).read_text())
    footprint=family_meta.get('footprint',2)
    clear_half=family_meta.get('clear_volume',{}).get('half_extent_xy',footprint*.45-.11)
    folder=output/culture;folder.mkdir(parents=True,exist_ok=True)
    scene=setup_scene(640,16);building_objects=imported(building);bb=bounds(building_objects)
    scale=2*clear_half*.94/max(bb[3]-bb[0],bb[4]-bb[1])
    height=(bb[5]-bb[2])*scale
    full=next(s for s in family['stages'] if s['stage']==ceiling)
    capacity=definition['frames_per_tier'];nominal_height=ceiling*family['pitch']/capacity
    vertical_scale=height*1.07/nominal_height
    specs={e['key']:(e['stage'],e['phase'] not in ['ready','erection']) for e in timeline(ceiling)}
    frames=[];sources={str(building.relative_to(ASSETS)).replace('\\','/'):sha(building)}
    camera=None
    # One camera for every state; fit the complete enclosure and platform.
    envelope=footprint*.45+.11
    framing=[Vector((x,y,z)) for x in [-envelope,envelope] for y in [-envelope,envelope] for z in [-.08,height*1.18+.15]]
    for number,(key,(stage,visible)) in enumerate(specs.items()):
        print('PREPARE_CONSTRUCTION',culture,key,flush=True)
        scene=setup_scene(640,16)
        scaffold_meshes=0;building_meshes=0
        if stage:
            state=next(s for s in family['stages'] if s['stage']==stage)
            path=ASSETS/state['glb'];assert sha(path)==state['glb_sha256']
            sources[state['glb']]=state['glb_sha256']
            objects=imported(path)
            if visible:
                hidden=set(state['hide_on_reveal'])
                actual={o.name for o in objects}
                assert hidden<=actual,'Scaffold mask names changed during import'
                for obj in list(objects):
                    if obj.name in hidden:
                        objects.remove(obj);bpy.data.objects.remove(obj,do_unlink=True)
            root=parent_group(objects,'Preview scaffold placement');root.scale.z=vertical_scale
            scaffold_meshes=sum(o.type=='MESH' for o in objects)
        if visible:
            objects=imported(building);root=parent_group(objects,'Preview finished building placement')
            root.scale=(scale,scale,scale)
            root.location=(-scale*(bb[0]+bb[3])/2,-scale*(bb[1]+bb[4])/2,-scale*bb[2])
            building_meshes=sum(o.type=='MESH' for o in objects)
        # An explicitly labelled studio plinth, never a synthetic colony.
        base=material('Construction studio plinth',(.045,.055,.065),.05,.85)
        box('Studio plinth',(0,0,-.035),(envelope*2.2,envelope*2.2,.07),base,.015)
        bpy.context.view_layer.update();fit_camera(scene,framing,(10,-10,8))
        if camera is None:camera=dict(camera_matrix=[list(row) for row in scene.camera.matrix_world],ortho_scale=scene.camera.data.ortho_scale)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type in ['MESH','EMPTY']:obj.select_set(True)
        path=folder/f'{number:03}.glb';export_glb_to(path)
        frames.append(dict(id=f'{culture}/{key}',key=key,stage=stage,building_visible=visible,
                           image=f'{number:03}.png',glb=path.name,sha256=sha(path),
                           scaffold_meshes=scaffold_meshes,building_meshes=building_meshes))
    archive=folder/'models.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as target:
        models=[]
        for frame in frames:
            name='models/'+frame['glb'];target.write(folder/frame['glb'],name)
            models.append(dict(id=frame['id'],path=name,sha256=frame['sha256'],animationKind='clips'))
        target.writestr('catalogue.json',json.dumps(dict(schemaVersion=1,models=models)))
    by_key={f['key']:f for f in frames}
    entries=[dict(e,image=by_key[e['key']]['image']) for e in timeline(ceiling)]
    plan=dict(issue=189,culture=culture,definition_id=identity,building_name=row['name'],family=family['family'],ceiling=ceiling,
              archive=archive.name,resolution=640,**camera,frames=frames,timeline=entries,
              sources=sources,source_integration_sha256=sha(ASSETS/'sources/docs/assets/reconstruction/scaffolds/culture-kits/integration.json'),
              generator_sha256=sha(Path(__file__)),scope='Authored asset studio cycle using actual OpenFA engine; not live simulation or gameplay integration',
              calibration=dict(building_uniform_scale=scale,building_original_bounds=bb,scaffold_vertical_scale=vertical_scale,
                               reason='Preview-only footprint and target-height calibration; original source assets are unchanged'))
    (folder/'sequence.json').write_text(json.dumps(plan,indent=2)+'\n')
    return culture


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);parser.add_argument('--culture')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for culture,identity in SELECTED:
        if args.culture and args.culture!=culture:continue
        prepare(culture,identity,args.output.resolve())
    print('CONSTRUCTION_PREVIEWS_PREPARED',flush=True)


if __name__=='__main__':main()
