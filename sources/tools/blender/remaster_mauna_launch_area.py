"""Author MN09 Launch Area from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/launch-area';maps=root/'sources/materials/mauna/launch-area';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610909);buffers={name:[] for name in ['cast-concrete-colour','used-brass-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','guide-pale-colour','window-orm','pale-alloy-colour']}
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
            buffers['guide-pale-colour'].extend([max(.01,c+cloud*.35+grain*.3-stain*.5) for c in (.48,.62,.80)]+[1])
            buffers['window-orm'].extend([1,.30,0,1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Matte pale coated sensor masts','pale-alloy-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);blue=material('Deep cobalt nonemissive colour fields','marking-red-colour');dark=material('Dark nonemissive service recesses')
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
    glass=material('Pale blue-white shaft guides','guide-pale-colour');node=glass.node_tree.nodes.get('Principled BSDF')
    for tex in glass.node_tree.nodes:
        if tex.type=='TEX_IMAGE' and tex.image==images['concrete-orm']:tex.image=images['window-orm']
    node.inputs['Emission Color'].default_value=(.12,.20,.35,1);node.inputs['Emission Strength'].default_value=.25
    red=material('Worn source red roof bands and zigzags','marking-red-colour')
    lining=material('Dark maroon nonemissive shaft lining');lining.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.065,.008,.010,1)
    black=material('Black nonemissive deep shaft floor');black.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.001,.001,.001,1)
    verts=[(x*r,y*r,z) for r,z in [(.90,.07),(.83,.55)] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    body=solid('Launch Area sloping concrete shell',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],concrete)
    cut(body,box('Temporary genuine square flight opening',(0,0,0),(1.61,1.61,4),concrete,bevel=0),'Actual square open shaft')
    plinth=box('Launch Area cast foot plinth',(0,0,.05),(1.84,1.84,.10),concrete,bevel=.005)
    cut(plinth,box('Temporary underground opening',(0,0,0),(1.70,1.70,4),concrete,bevel=0),'No concrete plug under opening')
    shaft=box('Launch Area maroon underground shaft',(0,0,-.735),(1.79,1.79,1.63),lining,bevel=0)
    cut(shaft,box('Temporary shaft bore',(0,0,-.735),(1.70,1.70,1.9),lining,bevel=0),'Actual open shaft lining')
    floor=box('Launch Area black deep shaft floor',(0,0,-1.57),(1.79,1.79,.04),black,bevel=0)
    attachments=[];fields=[];moving={};pivots={}
    def anchored(name,centre,size,mat,support,point):
        o=box(name,centre,size,mat,bevel=.002);attachments.append(dict(object=o.name,support=support.name,point=point));return o
    posts=[]
    for i,(x,y) in enumerate([(-.825,-.825),(.825,-.825),(.825,.828),(-.825,.828)]):posts.append(anchored('Launch Area brass corner post '+str(i),(x,y,.635),(.045,.045,.19),gold,body,[x,y,.545]))
    mast=anchored('Launch Area slender pale mast',(-.79,.828,1.12),(.045,.045,1.17),edge,body,[-.79,.828,.545])
    leg=anchored('Launch Area shorter mast brace leg',(-.50,.828,.815),(.035,.04,.56),edge,body,[-.50,.828,.545])
    # Diagonal bridge contacts both uprights rather than floating above them.
    a=Vector((-.79,.828,1.27));b=Vector((-.50,.828,1.08));delta=b-a
    bridge=box('Launch Area diagonal mast bridge',(a+b)/2,(.035,.04,delta.length+.035),edge,bevel=.001);bridge.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
    attachments += [dict(object=bridge.name,support=mast.name,point=list(a)),dict(object=bridge.name,support=leg.name,point=list(b))]
    front_rail=anchored('Launch Area mast forward thin rail',(-.823,.828,1.05),(.017,.025,1.03),edge,body,[-.823,.828,.545])
    for i,z in enumerate([.71,.90,1.09]):
        o=box('Launch Area mast small bridge '+str(i),(-.8065,.828,z),(.049,.024,.018),edge,bevel=.001)
        attachments += [dict(object=o.name,support=mast.name,point=[-.793,.828,z]),dict(object=o.name,support=front_rail.name,point=[-.820,.828,z])]
    def surface(obj,face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));t=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inv=obj.matrix_world.inverted();hit,q,norm,_=obj.ray_cast(inv@(t*u+n*3+Vector((0,0,z))),inv.to_3x3()@(-n));assert hit;return obj.matrix_world@q,(obj.matrix_world.to_3x3()@norm).normalized()
    def field(name,obj,face,u,z,w,h,mat,depth=.018):
        q,n=surface(obj,face,u,z);cut(obj,box('Temporary blind field cutter',q+n*.01,(w,h,2*(depth+.01)),concrete,n,0),'Actual blind '+name)
        o=box('Launch Area '+name,q-n*(depth+.003),(w-.006,h-.006,.014),mat,n,.001);fields.append(dict(object=o.name,body=obj.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.007));return q,n,o
    q,n,back=field('front dark vent',body,'front',0,.315,1.10,.19,dark,.025)
    v=(Vector((0,0,1))-n*n.z).normalized()
    for i,offset in enumerate([-.060,-.020,.020,.060]):
        o=box('Launch Area front vent rib '+str(i),q+v*offset-n*.020,(1.04,.012,.018),edge,n,.001);attachments.append(dict(object=o.name,support=back.name,point=list(q+v*offset-n*.028)))
    field('right lower dark vertical slot',body,'right',-.43,.19,.038,.19,dark,.012)
    # Three single-piece source zigzags avoid overlapping paint rectangles.
    outline=[(-.04,.14),(.06,.14),(.01,.03),(.075,.03),(-.03,-.14),(-.005,-.025),(-.07,-.025)]
    for i,u in enumerate([-.46,0,.46]):
        q,n=surface(body,'right',u,.345);t=Vector((0,1,0));v=(Vector((0,0,1))-n*n.z).normalized();vertices=[tuple(q+t*x+v*(z*1.30)+n*d) for d in [-.003,.003] for x,z in outline];count=len(outline);faces=[tuple(reversed(range(count))),tuple(range(count,count*2))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)];o=solid('Launch Area red wall zigzag '+str(i),vertices,faces,red);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();attachments.append(dict(object=o.name,support=body.name,point=list(q+t*.03+v*.117-n*.001)))
    # Small source green fields on the tall pale mast.
    for i,z in enumerate([1.23,1.34,1.45]):field('mast small dark field '+str(i),mast,'front',-.79,z,.025,.045,dark,.006)
    # Discrete pale guide points sit on shaft walls, never across the flight path.
    for side in [-1,1]:
        for i,z in enumerate([-.08,-.28,-.48]):
            o=box('Launch Area shaft guide '+str(side)+' '+str(i),(side*.849,0,z),(.012,.035,.035),glass,bevel=.001);attachments.append(dict(object=o.name,support=shaft.name,point=[side*.853,0,z]))
    for side in [-1,1]:
        pivot=bpy.data.objects.new('LaunchDoorNorth' if side>0 else 'LaunchDoorSouth',None);bpy.context.collection.objects.link(pivot);pivot.location=(0,side*.805,.55);pivots[side]=pivot
        leaf=box('Launch Area downward door '+str(side),(0,side*.4025,.565),(1.60,.803,.028),edge,bevel=.002);moving[leaf]=side
        # One worn source band per half, physically seated in the leaf top.
        paint=box('Launch Area red moving roof band '+str(side),(0,side*.405,.579),(1.53,.11,.004),red,bevel=.001);moving[paint]=side
        for i,x in enumerate([-.53,.53]):
            # Captive axle through a fixed rim bearing with an attached moving lug.
            bearing=box('Launch Area fixed hinge bearing '+str(side)+' '+str(i),(x,side*.843,.535),(.075,.086,.055),gold,bevel=.002)
            attachments.append(dict(object=bearing.name,support=body.name,point=[x,side*.818,.518]))
            bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.013,depth=.10,location=(x,side*.805,.55),rotation=(0,math.pi/2,0));axle=bpy.context.object;axle.name='Launch Area hinge axle '+str(side)+' '+str(i);axle.data.materials.append(gold)
            lug=box('Launch Area moving hinge lug '+str(side)+' '+str(i),(x,side*.796,.570),(.044,.020,.035),edge,bevel=.001);moving[lug]=side
    chips=[]
    for obj,p,n in [(body,Vector((-.815,-.10,.55)),Vector((0,0,1))),(plinth,Vector((.65,-.92,.055)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.020,location=p+n*.014);cut(obj,bpy.context.object,'Actual shallow cast service chip');chips.append(dict(body=obj.name,point=list(p),normal=list(n)))
    # Batch fixed accessory pieces while retaining editable named part groups.
    part_batches={};keep={body.name,plinth.name,shaft.name,floor.name}
    for mat,label in [(edge,'fixed pale assemblies'),(gold,'fixed brass assemblies'),(dark,'dark blind backings'),(glass,'pale shaft guides'),(red,'three source wall zigzags')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and o not in moving and list(o.data.materials)==[mat]]
        if not objects:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Launch Area '+label;g=o.vertex_groups.new(name=o.name);g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Launch Area '+label

    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/138';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    placement['preserve_ground_origin']=True;placement['ground_level']=0
    for pivot in pivots.values():pivot.parent=placement
    bpy.context.view_layer.update()
    for o in meshes:
        if o in moving:
            o.parent=pivots[moving[o]];o.matrix_parent_inverse=o.parent.matrix_world.inverted()
        else:o.parent=placement
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
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=97
    for side,pivot in pivots.items():
        pivot.rotation_mode='XYZ'
        for frame,weight in [(1,0),(25,1),(73,1),(97,0)]:
            pivot.rotation_euler.x=side*math.pi/2*weight;pivot.keyframe_insert(data_path='rotation_euler',frame=frame)
        action=pivot.animation_data.action;action.name='LaunchFacilityCycle';track=pivot.animation_data.nla_tracks.new();track.name='LaunchFacilityCycle';track.strips.new('LaunchFacilityCycle',1,action);pivot.animation_data.action=None
        for fc in action.fcurves:
            for key in fc.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(1)
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/138',key='MN09',name='Launch Area',culture='mauna',footprint=[2,2],definition_class=26,construction_updates=18,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=8,author='sources/tools/blender/remaster_mauna_launch_area.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=attachments,part_batches=part_batches,physical_chips=chips,interpretation=['Own square sloping pad,braced slender mast,four brass posts,front vent,three red wall zigzags,two red roof bands and downward-folding paired cover govern geometry.','Shaft depth,hinge engineering,point placement,recess depths and cell-relative dimensions authored. Own source mechanism retained;generic PB26 geometry is context only.'],scale_contract='2x2 placement footprint,+Zup/-Yfront;preserve ground origin0 and closed bind horizontal bounds. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn09-concept-review.json',animation_clips=['LaunchFacilityCycle'],launch_animation=dict(kind='deck',clip='LaunchFacilityCycle',closed_frame=1,open_first_frame=25,open_last_frame=73,end_frame=97,fps=24,source='Own descriptors2..5 moving cover,6..16 empty overlay open,17 foreground mask. Continuous timing authored;game maps attached ship altitude.'),hangar=dict(aperture_half_extent=.805,hinge_y=.805,hinge_z=.55,open_angle_degrees=90,shaft_floor=-1.55,transit_min_z=-1.25,terrain_cutout_required=True,ground_level=0,preserve_ground_origin=True),game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_LAUNCH_AREA_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
