"""Omit the transient projectile from the stationary loading-mechanism diagram."""
import bpy,json,sys,hashlib,shutil
from pathlib import Path
from mathutils import Vector,Matrix,kdtree
args=sys.argv[sys.argv.index('--')+1:];src,out=map(lambda p:Path(p).resolve(),args[:2]);out.mkdir(parents=True,exist_ok=True)
source=src/'missile-bay-extension.blend';bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['MissileBayRig'];model=json.loads((src/'model.json').read_text());names=sum(model['components'].values(),[])
def signature(ob):
 data=dict(vertices=[list(v.co) for v in ob.data.vertices] if ob.type=='MESH' else [],faces=[list(p.vertices) for p in ob.data.polygons] if ob.type=='MESH' else [],matrix=[list(r) for r in ob.matrix_basis],parent=ob.parent.name if ob.parent else None,materials=[m.name for m in ob.data.materials])
 return hashlib.sha256(json.dumps(data,sort_keys=True).encode()).hexdigest()
before={n:signature(bpy.data.objects[n]) for n in names};poses={}
for f in range(1,182):
 s.frame_set(f);bpy.context.view_layer.update();poses[f]={n:[v for row in bpy.data.objects[n].matrix_world for v in row] for n in names}
s.frame_set(1);bpy.context.view_layer.update();projectiles=[n for n in names if n.startswith('Lifted missile')];assert len(projectiles)==2
assert len(args)==3,'Supply the historical pre-feed source Blend as the third argument.'
historical=Path(args[2]).resolve();bpy.ops.wm.open_mainfile(filepath=str(historical));bpy.context.scene.frame_set(1);bpy.context.view_layer.update();edges=[]
for n in projectiles:
 ob=bpy.data.objects[n];edges.extend(tuple(ob.matrix_world@ob.data.vertices[i].co for i in edge.vertices) for edge in ob.data.edges)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['MissileBayRig']
tree=kdtree.KDTree(len(edges))
for i,(a,b) in enumerate(edges):tree.insert((a+b)*.5,i)
tree.balance();wire=bpy.data.objects['missile-loading-assembly technical wire'];old=wire.data;curve=bpy.data.curves.new('Loading mechanism without transient projectile','CURVE');curve.dimensions='3D';curve.bevel_depth=old.bevel_depth;curve.bevel_resolution=old.bevel_resolution
for mat in old.materials:curve.materials.append(mat)
removed=0
for sp in old.splines:
 assert sp.type=='POLY' and len(sp.points)==2;a,b=[wire.matrix_world@Vector(p.co[:3]) for p in sp.points];errors=[]
 for _,i,_ in tree.find_range((a+b)*.5,2e-5):
  c,d=edges[i];errors.append(min(max((a-c).length,(b-d).length),max((a-d).length,(b-c).length)))
 if errors and min(errors)<2e-5:removed+=1;continue
 new=curve.splines.new('POLY');new.points.add(1)
 for p,q in zip(new.points,sp.points):p.co=q.co
assert removed==176 and len(curve.splines)==400,(removed,len(curve.splines));wire.data=curve;bpy.data.curves.remove(old)
for f in poses:
 s.frame_set(f);bpy.context.view_layer.update();assert poses[f]=={n:[v for row in bpy.data.objects[n].matrix_world for v in row] for n in names}
s.frame_set(1);bpy.context.view_layer.update();assert before=={n:signature(bpy.data.objects[n]) for n in names}
bpy.ops.wm.save_as_mainfile(filepath=str(out/source.name));shutil.copy2(src/'missile-bay-extension.glb',out/'missile-bay-extension.glb')
model['technical_omitted_physical_nodes']=projectiles;model['technical_projectile_contract']='Transient carried missile remains in the180-frame solid mechanism; omitted from stationary technical mechanism diagrams. Old176 projectile segments removed;400 loading-hardware segments retained.'
(out/'model.json').write_text(json.dumps(model,indent=2)+'\n',encoding='utf-8');rig=json.loads((src/'solid-animation-timeline.json').read_text());rig['source_blend_sha256']=hashlib.sha256((out/source.name).read_bytes()).hexdigest();(out/'solid-animation-timeline.json').write_text(json.dumps(rig,separators=(',',':'))+'\n',encoding='utf-8')
proof=dict(previous_source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),source_sha256=rig['source_blend_sha256'],glb_sha256=hashlib.sha256((out/'missile-bay-extension.glb').read_bytes()).hexdigest(),physical_signatures=before,all181_physical_world_poses_unchanged=True,colour_glb_bytes_unchanged=True,transient_projectile_omitted_from_technical=projectiles,old_projectile_segments_removed=removed,loading_hardware_segments_retained=400,source_reference='_SCITEK/ST14.VID: technical loading study selects the blast doors and hydraulic mechanism; colour _MA/ST14.VID retains carried-projectile choreography.')
(out/'technical-refinement-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');s.render.filepath=str(out/'reload-solid.png');bpy.ops.render.render(write_still=True);print('BAY_TECHNICAL_PROJECTILE_REFINED',removed)
