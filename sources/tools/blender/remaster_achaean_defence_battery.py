"""AC20 source-shaped fork head retaining the existing heading controller/action."""
import sys,json,math,tempfile,uuid
from pathlib import Path
import bpy
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,sha
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import field
sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_blend

def signature():
    h=bpy.data.objects['DirectionalHead'];a=h.animation_data.action;curves=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for c in bag.fcurves:curves.append(dict(path=c.data_path,index=c.array_index,keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right)) for k in c.keyframe_points]))
    return dict(location=list(h.location),rotation_mode=h.rotation_mode,action=a.name,curves=curves)

def main():
    source=ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac20/model.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(1);original=signature();head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase']
    for o in list(scene.objects):
        if o not in [head,base]:bpy.data.objects.remove(o,do_unlink=True)
    folder='defence-battery';coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);gold=material(folder,'Ochre bearing and foot',(.39,.26,.10),.65,.45);dark=material(folder,'Dark source light backs',(.015,.020,.025),0,.83);blue=material(folder,'Blue white status lights',(.18,.28,.65),.1,.27,.15)
    worn_coral_pbr(coral,folder)
    body=lathe('AC20 narrow grounded pedestal',(0,0),[(0,.23),(.05,.27),(.15,.28),(.40,.28),(.70,.28),(.95,.27),(1.03,.24)],coral)
    lathe('AC20 stationary ochre sloping bearing',(0,0),[(.96,.27),(1.02,.29),(1.13,.24),(1.25,.13),(1.32,.10)],gold)
    box('AC20 grounded ochre left foot',(-.23,-.16,.17),(.22,.32,.34),gold,.035)
    box('AC20 coral right vertical relief',(.22,-.16,.51),(.13,.18,.98),coral,.025)
    for i,z in enumerate([.42,.72]):field(body,'AC20 blue status field '+str(i),0,z,.065,.065,blue,dark)
    cleanup(body);fixed=[o for o in scene.objects if o.type=='MESH']
    lathe('AC20 moving bearing spindle',(0,0),[(1.26,.08),(1.35,.10),(1.44,.10)],gold)
    bed=box('AC20 fork channel bed',(0,.06,1.43),(.48,.84,.08),coral,.025);bed.rotation_euler.x=-.4
    for i,x in enumerate([-.22,.22]):
        o=box('AC20 separate fork rail '+str(i),(x,0,1.51),(.14,1.08,.17),coral,.045);o.rotation_euler.x=-.4
    bridge=box('AC20 short rear fork bridge',(0,.43,1.34),(.52,.12,.15),coral,.025);bridge.rotation_euler.x=-.4
    # Functional interpretation requested in review: a recessed emitter facing
    # along the existing rails, without replacing the source-shaped open fork.
    emitter_origin=Vector((0,.24,1.46));emitter_rotation=Matrix.Rotation(-.4,3,'X')
    for name,offset,size,mat,bevel in [
        ('AC20 seated emitter housing',(0,0,0),(.28,.22,.20),gold,.022),
        ('AC20 recessed dark emitter surround',(0,-.114,0),(.21,.018,.14),dark,.012),
        ('AC20 emitter aperture',(0,-.126,0),(.12,.012,.075),blue,.008),
    ]:
        obj=box(name,emitter_origin+emitter_rotation@Vector(offset),size,mat,bevel);obj.rotation_euler.x=-.4
        obj['functional_detail']='Interpreted cannon emitter; not a recovered legacy muzzle shape'
    root=bpy.data.objects.new('PlacementRoot',None);scene.collection.objects.link(root);root['catalogue_id']='openfa:building/legacy/170';root['footprint']=[2,2];root['forward_axis']='-Y';root['dorsal_axis']='+Z'
    for c in [head,base]:world=c.matrix_world.copy();c.parent=root;c.matrix_world=world
    meshes=[o for o in scene.objects if o.type=='MESH'];moving=[o for o in meshes if o not in fixed]
    for o in meshes:
        world=o.matrix_world.copy();o.parent=base if o in fixed else head;o.matrix_world=world;bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name);normals=[tuple(n.vector) for n in o.data.corner_normals]
        for p in o.data.polygons:p.use_smooth=True
        o.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update();assert signature()==original
    count=sum(len(o.data.polygons) for o in meshes);assert count<30000
    scene.frame_set(1);output=ROOT/'sources/objects/achaean'/folder;output.mkdir(parents=True,exist_ok=True);scene.render.fps=16;scene.frame_start=1;scene.frame_end=17;bpy.context.preferences.filepaths.save_version=0
    temp=ROOT/'artifacts/achaean-building-export-temp';temp.mkdir(parents=True,exist_ok=True);old=tempfile.mkdtemp
    def mk(*a,**k):p=temp/uuid.uuid4().hex;p.mkdir();return str(p)
    tempfile.mkdtemp=mk
    action=head.animation_data.action;keys=[k for layer in action.layers for strip in layer.strips for bag in strip.channelbags for curve in bag.fcurves for k in curve.keyframe_points]
    saved=[(k,k.co.copy(),k.handle_left.copy(),k.handle_right.copy()) for k in keys]
    for k in keys:k.co.x*=4;k.handle_left.x*=4;k.handle_right.x*=4
    scene.render.fps=64;scene.frame_start=4;scene.frame_end=68;scene.frame_set(4)
    try:bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',export_yup=True,export_extras=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_frame_range=True)
    finally:
        tempfile.mkdtemp=old
        for k,co,left,right in saved:k.co=co;k.handle_left=left;k.handle_right=right
        scene.render.fps=16;scene.frame_start=1;scene.frame_end=17;scene.frame_set(1)
    assert signature()==original
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'),compress=True);p=output/'model.blend';p.write_bytes(clean_blend(p.read_bytes())[0])
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','remaster_achaean_manoeuvring_device.py','remaster_achaean_missile_launcher.py','checks_achaean_shipyard.py']
    dependencies=[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',source]
    meta=dict(issue=256,id='openfa:building/legacy/170',key='AC20',name='Defence Battery',culture='achaean',footprint=[2,2],definition_class=3,construction_updates=36,triangle_budget=30000,materials=4,mesh_nodes=len(meshes),triangles=count,author=Path(__file__).relative_to(ROOT).as_posix(),author_sha256=sha(Path(__file__)),helpers={p.relative_to(ROOT).as_posix():sha(p) for p in dependencies},binaries={ext:sha(output/f'model.{ext}') for ext in ['blend','glb']},animation=dict(retained_controller_signature=original,head='DirectionalHead',base='StaticBase',clip='Animation',export_bake_fps=64,fps=16,frames=[1,17],direction_count=16,moving_meshes=[o.name for o in moving],static_meshes=[o.name for o in fixed],timing_recovered=False),state_contract='Sixteen source surface heading rasters over separate stationary base. Original +Z heading controller/action retained exactly; authored preview timing is not a recovered idle/firing cycle. Source-shaped twin rail/trough head and fixed ochre bearing/foot,coral pedestal/two blue fields. No recoil/projectile sequence inferred. Runtime heading calibration,shared ACS2 and combat mapping separate.',scale_contract='Identity PlacementRoot groundZ0;Blender-Yfront/+Zup;2x2footprint. Source heading index registration and exact world/camera scale separate.',final_artistic_acceptance=False,game_client_integration=False)
    meta['emitter']=dict(housing='AC20 seated emitter housing',surround='AC20 recessed dark emitter surround',aperture='AC20 emitter aperture',head_local_origin=[0,.24,1.46],head_local_forward=[0,-math.cos(.4),math.sin(.4)],interpretation=True,firing_animation_recovered=False)
    meta['state_contract']+=' Review refinement adds an inset cannon emitter on a supported housing between the rails. Detailed emitter construction is interpreted; low-emission aperture is a readability cue, not a recovered firing effect.'
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('AC20_AUTHORED',count,len(meshes),flush=True)
if __name__=='__main__':main()


