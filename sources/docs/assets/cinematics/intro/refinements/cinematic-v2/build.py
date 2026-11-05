"""Cinematic lighting/material pass; load the previous complete checkpoint, extract B/C/D."""
import bpy,sys,argparse,math
from pathlib import Path
from mathutils import Vector
ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);bpy.ops.wm.open_mainfile(filepath=str(a.input));keep=[s for s in bpy.data.scenes if s.name.startswith(('B — ','C — ','D — '))]
for s in list(bpy.data.scenes):
 if s not in keep:bpy.data.scenes.remove(s)
for s in keep:
 bpy.context.window.scene=s;s.render.resolution_x=1920;s.render.resolution_y=786;s.render.resolution_percentage=100;s.cycles.samples=128;s.cycles.use_denoising=True;s.cycles.adaptive_threshold=.025;s.cycles.max_bounces=8;s.view_settings.look='AgX - Medium High Contrast';s['iteration']='cinematic-v2; procedural physically shaded surfaces, no legacy bitmap textures'
def stone(m,base):
 m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;n.clear();out=n.new('ShaderNodeOutputMaterial');bs=n.new('ShaderNodeBsdfPrincipled');bs.inputs['Roughness'].default_value=.82;l.new(bs.outputs[0],out.inputs[0]);co=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1.1,1.1,3.8);l.new(co.outputs['Object'],mapping.inputs[0]);t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=1.9;t.inputs['Detail'].default_value=6;t.inputs['Roughness'].default_value=.73;l.new(mapping.outputs[0],t.inputs['Vector']);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.15;r.color_ramp.elements[0].color=(*[x*.5 for x in base],1);r.color_ramp.elements[1].position=.85;r.color_ramp.elements[1].color=(*[x*1.6 for x in base],1);l.new(t.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],bs.inputs['Base Color']);fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=95;fine.inputs['Detail'].default_value=3;l.new(co.outputs['Object'],fine.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.28;b.inputs['Distance'].default_value=.018;l.new(fine.outputs['Fac'],b.inputs['Height']);b2=n.new('ShaderNodeBump');b2.inputs['Strength'].default_value=.25;b2.inputs['Distance'].default_value=.075;l.new(t.outputs['Fac'],b2.inputs['Height']);l.new(b.outputs[0],b2.inputs['Normal']);l.new(b2.outputs[0],bs.inputs['Normal'])
for m in bpy.data.materials:
 if m.name.startswith('Terrain /'):stone(m,(.16,.19,.21))
 elif m.name.startswith('Asteroids /'):stone(m,(.065,.095,.105))
 elif m.name.startswith(('Refined base / stained','Boot / worn','Footprint / battered','Mechanical boots /')):
  bs=m.node_tree.nodes.get('Principled BSDF')
  if bs:bs.inputs['Roughness'].default_value=.38;bs.inputs['Metallic'].default_value=.65
  # Directional machining and oxide patches, not high-contrast camouflage.
  n=m.node_tree.nodes;l=m.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=35;t.inputs['Detail'].default_value=4;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.12;b.inputs['Distance'].default_value=.006;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
def area(s,name,loc,target,power,color,size):
 d=bpy.data.lights.new(name,'AREA');d.energy=power;d.color=color;d.shape='DISK';d.size=size;o=bpy.data.objects.new(name,d);s.collection.objects.link(o);o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
for s in keep[:2]:
 for o in s.objects:
  if o.type=='LIGHT':
   if o.data.type=='SUN':o.data.energy=2.4;o.data.angle=.035;o.data.color=(.69,.80,1);o.rotation_euler=(.6,-.8,-.5)
   else:o.data.energy*=.25
 s.world.node_tree.nodes['Background'].inputs[0].default_value=(.028,.045,.065,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.18
 area(s,'Cinematic / broad cold bounce',(0,-8,16),(0,5,0),1100,(.42,.63,1),18)
C=next(s for s in keep if s.name.startswith('C — '));area(C,'Cinematic / warm base spill',(5.7,8.5,7),(5.7,10.3,4),220,(1,.39,.12),3);area(C,'Cinematic / footprint edge light',(-5,-3,5),(0,0,-1),700,(.7,.85,1),5)
# Fine real geometric rubble catches key light and contact shadows.
bpy.context.window.scene=C
import random
rng=random.Random(2026);rock=bpy.data.materials['Terrain / worn fractured pale basalt']
for i in range(100):
 x,y=rng.uniform(-12,12),rng.uniform(-15,20)
 if abs(x)<3.0 and abs(y)<3:continue
 # Raycast against the evaluated terrain to seat debris on the surface.
 C.frame_set(681);bpy.context.view_layer.update();hit,loc,normal,_,_,_=C.ray_cast(bpy.context.evaluated_depsgraph_get(),Vector((x,y,40)),Vector((0,0,-1)))
 if not hit:continue
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rng.uniform(.04,.18),location=loc);o=bpy.context.object;o.name='Cinematic / loose basalt fragment';o.scale=(1,.7,.55);o.rotation_euler=(rng.random(),rng.random(),rng.random()*6);o.data.materials.append(rock)
m=bpy.data.scenes.new('MASTER — Cinematic BCD v2');m.render.engine='CYCLES';m.render.fps=24;m.frame_start=329;m.frame_end=826;m.render.resolution_x=1920;m.render.resolution_y=1440;m.render.resolution_percentage=100;m.render.image_settings.file_format='PNG';m.view_settings.view_transform='AgX';m.view_settings.look='AgX - Medium High Contrast';ed=m.sequence_editor_create();seq=ed.strips;shots=[]
for s,ch in zip(keep,[1,3,5]):shots.append(seq.new_scene(s.name,s,ch,s.frame_start))
for x,start,end,ch in [(0,397,430,4),(1,737,778,6)]:seq.new_effect(name='Preserved dissolve',type='CROSS',channel=ch,frame_start=start,frame_end=end,input1=shots[x],input2=shots[x+1])

for o in next(s for s in keep if s.name.startswith('B — ')).objects:
 if o.type=='MESH' and o.name.startswith(('Asteroid ','Foreground hero')):
  for face in o.data.polygons:face.use_smooth=True
bpy.context.window.scene=m;m.frame_set(545);bpy.context.preferences.filepaths.save_version=0;a.out.parent.mkdir(parents=True,exist_ok=True);bpy.ops.wm.save_as_mainfile(filepath=str(a.out),compress=True)
