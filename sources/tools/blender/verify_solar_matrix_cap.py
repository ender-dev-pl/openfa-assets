"""Reopen current canonical PB28 and verify the no-weapon three-clip contract."""
import argparse,json,math,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from correct_solar_matrix_cap import meshes,signature,bounds,activate,pose,camera_setup,render_still,sha

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);root=args.root.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 folder=root/'sources/objects/terran/solar-matrix/refined';proof=root/'gallery/media/objects/terran/solar-matrix/correction-272'
 generation=json.loads((proof/'generation.json').read_text());blend=folder/'model.blend';glb=folder/'model.glb'
 assert sha(blend)==generation['blend_sha256'] and sha(glb)==generation['glb_sha256']
 assert sha(Path(__file__).with_name('correct_solar_matrix_cap.py'))==generation['generator_sha256']
 bpy.ops.wm.open_mainfile(filepath=str(blend));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
 for name,expected in generation['retained_mesh_signatures'].items():assert signature(bpy.data.objects[name])==expected,name
 assert not any('turret' in o.name.lower() or 'laser' in o.name.lower() for o in meshes())
 assert 'Flush collector service cap' in bpy.data.objects
 native_bounds=bounds(meshes());assert abs(native_bounds[0][2])<1e-6
 names=[o.name for o in meshes()];rest={o.name:o.matrix_basis.copy() for o in scene.objects};expected={}
 for clip in generation['clips']:
  activate(clip['name'],rest);expected[clip['name']]={frame:pose(frame,names) for frame in range(1,62 if clip['name']=='CatalogueTurn' else 32)}
 activate('CatalogueTurn',rest);pose(1,names);camera_setup(scene,480);render_still(scene,out/'native-current.png')
 for obj in list(scene.objects):
  if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(glb));scene.frame_set(1);bpy.context.view_layer.update();rest={o.name:o.matrix_basis.copy() for o in scene.objects}
 assert set(names)=={o.name for o in meshes()}
 imported_bounds=bounds(meshes());assert max(abs(a-b) for p,q in zip(native_bounds,imported_bounds) for a,b in zip(p,q))<1e-4
 errors={}
 for clip in generation['clips']:
  activate(clip['name'],rest);maximum=0
  for frame,baseline in expected[clip['name']].items():
   current=pose(frame,names)
   for name in names:maximum=max(maximum,max(abs(a-b) for a,b in zip(baseline[name],current[name])))
  assert maximum<.0001,(clip['name'],maximum);errors[clip['name']]=maximum
 activate('CatalogueTurn',rest);pose(1,names);camera_setup(scene,480);render_still(scene,out/'imported-current.png')
 result=dict(issue=272,blend_sha256=sha(blend),glb_sha256=sha(glb),verifier_sha256=sha(__file__),generator_sha256=generation['generator_sha256'],retained_meshes=len(generation['retained_mesh_signatures']),native_bounds=native_bounds,imported_bounds=imported_bounds,maximum_import_matrix_error=errors,independent_pose_count=sum(len(p) for p in expected.values()),native_render_sha256=sha(out/'native-current.png'),imported_render_sha256=sha(out/'imported-current.png'),weapon_meshes=0,service_cap=True,scope='Actual canonical native/independent GLB runtime check; game-client integration remains separate.')
 (out/'runtime-verification.json').write_bytes((json.dumps(result,indent=2)+'\n').encode())
 print('CANONICAL_UNARMED_SOLAR_VERIFIED',errors,flush=True)

if __name__=='__main__':main()
