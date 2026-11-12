"""AC26 bowl head, central emitter and four banded shaft retaining the existing heading controller/action."""
import sys,json,math,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,sha
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import field,patch
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_blend

def signature():
    h=bpy.data.objects['DirectionalHead'];a=h.animation_data.action;curves=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for c in bag.fcurves:curves.append(dict(path=c.data_path,index=c.array_index,keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right)) for k in c.keyframe_points]))
    return dict(location=list(h.location),rotation_mode=h.rotation_mode,action=a.name,curves=curves)

def main():
    source=ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac26/model.blend';bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(1);original=signature();head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase']
    for o in list(scene.objects):
        if o not in [head,base]:bpy.data.objects.remove(o,do_unlink=True)
    folder='power-tower';coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);gold=material(folder,'Ochre source fitting',(.39,.26,.10),.65,.45);dark=material(folder,'Dark bore and field backs',(.015,.020,.025),0,.83);blue=material(folder,'Dark cobalt source fields',(.012,.018,.20),.12,.30,.15);red=material(folder,'Four red shaft bands',(.58,.012,.006),.10,.48);slate=material(folder,'Slate lower oval fitting',(.16,.24,.29),.65,.43)
    worn_coral_pbr(coral,folder)
    body=lathe('AC26 grounded flared casing',(0,0),[(0,.29),(.03,.32),(.10,.34),(.22,.33),(.38,.30),(.52,.27),(.64,.23),(.69,.20),(.72,.18)],coral)
    verts=[];levels=[(0,.64),(.025,.67),(.08,.65),(.18,.58),(.32,.47),(.46,.36),(.59,.27),(.67,.21)]
    for z,x in levels:verts.extend([(-.12,-.08,z),(-x,-.08,z),(-x,.18,z),(-.12,.18,z)])
    faces=[]
    for j in range(len(levels)-1):
        for i in range(4):faces.append((4*j+i,4*j+(i+1)%4,4*(j+1)+(i+1)%4,4*(j+1)+i))
    faces.extend([tuple(reversed(range(4))),tuple(4*(len(levels)-1)+i for i in range(4))]);mesh=bpy.data.meshes.new('Sloping buttress');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new('AC26 grounded sloping buttress',mesh);scene.collection.objects.link(o);mesh.materials.append(coral);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=True
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x+.7,p.z)
    lathe('AC26 narrow stationary shaft',(0,0),[(.66,.18),(.69,.19),(1.51,.19),(1.56,.15)],coral)
    for i,z in enumerate([.83,1.03,1.23,1.43]):lathe('AC26 red shaft band '+str(i),(0,0),[(z-.028,.188),(z-.023,.194),(z+.023,.194),(z+.028,.188)],red)
    plate=patch('AC26 ochre raised service plate',body,(-.18,.45),[(-.065,-.10),(.065,-.10),(.065,.10),(-.065,.10)],gold)
    tree=BVHTree.FromPolygons([v.co for v in plate.data.vertices],[tuple(f.vertices) for f in plate.data.polygons])
    for i,z in enumerate([.39,.45,.51]):
        hit=tree.ray_cast(Vector((-.18,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None;normal=hit[1];o=box('AC26 ochre service rib '+str(i),hit[0]+normal*.003,(.09,.025,.018),gold,.006);o.rotation_mode='QUATERNION';o.rotation_quaternion=normal.to_track_quat('-Y','Z')
    patch('AC26 small slate ground oval',body,(-.055,.13),[(.10*math.cos(i*math.tau/12),.045*math.sin(i*math.tau/12)) for i in range(12)],slate)
    for col,x in enumerate([.025,.155]):
        for row,z in enumerate([.24,.40,.56]):field(body,'AC26 cobalt status field '+str(col*3+row),x,z,.065,.085,blue,dark)
    cleanup(body);fixed=[o for o in scene.objects if o.type=='MESH']
    lathe('AC26 moving bearing spindle',(0,0),[(1.52,.09),(1.54,.11),(1.65,.11),(1.69,.09)],coral)
    lathe('AC26 low bowl directional head',(0,0),[(1.60,.10),(1.62,.20),(1.66,.29),(1.72,.35),(1.78,.35),(1.83,.30),(1.86,.20),(1.87,.10)],coral)
    lathe('AC26 shallow head cap',(0,0),[(1.84,.13),(1.86,.17),(1.89,.15),(1.91,.11)],coral)
    axis=Vector((0,math.cos(.45),math.sin(.45)));origin=Vector((0,0,1.73));q=axis.to_track_quat('Z','Y')
    barrel=lathe('AC26 long central emitter',(0,0),[(.14,.095),(.20,.10),(.29,.08),(.43,.065),(.91,.047),(1.07,.044),(1.10,.040)],coral)
    from remaster_achaean_shipyard import cut
    cutter=lathe('temporary central bore',(0,0),[(.97,.027),(1.17,.027)],dark);cut(barrel,cutter,'Actual blind central aperture');cleanup(barrel)
    bore=lathe('AC26 recessed central emitter face',(0,0),[(.968,.026),(.977,.026)],dark)
    for obj in [barrel,bore]:obj.rotation_mode='QUATERNION';obj.rotation_quaternion=q;obj.location=origin
    for i,x in enumerate([-.17,.17]):
        prong=lathe('AC26 short flanking lug '+str(i),(0,0),[(.10,.045),(.16,.055),(.34,.036),(.42,.025)],coral);prong.rotation_mode='QUATERNION';prong.rotation_quaternion=q;prong.location=origin+Vector((x,0,0))
    root=bpy.data.objects.new('PlacementRoot',None);scene.collection.objects.link(root);root['catalogue_id']='openfa:building/legacy/176';root['footprint']=[2,2];root['forward_axis']='-Y';root['dorsal_axis']='+Z'
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
    meta=dict(issue=256,id='openfa:building/legacy/176',key='AC26',name='Power Tower',culture='achaean',footprint=[2,2],definition_class=18,construction_updates=50,triangle_budget=30000,materials=6,mesh_nodes=len(meshes),triangles=count,author=Path(__file__).relative_to(ROOT).as_posix(),author_sha256=sha(Path(__file__)),helpers={p.relative_to(ROOT).as_posix():sha(p) for p in dependencies},binaries={ext:sha(output/f'model.{ext}') for ext in ['blend','glb']},animation=dict(retained_controller_signature=original,head='DirectionalHead',base='StaticBase',clip='Animation',export_bake_fps=64,fps=16,frames=[1,17],direction_count=16,moving_meshes=[o.name for o in moving],static_meshes=[o.name for o in fixed],timing_recovered=False),emitter=dict(centre=list(origin),axis=list(axis),central_length=1.10,flanking_lengths=[.42,.42],recessed_face_distance=.977),state_contract='Directional Power Tower with one low bowl head/shallow cap,long central emitter and two shorter flanking lugs over stationary narrow shaft/four red bands,flared ground casing,left sloping buttress,three-rib ochre plate,six cobalt fields and small slate oval. All16 source headings reviewed;one long central/two short flanking projections interpreted from them. Exact original native heading controller/action retained. No firing/recoil/idle cycle recovered;current preview timing is heading demonstration. Shared ACS2,client heading/muzzle/state mapping separate;hidden bore/mechanism construction interpreted.',scale_contract='Identity PlacementRoot groundZ0;Blender-Yfront/+Zup;2x2footprint. Source anatomy/counts retained;exact heading index/world/camera/impact calibration and Android frame time separate.',final_artistic_acceptance=False,game_client_integration=False)
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('AC26_AUTHORED',count,len(meshes),flush=True)
if __name__=='__main__':main()


