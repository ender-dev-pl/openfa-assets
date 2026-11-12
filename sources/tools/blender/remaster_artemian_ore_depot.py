"""Author AR22 Ore Depot from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/ore-depot';maps=root/'sources/materials/artemian/ore-depot';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2602201);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2602205);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.22,.29,.33)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.60,.67,.70)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.26+.025*math.cos(11*u+3*v),.43,.33,1])
    oxidized_orm=[.35 if i%4==2 else value for i,value in enumerate(orm)]
    for name,pixels in [('oxidized-alloy-orm',oxidized_orm),('slate-blue-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('green-pipe-colour',red)]:
        image=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name in ['occlusion-roughness-metallic','oxidized-alloy-orm','used-metal-normal']:image.colorspace_settings.name='Non-Color'
        image.pixels.foreach_set(pixels);path=maps/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();images[name]=image
    def material(name,colour,image=None,emission=0,metal=.84,rough=.4):
        m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if image:
            tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=images[image];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);packed=m.node_tree.nodes.new('ShaderNodeTexImage');packed.image=images['oxidized-alloy-orm' if image in ['exposed-alloy-edge-colour','green-pipe-colour'] else 'occlusion-roughness-metallic'];split=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(packed.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic'])
            n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=images['used-metal-normal'];nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;m.node_tree.links.new(n.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
            if emission:m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color'])

        p.inputs['Emission Strength'].default_value=emission;return m
    alloy=material('Used Artemian slate-blue tower alloy',(.22,.29,.33),'slate-blue-alloy-colour');exposed=material('Pale worn socket side edge',(.60,.67,.70),'exposed-alloy-edge-colour');dark=material('Dark blind cap and base points',(.012,.016,.019),metal=.35,rough=.65);green=material('Oxidized green service pipe and foot socket',(.26,.43,.33),'green-pipe-colour')
    def apply(o,mod):
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    def boolean(o,cut,label):
        mod=o.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;apply(o,mod);bpy.data.objects.remove(cut,do_unlink=True)

    def solid(name,verts,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    controls=[(.025,.32),(.05,.40),(.12,.44),(.25,.45),(.32,.42),(.35,.35),(.38,.36),(.42,.43),(.50,.46),(.65,.46),(.70,.43),(.74,.35),(.77,.35),(.80,.43),(.90,.46),(1.04,.46),(1.10,.42),(1.13,.35),(1.16,.35),(1.19,.43),(1.29,.46),(1.44,.46),(1.49,.43),(1.52,.35),(1.55,.35),(1.58,.44),(1.66,.46),(1.77,.43),(1.92,.36),(2.08,.25),(2.19,.13),(2.235,.075),(2.25,.060)]
    controls=[(z,max(rr,.395) if .30<z<1.57 else rr) for z,rr in controls]
    def radius(z):
        zs=[q[0] for q in controls];rs=[q[1] for q in controls];slopes=[(b-a)/(y-x) for x,y,a,b in zip(zs,zs[1:],rs,rs[1:])];tangents=[slopes[0]]
        for a,b in zip(slopes,slopes[1:]):tangents.append(0 if a*b<=0 else 2*a*b/(a+b))
        tangents.append(slopes[-1]);i=min(len(zs)-2,next((j for j in range(len(zs)-1) if z<=zs[j+1]),len(zs)-2));h=zs[i+1]-zs[i];t=(z-zs[i])/h
        return (2*t**3-3*t**2+1)*rs[i]+(t**3-2*t**2+t)*h*tangents[i]+(-2*t**3+3*t**2)*rs[i+1]+(t**3-t**2)*h*tangents[i+1]
    count=96;rings=96;verts=[];faces=[]
    for j in range(rings):
        z=.025+(2.25-.025)*j/(rings-1);rr=radius(z)
        for i in range(count):a=i*math.tau/count;verts.append((rr*math.cos(a),rr*.86*math.sin(a),z))
    for j in range(rings-1):
        for i in range(count):faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    faces.extend([tuple(reversed(range(count))),tuple((rings-1)*count+i for i in range(count))]);body=solid('Ore Depot continuous slate tower with three middle drums',verts,faces,alloy)
    def lathe(name,profile,mat,point,normal):
        n=48;rotation=Vector(normal).to_track_quat('Z','Y');verts=[Vector(point)+rotation@Vector((rr*math.cos(i*math.tau/n),rr*math.sin(i*math.tau/n),z)) for z,rr in profile for i in range(n)];faces=[]
        for j in range(len(profile)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);return solid(name,verts,faces,mat)
    def surface(x,z):
        bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(Vector((x,-3,z)),Vector((0,1,0)));assert hit,(x,z);return q,n
    points=[]
    for i,(x,z) in enumerate([(-.05,2.13),(.06,.17),(.22,.17)]):
        q,n=surface(x,z);points.append(dict(point=list(q),normal=list(n)));cut=lathe('Temporary actual blind point recess',[(-.018,.026),(.07,.026)],alloy,q,n);boolean(body,cut,'Actual cap or base point recess '+str(i));lathe('Ore Depot dark recessed point '+str(i),[(-.021,.023),(-.010,.023)],dark,q,n)
    x,y=-.17,-.43;path=[Vector((x,y,.23)),Vector((x,y,1.30))]
    for j in range(1,25):
        t=j*math.pi/48;path.append(Vector((x,y+.08*(1-math.cos(t)),1.30+.08*math.sin(t))))
    n=24;verts=[];faces=[]
    for j,q in enumerate(path):
        tangent=(path[min(j+1,len(path)-1)]-path[max(j-1,0)]).normalized();u=Vector((1,0,0));v=tangent.cross(u).normalized()
        for i in range(n):a=i*math.tau/n;verts.append(q+.045*(math.cos(a)*u+math.sin(a)*v))
    for j in range(len(path)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(path)-1)*n+i for i in range(n))]);solid('Ore Depot continuous green pipe and inward elbow',verts,faces,green)
    q,n=surface(x,.14);front=-.475;back=q.y+.025;centre=Vector((x,(front+back)/2,.145));size=(.12,back-front,.24);bpy.ops.mesh.primitive_cube_add(size=1,location=centre);socket=bpy.context.object;socket.name='Ore Depot green rectangular foot socket'
    for v in socket.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
    socket.data.materials.append(green);socket.data.materials.append(exposed)
    mod=socket.modifiers.new('Rounded worn socket corners','BEVEL');mod.width=.004;mod.segments=3;mod.material=1;apply(socket,mod);foot_contact=list(q-n*.01)
    supports=[]
    for i,z in enumerate([.54,.92,1.31]):
        q,n=surface(x,z);a=q-n*.020;b=Vector((x,y-.010,z));axis=b-a;lathe('Ore Depot short green pipe mount '+str(i),[(-axis.length/2,.017),(axis.length/2,.017)],green,(a+b)/2,axis);supports.append(dict(body_point=list(q),normal=list(n),pipe_point=[x,y,z]))
    bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(Vector((.13,.05,3)),Vector((0,0,-1)));assert hit;dent=dict(point=list(q),normal=list(n));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.03,location=q+n*.025);boolean(body,bpy.context.object,'Actual tiny service dent on cap')
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/128';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o==body:
            uv=o.data.uv_layers.active
            for face in o.data.polygons:
                for index in face.loop_indices:
                    point=o.matrix_world@o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((point.x+1.1)/2.1,(point.y+1.15+point.z*.12)/2.1)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=e.calc_face_angle(0)<.60
        bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.use_smooth=True
        o.data.normals_split_custom_set([tuple(n.vector) for n in o.data.corner_normals])
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);print('MEASURED_TRIANGLES',triangles,flush=True);assert triangles<30000
    scratch=root/'artifacts/artemian-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])


    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/128',key='AR22',name='Ore Depot',culture='artemian',footprint=[2,2],definition_class=30,construction_updates=24,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,author='sources/tools/blender/remaster_artemian_ore_depot.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},dark_points=points,pipe_path=[list(q) for q in path],pipe_mounts=supports,foot_contact=foot_contact,physical_dent=dent,interpretation=['Own slate-blue stacked tower hasroundedfoot,3roundedmiddrums andtaperedbluntcap,1darkcappoint/2basepoints,greenfrontpipe/elbow/rectangularfoot socket.','Hidden necksections,pipe mounts,backside andcell-relative dimensions authored. PB30 isTerran context;no matching ore-storage research subject orown operating overlays establish ananimation.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/ar22-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_ORE_DEPOT_AUTHORED',triangles,len(meshes),len(created),flush=True)



if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
