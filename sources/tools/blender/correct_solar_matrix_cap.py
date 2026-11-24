"""Remove PB28's erroneous weapon assembly; verify and render all retained clips.

Protected PB31 and the separate legacy ST27 technical diagram are not inputs to
this focused physical-model repair. No panel/hinge or animation curve is edited.
"""
import argparse,hashlib,json,math,struct,subprocess,sys,tempfile
from pathlib import Path
import bpy
from mathutils import Vector

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def clean_png(path):
 data=Path(path).read_bytes();out=bytearray(data[:8]);offset=8
 while offset<len(data):
  size=struct.unpack_from('>I',data,offset)[0];end=offset+12+size
  if data[offset+4:offset+8] not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'}:out.extend(data[offset:end])
  offset=end
 Path(path).write_bytes(out)

def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']

def signature(obj):
 record=dict(vertices=[[round(x,7) for x in v.co] for v in obj.data.vertices],faces=[list(p.vertices) for p in obj.data.polygons],parent=obj.parent.name if obj.parent else None,parent_inverse=[[round(x,7) for x in row] for row in obj.matrix_parent_inverse])
 return hashlib.sha256(json.dumps(record,sort_keys=True).encode()).hexdigest()

def bounds(objects):
 points=[o.matrix_world@Vector(v) for o in objects for v in o.bound_box]
 return [[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]

def activate(clip,rest):
 for obj in bpy.context.scene.objects:
  if obj.name in rest:obj.matrix_basis=rest[obj.name].copy()
  if obj.animation_data:
   obj.animation_data.action=None
   for track in obj.animation_data.nla_tracks:track.mute=track.name!=clip;track.is_solo=False

def pose(frame,names):
 scene=bpy.context.scene;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame));bpy.context.view_layer.update()
 return {n:[v for row in bpy.data.objects[n].matrix_world for v in row] for n in names}

def camera_setup(scene,size):
 scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
 scene.render.resolution_x=scene.render.resolution_y=size;scene.render.resolution_percentage=100
 scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
 centre=Vector((0,0,1.7));direction=Vector((6,-10,7)).normalized()
 scene.camera.location=centre+direction*12;scene.camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
 scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=4.15

def render_still(scene,path):
 scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);clean_png(path)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 parser.add_argument('--ffmpeg',required=True)
 args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);root=args.root.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 bpy.context.preferences.filepaths.save_version=0
 source=root/'sources/objects/terran/solar-matrix/refined';media=out/'media';media.mkdir(exist_ok=True)
 sys.path.insert(0,str(root/'sources/ui/scitek/solar-matrix'))
 from export_solid import export_solid
 bpy.ops.wm.open_mainfile(filepath=str(source/'model.blend'));scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
 metadata=json.loads((source/'model.json').read_text());before=bounds(meshes())
 weapon=metadata['components'].get('laser-turret',[])
 assert len(weapon)==4,'Expected the specific erroneous PB28 weapon group'
 retained={o.name:signature(o) for o in meshes() if o.name not in weapon}
 original_rest={o.name:o.matrix_basis.copy() for o in scene.objects}
 original_animation={o.name:(o.animation_data.action,[(t,t.mute,t.is_solo) for t in o.animation_data.nla_tracks]) for o in scene.objects if o.animation_data}
 original_poses={}
 for clip_name in ['CatalogueTurn','PanelsClose','PanelsOpen']:
  activate(clip_name,original_rest);original_poses[clip_name]={frame:pose(frame,list(retained)) for frame in range(1,62 if clip_name=='CatalogueTurn' else 32)}
 for obj in scene.objects:
  obj.matrix_basis=original_rest[obj.name]
  if obj.name in original_animation:
   action,tracks=original_animation[obj.name];obj.animation_data.action=action
   for track,mute,solo in tracks:track.mute=mute;track.is_solo=solo
 scene.frame_set(1);bpy.context.view_layer.update()
 for name in weapon:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.105,depth=.025,location=(0,0,3.295))
 cap=bpy.context.object;cap.name='Flush collector service cap';cap.data.materials.append(bpy.data.materials['Research used matrix alloy'])
 cap.parent=bpy.data.objects['SolarMatrixRoot']
 metadata['components'].pop('laser-turret');metadata['components']['chassis'].append(cap.name)
 metadata.pop('technical_wires',None)
 metadata['phases']=[p for p in metadata.get('phases',[]) if p.get('component')!='laser-turret']
 metadata['correction_issue']='ender-dev-pl/openfa-assets#272'
 metadata['physical_variant']='Unprotected PB28: flush service cap, no weapon. Protected PB31 and legacy ST27 technical information are separate sources.'
 metadata['limitations'].append('The ST27 laser component must not be interpreted as installed on the unprotected PB28 physical model.')
 bpy.context.view_layer.update()
 for name,digest in retained.items():assert signature(bpy.data.objects[name])==digest,name
 after=bounds(meshes());assert abs(after[0][2]-before[0][2])<1e-6
 for axis in [0,1]:assert abs(after[0][axis]-before[0][axis])<1e-6 and abs(after[1][axis]-before[1][axis])<1e-6
 assert after[1][2]<before[1][2] and not any('laser' in o.name.lower() or 'turret' in o.name.lower() for o in meshes())
 blend=out/'model.blend';glb=out/'model.glb'
 bpy.ops.wm.save_as_mainfile(filepath=str(blend),compress=True)
 export_solid(bpy.data.objects['SolarMatrixRoot'],meshes(),glb)
 (out/'model.json').write_bytes((json.dumps(metadata,indent=2)+'\n').encode())
 raw=glb.read_bytes();doc=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
 clips=[]
 for i,a in enumerate(doc['animations']):
  accessors=[doc['accessors'][s['input']] for s in a['samplers']];start=min(v['min'][0] for v in accessors);end=max(v['max'][0] for v in accessors)
  clips.append(dict(index=i,name=a['name'],start=start,end=end,duration=end-start))
 assert {x['name'] for x in clips}=={'CatalogueTurn','PanelsClose','PanelsOpen'}
 rest={o.name:original_rest.get(o.name,o.matrix_basis).copy() for o in scene.objects};names=[o.name for o in meshes()];expected={};native_images={}
 camera_setup(scene,480)
 for clip in clips:
  activate(clip['name'],rest);expected[clip['name']]={}
  for frame in range(1,62 if clip['name']=='CatalogueTurn' else 32):
   expected[clip['name']][frame]=pose(frame,names)
   for name in retained:assert max(abs(a-b) for a,b in zip(original_poses[clip['name']][frame][name],expected[clip['name']][frame][name]))<1e-5,(clip['name'],frame,name,'Changed retained animation')
  for frame in [1,16,31]:
   pose(frame,names);p=media/f'native-{clip["name"]}-{frame:02}.png';render_still(scene,p);native_images[p.name]=sha(p)
 activate('CatalogueTurn',rest);pose(1,names);render_still(scene,media/'render.png')
 for obj in list(scene.objects):
  if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
 bpy.ops.import_scene.gltf(filepath=str(glb));scene.frame_set(1);bpy.context.view_layer.update();rest={o.name:o.matrix_basis.copy() for o in scene.objects}
 assert set(names)=={o.name for o in meshes()};errors={};previews=[]
 camera_setup(scene,480)
 for clip in clips:
  activate(clip['name'],rest);maximum=0
  for frame,baseline in expected[clip['name']].items():
   actual=pose(frame,names)
   for name in names:maximum=max(maximum,max(abs(a-b) for a,b in zip(baseline[name],actual[name])))
  assert maximum<.0001,(clip['name'],maximum);errors[clip['name']]=maximum
  for frame in [1,16,31]:pose(frame,names);render_still(scene,media/f'imported-{clip["name"]}-{frame:02}.png')
  camera_setup(scene,384);scene.render.film_transparent=False;scene.render.image_settings.color_mode='RGB'
  count=round(clip['duration']*24);poses=set()
  with tempfile.TemporaryDirectory(prefix='solar-frames-',dir=out) as temporary:
   frames=Path(temporary);assert frames.resolve().is_relative_to(out)
   for index in range(count):
    seconds=clip['start']+clip['duration']*index/(count-1);state=pose(seconds*15,names);poses.add(tuple(round(v,5) for m in state.values() for v in m))
    scene.render.filepath=str(frames/f'{index:04}.png');bpy.ops.render.render(write_still=True)
   video=media/f'animation-{clip["index"]:02}.webm'
   subprocess.run([args.ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate',str(count/clip['duration']),'-i',str(frames/'%04d.png'),'-frames:v',str(count),'-c:v','libvpx-vp9','-crf','30','-b:v','0','-deadline','good','-cpu-used','4','-threads','2','-pix_fmt','yuv420p','-an',str(video)],check=True)
  assert len(poses)>1
  previews.append(dict(**clip,video='gallery/media/objects/terran/solar-matrix/refined/'+video.name,sha256=sha(video),frames=count,fps=count/clip['duration'],distinct_pose_count=len(poses)))
  camera_setup(scene,480)
 manifest=dict(id='terran:solar-matrix',stage='shared-refined',glb='sources/objects/terran/solar-matrix/refined/model.glb',glb_sha256=sha(glb),blend_sha256=sha(blend),renderer='sources/tools/blender/correct_solar_matrix_cap.py',renderer_sha256=sha(__file__),clips=previews)
 (media/'animation-previews.json').write_bytes((json.dumps(manifest,indent=2)+'\n').encode())
 report=dict(issue=272,generator_sha256=sha(__file__),source_blend_sha256=sha(source/'model.blend'),blend_sha256=sha(blend),glb_sha256=sha(glb),removed_weapon_meshes=weapon,retained_mesh_signatures=retained,retained_animation_poses_verified=True,before_bounds=before,after_bounds=after,clips=clips,independent_pose_count=sum(len(v) for v in expected.values()),maximum_import_matrix_error=errors,native_render_sha256=native_images,note='Actual native and independent GLB pose/render checks. Protected PB31 and technical ST27 are unchanged. Game integration remains separate.')
 (out/'runtime-verification.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
 print('UNPROTECTED_SOLAR_VERIFIED',errors,flush=True)

if __name__=='__main__':main()
