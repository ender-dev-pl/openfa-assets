"""Check the added sensor ring and retained pod/engine arrangement in both forms."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();reports={}
for imported in [False,True]:
 if imported:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'virus-missile.glb'))
 else:bpy.ops.wm.open_mainfile(filepath=str(out/'virus-missile.blend'))
 bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
 sensors=[bpy.data.objects[f'Atmospheric resistance sensor {i+1}'] for i in range(4)]
 centres=[]
 for ob in sensors:
  vs=[ob.matrix_world@v.co for v in ob.data.vertices];tip=max(vs,key=lambda v:v.z);base=[v for v in vs if abs(v.z-.59)<1e-5]
  assert len(base)>=48
  centre=sum(base,Vector())/len(base);assert abs(centre.z-.59)<1e-5 and abs(tip.z-1.17)<1e-5
  assert abs(centre.xy.length-.37)<1e-5 and (tip.xy-centre.xy).length<1e-5
  assert max(abs((v.xy-centre.xy).length-.20) for v in base)<1e-5
  centres.append(centre)
 minimum=min((a-b).length for i,a in enumerate(centres) for b in centres[i+1:]);assert minimum>.40
 model=json.loads((out/'model.json').read_text());engines=[bpy.data.objects[n] for n in model['components']['main-thrusters']]
 top=max((ob.matrix_world@v.co).z for ob in engines for v in ob.data.vertices);assert top<.59
 reports['imported' if imported else 'native']=dict(sensor_count=4,minimum_sensor_axis_spacing=minimum,sensor_base_radius=.20,sensor_base_z=.59,sensor_tip_z=1.17,engine_top_z=top,vertical_engine_clearance=.59-top,retained_pod_count=len(model['components']['binary-agent-pods']),retained_thruster_meshes=len(engines))
(out/'anatomy-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((out/'virus-missile.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'virus-missile.glb').read_bytes()).hexdigest(),checks=reports,limitations=['Sensors intentionally intersect their supporting skirt. Hidden seating depth and exact dimensions are authored.']),indent=2)+'\n',encoding='utf-8');print('VIRUS_ANATOMY_VERIFIED')
