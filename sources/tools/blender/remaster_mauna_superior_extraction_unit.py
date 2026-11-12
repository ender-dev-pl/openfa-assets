"""Author MN18 Superior Extraction Unit from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/superior-extraction-unit';maps=root/'sources/materials/mauna/superior-extraction-unit';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611818);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-module-colour','brass-colour']}
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
            cloud=.065*cast_noise(5,u,v)+.018*cast_noise(19,u,v);grain=rng.uniform(-.025,.025);stain=max(0,cast_noise(9,u,v))*.10;aggregate=speckles.get((x,y),0);pore=.15 if rng.random()<.035 else 0;dust=.07*max(0,1-v*5)
            concrete_delta=cloud+grain+aggregate-stain-pore-dust
            buffers['cast-concrete-colour'].extend([max(.01,c+concrete_delta) for c in (.29,.34,.41)]+[1])
            scratch=.17 if ((x*7+y*31)%991<2 and rng.random()<.7) else 0
            redbase=(.26,.29,.32) if pore and grain>.007 else (.38,.018,.012)
            buffers['marking-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in redbase]+[1])
            buffers['concrete-orm'].extend([1,min(.98,max(.68,.85+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.76,max(.32,.54+grain+stain)),.72,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.035,.035),.5+rng.uniform(-.035,.035),1,1])
            buffers['pale-module-colour'].extend([max(.01,c+concrete_delta*.8) for c in (.42,.49,.48)]+[1])
            buffers['brass-colour'].extend([max(.01,c+cloud*.4+grain*.4-stain*.6+scratch*.2) for c in (.54,.39,.16)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Pale angular extraction module and guides','pale-module-colour');dark=material('Dark opaque green service recesses');dark.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.012,.025,.017,1)
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
    brass=material('Tarnished brass extraction fittings','brass-colour',True);red=material('Worn red inset extraction fields','marking-red-colour');warm=material('Seven opaque yellowgreen extraction points');p=warm.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.75,.65,.15,1);p.inputs['Emission Color'].default_value=(.75,.65,.15,1);p.inputs['Emission Strength'].default_value=.45
    contacts=[];fields=[];tri_fields=[];points=[];chips=[]
    def prism(name,outline,a,b,axis,mat):
        count=len(outline);vertices=[(q,x,z) if axis=='X' else (x,q,z) for q in [a,b] for x,z in outline];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)];o=solid(name,vertices,faces,mat);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
    base=box('Superior Unit low broad grounded base',(0,0,.18),(2.50,2.20,.36),concrete,bevel=.006)
    outer=[(-.90,-.35),(.30,-.35),(.30,.85),(-.90,.85)];inner=[(-.72,-.17),(.12,-.17),(.12,.67),(-.72,.67)]
    vertices=[(x,y,z) for ring,z in [(outer,.34),(outer,1.13),(inner,1.36)] for x,y in ring];faces=[(3,2,1,0),(8,9,10,11)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]+[(i+4,(i+1)%4+4,(i+1)%4+8,i+8) for i in range(4)]
    body=solid('Superior Unit pale angular block and sloping shoulder',vertices,faces,edge);contacts.append(dict(object=body.name,support=base.name,point=[-.3,.25,.35]))
    def blind(name,body,q,n,width,height,depth=.025,backmat=dark):
        q=Vector(q);n=Vector(n);cut(body,box('Temporary real blind field',q+n*.01,(width,height,(depth+.01)*2),concrete,n,0),'Actual blind service field')
        backing=box(name,q-n*(depth+.004),(width-.006,height-.006,.014),backmat,n,.001);fields.append(dict(object=backing.name,body=body.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.008));return backing
    blind('Superior Unit wide front dark field',base,(-.57,-1.10,.20),(0,-1,0),1.20,.24)
    channels=[]
    for i,y in enumerate([-.78,-.26,.26,.78]):
        channel=prism('Superior Unit low base channel '+str(i),[(.28,.34),(1.25,.34),(1.25,.44),(1.10,.52),(.28,.52)],y-.16,y+.16,'Y',concrete);channels.append(channel);contacts.append(dict(object=channel.name,support=base.name,point=[.8,y,.35]))
        blind('Superior Unit dark end bay '+str(i),base,(1.25,y,.20),(1,0,0),.29,.24)
    for i,(x,z,width,height) in enumerate([(-.68,.96,.30,.20),(-.68,.61,.30,.34),(-.10,.61,.55,.34)]):blind('Superior Unit rectangular red front field '+str(i),body,(x,-.35,z),(0,-1,0),width,height,.022,red)
    outline=[(-.40,1.08),(.19,.90),(-.40,.84)];centre=Vector((sum(x for x,z in outline)/3,-.35,sum(z for x,z in outline)/3))
    cut(body,prism('Temporary upper triangular field',outline,-.40,-.328,'Y',concrete),'Actual triangular red pocket')
    inset=[(centre.x+(x-centre.x)*.96,centre.z+(z-centre.z)*.96) for x,z in outline];triangle=prism('Superior Unit tapered upper right red field',inset,-.333,-.317,'Y',red);tri_fields.append(dict(object=triangle.name,body=body.name,point=list(centre),normal=[0,-1,0],depth=.022,contact_depth=.028))
    guides=[]
    for i,x in enumerate([-.57,-.29]):
        guide=box('Superior Unit tall pale guide '+str(i),(x,.27,1.665),(.055,.070,.63),edge,bevel=.003);guides.append(guide);contacts.append(dict(object=guide.name,support=body.name,point=[x,.27,1.355]))
    bar=box('Superior Unit shorter brass bar between guides',(-.43,.27,1.56),(.12,.06,.42),brass,bevel=.004);contacts.append(dict(object=bar.name,support=body.name,point=[-.43,.27,1.355]))
    stub=box('Superior Unit short pale rear roof stub',(.05,.60,1.45),(.065,.065,.20),edge,bevel=.003);contacts.append(dict(object=stub.name,support=body.name,point=[.05,.60,1.355]))
    stud=box('Superior Unit small brass front shoulder stud',(-.20,-.20,1.35),(.070,.065,.14),brass,bevel=.003);contacts.append(dict(object=stud.name,support=body.name,point=[-.20,-.20,1.30]))
    plaque=box('Superior Unit brass two-port side plaque',(.309,.08,.875),(.03,.22,.40),brass,bevel=.002);contacts.append(dict(object=plaque.name,support=body.name,point=[.299,.08,.875]))
    for i,z in enumerate([.78,.97]):blind('Superior Unit dark brass plaque port '+str(i),plaque,(.324,.08,z),(1,0,0),.08,.07,.008)
    strip=box('Superior Unit separate rear brass upright',(.309,.64,.73),(.035,.065,.50),brass,bevel=.003);contacts.append(dict(object=strip.name,support=body.name,point=[.298,.64,.73]))
    for i,x in enumerate([.47,.69]):
        rail=box('Superior Unit seated brass base corner rail '+str(i),(x,-1.107,.23),(.065,.035,.44),brass,bevel=.003);contacts.append(dict(object=rail.name,support=base.name,point=[x,-1.095,.23]))
    def point(name,backing,q,n,group):
        q=Vector(q);n=Vector(n);o=box(name,q+n*.009,(.046,.050,.016),warm,n,.001);contacts.append(dict(object=o.name,support=backing,point=list(q+n*.004)));points.append(dict(object=o.name,centre=list(q+n*.009),group=group))
    for i,x in enumerate([-.97,-.58,-.19]):point('Superior Unit front warm point '+str(i),'Superior Unit wide front dark field',(x,-1.073,.20),(0,-1,0),'front-three')
    for i,y in enumerate([-.78,-.26,.26,.78]):point('Superior Unit end warm point '+str(i),'Superior Unit dark end bay '+str(i),(1.223,y,.20),(1,0,0),'end-four')
    for obj in [body,*channels]:
        bevel=obj.modifiers.new('Restrained used cast edge chamfer','BEVEL');bevel.width=.008;bevel.segments=1;apply(obj,bevel)
    for obj,q,n in [(body,Vector((-.90,.4,.70)),Vector((-1,0,0))),(base,Vector((.95,-1.10,.20)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.018,location=q+n*.012);cut(obj,bpy.context.object,'Actual shallow cast spall');chips.append(dict(body=obj.name,point=list(q),normal=list(n)))
    part_batches={};keep={o.name for o in [base,body,*channels]}
    for mat,label in [(edge,'two pale guides and short stub'),(brass,'six attached brass fittings'),(red,'four split red front fields'),(warm,'seven opaque warm source points'),(dark,'seven dark seated backings')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]];assert objects
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Superior Unit '+label;group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Superior Unit '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/147';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z';placement['ground_level']=0;placement['preserve_ground_origin']=True
    bpy.context.view_layer.update()
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');uv=obj.data.uv_layers.active
        for face in obj.data.polygons:
            for index in face.loop_indices:
                q=obj.data.vertices[obj.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1.2)/2.4,q.z/2) if abs(face.normal.x)>.5 else ((q.x+1.3)/2.6,q.z/2) if abs(face.normal.y)>.5 else ((q.x+1.3)/2.6,(q.y+1.2)/2.4)
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');apply(obj,mod);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.to_mesh(obj.data);bm.free()
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*a,**k):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    meta=dict(schema_version=1,issue=261,id='openfa:building/legacy/147',key='MN18',name='Superior Extraction Unit',culture='mauna',footprint=[3,3],definition_class=21,construction_updates=44,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,author='sources/tools/blender/remaster_mauna_superior_extraction_unit.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,triangular_recesses=tri_fields,attachment_contacts=contacts,part_batches=part_batches,physical_chips=chips,warm_points=points,steady_point_emission=dict(colour=[.75,.65,.15],strength=.45,opaque=True,point_count=7,scope='Authored steady source-colour point appearance,not recovered flashing or client bloom.'),interpretation=['Own broad base/four channels, compact pale shouldered block/split red fields, paired pale guides/central shorter brass bar, sparse stubs and side/corner brass fittings govern anatomy.','Hidden walls,port shape and depth,three-dimensional guide/bar cross-sections and cell-relative dimensions develop the reviewed concept as authored engineering. Generic PB21/ST24 machinery/timing is not Mauna operation.'],scale_contract='3x3 placement footprint,ground0,+Z up/-Y front. Authored cell-relative dimensions,no recovered metric or calibrated client scale.',concept_review='sources/docs/reconstruction/models/mn18-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('MAUNA_SUPERIOR_EXTRACTION_AUTHORED',triangles,len(meshes),len(contacts),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
