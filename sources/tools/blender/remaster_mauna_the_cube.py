"""Author MN06 The Cube from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/the-cube';maps=root/'sources/materials/mauna/the-cube';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610606);buffers={name:[] for name in ['cast-concrete-colour','pale-alloy-colour','used-brass-colour','recess-red-colour','concrete-orm','metal-orm','cast-service-normal']}
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
            buffers['cast-concrete-colour'].extend([max(.01,c+concrete_delta) for c in (.29,.34,.41)]+[1]);buffers['pale-alloy-colour'].extend([max(.01,c+concrete_delta) for c in (.46,.51,.57)]+[1])
            scratch=.17 if ((x*7+y*31)%991<2 and rng.random()<.7) else 0
            buffers['used-brass-colour'].extend([max(.01,c+cloud*.7+grain*.5-stain*.9+scratch-pore*.3) for c in (.55,.36,.10)]+[1])
            buffers['recess-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in (.36,.045,.035)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Worn matte pale coated service inserts','pale-alloy-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);red=material('Dark red nonemissive recessed fittings','recess-red-colour');dark=material('Dark nonemissive service recesses')
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
    body=box('The Cube concrete core',(0,0,.98),(1.56,1.56,1.80),concrete,bevel=.010)
    roof=box('The Cube shallow overhanging roof lip',(0,0,1.89),(1.64,1.64,.12),concrete,bevel=.006)
    def surface(face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inverse=body.matrix_world.inverted();hit,q,normal,_=body.ray_cast(inverse@(tangent*u+n*3+Vector((0,0,z))),inverse.to_3x3()@(-n));assert hit;return body.matrix_world@q,(body.matrix_world.to_3x3()@normal).normalized()
    fields=[]
    def recess(name,face,u,z,width,height,mat,depth=.028):
        q,n=surface(face,u,z);cut(body,box('Temporary actual field cutter',q+n*.015,(width,height,2*(depth+.015)),concrete,n,0),'Actual blind field '+name);back=box('The Cube '+name,q-n*(depth+.003),(width-.006,height-.006,.014),mat,n,.001);fields.append(dict(object=back.name,point=list(q),normal=list(n),depth=depth));return q,n,back
    def join_parts(objects,name):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
    q,n,frontband=recess('upper front red band','front',0,1.62,1.48,.24,red);slits=[];slit_contacts=[]
    for i,u in enumerate([-.58,-.29,0,.29,.58]):
        centre=Vector((u,q.y,1.62));slits.append(box('Pale front slit '+str(i),centre-n*.015,(.055,.18,.032),edge,n,.001));slit_contacts.append(list(centre-n*.027))
    join_parts(slits,'The Cube five pale front slits')
    recess('upper corner red return','right',-.57,1.62,.34,.24,red)
    for i,z in enumerate([.30,.60]):
        recess('lower right red band '+str(i),'right',-.45,z,.64,.14,red)
        recess('lower front red return '+str(i),'front',.60,z,.28,.14,red)
    rightslits=[]
    for i,u in enumerate([0,.28,.49]):
        _,_,part=recess('pale side slit '+str(i),'right',u,1.43,.075,.32,edge,depth=.012);rightslits.append(part);fields[-1]['object']='The Cube three pale side slits'
    join_parts(rightslits,'The Cube three pale side slits')
    posts=[];caps=[];post_contacts=[]
    for i,u in enumerate([-.58,-.02,.54]):
        posts.append(box('Short front brass post '+str(i),(u,-.81,.335),(.18,.12,.63),gold,bevel=.003));caps.append(box('Pale post cap '+str(i),(u,-.81,.68),(.19,.13,.08),edge,bevel=.003));post_contacts.append(dict(index=i,body_contact=[u,-.765,.43],cap_contact=[u,-.81,.645]))
    join_parts(posts,'The Cube three short front brass posts');join_parts(caps,'The Cube three pale post caps')
    staves=[];stave_meta=[]
    for i,(u,bottom,top) in enumerate([(-.66,.02,1.65),(-.49,.04,1.70),(-.18,.02,.78),(.18,.04,1.32),(.64,.06,1.88)]):
        staves.append(box('Unequal right brass stave '+str(i),(.81,u,(bottom+top)/2),(.12,.10,top-bottom),gold,bevel=.003));stave_meta.append(dict(index=i,u=u,bottom=bottom,top=top,body_contact=[.765,u,.43]))
    join_parts(staves,'The Cube five unequal right brass staves')
    pins=[];pin_meta=[]
    for i,(x,y,height) in enumerate([(-.14,.56,.17),(.25,.06,.12),(.42,.06,.15)]):
        pins.append(box('Small angular roof pin '+str(i),(x,y,1.935+height/2),(.045,.045,height),gold,bevel=.001));pin_meta.append(dict(index=i,contact=[x,y,1.943],top=1.935+height))
    join_parts(pins,'The Cube three small brass roof pins')
    vent=box('The Cube low slotted roof block',(-.24,-.18,1.99),(.50,.32,.14),concrete,bevel=.004);cells=[];vent_cells=[]
    for i,x in enumerate([-.32,-.16]):
        cut(vent,box('Temporary blind roof cell',(x,-.18,2.06),(.12,.11,.12),concrete,bevel=0),'Two-cell reading of actual low roof slot');cells.append(box('Dark roof cell '+str(i),(x,-.18,1.997),(.112,.102,.014),dark,bevel=.001));vent_cells.append(dict(index=i,centre=[x,-.18],floor=2.0,contact=[x,-.18,1.995]))
    join_parts(cells,'The Cube two dark roof cells')
    chips=[]
    for obj,point,normal in [(body,Vector((-.38,-.78,.97)),Vector((0,-1,0))),(roof,Vector((.50,.40,1.95)),Vector((0,0,1)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.030,location=point+normal*.023);cut(obj,bpy.context.object,'Actual shallow cast service chip');chips.append(dict(body=obj.name,point=list(point),normal=list(normal)))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/135';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
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
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/135',key='MN06',name='The Cube',culture='mauna',footprint=[3,3],definition_class=255,construction_updates=30,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_the_cube.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,front_slit_contacts=slit_contacts,front_post_contacts=post_contacts,right_staves=stave_meta,roof_pins=pin_meta,roof_cells=vent_cells,physical_chips=chips,interpretation=['Own greybluecube/rooflip,redbands,5front/3rightpaleslits,3cappedfrontbrassposts/5unequalrightstaves,lowroofvent/3pins govern geometry.','Nearcornerbandextent,angularpins,two-cellroofventreading,hiddenrearwalls/attachmentdepths/cellrelative dimensions authored. Uniqueclass255hasno genericPB/STbinding;no operatinganimation/emission/symbols inferred.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn06-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_THE_CUBE_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
