"""Native ST12 component ownership and closed editable geometry checks."""
import bpy,bmesh,json,sys
from pathlib import Path
o=Path(sys.argv[sys.argv.index('--')+1]).resolve();bpy.ops.wm.open_mainfile(filepath=str(o/'improved-sensors.blend'));bpy.context.view_layer.update();m=json.loads((o/'model.json').read_text())
assert [p['component'] for p in m['phases']]==['data-collector','shielding-coils','calibration-indicators']
assert len(m['components']['shielding-coils'])==2
for name in m['components']['shielding-coils']:
    obj=bpy.data.objects[name];assert obj.type=='CURVE' and all(sp.use_cyclic_u for sp in obj.data.splines)
assert sum(n.startswith('Red data collector conductor') for n in m['components']['data-collector'])==8
assert sum(n.startswith('Collector trace terminal') for n in m['components']['data-collector'])==12
assert sum(n.startswith('Pale signal strength indicator') for n in m['components']['calibration-indicators'])==10
for name in m['components']['calibration-indicators']:
    if name.startswith('Pale signal strength indicator'):
        color=bpy.data.objects[name].data.materials[0].diffuse_color;assert min(color[:3])>.4,'Normal signal indicators are pale, not red wireframe highlights'
count=0;bounds={}
for role,names in m['components'].items():
    points=[]
    for name in names:
        obj=bpy.data.objects[name]
        if obj.type=='MESH':
            bm=bmesh.new();bm.from_mesh(obj.data);assert all(e.is_manifold for e in bm.edges),name;bm.free();count+=1;points.extend(obj.matrix_world@v.co for v in obj.data.vertices)
        elif obj.type=='CURVE':
            from mathutils import Vector
            points.extend(obj.matrix_world@Vector(p.co[:3]) for sp in obj.data.splines for p in sp.points)
    bounds[role]=dict(min=[min(p[i] for p in points) for i in range(3)],max=[max(p[i] for p in points) for i in range(3)])
assert bounds['calibration-indicators']['min'][2]>1.9 and bounds['calibration-indicators']['max'][2]>2.6
assert bounds['data-collector']['min'][2]<.1 and bounds['data-collector']['max'][2]>2
assert abs(bpy.data.objects['SensorsRotor'].scale.x-1.035)<1e-5
coilheight=bounds['shielding-coils']['max'][2]-bounds['shielding-coils']['min'][2];assert .45<coilheight<.70,'Colour preview coils must not be twice the height of the collector traces'
(o/'geometry-verification.json').write_text(json.dumps(dict(closed_meshes=count,closed_shielding_curves=2,caption_component_order=[p['component'] for p in m['phases']],component_bounds=bounds,root_scale=list(bpy.data.objects['SensorsRotor'].scale)),indent=2)+'\n',newline='\n');print('SENSORS_GEOMETRY_VERIFIED',count)
