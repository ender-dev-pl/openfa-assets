"""Author MN17 Advanced Extraction Unit from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/advanced-extraction-unit';maps=root/'sources/materials/mauna/advanced-extraction-unit';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611717);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-alloy-colour','brass-colour']}
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
            buffers['pale-alloy-colour'].extend([max(.01,c+cloud*.5+grain*.5-stain*.5+scratch*.3) for c in (.46,.51,.57)]+[1])
            buffers['brass-colour'].extend([max(.01,c+cloud*.4+grain*.4-stain*.6+scratch*.2) for c in (.39,.27,.10)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Pale nonmetal extraction access fields','pale-alloy-colour');dark=material('Dark nonemissive service recesses')
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
    red=material('Worn hooked red extraction stripe','marking-red-colour');brass=material('Tarnished brass roof posts','brass-colour',True);warm=material('Nine opaque warm extraction points');p=warm.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.70,.43,.10,1);p.inputs['Emission Color'].default_value=(.70,.43,.10,1);p.inputs['Emission Strength'].default_value=.35
    contacts=[];fields=[];chips=[];points=[]
    def prism(name,outline,a,b,axis,mat):
        count=len(outline);vertices=[(q,x,z) if axis=='X' else (x,q,z) for q in [a,b] for x,z in outline];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)];o=solid(name,vertices,faces,mat);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
    foot=box('Extraction Unit grounded foot',(0,-.07,.025),(2.64,1.54,.05),concrete,bevel=.005)
    tower=prism('Extraction Unit high continuous inclined block',[(-.64,.035),(.64,.035),(.64,1.85),(-.64,1.32)],-1.22,-.15,'X',concrete)
    lower=box('Extraction Unit low projecting body',(.53,0,.35),(1.44,1.28,.70),concrete,bevel=.005)
    ramp=prism('Extraction Unit sloping front tower foot',[(-.85,.025),(-.62,.025),(-.62,.48),(-.85,.12)],-1.22,-.15,'X',concrete)
    contacts += [dict(object=tower.name,support=foot.name,point=[-.70,0,.04]),dict(object=lower.name,support=foot.name,point=[.5,0,.04]),dict(object=ramp.name,support=foot.name,point=[-.7,-.75,.04]),dict(object=ramp.name,support=tower.name,point=[-.7,-.63,.2]),dict(object=lower.name,support=tower.name,point=[-.17,0,.35])]
    def blind(name,body,q,n,width,height,depth=.025,backmat=dark):
        q=Vector(q);n=Vector(n);cut(body,box('Temporary real blind field',q+n*.01,(width,height,(depth+.01)*2),concrete,n,0),'Actual blind service field')
        backing=box(name,q-n*(depth+.004),(width-.006,height-.006,.014),backmat,n,.001);fields.append(dict(object=backing.name,body=body.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.008));return q,n,depth
    blind('Extraction Unit tall dark front field',tower,(-.69,-.64,.80),(0,-1,0),.81,.78)
    blind('Extraction Unit low dark front field',lower,(.53,-.64,.31),(0,-1,0),1.08,.40)
    for i,z in enumerate([.22,.51]):blind('Extraction Unit pale square end panel '+str(i),lower,(1.25,.05,z),(1,0,0),.23,.23,backmat=edge)
    ducts=[]
    for i,y in enumerate([-.34,.34]):
        duct=prism('Extraction Unit long low roof duct '+str(i),[(-.20,.68),(1.10,.68),(1.10,.86),(.96,.98),(-.20,1.11)],y-.13,y+.13,'Y',concrete);ducts.append(duct)
        contacts += [dict(object=duct.name,support=lower.name,point=[.5,y,.69]),dict(object=duct.name,support=tower.name,point=[-.18,y,.90])]
        blind('Extraction Unit dark duct end '+str(i),duct,(1.10,y,.785),(1,0,0),.16,.10,.018)
    def roofheight(y):return 1.32+(y+.64)*.53/1.28
    outline=[(-1.13,-.64),(-.96,-.64),(-.96,-.32),(-.345,-.32),(-.345,-.64),(-.215,-.64),(-.215,-.19),(-.96,-.19),(-.96,.64),(-1.13,.64)];count=len(outline)
    vertices=[(x,y,roofheight(y)+offset) for offset in [-.006,.008] for x,y in outline];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)]
    roof=solid('Extraction Unit continuous red inclined crown hook',vertices,faces,red)
    contacts += [dict(object=roof.name,support=tower.name,point=q) for q in [[-1.04,0,1.582],[-.60,-.25,roofheight(-.25)-.003],[-.28,-.45,roofheight(-.45)-.003]]]
    for i,x in enumerate([-1.10,-.28]):
        strip=box('Extraction Unit red front downstroke '+str(i),(x,-.643,.80),(.13,.018,.88),red,bevel=.001);contacts.append(dict(object=strip.name,support=tower.name,point=[x+(-.03 if i==0 else .03),-.639,.80]))
    redramp=prism('Extraction Unit red sloping foot stripe',[(-.85,.114),(-.62,.474),(-.62,.488),(-.85,.128)],-1.13,-1.00,'X',red);contacts.append(dict(object=redramp.name,support=ramp.name,point=[-1.06,-.75,.274]))
    plinth=prism('Extraction Unit low brass post seating plinth',[(.22,roofheight(.22)-.02),(.48,roofheight(.48)-.02),(.48,1.81),(.22,1.81)],-.76,-.21,'X',concrete);contacts.append(dict(object=plinth.name,support=tower.name,point=[-.5,.35,roofheight(.35)-.01]))
    for i,(x,height) in enumerate([(-.65,.44),(-.32,.35)]):
        y=.36;surface=1.81
        post=box('Extraction Unit unequal brass upright '+str(i),(x,y,surface+height/2-.008),(.075,.075,height),brass,bevel=.005);contacts.append(dict(object=post.name,support=plinth.name,point=[x,y,surface-.004]))
    rib=box('Extraction Unit pale end structural rib',(1.253,.49,.35),(.030,.035,.65),edge,bevel=.002);contacts.append(dict(object=rib.name,support=lower.name,point=[1.245,.49,.35]))
    def point(name,backing,q,n,w,h,group):
        q=Vector(q);n=Vector(n);o=box(name,q+n*.009,(w,h,.016),warm,n,.001);contacts.append(dict(object=o.name,support=backing,point=list(q+n*.004)));points.append(dict(object=o.name,centre=list(q+n*.009),group=group))
    for i,x in enumerate([-1.00,-.80,-.60,-.40]):point('Extraction Unit tall warm point '+str(i),'Extraction Unit tall dark front field',(x,-.613,.99),(0,-1,0),.050,.068,'tall-front')
    for i,x in enumerate([.18,.53,.88]):point('Extraction Unit lower warm point '+str(i),'Extraction Unit low dark front field',(x,-.613,.31),(0,-1,0),.050,.058,'low-front')
    for i,y in enumerate([-.34,.34]):point('Extraction Unit duct warm point '+str(i),'Extraction Unit dark duct end '+str(i),(1.080,y,.785),(1,0,0),.040,.044,'duct-end')
    for obj in [tower,ramp,plinth,*ducts]:
        bevel=obj.modifiers.new('Restrained cast edge softening','BEVEL');bevel.width=.02 if obj==tower else .008;bevel.segments=1;apply(obj,bevel)
    for obj,q,n in [(tower,Vector((-1.22,.10,.55)),Vector((-1,0,0))),(foot,Vector((.73,-.84,.025)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.018,location=q+n*.012);cut(obj,bpy.context.object,'Actual shallow cast spall');chips.append(dict(body=obj.name,point=list(q),normal=list(n)))
    part_batches={};keep={o.name for o in [foot,tower,lower,ramp,plinth,*ducts]}
    for mat,label in [(edge,'three pale end assemblies'),(brass,'two unequal brass posts'),(red,'four continuous red assemblies'),(warm,'nine opaque warm source points'),(dark,'four dark blind backings')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]];assert objects
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Extraction Unit '+label;group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Extraction Unit '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/146';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z';placement['ground_level']=0;placement['preserve_ground_origin']=True
    bpy.context.view_layer.update()
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');uv=obj.data.uv_layers.active
        for face in obj.data.polygons:
            for index in face.loop_indices:
                q=obj.data.vertices[obj.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1)/2,q.z/2) if abs(face.normal.x)>.5 else ((q.x+1.5)/3,q.z/2) if abs(face.normal.y)>.5 else ((q.x+1.5)/3,(q.y+1)/2)
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');apply(obj,mod);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.to_mesh(obj.data);bm.free()
    bpy.context.view_layer.update();triangles=sum(len(obj.data.polygons) for obj in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*a,**k):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/146',key='MN17',name='Advanced Extraction Unit',culture='mauna',footprint=[3,3],definition_class=13,construction_updates=38,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,author='sources/tools/blender/remaster_mauna_advanced_extraction_unit.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=contacts,part_batches=part_batches,physical_chips=chips,warm_points=points,steady_point_emission=dict(colour=[.70,.43,.10],strength=.35,opaque=True,point_count=9,scope='Authored steady source-colour point appearance; no recovered pulse or client bloom guarantee.'),interpretation=['Own high inclined greyblue block, hooked red band, two unequal brass posts, low projecting body, two parallel low ducts, stacked pale end fields and warm point groups govern anatomy.','Hidden engineering, exact depths and cell-relative dimensions are authored. Generic Terran PB13/ST01 deep-drill machinery/rotation is context, not own Mauna operation.'],scale_contract='3x3 placement footprint, ground0, +Z up/-Y front. Native dimensions are authored; no recovered metric or calibrated client scale.',concept_review='sources/docs/reconstruction/models/mn17-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_ADVANCED_EXTRACTION_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
