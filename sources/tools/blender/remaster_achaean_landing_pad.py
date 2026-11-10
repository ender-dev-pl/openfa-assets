"""AC12 retained sliding-cover cycle rebuilt against actual open/closed legacy layers."""
import bpy,bmesh,math,sys,json,hashlib,tempfile,uuid
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,clean_blend,clean_png
from remaster_achaean_shipyard import worn_coral_pbr
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
RETAIN=ROOT/'sources/docs/assets/reconstruction/launch-facilities/achaean/ac12/model.blend'


def ring(name,profile,mat):
    n=96;verts=[(r*math.cos(2*math.pi*i/n),r*math.sin(2*math.pi*i/n),z) for r,z in profile for i in range(n)];faces=[]
    for j in range(len(profile)):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,((j+1)%len(profile))*n+i))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for f in mesh.polygons:
        f.use_smooth=True
        for li in f.loop_indices:
            vi=mesh.loops[li].vertex_index;uv.data[li].uv=(vi%n/(n-1),(vi//n)/(len(profile)-1))
    return o


def leaf_mesh(name,lo,hi,green,red):
    outline=[Vector((.76*math.cos(2*math.pi*i/96),.76*math.sin(2*math.pi*i/96))) for i in range(96)]
    for edge,above in [(lo,True),(hi,False)]:
        result=[]
        for a,b in zip(outline,outline[1:]+outline[:1]):
            ina=a.y>=edge if above else a.y<=edge;inb=b.y>=edge if above else b.y<=edge
            if ina:result.append(a)
            if ina!=inb:result.append(a+(b-a)*((edge-a.y)/(b.y-a.y)))
        outline=result
    n=len(outline);verts=[(p.x,p.y,z) for z in [.452,.460] for p in outline];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh)
    for x in [-.39,-.26,.26,.39]:bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(x,0,0),plane_no=(1,0,0),clear_inner=False,clear_outer=False,dist=1e-7)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();mesh.materials.append(green);mesh.materials.append(red);o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.material_index=int(face.normal.z>.5 and .26<abs(face.center.x)<.39)
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x/1.52+.5,p.y/1.52+.5)
    return o


def main():
    assert sha(RETAIN)=='865f66a4708c0c15594b374ccf822d92b6dc878cef3709ba73e1f7678623336e';bpy.ops.wm.open_mainfile(filepath=str(RETAIN),load_ui=False,use_scripts=False);old={}
    for sign in [-1,1]:
        for i in range(6):
            name=f'LaunchLeaf Transverse green cover {sign} {i}';o=bpy.data.objects[name];bpy.context.scene.frame_set(31);old[name]=[float(v) for v in o.location]
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=30;scene.frame_start=1;scene.frame_end=61;folder='landing-pad';root=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root);root['catalogue_id']='openfa:building/legacy/162';root['footprint']=[2,2]
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate mast and well',(.16,.24,.29),.7,.38);dark=material(folder,'Dark bay floor',(.01,.012,.016),0,.85);green=material(folder,'Worn green cover',(.14,.30,.22),.45,.55);red=material(folder,'Two red cover bands',(.28,.012,.008),.35,.55);blue=material(folder,'Blue mast bands',(.045,.03,.29),.30,.50);dark.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.10;worn_coral_pbr(coral,folder)
    ring('AC12 closed outer casing wall',[(1.185,.04),(1.215,.04),(1.215,.50),(1.185,.50)],coral)
    ring('AC12 rounded roof and inner lip',[(.77,.50),(1.215,.50),(1.20,.57),(1.07,.64),(.86,.62),(.77,.56)],coral)
    lathe('AC12 grounded low base',(0,0),[(0,1.10),(.04,1.215),(.08,1.215)],coral)
    lathe('AC12 dark continuous well floor',(0,0),[(.08,1.185),(.09,1.185)],dark)
    ring('AC12 short blue inner well',[(.65,.09),(.70,.09),(.70,.30),(.65,.30)],slate)
    for i,a in enumerate([-math.pi/2-.55,-math.pi/2,-math.pi/2+.55]):
        o=box('AC12 coral service field '+str(i),(1.21*math.cos(a),1.21*math.sin(a),.22),(.30,.035,.15),coral,.025);o.rotation_euler.z=a+math.pi/2
    for sign in [-1,1]:
        for i in range(6):
            lo=.76*i/6+.0006;hi=.76*(i+1)/6-.0006
            if sign<0:lo,hi=-hi,-lo
            name=f'LaunchLeaf Transverse green cover {sign} {i}';control=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(control);control.parent=root;o=leaf_mesh('AC12 cover segment '+str(sign)+' '+str(i),lo,hi,green,red);o.parent=control
            dx,dy,dz=old[name];assert abs(dy)<1e-8
            for fr,slide,lower in [(1,0,0),(10,0,1),(31,1,1),(52,0,1),(61,0,0)]:control.location=(0,dx*slide,dz*lower);control.keyframe_insert(data_path='location',frame=fr)
            action=control.animation_data.action;action.name=name+' retained travel'
            for curve in action.fcurves:
                for k in curve.keyframe_points:k.interpolation='LINEAR'
            track=control.animation_data.nla_tracks.new();track.name='LaunchFacilityCycle';track.strips.new('LaunchFacilityCycle',1,action);control.animation_data.action=None
    lathe('AC12 coral mast stem',(.95,.65),[(.55,.07),(1.19,.065),(1.24,.10),(1.29,.10)],coral)
    for i,z in enumerate([.87,.99,1.11]):lathe('AC12 blue mast collar '+str(i),(.95,.65),[(z,.071),(z+.04,.071)],blue)
    box('AC12 single straight slate mast',(.95,.65,1.77),(.075,.09,1.02),slate,.008)
    meshes=[o for o in scene.objects if o.type=='MESH']
    for o in meshes:
        if o.parent is None:o.parent=root
        bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name);normals=[tuple(n.vector) for n in o.data.corner_normals]
        for f in o.data.polygons:f.use_smooth=True
        o.data.normals_split_custom_set(normals)
    scene.frame_set(1);bpy.context.view_layer.update();output=ROOT/'sources/objects/achaean'/folder;output.mkdir(parents=True,exist_ok=True);bpy.context.preferences.filepaths.save_version=0;temp=ROOT/'artifacts/achaean-building-export-temp';temp.mkdir(parents=True,exist_ok=True);original=tempfile.mkdtemp
    def mk(*a,**k):p=temp/uuid.uuid4().hex;p.mkdir();return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',export_yup=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=True)
    finally:tempfile.mkdtemp=original
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'),compress=True);p=output/'model.blend';p.write_bytes(clean_blend(p.read_bytes())[0]);tri=sum(len(o.data.polygons) for o in meshes);helpers=[Path(__file__).with_name('achaean_remaster_geometry.py'),Path(__file__).with_name('remaster_achaean_shipyard.py'),ROOT/'tools/publication_support.py',RETAIN]
    meta=dict(issue=256,id='openfa:building/legacy/162',key='AC12',name='Landing Pad',culture='achaean',footprint=[2,2],definition_class=26,construction_updates=18,triangle_budget=30000,triangles=tri,mesh_nodes=len(meshes),materials=6,binaries={x:sha(output/f'model.{x}') for x in ['blend','glb']},author=Path(__file__).relative_to(ROOT).as_posix(),author_sha256=sha(Path(__file__)),helpers={p.relative_to(ROOT).as_posix():sha(p) for p in helpers},animation=dict(clip='LaunchFacilityCycle',fps=30,frames=[1,10,31,52,61],closed_frame=1,open_frame=31,end_frame=61,retained_open_translations=old,mechanism='paired fore/aft telescopic cover strips',continuous_timing_recovered=False,descriptor17_is_foreground=True,pose_map={str(i):(1 if i==2 else 15 if i==3 else 22 if i==4 else 27 if i==5 else 31) for i in range(2,17)}),state_contract='Retains the useful LaunchFacilityCycle label,61-frame closed/open/closed cycle and12 segment travel amplitudes from the prior refinement. Axis is aligned fore/aft from actual paired strip imagery; vertical pre-stow and hidden cavity are authored engineering. Descriptors2–5 are visible cover phases,6–16 empty/open,17 foreground rather than a lid pose. Original timing/hidden engineering/foreground composition not recovered.',scale_contract='PlacementRoot at groundZ0; Blender-Y front/+Zup. Client tile/ship scale remains separate.',game_client_integration=False,final_artistic_acceptance=False)
    (output/'model.json').write_text(json.dumps(meta,indent=2)+chr(10),encoding='utf-8');print('AC12_AUTHORED',tri,len(meshes),flush=True)
if __name__=='__main__':main()
