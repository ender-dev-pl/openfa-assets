"""Replace the PB08 perimeter fence with four small, low service access points."""
import argparse,json,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from correct_terran_mines import bounds,meshes,signature,box,cylinder,render,clean_render,sha,evaluated_triangles,PREFIX


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.open_mainfile(filepath=str(args.input))
 assert not any('point service' in o.name for o in meshes()),'Use the outgoing fenced model once'
 old=bounds(meshes());retained={o.name:signature(o) for o in meshes() if o.get('mine_correction_role')!='utility'}
 removed=[]
 for obj in list(meshes()):
  if obj.get('mine_correction_role')=='utility':removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
 assert any('fence' in x for x in removed)
 steel=bpy.data.materials['Mine correction | used steel'];dark=bpy.data.materials['Mine correction | dark housing'];grime=bpy.data.materials['Mine correction | joint dirt']
 cx,cy=[(old[0][i]+old[1][i])/2 for i in range(2)]
 # Separate access covers for buried service lines. Four compact extremities,
 # no perimeter rails, continuous outline, visible cable loop or bright markers.
 devices=[('west',(old[0][0]+.09,cy+.26),(.18,.22,.12)),
          ('east',(old[1][0]-.09,cy-.29),(.18,.22,.12)),
          ('south',(cx+.27,old[0][1]+.10),(.22,.20,.105)),
          ('north',(cx-.28,old[1][1]-.10),(.22,.20,.105))]
 for label,(x,y),(w,d,h) in devices:
  box('point service '+label+' dirty plinth',(x,y,.012),(w,d,.024),grime)
  box('point service '+label+' housing',(x,y,h/2),(w,d,h),dark)
  box('point service '+label+' steel lid',(x,y,h+.006),(w-.018,d-.018,.012),steel)
  box('point service '+label+' recessed seam',(x,y,h+.0125),(.008,d-.038,.001),dark)
  for dx,dy in [(-1,-1),(1,1)]:
   cylinder('point service '+label+' lid fastener',(x+dx*(w/2-.028),y+dy*(d/2-.028),h+.013),.007,.003,steel,'utility',vertices=8)
  box('point service '+label+' worn corner',(x-w*.25,y-d*.30,h+.0125),(.018,.009,.001),steel)
 bpy.context.view_layer.update()
 new=bounds(meshes());assert max(abs(a-b) for r,s in zip(old,new) for a,b in zip(r,s))<.00001,(old,new)
 for name,digest in retained.items():assert signature(bpy.data.objects[name])==digest,name
 assert not any('fence' in o.name.lower() for o in meshes())
 args.output.mkdir(parents=True,exist_ok=True);media=args.output/'media';media.mkdir(exist_ok=True)
 scene=bpy.context.scene;scene['mine_point_utilities_issue']='ender-dev-pl/openfa-assets#271'
 bpy.ops.wm.save_as_mainfile(filepath=str(args.output/'model.blend'),compress=True)
 bpy.ops.object.select_all(action='DESELECT')
 for obj in meshes():obj.select_set(True)
 bpy.ops.export_scene.gltf(filepath=str(args.output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=False,export_yup=True)
 for name,a in [('front-quarter',-60),('rear-quarter',120)]:render(scene,media/(name+'.png'),a,(cx,cy,.85),4.25)
 scene.camera.location=(0,0,10);scene.camera.rotation_euler=(0,0,0);scene.camera.data.ortho_scale=3.75
 scene.render.filepath=str(media/'top.png');bpy.ops.render.render(write_still=True);clean_render(media/'top.png')
 report=dict(format='terran-mine-point-utility-correction-v1',issue=271,identity='terran:mine',source_sha256=sha(args.input),
  generator_sha256=sha(__file__),base_generator_sha256=sha(Path(__file__).with_name('correct_terran_mines.py')),
  blend_sha256=sha(args.output/'model.blend'),glb_sha256=sha(args.output/'model.glb'),original_bounds=old,bounds=new,footprint=[2,2],
  unchanged_original_meshes=retained,removed_utility_meshes=removed,added_meshes=[o.name for o in meshes() if 'point service' in o.name],
  mesh_objects=len(meshes()),triangles=evaluated_triangles(meshes()),native_renders={n:sha(media/(n+'.png')) for n in ['front-quarter','rear-quarter','top']},
  utility_contract=dict(installation_count=4,maximum_height=.14,continuous_perimeter=False,retained_structure_scale=.75),
  note='Four low service access points preserve the previous envelope and every retained deck/trestle/drill mesh. No PB13 geometry or gameplay changes.')
 (args.output/'correction.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
 print('POINT_UTILITIES_GENERATED',report['mesh_objects'],report['triangles'],flush=True)


if __name__=='__main__':main()
