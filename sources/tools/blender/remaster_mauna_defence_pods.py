"""Author MN13 Defence Pods from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def signature(head):
    a=head.animation_data.action;curves=[]
    for layer in a.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for c in bag.fcurves:curves.append(dict(path=c.data_path,index=c.array_index,keys=[dict(co=list(k.co),interpolation=k.interpolation,left=list(k.handle_left),right=list(k.handle_right)) for k in c.keyframe_points]))
    return dict(location=list(head.location),rotation_mode=head.rotation_mode,action=a.name,curves=curves)


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/defence-pods';maps=root/'sources/materials/mauna/defence-pods';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(root/'sources/docs/assets/bootstrap-3d/full-catalogue/mauna/mn13/model.blend'),load_ui=False,use_scripts=False)
    head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase'];bpy.context.scene.frame_set(1);original=signature(head)
    for obj in list(bpy.context.scene.objects):
        if obj not in [head,base]:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611313);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-alloy-colour']}
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Worn grey steel head and vent frame','pale-alloy-colour',True);dark=material('Dark nonemissive service recesses')
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
    red=material('Worn red source identification strip','marking-red-colour')
    def recalc(obj):
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
    def taper(name,levels,mat):
        vertices=[(x*r,y*r,z) for z,r in levels for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]];faces=[(3,2,1,0)]+[(i*4+j,i*4+(j+1)%4,(i+1)*4+(j+1)%4,(i+1)*4+j) for i in range(len(levels)-1) for j in range(4)]+[tuple(range((len(levels)-1)*4,len(levels)*4))]
        o=solid(name,vertices,faces,mat);recalc(o);return o
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=32):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);return o
    foot=box('Defence Pods grounded low rectangular foot',(0,0,.065),(1.88,1.88,.13),concrete,bevel=.008)
    body=taper('Defence Pods truncated square concrete base',[(.10,.90),(.95,.64)],concrete)
    fixed=cylinder('Defence Pods fixed supported bearing',(0,0,.995),.34,.13,edge)
    moving=cylinder('Defence Pods moving bearing',(0,0,1.095),.32,.13,edge)
    outline=[(-.28,1.21),(.28,1.21),(.28,1.59),(.13,1.78),(-.10,1.78),(-.28,1.60)]
    vertices=[(x,y,z-.10) for x in [-.26,.26] for y,z in outline];n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    shell=solid('Defence Pods compact directional head',vertices,faces,edge);recalc(shell)
    bevel=shell.modifiers.new('Rounded source head edges','BEVEL');bevel.width=.065;bevel.segments=3;apply(shell,bevel)
    axis=Vector((0,-math.cos(math.radians(35)),math.sin(math.radians(35))));start=Vector((0,-.13,1.58));length=1.12
    collar=cylinder('Defence Pods seated barrel collar',start+axis*.095,.105,.19,edge,axis)
    # A single closed tapered barrel has a genuinely recessed terminal bore.
    bpy.ops.mesh.primitive_cone_add(vertices=32,radius1=.071,radius2=.047,depth=length,location=start+axis*(length/2));barrel=bpy.context.object;barrel.name='Defence Pods single long barrel';barrel.rotation_euler=axis.to_track_quat('Z','Y').to_euler();barrel.data.materials.append(edge)
    muzzle=start+axis*length
    cut(barrel,cylinder('Temporary muzzle recess',muzzle+axis*.005,.027,.15,edge,axis),'Actual blind muzzle bore')
    bore=cylinder('Defence Pods seated dark bore backing',muzzle-axis*.074,.025,.018,dark,axis)
    fields=[];contacts=[];chips=[]
    def surface(face,t,z):
        normal=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inv=body.matrix_world.inverted();hit,q,n,_=body.ray_cast(inv@(normal*3+tangent*t+Vector((0,0,z))),inv.to_3x3()@(-normal));assert hit;return body.matrix_world@q,(body.matrix_world.to_3x3()@n).normalized()
    q,normal=surface('front',-.29,.525);mark=box('Defence Pods broad red strip',q, (.205,.81,.006),red,normal,.001)
    contacts.append(dict(object=mark.name,support=body.name,point=list(q-normal*.001)))
    for row in range(4):
        for column in range(2):
            q,n=surface('right',-.11+column*.22,.36+row*.115)
            cut(body,box('Temporary vent cutter',q+n*.008,(.17,.078,.068),concrete,n,0),'Actual source vent cell')
            backing=box('Defence Pods dark vent '+str(row*2+column),q-n*.030,(.164,.072,.014),dark,n,.001)
            fields.append(dict(object=backing.name,body=body.name,point=list(q),normal=list(n),depth=.026,contact_depth=.032))
    q,n=surface('right',0,.5325);vertical=(Vector((0,0,1))-n*n.z).normalized();horizontal=vertical.cross(n).normalized()
    for i,(du,dv,w,h) in enumerate([(-.235,0,.035,.52),(.235,0,.035,.52),(0,-.247,.50,.035),(0,.247,.50,.035)]):
        centre=q+horizontal*du+vertical*dv
        o=box('Defence Pods vent frame '+str(i),centre,(w,h,.024),edge,n,.001);contacts.append(dict(object=o.name,support=body.name,point=list(centre-n*.005)))
    plate=box('Defence Pods small head service plate',(-.263,.06,1.33),(.15,.15,.012),dark,(-1,0,0),.002)
    for obj,p,n in [(foot,Vector((.56,-.94,.065)),Vector((0,-1,0))),(body,Vector((-.50,.02,.95)),Vector((0,0,1)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.019,location=p+n*.013);cut(obj,bpy.context.object,'Actual shallow used cast chip');chips.append(dict(body=obj.name,point=list(p),normal=list(n)))
    fixed_meshes=[foot,body,fixed,mark]+[o for o in bpy.context.scene.objects if o.type=='MESH' and (o.name.startswith('Defence Pods dark vent ') or o.name.startswith('Defence Pods vent frame '))]
    moving_meshes=[moving,shell,collar,barrel,bore,plate]
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/142';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z';placement['ground_level']=0;placement['preserve_ground_origin']=True
    for controller in [base,head]:
        world=controller.matrix_world.copy();controller.parent=placement;controller.matrix_world=world
    bpy.context.view_layer.update()
    meshes=fixed_meshes+moving_meshes
    for obj in meshes:
        world=obj.matrix_world.copy();obj.parent=head if obj in moving_meshes else base;obj.matrix_world=world
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        # Stable local planar coordinates retain material wear at gameplay scale.
        uv=obj.data.uv_layers.active
        for f in obj.data.polygons:
            for index in f.loop_indices:
                p=obj.data.vertices[obj.data.loops[index].vertex_index].co
                uv.data[index].uv=((p.y+1)/2,p.z/2) if abs(f.normal.x)>.5 else ((p.x+1)/2,p.z/2) if abs(f.normal.y)>.5 else ((p.x+1)/2,(p.y+1)/2)
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');apply(obj,mod);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.to_mesh(obj.data);bm.free()
    bpy.context.view_layer.update();assert signature(head)==original
    triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=17;scene.render.fps=16;scene.frame_set(1)
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*a,**k):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    # Bake more quaternion samples without changing the native controller keys.
    action=head.animation_data.action;keys=[key for layer in action.layers for strip in layer.strips for bag in strip.channelbags for curve in bag.fcurves for key in curve.keyframe_points];saved=[(k,k.co.copy(),k.handle_left.copy(),k.handle_right.copy()) for k in keys]
    for key in keys:key.co.x*=4;key.handle_left.x*=4;key.handle_right.x*=4
    scene.render.fps=64;scene.frame_start=4;scene.frame_end=68;scene.frame_set(4)
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_extras=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_frame_range=True)
    finally:
        tempfile.mkdtemp=old
        for key,co,left,right in saved:key.co=co;key.handle_left=left;key.handle_right=right
        scene.render.fps=16;scene.frame_start=1;scene.frame_end=17;scene.frame_set(1)
    assert signature(head)==original
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    meta=dict(schema_version=1,issue=261,id='openfa:building/legacy/142',key='MN13',name='Defence Pods',culture='mauna',footprint=[2,2],definition_class=3,construction_updates=34,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,author='sources/tools/blender/remaster_mauna_defence_pods.py',author_sha256=sha(Path(__file__)),binaries={ext:sha(out/('model.'+ext)) for ext in ['blend','glb']},textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=contacts,physical_chips=chips,animation=dict(head=head.name,base=base.name,retained_controller_signature=original,moving_meshes=[o.name for o in moving_meshes],static_meshes=[o.name for o in fixed_meshes],fps=16,frames=[1,17],export_bake_fps=64,direction_count=16,timing_recovered=False),barrel=dict(axis=list(axis),start=list(start),length=length,muzzle=list(muzzle),bore_depth=.070),scale_contract='2x2 placement footprint, ground0, +Z up/-Y front. Native dimensions and barrel elevation are authored; no metric recovery or calibrated muzzle socket claimed.',concept_review='sources/docs/reconstruction/models/mn13-concept-review.json',animation_clips=['Animation'],source_controller='sources/docs/assets/bootstrap-3d/full-catalogue/mauna/mn13/model.blend',source_controller_sha256=sha(root/'sources/docs/assets/bootstrap-3d/full-catalogue/mauna/mn13/model.blend'),interpretation=['Own sixteen directional heads over a fixed source base establish heading movement and ONE slender barrel. Prior twin gold muzzles are superseded by actual own-source anatomy.','Head bearings, muzzle bore, hidden walls, material depth, dimensions and elevation are authored. Generic Terran PB03/ST02 is functional context only. Heading preview is not an autonomous game scan or a recovered firing/recoil cycle.'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('MAUNA_DEFENCE_PODS_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
