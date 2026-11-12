"""Author MN12 Arms Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/arms-block';maps=root/'sources/materials/mauna/arms-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611212);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-alloy-colour']}
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
    red=material('Worn red source three-pronged industrial mark','marking-red-colour')
    amber=material('Opaque warm amber service points');p=amber.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.55,.30,.06,1);p.inputs['Roughness'].default_value=.40;p.inputs['Emission Color'].default_value=(.30,.18,.05,1);p.inputs['Emission Strength'].default_value=.65
    attachments=[];fields=[];points=[]
    def prism(name,outline,a,b,axis,mat):
        vertices=[(x,u,v) if axis=='X' else (u,x,v) for x in [a,b] for u,v in outline];n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        o=solid(name,vertices,faces,mat);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
    base=box('Arms Block low rectangular cast plinth',(.06,-.04,.06),(2.24,1.28,.12),concrete,bevel=.005)
    body=prism('Arms Block tall inclined emblem block',[(-.60,.10),(.54,.10),(.54,1.85),(-.15,1.85)],-1.00,-.10,'X',concrete)
    lower=box('Arms Block lower connected service block',(.40,.005,.75),(1.04,1.07,1.30),concrete,bevel=.004)
    nose=prism('Arms Block low projecting sloping end foot',[(.89,.08),(1.18,.08),(1.18,.16),(.98,.47),(.89,.47)],-.58,.55,'Y',concrete)
    tower=box('Arms Block square upper tower',(-.56,.20,2.315),(.52,.48,.97),concrete,bevel=.005)
    post=box('Arms Block short lower roof service post',(.40,.07,1.5775),(.10,.14,.385),concrete,bevel=.003)
    attachments += [dict(object=body.name,support=base.name,point=[-.7,0,.11]),dict(object=lower.name,support=base.name,point=[.5,0,.11]),dict(object=nose.name,support=lower.name,point=[.905,0,.35]),dict(object=nose.name,support=base.name,point=[1.1,0,.10]),dict(object=tower.name,support=body.name,point=[-.56,.20,1.842]),dict(object=post.name,support=lower.name,point=[.4,.07,1.395]),dict(object=body.name,support=lower.name,point=[-.11,0,.9])]
    def anchored(name,centre,size,mat,support,witness):
        o=box(name,centre,size,mat,bevel=.002);attachments.append(dict(object=o.name,support=support.name,point=witness));return o
    cap=anchored('Arms Block pale tower roof cap',(-.56,.20,2.81),(.56,.52,.03),edge,tower,[-.56,.20,2.797])
    anchored('Arms Block long roof mast',(-.48,.24,3.21),(.045,.045,.80),edge,cap,[-.48,.24,2.815])
    anchored('Arms Block short roof mast',(-.70,.11,2.935),(.040,.040,.25),edge,cap,[-.70,.11,2.815])
    def surface(obj,face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));t=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inv=obj.matrix_world.inverted();hit,q,norm,_=obj.ray_cast(inv@(t*u+n*4+Vector((0,0,z))),inv.to_3x3()@(-n));assert hit;return obj.matrix_world@q,(obj.matrix_world.to_3x3()@norm).normalized()
    def field(name,obj,face,u,z,w,h,depth=.024):
        q,n=surface(obj,face,u,z);cut(obj,box('Temporary blind field cutter',q+n*.01,(w,h,2*(depth+.01)),concrete,n,0),'Actual blind '+name)
        back=box('Arms Block '+name,q-n*(depth+.003),(w-.006,h-.006,.014),dark,n,.001);fields.append(dict(object=back.name,body=obj.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.007));return q,n,back
    def pane(group,index,q,n,back,du,dv,w=.035,h=.045):
        u=Vector((1,0,0)) if abs(n.y)>.5 else Vector((0,1,0));v=(Vector((0,0,1))-n*n.z).normalized();centre=q+u*du+v*dv-n*.019
        o=box('Arms Block amber '+group+' '+str(index),centre,(w,h,.014),amber,n,.001);witness=q+u*du+v*dv-n*.023;attachments.append(dict(object=o.name,support=back.name,point=list(witness)));points.append(dict(object=o.name,group=group,centre=list(centre)))
    q,n,b=field('tower front dark field',tower,'front',-.56,2.36,.33,.66)
    for i,(u,v) in enumerate([(0,.25),(-.07,.04),(.07,.04),(-.07,-.11),(.07,-.11)]):pane('tower-front',i,q,n,b,u,v)
    q,n,b=field('tower right dark field',tower,'right',.20,2.36,.27,.66)
    for i,v in enumerate([.25,0,-.15]):pane('tower-right',i,q,n,b,0,v)
    q,n,b=field('lower upper front dark field',lower,'front',.23,1.04,.48,.35)
    for i,v in enumerate([.065,-.065]):pane('lower-front-upper',i,q,n,b,-.12,v)
    q,n,b=field('lower lower front dark field',lower,'front',.23,.56,.48,.37)
    for i,(u,v) in enumerate([(-.12,.075),(-.12,-.075),(.14,.075),(.14,-.075)]):pane('lower-front-lower',i,q,n,b,u,v)
    q,n,b=field('lower end dark field',lower,'right',-.02,.67,.64,.60)
    for i,(u,v) in enumerate([(-.19,.085),(-.19,-.085),(.19,.085),(.19,-.085)]):pane('lower-end',i,q,n,b,u,v)
    q,n,b=field('roof post dark field',post,'front',.40,1.58,.07,.14,.024);pane('roof-post',0,q,n,b,0,0,.030,.041)
    for i,x in enumerate([-.91,-.65,-.37]):
        q,n,b=field('under emblem dark field '+str(i),body,'front',x,.285,.14,.10);pane('under-emblem',i,q,n,b,0,0,.030,.039)
    # Pale framing sits into the actual end face, including its recessed centre.
    for i,y in enumerate([-.42,-.02,.38]):anchored('Arms Block pale end upright '+str(i),(.923,y,.75),(.065,.055,.82),edge,lower,[.892,y,.75])
    anchored('Arms Block pale end cross frame',(.923,-.02,1.10),(.065,.87,.045),edge,lower,[.91,0,1.10])
    for i,x in enumerate([.10,.66]):
        vent=anchored('Arms Block low roof service fitting '+str(i),(x,-.23,1.425),(.19,.18,.07),edge,lower,[x,-.23,1.395]);field('roof fitting dark field '+str(i),vent,'front',x,1.425,.13,.028,.024)
    # One closed thin paint solid follows the continuous inclined source wall.
    outline=[(-.31,-.55),(-.31,.25),(-.12,.25),(-.12,.65),(.03,.65),(.03,.29),(.27,.29),(.27,-.55),(.13,-.55),(.13,.11),(.03,.11),(.03,-.55),(-.11,-.55),(-.11,.11),(-.17,.11),(-.17,-.55)]
    q,n=surface(body,'front',-.56,1.00);u=Vector((1,0,0));v=(Vector((0,0,1))-n*n.z).normalized();vertices=[tuple(q+u*x+v*z+n*d) for d in [-.003,.003] for x,z in outline];count=len(outline);faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)];mark=solid('Arms Block red source three-pronged mark',vertices,faces,red);bm=bmesh.new();bm.from_mesh(mark.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mark.data);bm.free();attachments.append(dict(object=mark.name,support=body.name,point=list(q+u*(-.24)-n*.001)))
    chips=[]
    for o,p,n in [(body,Vector((-.96,.0,1.85)),Vector((0,0,1))),(base,Vector((.78,-.68,.055)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.020,location=p+n*.014);cut(o,bpy.context.object,'Actual shallow cast service chip');chips.append(dict(body=o.name,point=list(p),normal=list(n)))
    part_batches={};keep={o.name for o in [body,lower,base,nose,tower,post]}
    for mat,label in [(edge,'pale roof and end assemblies'),(dark,'dark blind backings'),(red,'red industrial mark'),(amber,'twenty-two source amber points')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]]
        if not objects:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Arms Block '+label;g=o.vertex_groups.new(name=o.name);g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Arms Block '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/141';placement['footprint']=[4,4];placement['local_forward']='-Y';placement['local_up']='+Z'
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
                q=o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1.2)/2.4,q.z/3.8) if abs(f.normal.x)>.5 else ((q.x+1.2)/2.4,q.z/3.8) if abs(f.normal.y)>.5 else ((q.x+1.2)/2.4,(q.y+1.2)/2.4)
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
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/141',key='MN12',name='Arms Block',culture='mauna',footprint=[4,4],definition_class=7,construction_updates=36,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_arms_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=attachments,part_batches=part_batches,physical_chips=chips,warm_points=points,steady_service_field_emission=dict(colour=[.30,.18,.05],strength=.65,opaque=True,scope='Authored steady source-colour preservation,not recovered light phases.'),interpretation=['Own sloping red-emblem block,tower with two unequal masts,lower service block/end framing/sloping foot/roof post and22visible warm points govern anatomy.','Hidden rear walls,roof-fitting depths,paint profile,mount engineering andcell-relative dimensions authored. GenericPB07factory/ST06armour context doesnot establish Mauna operation.'],scale_contract='4x4 placement footprint,+Zup/-Yfront,ground0. Cell-relative dimensions authored;metric scale not recovered.',concept_review='sources/docs/reconstruction/models/mn12-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_ARMS_BLOCK_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
