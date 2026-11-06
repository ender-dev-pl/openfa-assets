"""Reject the actual ST05 proportion and caption-assignment regressions."""
import bpy,bmesh,json,sys,math
from pathlib import Path
from mathutils import Matrix
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'asteroid-tracker.blend'));bpy.context.view_layer.update()
m=json.loads((o/'model.json').read_text());root=bpy.data.objects['TrackerRotor'];assert abs(root.scale.z-.72)<1e-6
bounds={};closed=0
for role,names in m['components'].items():
    points=[]
    for name in names:
        obj=bpy.data.objects[name]
        if obj.type=='MESH':
            points.extend(obj.matrix_world@v.co for v in obj.data.vertices)
            bm=bmesh.new();bm.from_mesh(obj.data);assert all(e.is_manifold for e in bm.edges),name;bm.free();closed+=1
    bounds[role]=dict(min=[min(p[i] for p in points) for i in range(3)],max=[max(p[i] for p in points) for i in range(3)])
assert m['components']['data-storage']==['Left upper data-bank module']
assert bounds['data-storage']['max'][0]<-.4 and bounds['data-storage']['min'][2]>1.5
assert bounds['calibration-device']['min'][2]>1.5 and bounds['calibration-device']['max'][2]>2
assert len(m['components']['calibration-device'])==4
assert all('calibration' in name.lower() for name in m['components']['calibration-device'])
assert all(bpy.data.objects[name].hide_render for name in m['components']['calibration-device'])
assert next(p for p in m['phases'] if p['component']=='calibration-device')['isolated_detail']
assert all('Upper interface indicator' not in name for name in m['components']['user-interface'])
ratios=[]
for name in m['components']['cooling-fans']:
    if not name.startswith('Twin fan dark intake'):continue
    obj=bpy.data.objects[name];matrix=Matrix.Rotation(-root.rotation_euler.z,4,'Z')@obj.matrix_world;points=[matrix@v.co for v in obj.data.vertices]
    ratio=(max(p.x for p in points)-min(p.x for p in points))/(max(p.z for p in points)-min(p.z for p in points));assert abs(ratio-1)<.01;ratios.append(ratio)
assert len(ratios)==2
(o/'geometry-refinement-proof.json').write_text(json.dumps(dict(closed_meshes=closed,root_scale=list(root.scale),component_bounds=bounds,fan_roundness_ratios=ratios,caption_correspondence='Information frames84/225/366/507 map through Same/Fram timeline to updates34/99/164/229: CRT, fan pair, left upper data bank, isolated coarse screw.',calibration_placement='Authored schematic staging only; original mounting point remains unresolved. Hidden from the solid model and standard whole-device wireframe.'),indent=2)+'\n')
print('TRACKER_REFINEMENT_GEOMETRY_VERIFIED',closed)
