"""Actual native/import mouth rays, lower-engine contacts and retained sockets."""
import bpy,sys,json,hashlib
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index('--')+1:];out,base=map(lambda x:Path(x).resolve(),args[:2])
bpy.ops.wm.open_mainfile(filepath=str(base));s=bpy.context.scene;s.frame_set(1);oldroot=bpy.data.objects['PlacementRoot'];sockets={o.name:[list(row) for row in o.matrix_world] for o in oldroot.children_recursive if o.type=='EMPTY'};assert len(sockets)>=8
def hit(ob,origin,direction):
 inv=ob.matrix_world.inverted();ok,p,normal,index=ob.ray_cast(inv@origin,(inv.to_3x3()@direction).normalized())
 return ob.matrix_world@p if ok else None
def inside(ob,p):
 direction=Vector((.173,.291,.941)).normalized();count=0;origin=p.copy()
 for i in range(100):
  found=hit(ob,origin,direction)
  if found is None:return count%2==1
  count+=1;origin=found+direction*1e-5
 raise AssertionError('ray did not escape '+ob.name)
reports={}
for imported in [False,True]:
 if imported:
  bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(out/'command-cruiser.glb'))
 else:bpy.ops.wm.open_mainfile(filepath=str(out/'command-cruiser.blend'))
 s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update();root=bpy.data.objects['CommandCruiserRoot'];errors=[]
 for name,matrix in sockets.items():
  ob=bpy.data.objects[name];assert ob.parent==root;errors.append(max(abs(ob.matrix_world[i][j]-matrix[i][j]) for i in range(4) for j in range(4)))
 assert max(errors)<1e-6
 meshes=[o for o in s.objects if o.type=='MESH'];rays=[]
 for x,z,nozzle,throat in [(-.30,-.10,'Command Cruiser exhaust -1','Command Cruiser exhaust throat -1'),(.30,-.10,'Command Cruiser exhaust 1','Command Cruiser exhaust throat 1'),(0,.25,'Ancillary thruster 1 hollow exhaust','Ancillary thruster 1 recessed throat'),(0,-.45,'Ancillary thruster 2 hollow exhaust','Ancillary thruster 2 recessed throat')]:
  origin=Vector((x,3,z));direction=Vector((0,-1,0));assert hit(bpy.data.objects[nozzle],origin,direction) is None,nozzle
  hits=[(o.name,p) for o in meshes if (p:=hit(o,origin,direction)) is not None];first=max(hits,key=lambda row:row[1].y);assert first[0]==throat,(nozzle,first)
  rays.append(dict(nozzle=nozzle,first_hit=throat,throat_y=first[1].y))
 support=bpy.data.objects['Ancillary lower thruster hull attachment'];hull=bpy.data.objects['Command Cruiser continuous faceted hull'];housing=bpy.data.objects['Ancillary thruster 2 housing']
 top=Vector((0,1.80,-.25));bottom=Vector((0,1.80,-.35));assert inside(support,top) and inside(hull,top),'hull support contact';assert inside(support,bottom) and inside(housing,bottom),'engine support contact'
 reports['imported' if imported else 'native']=dict(socket_count=len(sockets),socket_matrix_max_error=max(errors),clear_mouth_rays=rays,lower_engine_support_contacts_verified=True)
(out/'anatomy-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((out/'command-cruiser.blend').read_bytes()).hexdigest(),glb_sha256=hashlib.sha256((out/'command-cruiser.glb').read_bytes()).hexdigest(),checks=reports,sockets=sockets),indent=2)+'\n',encoding='utf-8');print('COMMAND_ANATOMY_VERIFIED')
