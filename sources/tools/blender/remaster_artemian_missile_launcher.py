"""Author AR16 Missile Launcher from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/missile-launcher';maps=root/'sources/materials/artemian/missile-launcher';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2601601);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2601605);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.29,.43,.36)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.42,.49,.55)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.82+.04*math.sin(5*u+7*v),.73+.03*math.cos(7*u-3*v),.20,1]);red.extend([.55+.05*math.cos(11*u+3*v),.24,.10,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('yellow-status-colour',amber)]:
        image=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name in ['occlusion-roughness-metallic','used-metal-normal']:image.colorspace_settings.name='Non-Color'
        image.pixels.foreach_set(pixels);path=maps/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();images[name]=image
    def material(name,colour,image=None,emission=0,metal=.84,rough=.4):
        m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if image:
            tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=images[image];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);packed=m.node_tree.nodes.new('ShaderNodeTexImage');packed.image=images['occlusion-roughness-metallic'];split=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(packed.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic'])
            n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=images['used-metal-normal'];nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;m.node_tree.links.new(n.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
            if emission:m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value=emission;return m
    alloy=material('Used Artemian muted green alloy',(.29,.43,.36),'muted-green-alloy-colour');exposed=material('Worn exposed alloy rims',(.42,.49,.55),'exposed-alloy-edge-colour');dark=material('Dark recessed ports',(.012,.018,.021),metal=.30,rough=.65)
    warm=material('Warm yellow status core',(.82,.73,.20),'yellow-status-colour',emission=1.2)
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    moving=[]
    def lathe(name,profile,mat,n=96,origin=(0,0,0),axis=(0,0,1),closed_profile=False):
        origin=Vector(origin);rotation=Vector(axis).normalized().to_track_quat('Z','Y');verts=[];faces=[]
        for z,r in profile:
            for i in range(n):
                a=i*math.tau/n;verts.append(origin+rotation@Vector((r*math.cos(a),r*math.sin(a),z)))
        for j in range(len(profile)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        if closed_profile:
            for i in range(n):faces.append(((len(profile)-1)*n+i,(len(profile)-1)*n+(i+1)%n,(i+1)%n,i))
        else:faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
        return solid(name,verts,faces,mat)
    def smooth_profile(controls,steps=3):
        result=[]
        for a,b in zip(controls,controls[1:]):
            for j in range(steps):t=j/steps;result.append(tuple(x+(y-x)*t for x,y in zip(a,b)))
        result.append(controls[-1]);return result
    profile=smooth_profile([(.025,.70),(.06,.74),(.15,.76),(.25,.75),(.40,.70),(.55,.61),(.64,.55),(.70,.53),(.80,.51),(1.00,.47),(1.20,.445),(1.37,.445),(1.42,.455),(1.42,.32),(.12,.32),(.12,.02)])
    body=lathe('Missile Launcher hollow flared body and neck',profile,alloy,128);body.data.materials.append(exposed);body.data.materials.append(dark)
    for face in body.data.polygons:
        centre=sum((body.data.vertices[i].co for i in face.vertices),Vector())/len(face.vertices)
        if centre.z<.61:face.material_index=1
        if centre.xy.length<.325 and centre.z>.115:face.material_index=2
    # Two sealed curved surfaces joined at the outer lip: genuine concave
    # underside without an axial hole or coincident overlapping cap disks.
    outer=smooth_profile([(1.425,.51),(1.45,.52),(1.48,.50),(1.54,.42),(1.58,.29),(1.60,.16),(1.605,.02)],3)
    inner=smooth_profile([(1.575,.02),(1.57,.16),(1.55,.29),(1.51,.42),(1.46,.49),(1.435,.50)],3)
    n=128;verts=[];faces=[]
    for z,r in outer+inner:
        for i in range(n):a=i*math.tau/n;verts.append((r*math.cos(a),r*math.sin(a),z))
    for start,count in [(0,len(outer)),(len(outer),len(inner))]:
        for j in range(start,start+count-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple((len(outer)-1)*n+i for i in range(n)),tuple(len(outer)*n+i for i in reversed(range(n)))])
    last=(len(outer)+len(inner)-1)*n
    for i in range(n):faces.append((i,(i+1)%n,last+(i+1)%n,last+i))
    cap=solid('Missile Launcher single shallow hinged cap',verts,faces,alloy);cap.data.materials.append(exposed);moving.append(cap)
    for face in cap.data.polygons:
        z=sum(cap.data.vertices[i].co.z for i in face.vertices)/len(face.vertices)
        if 1.43<z<1.45:face.material_index=1
    def cube(name,centre,size,mat,normal=None):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        if normal is not None:o.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
        o.data.materials.append(mat);mod=o.modifiers.new('Small worn corner radii','BEVEL');mod.width=min(size)*.10;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    hinge_origin=Vector((-.52,0,1.44))
    lug=cube('Missile Launcher moving cap hinge lug',(-.48,0,1.45),(.16,.36,.08),alloy);moving.append(lug)
    axle=lathe('Missile Launcher fixed horizontal hinge axle',[(-.30,.045),(.30,.045)],exposed,64,hinge_origin,(0,1,0))
    for i,y in enumerate([-.19,.19]):cube('Missile Launcher fixed hinge bearing '+str(i),(-.46,y,1.38),(.20,.12,.16),alloy)
    for i,(x,top) in enumerate([(-.26,.70),(-.10,.87)]):
        cube('Missile Launcher unequal pale upright '+str(i),(x,-.77,(.025+top)/2),(.035,.045,top-.025),exposed)
        cube('Missile Launcher short foot mount '+str(i),(x,-.715,.07),(.07,.17,.09),exposed)
    cube('Missile Launcher short joining rung',(-.18,-.66,.615),(.21,.28,.055),exposed)
    bpy.context.view_layer.update();direction=Vector((math.cos(math.radians(-35)),math.sin(math.radians(-35)),0));hit,light_point,light_normal,_=body.ray_cast(Vector((0,0,1.05))+direction*3,-direction);assert hit
    lathe('Missile Launcher upper status rim',[(-.009,.095),(.011,.095)],exposed,64,light_point,light_normal)
    lathe('Missile Launcher upper dark status seat',[(.008,.071),(.016,.071)],dark,64,light_point,light_normal)
    cube('Missile Launcher yellow square status core',light_point+light_normal*.020,(.095,.095,.012),warm,light_normal)
    direction=Vector((math.cos(math.radians(-25)),math.sin(math.radians(-25)),0));hit,port_point,port_normal,_=body.ray_cast(Vector((0,0,.25))+direction*3,-direction);assert hit
    cut=lathe('Temporary actual lower opening cutter',[(-.030,.055),(.020,.055)],alloy,64,port_point,port_normal)
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Stable lower opening faces','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Actual lower dark recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    lathe('Missile Launcher lower recessed dark floor',[(-.033,.054),(-.025,.054)],dark,64,port_point,port_normal)
    lathe('Missile Launcher lower opening rim',[(-.010,.075),(.010,.075),(.010,.056),(-.010,.056)],exposed,64,port_point,port_normal,closed_profile=True)
    # Small real wear cuts are independent of the launch shaft and hinge.
    for i,(x,y,z) in enumerate([(-.38,-.39,1.1),(.30,-.59,.5)]):
        radial=Vector((x,y,0)).normalized();bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((0,0,z))+radial*3,-radial);assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Real small alloy chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    radial=Vector((-.8,-.6,0));bpy.context.view_layer.update();hit,dent_point,dent_normal,_=body.ray_cast(Vector((0,0,.39))+radial*3,-radial);assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.035,location=dent_point+dent_normal*.029);cut=bpy.context.object
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Actual shallow lower body dent','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/122';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    pivot=bpy.data.objects.new('LaunchLidPivot',None);bpy.context.collection.objects.link(pivot);pivot.parent=root_object;pivot.location=hinge_origin;pivot['purpose']='Single cap hinge from own progressive overlays;hidden axis position/angle and timing authored';bpy.context.view_layer.update()
    for o in meshes:
        o.parent=pivot if o in moving else root_object
        if o in moving:o.matrix_parent_inverse=pivot.matrix_world.inverted()
        bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o in [body,cap]:
            uv=o.data.uv_layers.active
            for face in o.data.polygons:
                values=[]
                for index in face.loop_indices:
                    p=o.data.vertices[o.data.loops[index].vertex_index].co;values.append((math.atan2(p.y,p.x)/math.tau+.5,p.z/1.65))
                seam=max(u for u,v in values)-min(u for u,v in values)>.5
                for index,(u,v) in zip(face.loop_indices,values):uv.data[index].uv=(u+1 if seam and u<.5 else u,v)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=e.calc_face_angle(0)<.60
        bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.use_smooth=True
        o.data.normals_split_custom_set([tuple(n.vector) for n in o.data.corner_normals])
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=61;pivot.rotation_mode='XYZ'
    for frame,angle in [(1,0),(31,-math.radians(110)),(61,0)]:pivot.rotation_euler.y=angle;pivot.keyframe_insert(data_path='rotation_euler',frame=frame)
    action=pivot.animation_data.action;action.name='LaunchFacilityCycle';track=pivot.animation_data.nla_tracks.new();track.name='LaunchFacilityCycle';track.strips.new('LaunchFacilityCycle',1,action);pivot.animation_data.action=None
    for fc in action.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(1);bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/artemian-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/122',key='AR16',name='Missile Launcher',culture='artemian',footprint=[2,2],definition_class=14,construction_updates=30,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,author='sources/tools/blender/remaster_artemian_missile_launcher.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},physical_dent=dict(point=list(dent_point),normal=list(dent_normal)),status=dict(point=list(light_point),normal=list(light_normal)),lower_port=dict(point=list(port_point),normal=list(port_normal)),hinge=dict(origin=list(hinge_origin),axis='+Y',open_angle_degrees=-110,aperture_radius=.32,shaft_floor=.12),interpretation=['Own progressive overlays establish one mechanically attached cap above fixed green neck/slate-blue flared foot;two unequal rails,upper yellow square point and lower dark recess.','Preserves earlier single-lid mechanism;hidden hinge axis/angle,shaft sections/depth and2.5second timing authored. No generic iris or magazine loader.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Cell-relative authored proportions;no recovered metric height or calibrated client scale.',concept_review='sources/docs/reconstruction/models/ar16-concept-review.json',animation_clips=['LaunchFacilityCycle'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_MISSILE_LAUNCHER_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
