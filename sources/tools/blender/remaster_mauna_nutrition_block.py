"""Author MN03 Nutrition Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/nutrition-block';maps=root/'sources/materials/mauna/nutrition-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610303);buffers={name:[] for name in ['cast-concrete-colour','chipped-concrete-edge-colour','used-brass-colour','recess-red-colour','concrete-orm','metal-orm','cast-service-normal']}
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
            buffers['cast-concrete-colour'].extend([max(.01,c+concrete_delta) for c in (.29,.34,.41)]+[1]);buffers['chipped-concrete-edge-colour'].extend([max(.01,c+concrete_delta) for c in (.40,.45,.51)]+[1])
            scratch=.17 if ((x*7+y*31)%991<2 and rng.random()<.7) else 0
            buffers['used-brass-colour'].extend([max(.01,c+cloud*.7+grain*.5-stain*.9+scratch-pore*.3) for c in (.55,.36,.10)]+[1])
            buffers['recess-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in (.49,.105,.070)]+[1])
            buffers['concrete-orm'].extend([1,min(.98,max(.68,.85+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.76,max(.32,.54+grain+stain)),.72,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.035,.035),.5+rng.uniform(-.035,.035),1,1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Mauna exposed aggregate edge','chipped-concrete-edge-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);red=material('Dark red nonemissive recessed fittings','recess-red-colour');dark=material('Dark nonemissive service recesses')
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
    profile=[(.08,1.03),(.23,1.06),(.68,.74),(.78,.69),(2.52,.69)]
    verts=[(x*h,y*h,z) for z,h in profile for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]];faces=[]
    for j in range(len(profile)-1):
        for i in range(4):faces.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
    faces.extend([(3,2,1,0),tuple((len(profile)-1)*4+i for i in range(4))]);body=solid('Nutrition Block square tower and flared base',verts,faces,concrete);body.data.materials.append(edge);mod=body.modifiers.new('Small cast perimeter chamfers','BEVEL');mod.width=.007;mod.segments=2;mod.material=1;apply(body,mod)
    def surface(face,u,z):
        normal=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));origin=tangent*u+normal*3+Vector((0,0,z));bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(origin,-normal);assert hit;return q,n
    rects=[]
    def recess(family,face,u,z,width,height,mat):
        q,n=surface(face,u,z);cut(body,box('Temporary actual recess',q+n*.015,(width,height,.10),concrete,n,0),'Blind service field '+family);name='Nutrition Block '+family;box(name,q-n*.037,(width-.006,height-.006,.014),mat,n,.001);rects.append(dict(family=family,object=name,point=list(q),normal=list(n),depth=.035));return q,n
    for family,face,u,z,w,h in [('short red strip','front',-.45,1.31,.10,.80),('near red strip','front',.59,1.56,.08,1.55),('far red strip','right',.59,1.56,.08,1.55)]:recess(family,face,u,z,w,h,red)
    for i,u in enumerate([-.35,-.12,.11]):recess('upper dark slot '+str(i),'right',u,2.18,.075,.32,dark)
    q,n=recess('front vent backing','front',-.04,2.13,.96,.42,dark);slats=[]
    for i,z in enumerate([2.04,2.22]):
        centre=Vector((q.x,q.y,z));box('Nutrition Block pale vent slat '+str(i),centre-n*.030,(.88,.060,.050),edge,n,.002);slats.append(dict(index=i,point=list(centre-n*.043)))
    q,n=recess('amber stack backing','right',-.10,1.34,.20,.70,dark);amber=[]
    for i,z in enumerate([1.12,1.34,1.56]):
        centre=Vector((q.x,q.y,z));box('Nutrition Block amber stack point '+str(i),centre-n*.024,(.12,.12,.032),gold,n,.003);amber.append(dict(index=i,point=list(centre-n*.034)))
    pale=[]
    for i,z in enumerate([1.00,1.20,1.40]):
        q,n=surface('front',.08,z);box('Nutrition Block pale front point '+str(i),q+n*.012,(.065,.065,.040),edge,n,.002);pale.append(dict(index=i,point=list(q-n*.004)))
    roof=box('Nutrition Block low square roof cap',(0,0,2.57),(.62,.62,.18),concrete,bevel=.005)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.065,depth=.08,location=(0,0,2.66));cut(roof,bpy.context.object,'Blind round roof point recess');bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.052,depth=.040,location=(0,0,2.635));top=bpy.context.object;top.name='Nutrition Block small brass roof point';top.data.materials.append(gold);mod=top.modifiers.new('Worn point chamfer','BEVEL');mod.width=.002;mod.segments=2;apply(top,mod)
    def join_parts(objects,name):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
    feet=[];fins_meta=[]
    for face in range(4):
        angle=face*math.pi/2;normal=Vector((math.sin(angle),-math.cos(angle),0));tangent=Vector((math.cos(angle),math.sin(angle),0));fins=[]
        for i,u in enumerate([-.52,0,.52]):
            outline=[(.78,.74),(.70,.73),(.98,.24),(1.10,.24)];verts=[tangent*(u+du)+normal*d+Vector((0,0,z)) for du in [-.055,.055] for d,z in outline];f=[(3,2,1,0),(4,5,6,7)]+[(j,(j+1)%4,(j+1)%4+4,j+4) for j in range(4)];fins.append(solid('Pale base buttress '+str(face)+' '+str(i),verts,f,edge));centre=tangent*u+normal*1.075+Vector((0,0,.165));foot=box('Brass foot '+str(face)+' '+str(i),centre,(.145,.16,.31),gold,bevel=.004);foot.rotation_euler.z=angle;feet.append(foot);fins_meta.append(dict(face=face,index=i,body_contact=list(tangent*u+normal*.731+Vector((0,0,.695))),foot_contact=list(tangent*u+normal*1.044+Vector((0,0,.26)))))
        join_parts(fins,'Nutrition Block three pale buttresses face '+str(face))
    join_parts(feet,'Nutrition Block twelve brass feet')
    chips=[]
    for label,target,point,normal in [('roof',roof,Vector((.21,-.17,2.66)),Vector((0,0,1))),('tower',body,Vector((.69,-.46,1.84)),Vector((1,0,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.030,location=point+normal*.023);cut(target,bpy.context.object,'Actual shallow service chip '+label);chips.append(dict(label=label,object=target.name,point=list(point),normal=list(normal)))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/132';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
    for o in meshes:
        o.parent=placement;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);materials=[];indices=[]
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
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/132',key='MN03',name='Nutrition Block',culture='mauna',footprint=[3,3],definition_class=37,construction_updates=26,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_nutrition_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=rects,vent_slats=slats,amber_stack=amber,pale_front_points=pale,buttress_contacts=fins_meta,roof_point_floor=2.62,physical_chips=chips,interpretation=['Own tallsquareconcretetower/flaredbase,3pale/brassfeetpervisibleface,front2slats/3palepoints,right3slots/3amberpoints,redstrips andsmallroundroofpoint govern geometry.','Hiddenrearfootrepeat,internalrecessdepths andcellrelative dimensions authored. PB37isgenericTerranfunctioncontext,notMauna geometry oroperatingmotion. No exposedvats/glow inferred.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn03-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_NUTRITION_BLOCK_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
