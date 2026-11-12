"""Author MN21 Laser Boost from own legacy evidence and reviewed real ImageGen concept."""
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
    out=root/'sources/objects/mauna/laser-boost';maps=root/'sources/materials/mauna/laser-boost';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(root/'sources/docs/assets/bootstrap-3d/full-catalogue/mauna/mn21/model.blend'),load_ui=False,use_scripts=False)
    head=bpy.data.objects['DirectionalHead'];base=bpy.data.objects['StaticBase'];bpy.context.scene.frame_set(1);original=signature(head)
    for obj in list(bpy.context.scene.objects):
        if obj not in [head,base]:bpy.data.objects.remove(obj,do_unlink=True)
    bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2612121);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-alloy-colour','brass-colour']}
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
            buffers['pale-alloy-colour'].extend([max(.01,c+cloud*.5+grain*.5-stain*.5+scratch*.3) for c in (.34,.40,.46)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Worn greyblue steel head and support','pale-alloy-colour',True);dark=material('Dark nonemissive service recesses')
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
    red=material('Worn red Laser Boost side markings','marking-red-colour');brass=material('Aged opaque brass hooked fittings','brass-colour',True)
    def recalc(o):
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
    def prism(name,outline,a,b,axis,mat):
        count=len(outline);vertices=[(x,u,v) if axis=='X' else (u,x,v) for x in [a,b] for u,v in outline];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)];o=solid(name,vertices,faces,mat);recalc(o);return o
    def cylinder(name,centre,radius,depth,mat):
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.data.materials.append(mat);return o
    foot=box('Laser Boost grounded low foot',(0,-.04,.05),(1.62,1.56,.10),concrete,bevel=.006)
    vertices=[(x,y,z) for z,xw,y0,y1 in [(.08,.78,-.78,.70),(1.08,.52,-.34,.46)] for x,y in [(-xw,y0),(xw,y0),(xw,y1),(-xw,y1)]]
    body=solid('Laser Boost flared fixed cast base',vertices,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],concrete);recalc(body);mod=body.modifiers.new('Small cast edge breaks','BEVEL');mod.width=.006;mod.segments=1;apply(body,mod)
    fixed=cylinder('Laser Boost fixed supported bearing',(0,0,1.15),.25,.18,edge)
    bearing=cylinder('Laser Boost moving bearing',(0,0,1.25),.23,.08,edge)
    support=prism('Laser Boost pierced rotating cradle',[(-.30,1.26),(.36,1.26),(.36,1.456),(-.30,1.885)],-.12,.12,'X',edge)
    cut(support,prism('Temporary triangular cradle opening',[(-.17,1.34),(.21,1.34),(-.17,1.69)],-.3,.3,'X',edge),'Actual triangular through opening')
    outline=[(-.28,.45),(.28,.45),(.28,-.22),(.12,-.44),(.10,-1.20),(-.10,-1.20),(-.12,-.44),(-.28,-.22)];count=len(outline)
    vertices=[(x,y,1.82-.65*y+d*(1 if y>=-.44 else max(.53,1-(abs(y)-.44)*.62))) for d in [-.15,.15] for x,y in outline];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    blade=solid('Laser Boost single inclined tapered blade',vertices,faces,edge);recalc(blade)
    contacts=[];fields=[];chips=[];backs=[];hooks=[];ribs=[];marks=[]
    for i,offset in enumerate([-.05,.05]):
        profile=[(y,1.82-.65*y+offset+d) for y,d in [(-.17,-.0125),(.30,-.0125),(.30,.0125),(-.17,.0125)]]
        cut(blade,prism('Temporary true inclined groove',profile,-.33,-.245,'X',edge),'Actual elongated blind groove')
        profile=[(y,1.82-.65*y+offset+d) for y,d in [(-.167,-.010),(.297,-.010),(.297,.010),(-.167,.010)]]
        back=prism('Laser Boost dark seated blade groove '+str(i),profile,-.249,-.237,'X',dark);backs.append(back)
        fields.append(dict(object=back.name,body=blade.name,point=[-.28,.04,1.82-.65*.04+offset],normal=[-1,0,0],depth=.035,contact_depth=.038,moving=True))
    mod=blade.modifiers.new('Small machined blade and groove edges','BEVEL');mod.width=.002;mod.segments=1;apply(blade,mod)
    def front_y(z):return -.78+.44*(z-.08)
    def stroke(points,width):
        points=[Vector(p) for p in points];dirs=[(b-a).normalized() for a,b in zip(points,points[1:])];norms=[Vector((-d.y,d.x)) for d in dirs];left=[];right=[]
        for i,p in enumerate(points):
            if i==0:n=norms[0]*width/2
            elif i==len(points)-1:n=norms[-1]*width/2
            else:m=(norms[i-1]+norms[i]).normalized();n=m*(width/2/m.dot(norms[i]))
            left.append(tuple(p+n));right.append(tuple(p-n))
        return left+list(reversed(right))
    for i,x in enumerate([-.28,.28]):
        profile=[(front_y(.23)-.010,.23),(front_y(.60)-.010,.60),(front_y(.65)-.060,.68),(front_y(.68)-.030,.74),(front_y(.72)+.040,.74),(front_y(.72)+.090,.68)]
        hook=prism('Laser Boost continuous hooked front brass '+str(i),stroke(profile,.08),x-.06,x+.06,'X',brass);hooks.append(hook)
        for z in [.3,.45,.60]:contacts.append(dict(object=hook.name,support=body.name,point=[x,front_y(z)+.002,z]))
    for i,x in enumerate([-.50,.50]):
        profile=[(front_y(.10)-.025,.10),(front_y(.98)-.025,.98),(front_y(.98)+.025,.98),(front_y(.10)+.025,.10)]
        rib=prism('Laser Boost sloping structural front rib '+str(i),profile,x-.03,x+.03,'X',edge);ribs.append(rib)
        for z in [.2,.5,.8]:contacts.append(dict(object=rib.name,support=body.name,point=[x,front_y(z)+.003,z]))
    def side_mark(name,profile):
        normal=Vector((1,0,.26)).normalized();n=len(profile);vertices=[tuple(Vector((.78-.26*(z-.08),y,z))+normal*d) for d in [-.003,.006] for y,z in profile]
        faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];o=solid(name,vertices,faces,red);recalc(o);return o
    mark=side_mark('Laser Boost long narrow red side stripe',[(-.08,.17),(-.15,.92),(-.06,.92),(.01,.17)]);marks.append(mark)
    contacts.append(dict(object=mark.name,support=body.name,point=[.78-.26*(.55-.08)-.001,-.07,.55]))
    flag=side_mark('Laser Boost smaller angular red side flag',[(.09,.92),(.30,.85),(.30,.72),(.20,.72),(.18,.48),(.10,.52)]);marks.append(flag)
    contacts.append(dict(object=flag.name,support=body.name,point=[.78-.26*(.75-.08)-.001,.17,.75]))
    contacts += [dict(object=body.name,support=foot.name,point=[.4,0,.09]),dict(object=fixed.name,support=body.name,point=[.10,0,1.07]),dict(object=bearing.name,support=fixed.name,point=[.1,0,1.225]),dict(object=support.name,support=bearing.name,point=[0,0,1.275])]
    for y in [-.24,.28]:contacts.append(dict(object=blade.name,support=support.name,point=[0,y,1.68-.65*y]))
    for q,n in [(Vector((.35,.10,1.08)),Vector((0,0,1))),(Vector((.63,-.82,.05)),Vector((0,-1,0)))]:
        obj=body if q.z>1 else foot;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.019,location=q+n*.013);cut(obj,bpy.context.object,'Actual shallow cast chip');chips.append(dict(body=obj.name,point=list(q),normal=list(n)))
    fixed_meshes=[foot,body,fixed]+hooks+ribs+marks;moving_meshes=[bearing,support,blade]+backs
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/150';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z';placement['ground_level']=0
    for controller in [head,base]:
        world=controller.matrix_world.copy();controller.parent=placement;controller.matrix_world=world
    bpy.context.view_layer.update();meshes=fixed_meshes+moving_meshes
    for obj in meshes:
        world=obj.matrix_world.copy();obj.parent=head if obj in moving_meshes else base;obj.matrix_world=world;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');uv=obj.data.uv_layers.active
        for face in obj.data.polygons:
            for i in face.loop_indices:
                p=obj.data.vertices[obj.data.loops[i].vertex_index].co;uv.data[i].uv=((p.y+1)/2,p.z/2.2) if abs(face.normal.x)>.5 else ((p.x+1)/2,p.z/2.2) if abs(face.normal.y)>.5 else ((p.x+1)/2,(p.y+1)/2)
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');apply(obj,mod);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.to_mesh(obj.data);bm.free()
    bpy.context.view_layer.update();assert signature(head)==original;triangles=sum(len(obj.data.polygons) for obj in meshes);assert triangles<30000
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=17;scene.render.fps=16;scene.frame_set(1)
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*a,**k):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk;keys=[key for layer in head.animation_data.action.layers for strip in layer.strips for bag in strip.channelbags for curve in bag.fcurves for key in curve.keyframe_points];saved=[(key,key.co.copy(),key.handle_left.copy(),key.handle_right.copy()) for key in keys]
    for key in keys:key.co.x*=4;key.handle_left.x*=4;key.handle_right.x*=4
    scene.render.fps=64;scene.frame_start=4;scene.frame_end=68;scene.frame_set(4)
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_extras=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_frame_range=True)
    finally:
        tempfile.mkdtemp=old
        for key,co,left,right in saved:key.co=co;key.handle_left=left;key.handle_right=right
        scene.render.fps=16;scene.frame_start=1;scene.frame_end=17;scene.frame_set(1)
    assert signature(head)==original;bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    meta=dict(schema_version=1,issue=261,id='openfa:building/legacy/150',key='MN21',name='Laser Boost',culture='mauna',footprint=[2,2],definition_class=18,construction_updates=28,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_laser_boost.py',author_sha256=sha(Path(__file__)),binaries={ext:sha(out/('model.'+ext)) for ext in ['blend','glb']},textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=contacts,physical_chips=chips,animation=dict(head=head.name,base=base.name,retained_controller_signature=original,moving_meshes=[o.name for o in moving_meshes],static_meshes=[o.name for o in fixed_meshes],fps=16,frames=[1,17],export_bake_fps=64,direction_count=16,timing_recovered=False),scale_contract='2x2 placement footprint, ground0, +Z up/-Y front. Dimensions, rail angle and socket are authored, not recovered metric calibration.',concept_review='sources/docs/reconstruction/models/mn21-concept-review.json',animation_clips=['Animation'],source_controller='sources/docs/assets/bootstrap-3d/full-catalogue/mauna/mn21/model.blend',source_controller_sha256=sha(root/'sources/docs/assets/bootstrap-3d/full-catalogue/mauna/mn21/model.blend'),interpretation=['Own sixteen direction heads establish one flattened inclined tapered blade with two elongated grooves over a narrow rotating cradle. Prior two round muzzles are superseded by own source anatomy.','Two front hooked brass fittings and long stripe/smaller red side flag govern fixed anatomy. Exact hidden structure,bearing,groove depths and sections are authored;generic PB18/ST18 and turret optimiser ST31 are context only. No firing,recoil or autonomous scan timing inferred.'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('MAUNA_LASER_BOOST_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
