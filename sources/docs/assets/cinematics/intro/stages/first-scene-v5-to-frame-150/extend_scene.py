import bpy,json,hashlib,shutil
import numpy as np
from pathlib import Path
from mathutils import Matrix,Vector,Quaternion
p=Path(__file__).resolve().parent;old=p.parent/'first-scene-v4-ship-fit';s=bpy.context.scene;d=json.loads((p/'extension-poses.json').read_text());ship=next(o for o in s.objects if o.name.startswith('SHIP —'));cam=Matrix(d['camera_world']);s.frame_set(192);previous=ship.rotation_quaternion.copy()
for row in d['poses']:
 x,y,z,w=row['rotation'];q=cam.to_quaternion()@Quaternion((w,x,y,z))
 if previous.dot(q)<0:q.negate()
 previous=q.copy();ship.rotation_quaternion=q;ship.location=cam@Vector(row['translation']);ship.keyframe_insert('location',frame=row['frame']);ship.keyframe_insert('rotation_quaternion',frame=row['frame'])
for fc in ship.animation_data.action.fcurves:
 for key in fc.keyframe_points:key.interpolation='LINEAR'
nebula=next(o for o in s.objects if o.name.startswith('Following shot — nebula'));vis=nebula.active_material.node_tree.nodes['Nebula reveal / 24 fps']
for f,v in [(209,1),(217,.85),(225,.4),(237,0),(302,0)]:
 vis.outputs[0].default_value=v;vis.outputs[0].keyframe_insert('default_value',frame=f)
collection=bpy.data.collections.new('05 — Spiral galaxy transition / independent procedural fields');s.collection.children.link(collection)
def field(name,filename,keys):
 rgba=np.load(p/filename);h,w=rgba.shape[:2];image=bpy.data.images.new(name,width=w,height=h,float_buffer=True);image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(rgba.ravel());image.file_format='OPEN_EXR';image.filepath_raw=str(p/(filename.replace('.npy','.exr')));image.save();image.pack()
 mat=bpy.data.materials.new(name+' / camera emission');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;n.clear();tex=n.new('ShaderNodeTexImage');tex.image=image;tex.interpolation='Linear';uv=n.new('ShaderNodeTexCoord');l.new(uv.outputs['UV'],tex.inputs['Vector']);em=n.new('ShaderNodeEmission');l.new(tex.outputs['Color'],em.inputs['Color']);value=n.new('ShaderNodeValue');value.name='Shot dissolve'
 for f,v in keys:value.outputs[0].default_value=v;value.outputs[0].keyframe_insert('default_value',frame=f)
 l.new(value.outputs[0],em.inputs['Strength']);tr=n.new('ShaderNodeBsdfTransparent');add=n.new('ShaderNodeAddShader');l.new(tr.outputs[0],add.inputs[0]);l.new(em.outputs[0],add.inputs[1]);lp=n.new('ShaderNodeLightPath');mix=n.new('ShaderNodeMixShader');l.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);l.new(tr.outputs[0],mix.inputs[1]);l.new(add.outputs[0],mix.inputs[2]);out=n.new('ShaderNodeOutputMaterial');l.new(mix.outputs[0],out.inputs['Surface'])
 obj=nebula.copy();obj.data=nebula.data.copy();obj.name=name;obj.data.materials.clear();obj.data.materials.append(mat);collection.objects.link(obj);obj.location.z=-42.6 if 'next-cloud' in filename else -42.8;obj.scale=(17.04,14.91,1) if 'next-cloud' in filename else (17.12,14.98,1);obj['provenance']='Independent mathematical synthesis; regenerate using prepare_extension.py. No original video pixels sampled.';return obj
field('Spiral galaxy — dusty elliptical arms, cyan core and diffraction','procedural-galaxy.npy',[(1,0),(209,0),(217,.25),(225,.65),(237,1),(289,1),(302,.78)])
field('Next dissolve — faint turquoise filaments','procedural-next-cloud.npy',[(1,0),(289,0),(302,.48)])
s.frame_end=302;s['source_frame_range']='Original zero-based frames 0..150 inclusive';s['last_half_frame']='Original frame 150 held for the second 24fps sample';s.frame_set(241)
scene=p/'opening-to-frame-150.blend';bpy.ops.wm.save_as_mainfile(filepath=str(scene))
# Earlier images remain identical by construction: poses retained and new fields at zero strength.
frames=p/'rendered-frames';frames.mkdir(exist_ok=True);state={'scene_sha256':hashlib.sha256(scene.read_bytes()).hexdigest(),'completed':{},'reused_from_v4':192}
for i in range(192):
 src=old/'rendered-frames'/f'frame-{i:06d}.png';dst=frames/src.name
 if not dst.exists():shutil.copyfile(src,dst)
 state['completed'][str(i)]=hashlib.sha256(dst.read_bytes()).hexdigest()
(p/'render-state.json').write_text(json.dumps(state,indent=2)+'\n')
s.render.resolution_x=640;s.render.resolution_y=560;s.cycles.samples=16;(p/'preview').mkdir(exist_ok=True)
for n in [100,110,120,140,150]:
 s.frame_set(n*2+1);s.render.filepath=str(p/'preview'/f'frame-{n:03d}.png');bpy.ops.render.render(write_still=True)
