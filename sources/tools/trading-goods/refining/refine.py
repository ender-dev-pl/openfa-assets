"""Role-aware physically shaded refinement of preserved trading-good models."""
import bpy,bmesh,sys,argparse,json,math,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.noise import noise_vector
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,required=True);ap.add_argument('--items',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args(sys.argv[sys.argv.index('--')+1:]);coverage=json.loads((a.repo/'docs/trading-goods/coverage.json').read_text())['items']
def put(bs,name,value):
 if name in bs.inputs:bs.inputs[name].default_value=value

def role(number,name,bs):
 s=name.lower()
 if number==38 and 'wood' in s:return 'metal'
 if number==46:return 'organic'
 if number==62 and 'wood' not in s:return 'paper'
 if number==73 and 'pale medical' in s:return 'paper'
 if number==71 and 'red markings' in s:return 'paper'
 if any(w in s for w in ['printed','label','sticker','paper']):return 'paper'
 if any(w in s for w in ['leather','folio cover']):return 'leather'
 if 'wood' in s or number in [55,59] and ('case' in s or 'lacquer' in s):return 'wood'
 if any(w in s for w in ['woven','cloth','sack','selvage','rolled edge']):return 'fabric'
 if 'pearl' in s or number==33:return 'pearl'
 if number in range(25,38) or any(w in s for w in ['jewel','cabochon','raw opal','colour play']):return 'gem'
 if any(w in s for w in ['glass','crystal','tinted bottle','holographic globe','photoplasmic shell']):return 'glass'
 if 'mineral' in s:return 'stone'
 if 'water storage tanks' in s:return 'metal'
 if number==46 and 'ivory' in s:return 'organic'
 if any(w in s for w in ['mushroom','seaweed','kernels','husk','huskar leaf','cheese','chocolate','egg shell','organic']):return 'organic'
 if any(w in s for w in ['horn','ivory']):return 'horn'
 if 'graphite' in s or 'nozzle' in s or 'refractory' in s:return 'carbon'
 if 'ceramic' in s:return 'ceramic'
 if any(w in s for w in ['enamel','lacquer','container','shell','case','flask','restraint','markings','band']):return 'paint'
 if any(w in s for w in ['metal','alloy','gold','silver','bronze','copper','brass','titanium','foil','pewter','platinum','fittings','machined']):return 'metal'
 if bs.inputs['Transmission Weight'].default_value>.1:return 'glass'
 return 'paint'

def material(m,number,scale):
 old=m.node_tree.nodes.get('Principled BSDF') if m.use_nodes else None
 if old is None:return None
 c=tuple(old.inputs['Base Color'].default_value[:3]);c=tuple(v*.65 for v in c) if 'cheese wax' in m.name.lower() else c;em=tuple(old.inputs['Emission Color'].default_value[:3]);strength=old.inputs['Emission Strength'].default_value;r=role(number,m.name,old);n=m.node_tree.nodes;l=m.node_tree.links;n.clear();bs=n.new('ShaderNodeBsdfPrincipled');bs.name='Principled BSDF';out=n.new('ShaderNodeOutputMaterial');l.new(bs.outputs[0],out.inputs['Surface']);put(bs,'Base Color',(*c,1));put(bs,'Emission Color',(*em,1));put(bs,'Emission Strength',strength);put(bs,'Coat Weight',0);put(bs,'IOR',1.48)
 rough={'metal':.36,'paint':.48,'glass':.065,'gem':.035,'pearl':.22,'fabric':.84,'leather':.58,'wood':.57,'organic':.55,'horn':.40,'paper':.90,'stone':.76,'carbon':.73,'ceramic':.30}[r];rough=.78 if r=='organic' and 'mushroom' in m.name.lower() else .34 if r=='organic' and 'egg shell' in m.name.lower() else .42 if r=='organic' and 'kernels' in m.name.lower() else .68 if 'cheese interior' in m.name.lower() else .42 if 'cheese wax' in m.name.lower() else rough;rough={9:.92,10:.50,11:.45,12:.72,13:.38,14:.92,15:.92}.get(number,rough) if r=='fabric' else rough;put(bs,'Roughness',rough);put(bs,'Metallic',.92 if r=='metal' else .08 if r=='carbon' else 0)
 tex=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,1,1)
 if r=='metal':mapping.inputs[1].default_value=(24,24,.45);put(bs,'Anisotropic IOR Level',.35)
 if r=='wood':mapping.inputs[1].default_value=(.22,6,6)
 l.new(tex.outputs['Object'],mapping.inputs[0]);coarse=n.new('ShaderNodeTexNoise');coarse.name='Natural low-amplitude surface variation';coarse.inputs['Scale'].default_value=5 if r=='wood' else 10;coarse.inputs['Detail'].default_value=4;coarse.inputs['Roughness'].default_value=.72;l.new(mapping.outputs[0],coarse.inputs['Vector']);ramp=n.new('ShaderNodeMapRange');ramp.inputs['To Min'].default_value=max(.015,rough*.73);ramp.inputs['To Max'].default_value=min(1,rough*1.23);l.new(coarse.outputs['Fac'],ramp.inputs['Value']);l.new(ramp.outputs['Result'],bs.inputs['Roughness'])
 if r not in ['gem','glass','pearl']:
  cr=n.new('ShaderNodeValToRGB');cr.name='Subtle colour variation, not painted camouflage';cr.color_ramp.elements[0].position=.12;cr.color_ramp.elements[0].color=(*[v*(.92 if r=='fabric' else .78) for v in c],1);cr.color_ramp.elements[1].position=.88;cr.color_ramp.elements[1].color=(*[min(1,v*(1.03 if r=='fabric' else 1.08)) for v in c],1);l.new(coarse.outputs['Fac'],cr.inputs[0]);l.new(cr.outputs[0],bs.inputs['Base Color'])
 fine=n.new('ShaderNodeTexNoise');fine.name='Microscopic pores and machining';fine.inputs['Scale'].default_value=210 if r in ['fabric','paper'] else 120;fine.inputs['Detail'].default_value=2;l.new(mapping.outputs[0],fine.inputs['Vector']);b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.20 if r not in ['glass','gem','pearl'] else .018;b.inputs['Distance'].default_value=scale*(.00035 if r not in ['paper','glass','gem','pearl'] else .00008);l.new(fine.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
 if r in ['glass','gem']:
  put(bs,'Transmission Weight',.98);put(bs,'IOR',2.417 if number==25 else 1.77 if number in [27,28] else 1.60 if r=='gem' else 1.46);put(bs,'Base Color',(*[.38+.60*v for v in c],1));vol=n.new('ShaderNodeVolumeAbsorption');vol.inputs['Color'].default_value=(*[.08+.90*v for v in c],1);vol.inputs['Density'].default_value=.32 if r=='glass' else .18;l.new(vol.outputs[0],out.inputs['Volume']);put(bs,'Coat Weight',.05)
 if r=='fabric':
  put(bs,'Sheen Tint',(*c,1));put(bs,'Sheen Weight',.75 if number in [9,15] else .30);put(bs,'Sheen Roughness',.65);put(bs,'Tangent',(1,0,0));put(bs,'Anisotropic IOR Level',.65 if number in [10,11,13] else 0);wave=n.new('ShaderNodeTexWave');wave.bands_direction='X';wave.inputs['Scale'].default_value=35 if number in [10,11,13] else 22;wave.inputs['Distortion'].default_value=2;l.new(tex.outputs['Object'],wave.inputs['Vector']);w=n.new('ShaderNodeBump');w.inputs['Strength'].default_value=.24;w.inputs['Distance'].default_value=scale*(.00065 if number in [10,11,13] else .0010);cross=n.new('ShaderNodeTexWave');cross.bands_direction='Y';cross.inputs['Scale'].default_value=35 if number in [10,11,13] else 22;l.new(tex.outputs['Object'],cross.inputs['Vector']);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(wave.outputs['Color'],mul.inputs[0]);l.new(cross.outputs['Color'],mul.inputs[1]);l.new(mul.outputs[0],w.inputs['Height']);l.new(b.outputs[0],w.inputs['Normal']);l.new(w.outputs[0],bs.inputs['Normal'])
 if r in ['organic','horn','pearl']:
  put(bs,'Subsurface Weight',.035 if 'cheese wax' in m.name.lower() else .12 if r=='organic' else .055);put(bs,'Subsurface Radius',(.35,.18,.08));put(bs,'Coat Weight',.35 if r=='pearl' else .04);put(bs,'Coat Roughness',.18)
 if r=='leather':
  pores=n.new('ShaderNodeTexVoronoi');pores.inputs['Scale'].default_value=55;b.inputs['Strength'].default_value=.38;b.inputs['Distance'].default_value=scale*.0018;l.new(tex.outputs['Object'],pores.inputs['Vector']);l.new(pores.outputs['Distance'],b.inputs['Height']);put(bs,'Sheen Weight',.13)
 if r=='paint':put(bs,'Coat Weight',.10);put(bs,'Coat Roughness',.30)
 if r=='wood':
  b.inputs['Distance'].default_value=scale*.0008
  if number in [55,59]:put(bs,'Coat Weight',.25);put(bs,'Coat Roughness',.25)
 m['physical_surface_role']=r;m['refinement']='role-aware PBR pass 2';return dict(name=m.name,role=r,roughness=rough,base_colour=list(bs.inputs['Base Color'].default_value),micro_relief_distance=b.inputs['Distance'].default_value)

for number in map(int,a.items.split(',')):
 item=coverage[number-1];ident=item['legacy_stem'];source=a.repo/item['native'];source_hash=hashlib.sha256(source.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;bpy.context.view_layer.update();points=[o.matrix_world@v.co for o in s.objects if o.type=='MESH' for v in o.data.vertices];span=max(max(p[i] for p in points)-min(p[i] for p in points) for i in range(3));used={m for o in s.objects if o.type in ['MESH','CURVE','FONT'] for m in o.data.materials};materials=[entry for m in sorted(used,key=lambda m:m.name) if (entry:=material(m,number,span))]
 if number==48:
  wheel=next(o for o in s.objects if o.name.endswith('whole cheese wheel with removed wedge'));wheel.data=wheel.data.copy();bm=bmesh.new();bm.from_mesh(wheel.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(wheel.data);bm.free()
  holes=[o for o in s.objects if 'cheese cut-face hole' in o.name]
  for proxy in holes:
   co=proxy.location.copy();co.y=math.tan(.45)*co.x;bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1,location=co);cutter=bpy.context.object;cutter.scale=(.055,.065,.055)
   for m in wheel.data.materials:cutter.data.materials.append(m)
   for face in cutter.data.polygons:face.material_index=1
   mod=wheel.modifiers.new('Actual cheese cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.context.view_layer.objects.active=wheel;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);bpy.data.objects.remove(proxy,do_unlink=True)
  for face in wheel.data.polygons:face.use_smooth=True
  split=wheel.modifiers.new('Keep planar cuts and smooth round wax wall','EDGE_SPLIT');split.split_angle=math.radians(35)
  bevel=wheel.modifiers.new('Soft wax edge radius','BEVEL');bevel.width=span*.0018;bevel.segments=2
 for o in s.objects:
  if o.type!='MESH':continue
  if 'inventory sticker' in o.name:
   o.data=o.data.copy()
   for v in o.data.vertices:v.co.x*=1.065;v.co.y*=1.065
  roles={m.get('physical_surface_role') for m in o.data.materials}
  if roles.intersection({'organic','horn','stone','fabric'}):
   o.data=o.data.copy();o.data.update();radius=max((v.co.length for v in o.data.vertices),default=1);amount=radius*(.001 if 'fabric' in roles else .0035);seed=(int(hashlib.sha256(o.name.encode()).hexdigest()[:6],16)%1000)*.017
   for v in o.data.vertices:v.co+=v.normal*amount*noise_vector(v.co*9+Vector((seed,3.1,2.2))).x
  if roles.intersection({'metal','paint','ceramic','carbon'}) and len(o.data.polygons)<1800:
   if not any(mod.type=='BEVEL' for mod in o.modifiers):
    mod=o.modifiers.new('Small manufactured edge radius','BEVEL');mod.width=span*.0014;mod.segments=2;mod.limit_method='ANGLE'
   for p in o.data.polygons:
    if len(p.vertices)>4:p.use_smooth=False
 s['refinement']='PBR pass 2; original checkpoint preserved';s['baseline_native_sha256']=source_hash;s.render.filepath='//renders/';bpy.context.preferences.filepaths.save_version=0;out=a.out/ident;out.mkdir(parents=True,exist_ok=True);native=out/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
 # GLB deliberately carries physical scalar/base-colour values; native procedural graphs stay intact.
 for m in used:
  bs=m.node_tree.nodes.get('Principled BSDF')
  if not bs:continue
  for name in ['Base Color','Roughness','Normal']:
   for link in list(bs.inputs[name].links):m.node_tree.links.remove(link)
 for o in list(s.objects):
  if o.type in ['CURVE','FONT']:
   bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
 bpy.ops.export_scene.gltf(filepath=str(out/(ident+'.glb')),export_format='GLB',export_animations=False,export_apply=True,export_cameras=False,export_lights=False)
 (out/'refinement.json').write_text(json.dumps(dict(item_id=item['id'],legacy_stem=ident,baseline_native=item['native'],baseline_native_sha256=source_hash,builder_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),refined_native_sha256=hashlib.sha256(native.read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/(ident+'.glb')).read_bytes()).hexdigest(),materials=materials,glb_materials='Scalar/base-colour fallback; procedural shader baking deferred',model_geometry='Original parts retained with small manufactured edge radii; deterministic normal displacement on organic, horn, stone and fabric meshes; cask label placement corrected; cheese proxy holes replaced by actual cavities where applicable'),indent=2)+'\n');assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash;print('REFINED_MODEL_BUILT',ident,flush=True)
