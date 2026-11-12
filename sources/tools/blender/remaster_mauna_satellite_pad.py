"""Author MN10 Satellite Pad from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/satellite-pad';maps=root/'sources/materials/mauna/satellite-pad';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611010);buffers={name:[] for name in ['cast-concrete-colour','used-brass-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-alloy-colour']}
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
            buffers['used-brass-colour'].extend([max(.01,c+cloud*.7+grain*.5-stain*.9+scratch-pore*.3) for c in (.55,.36,.10)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Matte pale coated sensor masts','pale-alloy-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);dark=material('Dark nonemissive service recesses')
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
    green=material('Dark green nonemissive mast fields');green.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.018,.045,.025,1)
    lining=material('Dark slate nonemissive well lining');lining.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.025,.035,.050,1)
    black=material('Black nonemissive deep well floor');black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.001,.001,.001,1)
    def cylinder(name,radius,low,high,mat):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=high-low,location=(0,0,(low+high)/2))
        o=bpy.context.object;o.name=name;o.data.materials.append(mat);return o
    def annulus(name,outer,inner,low,high,mat):
        count=64;vertices=[(r*math.cos(i*math.tau/count),r*math.sin(i*math.tau/count),z) for r,z in [(outer,low),(outer,high),(inner,low),(inner,high)] for i in range(count)];faces=[]
        for i in range(count):
            j=(i+1)%count;faces.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),(count+i,count+j,3*count+j,3*count+i),(i,2*count+i,2*count+j,j)])
        return solid(name,vertices,faces,mat)
    vertices=[(x*r,y*r,z) for r,z in [(.90,.07),(.76,.74)] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    body=solid('Satellite Pad sloping cast concrete body',vertices,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],concrete)
    cut(body,cylinder('Temporary actual open bore',.56,-2,3,concrete),'Permanent circular open well')
    plinth=box('Satellite Pad low cast foot',(0,0,.05),(1.84,1.84,.10),concrete,bevel=.005)
    cut(plinth,cylinder('Temporary foot bore',.56,-2,3,concrete),'No concrete plug below opening')
    shaft=annulus('Satellite Pad underground slate lining',.59,.56,-1.24,.74,lining)
    floor=cylinder('Satellite Pad deep black floor',.59,-1.27,-1.23,black)
    attachments=[];fields=[]
    def anchored(name,centre,size,mat,support,point):
        o=box(name,centre,size,mat,bevel=.002);attachments.append(dict(object=o.name,support=support.name,point=point));return o
    for i,(x,y) in enumerate([(-.66,-.66),(.66,-.66),(.66,.66),(-.66,.66)]):
        anchored('Satellite Pad brass top post '+str(i),(x,y,.845),(.065,.065,.25),gold,body,[x,y,.733])
    # One connected, stepped-top flat upright; no diagonal brace/second mast.
    outline=[(.635,.725),(.755,.725),(.755,1.77),(.707,1.77),(.707,1.95),(.635,1.95)]
    vertices=[(x,y,z) for y in [.6925,.7475] for x,z in outline];n=len(outline)
    faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mast=solid('Satellite Pad single unbraced pale mast',vertices,faces,edge)
    bm=bmesh.new();bm.from_mesh(mast.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mast.data);bm.free()
    attachments.append(dict(object=mast.name,support=body.name,point=[.675,.72,.733]))
    rim=annulus('Satellite Pad narrow functional well rim',.61,.561,.732,.773,edge)
    attachments.append(dict(object=rim.name,support=body.name,point=[.602,0,.738]))
    for i in range(16):
        angle=i*math.tau/16;n=Vector((math.cos(angle),math.sin(angle),0));o=box('Satellite Pad vertical inner flute '+str(i),n*.564+Vector((0,0,.50)),(.022,.026,.49),edge,bevel=.001);o.rotation_euler.z=angle
        attachments.append(dict(object=o.name,support=shaft.name,point=list(n*.574+Vector((0,0,.50)))))
    attachments += [dict(object=body.name,support=plinth.name,point=[.80,0,.085]),dict(object=shaft.name,support=body.name,point=[.577,0,.20]),dict(object=floor.name,support=shaft.name,point=[.58,0,-1.235])]
    def surface(obj,face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));t=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inv=obj.matrix_world.inverted();hit,q,norm,_=obj.ray_cast(inv@(t*u+n*3+Vector((0,0,z))),inv.to_3x3()@(-n));assert hit;return obj.matrix_world@q,(obj.matrix_world.to_3x3()@norm).normalized()
    def field(name,obj,face,u,z,w,h,mat,depth=.018):
        q,n=surface(obj,face,u,z);cut(obj,box('Temporary blind field cutter',q+n*.01,(w,h,2*(depth+.01)),concrete,n,0),'Actual blind '+name)
        o=box('Satellite Pad '+name,q-n*(depth+.003),(w-.006,h-.006,.014),mat,n,.001);fields.append(dict(object=o.name,body=obj.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.007));return q,n,o
    q,n,back=field('front recessed vent',body,'front',-.12,.42,1.15,.30,dark,.045)
    v=(Vector((0,0,1))-n*n.z).normalized()
    for i,offset in enumerate([-.10,0,.10]):
        o=box('Satellite Pad front vent ledge '+str(i),q+v*offset-n*.040,(1.08,.025,.018),edge,n,.001)
        attachments.append(dict(object=o.name,support=back.name,point=list(q+v*offset-n*.048)))
    field('front right narrow vertical field',body,'front',.615,.37,.045,.31,dark,.020)
    for i,z in enumerate([1.50,1.62,1.74]):field('mast small green field '+str(i),mast,'front',.671,z,.035,.055,green,.012)
    outline=[(-.04,.14),(.06,.14),(.01,.03),(.075,.03),(-.03,-.14),(-.005,-.025),(-.07,-.025)]
    for i,u in enumerate([-.33,.26]):
        q,n=surface(body,'right',u,.46);t=Vector((0,1,0));v=(Vector((0,0,1))-n*n.z).normalized();vertices=[tuple(q+t*x+v*(z*1.15)+n*d) for d in [-.003,.003] for x,z in outline];count=len(outline);faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)];o=solid('Satellite Pad red source zigzag '+str(i),vertices,faces,red);attachments.append(dict(object=o.name,support=body.name,point=list(q+t*.03+v*.105-n*.001)))
    chips=[]
    for obj,p,n in [(body,Vector((.70,.05,.74)),Vector((0,0,1))),(plinth,Vector((.65,-.92,.055)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.020,location=p+n*.014);cut(obj,bpy.context.object,'Actual shallow cast service chip');chips.append(dict(body=obj.name,point=list(p),normal=list(n)))
    part_batches={};keep={body.name,plinth.name,shaft.name,floor.name}
    for mat,label in [(edge,'pale functional fittings'),(gold,'four brass posts'),(dark,'dark blind fields'),(red,'two red source markings'),(green,'three dark green mast fields')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]]
        if not objects:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Satellite Pad '+label;g=o.vertex_groups.new(name=o.name);g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Satellite Pad '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/139';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
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
                q=o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1.2)/2.4,q.z/2.8) if abs(f.normal.x)>.5 else ((q.x+1.2)/2.4,q.z/2.8) if abs(f.normal.y)>.5 else ((q.x+1.2)/2.4,(q.y+1.2)/2.4)
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
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/139',key='MN10',name='Satellite Pad',culture='mauna',footprint=[3,3],definition_class=9,construction_updates=24,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=8,author='sources/tools/blender/remaster_mauna_satellite_pad.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=attachments,part_batches=part_batches,physical_chips=chips,interpretation=['Own static open well,sloping square body,straight unbraced rear-right mast,four brass posts,front vent/narrow front field andtwo red right zigzags govern geometry.','Sixteen inner flutes,well depth,hidden mount engineering,recess dimensions andcell-relative proportions authored. GenericTerranPB09iris is not transferred. Extra lower-right slot/base artifact in concept omitted.'],scale_contract='3x3 placement footprint,+Zup/-Yfront;preserve ground0 andclosed horizontal span;underground well must not lift building. No recovered metric/payload dimensions.',concept_review='sources/docs/reconstruction/models/mn10-concept-review.json',animation_clips=[],well=dict(open_radius=.56,conservative_clear_radius=.54,floor_top=-1.23,ground_level=0,preserve_ground_origin=True,terrain_cutout_required=True),game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_SATELLITE_PAD_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
