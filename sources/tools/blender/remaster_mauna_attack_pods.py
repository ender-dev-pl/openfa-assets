"""Author MN14 Attack Pods from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/attack-pods';maps=root/'sources/materials/mauna/attack-pods';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611414);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-alloy-colour','brass-colour']}
    # Deterministic sparse roughcast spalls, patina streaks and fine pores.
    # These are authored surface maps,not borrowed legacy pixels.
    grids={n:[[rng.uniform(-1,1) for _ in range(n)] for _ in range(n)] for n in [5,9,19]}
    def cast_noise(n,u,v):
        x=u*n;y=v*n;ix=int(x);iy=int(y);a=x-ix;b=y-iy;a=a*a*(3-2*a);b=b*b*(3-2*b);g=grids[n]
        return (g[iy%n][ix%n]*(1-a)+g[iy%n][(ix+1)%n]*a)*(1-b)+(g[(iy+1)%n][ix%n]*(1-a)+g[(iy+1)%n][(ix+1)%n]*a)*b
    speckles={}
    for i in range(85):
        cx=rng.randrange(size);cy=rng.randrange(size);radius=rng.randrange(1,4)
        for dy in range(-radius,radius+1):
            for dx in range(-radius,radius+1):
                if dx*dx+dy*dy<radius*radius*rng.uniform(.65,1.1):speckles[((cx+dx)%size,(cy+dy)%size)]=rng.uniform(.010,.035)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=.040*cast_noise(5,u,v)+.018*cast_noise(19,u,v);grain=rng.uniform(-.025,.025);stain=max(0,cast_noise(9,u,v))*.065;aggregate=speckles.get((x,y),0);pore=.15 if rng.random()<.035 else 0;dust=.07*max(0,1-v*5)
            concrete_delta=cloud+grain+aggregate-stain-pore-dust
            buffers['cast-concrete-colour'].extend([max(.01,c+concrete_delta) for c in (.29,.34,.41)]+[1])
            scratch=.17 if ((x*7+y*31)%991<2 and rng.random()<.7) else 0
            buffers['marking-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in (.32,.018,.012)]+[1])
            buffers['concrete-orm'].extend([1,min(.98,max(.68,.85+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.76,max(.32,.54+grain+stain)),.72,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.035,.035),.5+rng.uniform(-.035,.035),1,1])
            buffers['pale-alloy-colour'].extend([max(.01,c+cloud*.5+grain*.5-stain*.5+scratch*.3) for c in (.46,.51,.57)]+[1])
            buffers['brass-colour'].extend([max(.01,c+cloud*.6+grain*.5-stain*.8+scratch*.4) for c in (.66,.47,.22)]+[1])
    images={}
    for name,pixels in buffers.items():
        im=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name.endswith('-orm') or name.endswith('-normal'):im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(pixels);path=maps/(name+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();path.write_bytes(clean_png(path.read_bytes()));im.pack();images[name]=im
    def material(name,colour=None,metal=False):
        m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.012,.016,.020,1);p.inputs['Roughness'].default_value=.85
        if colour:
            tex=n.new('ShaderNodeTexImage');tex.image=images[colour];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);orm=n.new('ShaderNodeTexImage');orm.image=images['metal-orm' if metal else 'concrete-orm'];split=n.new('ShaderNodeSeparateColor');m.node_tree.links.new(orm.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic']);texn=n.new('ShaderNodeTexImage');texn.image=images['cast-service-normal'];normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.10 if metal else .45;m.node_tree.links.new(texn.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        return m
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Matte pale coated service frames','pale-alloy-colour');dark=material('Dark nonemissive service recesses')
    def apply(o,mod):bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    def solid(name,verts,faces,mat):
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();assert not me.validate();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    def box(name,centre,size,mat,normal=None,bevel=.003):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        if normal is not None:
            normal=Vector(normal).normalized();v=(Vector((0,0,1))-normal*normal.z).normalized();u=v.cross(normal).normalized();o.rotation_euler=Matrix((u,v,normal)).transposed().to_euler()
        o.data.materials.append(mat)
        if bevel:
            mod=o.modifiers.new('Practical planar edge chamfer','BEVEL');mod.width=bevel;mod.segments=1;apply(o,mod)
        return o
    def cut(o,tool,label):
        mod=o.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;apply(o,mod);bpy.data.objects.remove(tool,do_unlink=True)
    red=material('Worn red source well band','marking-red-colour');brass=material('Tarnished brass supports and bent fittings','brass-colour',True)
    attachments=[];fields=[];chips=[]
    def recalc(obj):
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    def octagon(h,c):return [(-h+c,-h),(h-c,-h),(h,-h+c),(h,h-c),(h-c,h),(-h+c,h),(-h,h-c),(-h,-h+c)]
    def column(name,outline,low,high,mat):
        n=len(outline);verts=[(x,y,z) for z in [low,high] for x,y in outline];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];o=solid(name,verts,faces,mat);recalc(o);return o
    def ring(name,outer,inner,low,high,mat):
        n=len(outer);verts=[(x,y,z) for z,points in [(low,outer),(high,outer),(low,inner),(high,inner)] for x,y in points];faces=[]
        for i in range(n):
            j=(i+1)%n;faces.extend([(i,j,n+j,n+i),(2*n+j,2*n+i,3*n+i,3*n+j),(n+i,n+j,3*n+j,3*n+i),(j,i,2*n+i,2*n+j)])
        o=solid(name,verts,faces,mat);recalc(o);return o
    foot=box('Attack Pods grounded rectangular foot',(0,0,.065),(1.96,1.96,.13),concrete,bevel=.008)
    vertices=[(x*r,y*r,z) for z,r in [(.10,.94),(.95,.70)] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]];body=solid('Attack Pods low truncated square cast body',vertices,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],concrete);recalc(body)
    for obj in [body,foot]:cut(obj,column('Temporary actual open-well cutter',octagon(.38,.05),-.2,1.5,concrete),'Actual unobstructed open well')
    band=ring('Attack Pods raised red well band',octagon(.50,.075),octagon(.38,.05),.94,1.11,red)
    lip=ring('Attack Pods pale upper well lip',octagon(.51,.075),octagon(.36,.05),1.105,1.145,edge)
    lining=ring('Attack Pods dark deep well lining',octagon(.39,.05),octagon(.36,.05),.08,1.125,dark)
    floor=box('Attack Pods recessed black well floor',(0,0,.05),(.80,.80,.10),dark,bevel=0)
    attachments += [dict(object=body.name,support=foot.name,point=[.65,0,.11]),dict(object=band.name,support=body.name,point=[.45,0,.945]),dict(object=lip.name,support=band.name,point=[.45,0,1.108]),dict(object=lining.name,support=body.name,point=[.385,0,.50]),dict(object=lining.name,support=lip.name,point=[.375,0,1.115]),dict(object=floor.name,support=lining.name,point=[.375,0,.09])]
    def anchored(name,centre,size,mat,support,witness,normal=None):
        o=box(name,centre,size,mat,normal,.002);attachments.append(dict(object=o.name,support=support.name,point=witness));return o
    posts=[];rails=[]
    for i,x in enumerate([.54,.66]):
        post=anchored('Attack Pods tall brass support '+str(i),(x,.42,1.455),(.050,.070,1.04),brass,body,[x,.42,.945]);posts.append(post)
        rail=anchored('Attack Pods narrow crosshead rail '+str(i),(x,.42,1.98),(.035,.84,.060),edge,post,[x,.42,1.963]);rails.append(rail)
    for i,y in enumerate([.08,.216,.352,.488,.624,.76]):
        rib=anchored('Attack Pods supported crosshead rib '+str(i),(.60,y,1.975),(.15,.034,.032),edge,rails[0],[.54,y,1.975]);attachments.append(dict(object=rib.name,support=rails[1].name,point=[.66,y,1.975]))
    anchored('Attack Pods short pale roof upright',(-.57,-.49,1.16),(.05,.05,.45),edge,body,[-.57,-.49,.945])
    # Each strap is one genuinely bent solid rather than floating boxes.
    for i,y in enumerate([-.44,0,.44]):
        outline=[(.80,.50),(.96,.50),(1.00,.44),(1.00,.12),(.92,.12),(.92,.39),(.80,.42)];n=len(outline);verts=[(x,v,z) for v in [y-.055,y+.055] for x,z in outline];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        strap=solid('Attack Pods bent brass side fitting '+str(i),verts,faces,brass);recalc(strap);bevel=strap.modifiers.new('Worn soft bent strap edges','BEVEL');bevel.width=.008;bevel.segments=2;apply(strap,bevel);attachments.append(dict(object=strap.name,support=body.name,point=[.815,y,.46]))
    # Blind front field and its supported pale frame follow the cast incline.
    normal=Vector((0,-.85,.24)).normalized();vertical=(Vector((0,0,1))-normal*normal.z).normalized();q=Vector((0,-.94+.24*(.48-.10)/.85,.48));cut(body,box('Temporary front recess cutter',q+normal*.008,(1.08,.36,.080),concrete,normal,0),'Actual blind front service recess')
    backing=box('Attack Pods seated front service backing',q-normal*.036,(1.074,.354,.018),dark,normal,.001);fields.append(dict(object=backing.name,body=body.name,point=list(q),normal=list(normal),depth=.032,contact_depth=.040))
    for i,(du,dv,w,h) in enumerate([(-.565,0,.034,.43),(.565,0,.034,.43),(0,-.207,1.16,.034),(0,.207,1.16,.034)]):
        centre=q+Vector((du,0,0))+vertical*dv;anchored('Attack Pods pale front frame '+str(i),centre,(w,h,.020),edge,body,list(centre-normal*.004),normal)
    for obj,p,n in [(body,Vector((-.64,0,.95)),Vector((0,0,1))),(foot,Vector((.65,-.98,.055)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.019,location=p+n*.013);cut(obj,bpy.context.object,'Actual shallow used cast chip');chips.append(dict(body=obj.name,point=list(p),normal=list(n)))
    # Static accessories batch by material; named vertex groups preserve
    # editable parts and let the verifier test actual individual supports.
    part_batches={};keep={o.name for o in [body,foot,band,lip,lining,floor]}
    for mat,label in [(edge,'pale supported assemblies'),(brass,'five source brass assemblies'),(dark,'front blind backing')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]]
        if not objects:continue
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            part_batches[obj.name]='Attack Pods '+label;group=obj.vertex_groups.new(name=obj.name);group.add(list(range(len(obj.data.vertices))),1,'REPLACE');obj.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Attack Pods '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/143';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z';placement['ground_level']=0
    bpy.context.view_layer.update()
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');uv=obj.data.uv_layers.active
        for face in obj.data.polygons:
            for i in face.loop_indices:
                p=obj.data.vertices[obj.data.loops[i].vertex_index].co;uv.data[i].uv=((p.y+1)/2,p.z/2.1) if abs(face.normal.x)>.5 else ((p.x+1)/2,p.z/2.1) if abs(face.normal.y)>.5 else ((p.x+1)/2,(p.y+1)/2)
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');apply(obj,mod);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.to_mesh(obj.data);bm.free()
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*a,**k):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/143',key='MN14',name='Attack Pods',culture='mauna',footprint=[2,2],definition_class=14,construction_updates=34,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_attack_pods.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=attachments,part_batches=part_batches,physical_chips=chips,well=dict(shape='Chamfered square',inner_halfwidth=.36,mouth_top=1.145,floor_top=.10,ground_level=0,fixed_open=True,hidden_floor_depth_authored=True,missile_clearance_calibrated=False),interpretation=['Own fixed-open body1, empty activity2..16 and foregroundmask17 govern the static open well. Three bent brass side fittings, two tall brass supports, one narrow rail/rib crosshead and one short pale post follow source and reviewed concept.','Hidden shaft lining/floor depth, support engineering, rib count, dimensions and material depths are authored. Generic Terran PB14 iris and ST14 technology tower do not establish Mauna operation.'],scale_contract='2x2 placement footprint, ground0, +Z up/-Y front. Cell-relative dimensions authored; metric launch corridor and missile socket are not calibrated.',concept_review='sources/docs/reconstruction/models/mn14-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_ATTACK_PODS_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
