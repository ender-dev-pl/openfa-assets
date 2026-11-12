"""Runtime shape checks for the reported annular-neck/roof-intersection defect."""
import bpy,json,sys,math,hashlib
from pathlib import Path
from mathutils import Vector
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(out/'repair-facility.blend'));s=bpy.context.scene;s.frame_set(1)
roof=bpy.data.objects['Workshop gold roof'];checks={}
for i in range(4):
    ob=bpy.data.objects['Research data dish '+str(i)];hits=[]
    for radius in [0,.028,.056,.084,.105]:
        hit,point,normal,index=ob.ray_cast(Vector((radius,0,.25)),Vector((0,0,-1)))
        assert hit,(ob.name,radius,'reflector hole')
        hits.append(float(point.z))
    assert all(b>a+1e-4 for a,b in zip(hits,hits[1:])),(ob.name,'not a continuous concave bowl',hits)
    hit,back,_,_=ob.ray_cast(Vector((0,0,-.003)),Vector((0,0,-1)))
    assert hit and .004<hits[0]-back.z<.006,(ob.name,'centre wall is not thin')
    assert .075<hits[-1]-hits[0]<.10,(ob.name,'reflector is too shallow for ST22')
    clearances=[]
    # The entire object is the thin reflector. There is no separate stalk.
    assert len(ob.data.vertices)==578,(ob.name,'unexpected stalk geometry')
    for v in ob.data.vertices[:578]:
        world=ob.matrix_world@v.co
        origin=roof.matrix_world.inverted()@Vector((world.x,world.y,5))
        direction=roof.matrix_world.inverted().to_3x3()@Vector((0,0,-1))
        ok,p,_,_=roof.ray_cast(origin,direction)
        if ok:clearances.append(float(world.z-(roof.matrix_world@p).z))
    assert clearances and .0005<min(clearances)<.004,(ob.name,'reflector must nearly touch the dome without intersecting',min(clearances))
    checks[ob.name]=dict(front_radial_ray_heights=hits,centre_wall_thickness=hits[0]-float(back.z),minimum_reflector_roof_clearance=min(clearances))

# Present the same dish in the exact closeup pose used by the wire presentation.
model=json.loads((out/'model.json').read_text());phase=model['phases'][0];root=bpy.data.objects['RepairFacilityRoot'];root.animation_data_clear();root.rotation_euler=phase['closeup_rotation_euler'];target=root.rotation_euler.to_matrix()@Vector(phase['local_target'])
s.camera.location=(target.x,target.y-12,target.z+.15);s.camera.rotation_euler=(target-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=phase['ortho_scale'];s.render.resolution_x=s.render.resolution_y=640;s.cycles.samples=16
# Isolate the selected reflector so the other three transparent wire dishes
# cannot overlap it in this shape-inspection pair. Full films retain all parts.
selected=bpy.data.objects['Research data dish 3']
for ob in s.objects:
    if ob.type=='MESH':ob.hide_render=ob!=selected
s.render.filepath=str(out/'dish-solid-closeup.png');bpy.ops.render.render(write_still=True)
wire=bpy.data.objects['four-data-dishes technical wire']
wire.data=wire.data.copy();assert len(wire.data.splines)%4==0
per_dish=len(wire.data.splines)//4
for index in reversed(range(3*per_dish)):wire.data.splines.remove(wire.data.splines[index])
for ob in s.objects:
    if ob.type=='MESH':ob.hide_render=True
    if ob.type=='CURVE':ob.hide_render=ob!=wire
s.view_settings.view_transform='Standard';s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=0
s.render.filepath=str(out/'dish-wire-closeup.png');bpy.ops.render.render(write_still=True)
centre=selected.matrix_world@Vector((0,0,0));direction=selected.matrix_world.to_3x3()@Vector((0,-1,.20));direction.normalize()
s.camera.location=centre+direction*12;s.camera.rotation_euler=(centre-s.camera.location).to_track_quat('-Z','Y').to_euler();s.camera.data.ortho_scale=.32
s.render.filepath=str(out/'dish-wire-side.png');bpy.ops.render.render(write_still=True)
wire.hide_render=True;selected.hide_render=False;s.view_settings.view_transform='AgX';s.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.35
s.render.filepath=str(out/'dish-solid-side.png');bpy.ops.render.render(write_still=True)
(out/'dish-shape-verification.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256((out/'repair-facility.blend').read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),runtime_front_and_back_rays=True,solid_and_wire_same_geometry=True,dishes=checks,reference='Actual PB15 colour and ST22 decoded updates3/34/63; visual comparison required, not established by numeric export checks.'),indent=2)+'\n')
print('REPAIR_DISH_SHAPE_VERIFIED',min(x['minimum_reflector_roof_clearance'] for x in checks.values()))
