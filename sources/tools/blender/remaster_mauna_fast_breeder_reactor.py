"""Author MN11 Fast Breeder Reactor from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/fast-breeder-reactor';maps=root/'sources/materials/mauna/fast-breeder-reactor';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611111);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-alloy-colour']}
    # Deterministic sparse roughcast spalls, patina streaks and fine pores.
    # These are authored surface maps,not borrowed legacy pixels.
    grids={n:[[rng.uniform(-1,1) for _ in range(n)] for _ in range(n)] for n in [5,9,19]}
    def cast_noise(n,u,v):
        x=u*n;y=v*n;ix=int(x);iy=int(y);a=x-ix;b=y-iy;a=a*a*(3-2*a);b=b*b*(3-2*b);g=grids[n]
        return (g[iy%n][ix%n]*(1-a)+g[iy%n][(ix+1)%n]*a)*(1-b)+(g[(iy+1)%n][ix%n]*(1-a)+g[(iy+1)%n][(ix+1)%n]*a)*b
    speckles={}
    for i in range(85):
        cx=rng.randrange(size);cy=rng.randrange(size);radius=rng.randrange(2,7)
        for dy in range(-radius,radius+1):
            for dx in range(-radius,radius+1):
                if dx*dx+dy*dy<radius*radius*rng.uniform(.65,1.1):speckles[((cx+dx)%size,(cy+dy)%size)]=rng.uniform(.035,.10)
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
    red=material('Two worn source red zigzags','marking-red-colour')
    red=material('Worn source muted red vertical strips','marking-red-colour')
    light=material('Opaque pale blue-white service fields');node=light.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.52,.75,.86,1);node.inputs['Roughness'].default_value=.43;node.inputs['Emission Color'].default_value=(.35,.60,.75,1);node.inputs['Emission Strength'].default_value=.65
    ribmetal=material('Darker worn vertical service metal');ribmetal.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.12,.16,.19,1);ribmetal.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.62
    green=material('Tiny opaque muted green service points');green.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.015,.040,.020,1)
    attachments=[];fields=[];bodies=[]
    def loft(name,rings):
        vertices=[]
        for r,z in rings:
            c=.06
            vertices += [(x,y,z) for x,y in [(r-c,-r),(r,-r+c),(r,r-c),(r-c,r),(-r+c,r),(-r,r-c),(-r,-r+c),(-r+c,-r)]]
        faces=[tuple(reversed(range(8))),tuple(range(8*(len(rings)-1),8*len(rings)))]
        for k in range(len(rings)-1):
            for i in range(8):j=(i+1)%8;faces.append((8*k+i,8*k+j,8*(k+1)+j,8*(k+1)+i))
        o=solid(name,vertices,faces,concrete);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
    for i in range(3):
        base=float(i);top=.92 if i<2 else 1.10
        bodies.append(loft('Fast Breeder Reactor main module '+str(i),[(.30,base+.025),(.36,base+.105),(.36,base+.80),(.28 if i==2 else .30,base+top)]))
    foot=box('Fast Breeder Reactor narrow cast foot',(0,0,.025),(.61,.61,.05),concrete,bevel=.003)
    attachments.append(dict(object=bodies[0].name,support=foot.name,point=[0,0,.035]))
    necks=[]
    for i in range(2):
        o=box('Fast Breeder Reactor connected waist '+str(i),(0,0,i+.9675),(.54,.54,.165),concrete,bevel=.003);necks.append(o)
        attachments += [dict(object=o.name,support=bodies[i].name,point=[0,0,i+.905]),dict(object=o.name,support=bodies[i+1].name,point=[0,0,i+1.035])]
    def surface(obj,face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));t=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inv=obj.matrix_world.inverted();hit,q,norm,_=obj.ray_cast(inv@(t*u+n*3+Vector((0,0,z))),inv.to_3x3()@(-n));assert hit;return obj.matrix_world@q,(obj.matrix_world.to_3x3()@norm).normalized()
    def field(name,obj,face,u,z,w,h,mat,depth=.018):
        q,n=surface(obj,face,u,z);cut(obj,box('Temporary blind field cutter',q+n*.01,(w,h,2*(depth+.01)),concrete,n,0),'Actual blind '+name)
        o=box('Fast Breeder Reactor '+name,q-n*(depth+.003),(w-.006,h-.006,.014),mat,n,.001);fields.append(dict(object=o.name,body=obj.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.007));return q,n,o
    for i,o in enumerate(bodies):
        z=float(i)
        field('red vertical strip '+str(i),o,'front',-.24,z+.455,.11,.61,red,.012)
        q,n,back=field('main dark vertical recess '+str(i),o,'front',.06,z+.455,.20,.61,dark,.025)
        for j,x in enumerate([.025,.11]):
            rib=box('Fast Breeder Reactor vertical service rib '+str(i)+' '+str(j),Vector((x,q.y,z+.455))-n*.020,(.018,.53,.018),ribmetal,n,.001)
            attachments.append(dict(object=rib.name,support=back.name,point=[x,float((q-n*.028).y),z+.455]))
        field('narrow dark vertical recess '+str(i),o,'front',.235,z+.455,.025,.58,dark,.015)
        field('muted green field '+str(i),o,'front',-.13,z+.765,.025,.023,green,.006)
        for j,u in enumerate([-.12,.12]):
            field('bright right service field '+str(i)+' '+str(j),o,'right',u,z+.55,.18,.48,light,.015)
            field('lower opaque right field '+str(i)+' '+str(j),o,'right',u,z+.20,.16,.13,edge,.012)
    stub=box('Fast Breeder Reactor short roof stub',(-.19,.08,3.19),(.045,.045,.20),edge,bevel=.002)
    attachments.append(dict(object=stub.name,support=bodies[2].name,point=[-.19,.08,3.095]))
    for i,(x,y) in enumerate([(0,-.08),(.16,.02)]):
        q=Vector((x,y,3.10));n=Vector((0,0,1));depth=.012
        cut(bodies[2],box('Temporary roof blind field',q+n*.005,(.09,.08,.034),concrete,bevel=0),'Actual roof blind recess')
        back=box('Fast Breeder Reactor small roof field '+str(i),q-n*(depth+.003),(.084,.074,.014),dark,bevel=.001);fields.append(dict(object=back.name,body=bodies[2].name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.007))
    chips=[]
    for o,p,n in [(bodies[0],Vector((-.13,-.36,.40)),Vector((0,-1,0))),(bodies[2],Vector((.36,.27,2.70)),Vector((1,0,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.020,location=p+n*.014);cut(o,bpy.context.object,'Actual small cast service chip');chips.append(dict(body=o.name,point=list(p),normal=list(n)))
    part_batches={};keep={o.name for o in bodies+necks+[foot]}
    for mat,label in [(edge,'pale service assemblies'),(dark,'dark blind fields'),(red,'three red vertical strips'),(light,'six bright right fields'),(green,'three muted green fields'),(ribmetal,'six dark service ribs')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]]
        if not objects:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Fast Breeder Reactor '+label;g=o.vertex_groups.new(name=o.name);g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Fast Breeder Reactor '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/140';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    placement['preserve_ground_origin']=True;placement['ground_level']=0
    bpy.context.view_layer.update()
    for o in meshes:
        o.parent=placement
        bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);materials=[];indices=[]
        for f in o.data.polygons:
            mat=o.data.materials[f.material_index]
            if mat not in materials:materials.append(mat)
            indices.append(materials.index(mat))
        o.data.materials.clear()
        for mat in materials:o.data.materials.append(mat)
        for f,index in zip(o.data.polygons,indices):f.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        uv=o.data.uv_layers.active
        for f in o.data.polygons:
            for index in f.loop_indices:
                q=o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1.2)/2.4,q.z/3.3) if abs(f.normal.x)>.5 else ((q.x+1.2)/2.4,q.z/3.3) if abs(f.normal.y)>.5 else ((q.x+1.2)/2.4,(q.y+1.2)/2.4)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');apply(o,mod);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name;bm.to_mesh(o.data);bm.free()
        for f in o.data.polygons:f.use_smooth=False
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/140',key='MN11',name='Fast Breeder Reactor',culture='mauna',footprint=[2,2],definition_class=28,construction_updates=52,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=7,author='sources/tools/blender/remaster_mauna_fast_breeder_reactor.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=attachments,part_batches=part_batches,physical_chips=chips,steady_service_field_emission=dict(colour=[.35,.60,.75],strength=.65,opaque=True,scope='Authored steady source-colour preservation;not recovered timed operation or exposed reactor core.'),interpretation=['Three connected vertically elongated chamfered modules,red left-face strips/dark recesses,paired bright right service fields/smaller opaque fields below,sloping top andshort roofstub govern geometry.','Hidden rear walls,waist engineering,blind depths,roof field reading andcell-relative proportions authored. GenericTerranSolarMatrix/PB28/ST27 andPowerplant/ST21arecontext,not this Mauna anatomy or operation.'],scale_contract='2x2 placement footprint,+Zup/-Yfront,ground0. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn11-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_FAST_BREEDER_REACTOR_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
