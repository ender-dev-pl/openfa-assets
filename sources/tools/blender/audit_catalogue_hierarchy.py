"""Read-only asset hierarchy and sampled node-transform comparison in actual Blender."""
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_catalogue_texture_uv import parse_glb

REPO=Path(__file__).resolve().parents[2]
OUTPUT=REPO/'docs/assets/reconstruction/evidence/catalogue-hierarchy'
PROPERTIES=['catalogue_id','forward_axis','calibration','footprint_width','footprint_height']
PHASES=[0,.25,.5,.75,1]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def asset_objects(native):
    scene=bpy.context.scene
    if not native: return [o for o in scene.objects if o.type in ['MESH','EMPTY'] and not o.get('preview_only')]
    objects={o for o in scene.objects if o.type=='MESH' and not o.get('preview_only')}
    collections=[c for c in bpy.data.collections if c.asset_data]
    candidates={o for c in collections for o in c.all_objects} if collections else set(scene.objects)
    objects.update(o for o in candidates if o.type=='EMPTY' and not o.get('preview_only'))
    for obj in list(objects):
        parent=obj.parent
        while parent:
            if parent.type in ['MESH','EMPTY']: objects.add(parent)
            parent=parent.parent
    return sorted(objects,key=lambda o:o.name)


def range_and_actions(objects):
    actions={};unknown=[]
    for obj in objects:
        animation=obj.animation_data
        if not animation: continue
        if animation.action: actions[obj.name+': active action']=list(animation.action.frame_range)
        if animation.use_nla:
            for track in animation.nla_tracks:
                if track.mute: continue
                for strip in track.strips:
                    if strip.mute: continue
                    if strip.type=='CLIP': actions[obj.name+': NLA '+track.name+'/'+strip.name]=[strip.frame_start,strip.frame_end]
                    else: unknown.append(obj.name+': uninspected NLA strip type '+strip.type)
        if animation.drivers: unknown.append(obj.name+': drivers not separately interpreted')
    bounds=[min(v[0] for v in actions.values()),max(v[1] for v in actions.values())] if actions else None
    return bounds,actions,unknown


def capture(objects):
    bounds,actions,unknown=range_and_actions(objects);poses={}
    for phase in PHASES if bounds else [0]:
        frame=bounds[0]+phase*(bounds[1]-bounds[0]) if bounds else 1
        bpy.context.scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
        poses[str(phase)]={o.name:[float(v) for row in o.matrix_world for v in row] for o in objects}
    first=poses['0'];nodes={}
    for obj in objects:
        properties={key:obj[key] for key in PROPERTIES if key in obj}
        nodes[obj.name]=dict(type=obj.type,parent=obj.parent.name if obj.parent else None,
            first_world_matrix=first[obj.name],properties=properties)
    return dict(nodes=nodes,action_range=bounds,actions=actions,uninspected=unknown),poses


def compare(native,imported,native_poses,imported_poses):
    a=native['nodes'];b=imported['nodes'];common=a.keys()&b.keys()
    issues=[];parents={};properties={};types={};errors={}
    for name in sorted(common):
        if a[name]['parent']!=b[name]['parent']: parents[name]=[a[name]['parent'],b[name]['parent']]
        if a[name]['type']!=b[name]['type']: types[name]=[a[name]['type'],b[name]['type']]
        missing={k:dict(native=v,imported=b[name]['properties'].get(k)) for k,v in a[name]['properties'].items() if b[name]['properties'].get(k)!=v}
        if missing: properties[name]=missing
        values=[]
        for phase,pose in native_poses.items():
            other=imported_poses.get(phase,imported_poses['0'])
            values.append(max(abs(x-y) for x,y in zip(pose[name],other[name])))
        errors[name]=max(values)
    if bool(native['actions'])!=bool(imported['actions']): issues.append('Active node animation presence differs')
    if native['uninspected'] or imported['uninspected']: issues.append('Additional animation interpretation required')
    return dict(missing_imported=sorted(a.keys()-b.keys()),extra_imported=sorted(b.keys()-a.keys()),
        parent_differences=parents,type_differences=types,property_differences=properties,
        maximum_sampled_matrix_error=max(errors.values(),default=0),
        nodes_above_1e5={k:v for k,v in errors.items() if v>1e-5},issues=issues)


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True);inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    records=json.loads(inventory_path.read_text())['records'];assert len(records)==303;rows=[]
    for index,record in enumerate(records):
        study=[s for s in record['available_studies'] if s['present']][-1]
        source=REPO/study['blend'];export=source.with_suffix('.glb');before=dict(blend_sha256=sha(source),glb_sha256=sha(export))
        assert before['blend_sha256']==study['sha256']
        bpy.ops.wm.open_mainfile(filepath=str(source));native,poses=capture(asset_objects(True))
        document,_=parse_glb(export);clips=[dict(name=a.get('name'),channels=len(a['channels'])) for a in document.get('animations',[])]
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(export))
        imported,other=capture(asset_objects(False));comparison=compare(native,imported,poses,other)
        if len(clips)>1: comparison['issues'].append('Multiple GLB clips: only active imported actions sampled')
        assert before==dict(blend_sha256=sha(source),glb_sha256=sha(export))
        path=OUTPUT/f'{index:03}.json';data=dict(issue=1112,id=record['id'],category=record['category'],blend=study['blend'],**before,
            native=native,imported=imported,comparison=comparison,glb_clips=clips,source_assets_unchanged=True,final_visual_acceptance=False)
        path.write_text(json.dumps(data,indent=2)+'\n');rows.append(dict(id=record['id'],report=path.name,sha256=sha(path),
            native_nodes=len(native['nodes']),imported_nodes=len(imported['nodes']),animated=bool(native['actions']),
            maximum_sampled_matrix_error=comparison['maximum_sampled_matrix_error']))
        print('CATALOGUE_HIERARCHY_INSPECTED',record['id'],comparison['maximum_sampled_matrix_error'],flush=True)
    (OUTPUT/'summary.json').write_text(json.dumps(dict(issue=1112,blender=bpy.app.version_string,auditor_sha256=sha(Path(__file__)),
        glb_parser_sha256=sha(Path(__file__).with_name('audit_catalogue_texture_uv.py')),inventory_sha256=sha(inventory_path),
        definitions=len(rows),normalized_phases=PHASES,records=rows,final_visual_acceptance=False,
        scope='Selected native mesh/empty hierarchy, metadata helpers and normalized active-action node matrices at five phases. No complete deformation/all-clip/continuous motion, calibrated mount or final art/game integration acceptance.'),indent=2)+'\n')
    print('CATALOGUE_HIERARCHY_AUDIT_OK',len(rows),flush=True)


if __name__=='__main__': main()
