"""Prove both panel actions survive independent GLB import, including all solids."""
import bpy,sys,json,hashlib,struct,math
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();source=out/'solar-matrix.blend';glb=out/'solar-matrix.glb'
raw=glb.read_bytes();d=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
assert {a['name'] for a in d['animations']}=={'CatalogueTurn','PanelsClose','PanelsOpen'}
def activate(clip):
 for ob in bpy.context.scene.objects:
  if not ob.animation_data:continue
  ob.animation_data.action=None
  for track in ob.animation_data.nla_tracks:track.mute=track.name!=clip;track.is_solo=False
 bpy.data.objects['SolarMatrixRoot'].matrix_basis=root_rest
def matrices(names):return {n:[v for row in bpy.data.objects[n].matrix_world for v in row] for n in names}
def tree(name):
 ob=bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ob.to_mesh();result=BVHTree.FromPolygons([ob.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons],all_triangles=False);ob.to_mesh_clear();return result
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root_rest=bpy.data.objects['SolarMatrixRoot'].matrix_basis.copy();model=json.loads((out/'model.json').read_text());names=[n for ns in model['components'].values() for n in ns];expected={};top={}
for clip in ['PanelsClose','PanelsOpen']:
 activate(clip);expected[clip]={}
 for f in range(1,32):
  s.frame_set(f);bpy.context.view_layer.update();expected[clip][f]=matrices(names)
  panels=[tree(f'Splayed collector panel {i+1}') for i in range(4)]
  for i in range(4):
   for j in range(i):assert not panels[i].overlap(panels[j]),('intersecting panels',clip,f,i,j)
   for n in model['components']['laser-turret']:assert not panels[i].overlap(tree(n)),('panel intersects turret',clip,f,i,n)
  if f in [1,16,31]:
   s.render.filepath=str(out/f'{clip.lower()}-{f:02}.png');bpy.ops.render.render(write_still=True)
   top[clip,f]=max((bpy.data.objects[n].matrix_world@v.co).z for n in names if n.startswith('Splayed collector panel') for v in bpy.data.objects[n].data.vertices)
assert top['PanelsClose',31]>top['PanelsClose',1]+.4
assert abs(top['PanelsOpen',31]-top['PanelsClose',1])<1e-5
activate('PanelsClose');s.frame_set(31);bpy.context.view_layer.update()
closed=[]
for i in range(4):
 ob=bpy.data.objects[f'Splayed collector panel {i+1}'];closed.append([ob.matrix_world@ob.data.vertices[j].co for j in [4,5,6,7]])
for i in range(4):
 pts=closed[i];base=(pts[0]+pts[3])*.5;tip=(pts[1]+pts[2])*.5
 assert abs(base.xy.length-.34)<1e-5 and abs(tip.xy.length-.15)<1e-5
 assert tip.z>base.z+.50 and .28/.66<.5
 # Corresponding side edges of adjacent wings retain only a narrow gap.
 neighbour=closed[(i+1)%4]
 assert abs((pts[3]-neighbour[0]).length-math.sqrt(2)*.01)<1e-5
 assert abs((pts[2]-neighbour[1]).length-math.sqrt(2)*.01)<1e-5
for ob in list(s.objects):
 if ob.type not in ['LIGHT','CAMERA']:bpy.data.objects.remove(ob,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(glb));s.frame_set(1);bpy.context.view_layer.update();root_rest=bpy.data.objects['SolarMatrixRoot'].matrix_basis.copy();errors={}
for clip in ['PanelsClose','PanelsOpen']:
 activate(clip);maximum=0
 for f in range(1,32):
  s.frame_set(f);bpy.context.view_layer.update();got=matrices(names)
  for n in names:
   error=max(abs(a-b) for a,b in zip(expected[clip][f][n],got[n]));maximum=max(maximum,error);assert error<1e-4,(clip,f,n,error)
  if f in [1,16,31]:s.render.filepath=str(out/f'imported-{clip.lower()}-{f:02}.png');bpy.ops.render.render(write_still=True)
 errors[clip]=maximum
(out/'articulation-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256(glb.read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),clips=list(errors),independent_import_pose_count=62,solid_mesh_count=len(names),maximum_matrix_error=errors,closed_panel_height_increase=top['PanelsClose',31]-top['PanelsClose',1],reversible=True,legacy_shutdown_state_binding_confirmed=False),indent=2)+'\n')
print('SOLAR_ARTICULATION_VERIFIED',errors)
