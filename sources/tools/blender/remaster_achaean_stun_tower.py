"""AC25 spherical cannon head and flared casing retaining the existing heading controller/action."""
import sys,json,math,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
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
    source=ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac25/model.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(1);original=signature();head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase']
    for o in list(scene.objects):
        if o not in [head,base]:bpy.data.objects.remove(o,do_unlink=True)
    folder='stun-tower';coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);gold=material(folder,'Ochre left fitting',(.39,.26,.10),.65,.45);dark=material(folder,'Dark muzzle and field backs',(.015,.020,.025),0,.83);blue=material(folder,'Blue source fields',(.18,.28,.48),.1,.30,.15);red=material(folder,'Red neck',(.32,.012,.006),.35,.45);slate=material(folder,'Slate left fitting',(.13,.21,.26),.65,.43)
    worn_coral_pbr(coral,folder)
    body=lathe('AC25 grounded flared casing',(0,0),[(0,.33),(.025,.36),(.07,.37),(.13,.36),(.28,.33),(.45,.29),(.63,.245),(.78,.21),(.90,.18),(.97,.16),(1.01,.16)],coral)
    for side in [-1,1]:
        verts=[];levels=[(0,.57),(.025,.60),(.08,.60),(.18,.54),(.35,.44),(.52,.36),(.70,.29),(.82,.245),(.90,.215)]
        for z,x in levels:
            verts.extend([(side*.14,-.08,z),(side*x,-.08,z),(side*x,.18,z),(side*.14,.18,z)])
        faces=[]
        for j in range(len(levels)-1):
            for i in range(4):faces.append((4*j+i,4*j+(i+1)%4,4*(j+1)+(i+1)%4,4*(j+1)+i))
        faces.extend([tuple(reversed(range(4))),tuple(4*(len(levels)-1)+i for i in range(4))]);mesh=bpy.data.meshes.new('Curved buttress');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new('AC25 grounded buttress '+str(side),mesh);scene.collection.objects.link(o);mesh.materials.append(coral);uv=mesh.uv_layers.new()
        for face in mesh.polygons:
            face.use_smooth=True
            for li in face.loop_indices:
                p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x+.6,p.z)
    lathe('AC25 red narrow neck',(0,0),[(.93,.16),(.96,.18),(1.09,.18),(1.12,.16)],red)
    lathe('AC25 stationary rounded collar',(0,0),[(1.06,.16),(1.10,.20),(1.14,.27),(1.19,.30),(1.25,.30),(1.30,.27),(1.34,.20),(1.37,.12)],coral)
    lathe('AC25 left slate service fitting',(-.27,-.12),[(.10,.045),(.14,.068),(.65,.068),(.70,.045)],slate)
    lathe('AC25 left ochre coupling',(-.27,-.12),[(.58,.07),(.61,.09),(.77,.09),(.82,.07)],gold)
    for col,x in enumerate([.025,.16]):
        for row,z in enumerate([.28,.46,.64]):field(body,'AC25 blue status field '+str(col*3+row),x,z,.07,.085,blue,dark)
    cleanup(body);fixed=[o for o in scene.objects if o.type=='MESH']
    lathe('AC25 moving bearing spindle',(0,0),[(1.32,.10),(1.36,.12),(1.46,.12),(1.49,.10)],coral)
    radius=.34;centre=1.78
    profile=[(centre-radius*math.cos(i*math.pi/32),max(.002,radius*math.sin(i*math.pi/32))) for i in range(33)]
    sphere=lathe('AC25 spherical directional head',(0,0),profile,coral)
    axis=Vector((0,math.cos(.45),math.sin(.45)));origin=Vector((0,0,centre));q=axis.to_track_quat('Z','Y')
    barrel=lathe('AC25 tapered raised nozzle',(0,0),[(.25,.095),(.30,.105),(.35,.09),(.40,.07),(.68,.055),(.73,.052),(.75,.045)],coral)
    # Real blind bore: annular lip and a dark recessed face, never a painted cap.
    from remaster_achaean_shipyard import cut
    cutter=lathe('temporary nozzle bore',(0,0),[(.63,.032),(.82,.032)],dark)
    cut(barrel,cutter,'Actual recessed muzzle');cleanup(barrel)
    bore=lathe('AC25 recessed muzzle face',(0,0),[(.628,.031),(.637,.031)],dark)
    for obj in [barrel,bore]:obj.rotation_mode='QUATERNION';obj.rotation_quaternion=q;obj.location=origin
    root=bpy.data.objects.new('PlacementRoot',None);scene.collection.objects.link(root);root['catalogue_id']='openfa:building/legacy/175';root['footprint']=[2,2];root['forward_axis']='-Y';root['dorsal_axis']='+Z'
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
    meta=dict(issue=256,id='openfa:building/legacy/175',key='AC25',name='Stun Tower',culture='achaean',footprint=[2,2],definition_class=27,construction_updates=26,triangle_budget=30000,materials=6,mesh_nodes=len(meshes),triangles=count,author=Path(__file__).relative_to(ROOT).as_posix(),author_sha256=sha(Path(__file__)),helpers={p.relative_to(ROOT).as_posix():sha(p) for p in dependencies},binaries={ext:sha(output/f'model.{ext}') for ext in ['blend','glb']},animation=dict(retained_controller_signature=original,head='DirectionalHead',base='StaticBase',clip='Animation',export_bake_fps=64,fps=16,frames=[1,17],direction_count=16,moving_meshes=[o.name for o in moving],static_meshes=[o.name for o in fixed],timing_recovered=False),nozzle=dict(centre=list(origin),axis=list(axis),muzzle_depth=.113,head_sphere_radius=radius),state_contract='Directional Stun Tower with one spherical head,short raised tapered nozzle and actual recessed muzzle over a stationary rounded collar,red neck,flared casing/two grounded buttresses,left ochre/slate fitting and six blue source fields. All16 original headings reviewed;original native heading controller/action retained exactly. Dense GLB sampling preserves original clip name/timing. No firing/recoil/continuous idle timing recovered. Shared ACS2,client heading/muzzle/state mapping separate;hidden nozzle/engineering interpreted.',scale_contract='Identity PlacementRoot groundZ0;Blender-Yfront/+Zup;2x2footprint. Source anatomical proportions retained;exact heading index/world/camera/impact calibration and Android frame time separate.',final_artistic_acceptance=False,game_client_integration=False)
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('AC25_AUTHORED',count,len(meshes),flush=True)
if __name__=='__main__':main()


