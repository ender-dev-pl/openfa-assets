"""Author AR17 Auto-deterrent from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/auto-deterrent';maps=root/'sources/materials/artemian/auto-deterrent';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2601701);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2601705);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.29,.43,.36)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.42,.49,.55)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.55+.05*math.cos(11*u+3*v),.24,.10,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal)]:
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
    body=lathe('Auto-deterrent fixed two-hoop base and pale shoulder',smooth_profile([(.025,.60),(.06,.72),(.12,.79),(.22,.80),(.235,.82),(.26,.82),(.275,.80),(.40,.79),(.425,.81),(.45,.81),(.465,.78),(.58,.75),(.62,.70),(.69,.57),(.78,.35),(.84,.24)]),alloy,128);body.data.materials.append(exposed)
    for face in body.data.polygons:
        z=sum(body.data.vertices[i].co.z for i in face.vertices)/len(face.vertices)
        if z>.685 or z<.075:face.material_index=1
    head=lathe('Auto-deterrent small rounded rotating head',[(1.04+.27*math.sin(math.radians(-78+166*i/32)),.33*math.cos(math.radians(-78+166*i/32))) for i in range(33)],alloy,96);moving.append(head)
    direction=Vector((.72,.48,.72)).normalized();emitter_origin=Vector((.18,.12,1.20))
    original=[(0,.14),(.10,.14),(.115,.151),(.145,.146),(.16,.130),(.29,.113),(.30,.124),(.33,.120),(.345,.106),(.49,.086),(.50,.096),(.53,.091),(.545,.079),(.68,.059),(.69,.069),(.72,.065),(.735,.053),(.86,.043),(.90,.040),(.90,.027),(.82,.027)]
    profile=[(t*.95/.90,r*.85) for t,r in original];tube=lathe('Auto-deterrent single tapered emitter with blind bore',smooth_profile(profile,2),alloy,64,emitter_origin,direction);tube.data.materials.append(exposed);moving.append(tube)
    for face in tube.data.polygons:
        t=sum((tube.data.vertices[i].co-emitter_origin).dot(direction) for i in face.vertices)/len(face.vertices)*.90/.95
        if any(a<t<b for a,b in [(.115,.120),(.30,.305),(.50,.505),(.69,.695),(.89,.90)]):face.material_index=1
    ports=[]
    for i,angle in enumerate([-45,-15]):
        radial=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0));bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((0,0,.53))+radial*3,-radial);assert hit
        cut=lathe('Temporary actual fixed-point recess',[(-.030,.045),(.020,.045)],alloy,64,point,normal)
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Stable point cut faces','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('True front-side point recess '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
        lathe('Auto-deterrent fixed dark point '+str(i),[(-.033,.044),(-.025,.044)],dark,64,point,normal)
        lathe('Auto-deterrent fixed point rim '+str(i),[(-.010,.065),(.010,.065),(.010,.046),(-.010,.046)],exposed,64,point,normal,closed_profile=True)
        ports.append(dict(angle_deg=angle,point=list(point),normal=list(normal)))
    for i,(x,y) in enumerate([(-.18,.10),(.10,.20)]):
        bpy.context.view_layer.update();hit,point,normal,_=head.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        bpy.context.view_layer.objects.active=head;mod=head.modifiers.new('Stable chip faces','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=head.modifiers.new('Real small head chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    radial=Vector((-.8,-.6,0));bpy.context.view_layer.update();hit,dent_point,dent_normal,_=body.ray_cast(Vector((0,0,.33))+radial*3,-radial);assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.035,location=dent_point+dent_normal*.029);cut=bpy.context.object
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Real shallow base dent','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/123';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    yaw=bpy.data.objects.new('AutoDeterrentYaw',None);bpy.context.collection.objects.link(yaw);yaw.parent=root_object;yaw['purpose']='Continuous azimuth preview of the 16 own sprite headings;duration authored,not gameplay aiming logic'
    for o in meshes:
        o.parent=yaw if o in moving else root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o in [body,head]:
            uv=o.data.uv_layers.active
            for face in o.data.polygons:
                values=[]
                for index in face.loop_indices:
                    p=o.data.vertices[o.data.loops[index].vertex_index].co;values.append((math.atan2(p.y,p.x)/math.tau+.5,((p.z-.77)/.55 if o==head else (p.z-.025)/.84)))
                seam=max(u for u,v in values)-min(u for u,v in values)>.5
                for index,(u,v) in zip(face.loop_indices,values):uv.data[index].uv=(u+1 if seam and u<.5 else u,v)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=True if o==head else e.calc_face_angle(0)<.60
        bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.use_smooth=True
        o.data.normals_split_custom_set([tuple(n.vector) for n in o.data.corner_normals])
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=97;yaw.rotation_mode='XYZ'
    for frame,angle in [(1,0),(25,math.pi/2),(49,math.pi),(73,3*math.pi/2),(97,math.tau)]:yaw.rotation_euler.z=angle;yaw.keyframe_insert(data_path='rotation_euler',frame=frame)
    action=yaw.animation_data.action;action.name='AutoDeterrentAzimuth';track=yaw.animation_data.nla_tracks.new();track.name='AutoDeterrentAzimuth';track.strips.new('AutoDeterrentAzimuth',1,action);yaw.animation_data.action=None
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/123',key='AR17',name='Auto-deterrent',culture='artemian',footprint=[2,2],definition_class=17,construction_updates=28,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=3,author='sources/tools/blender/remaster_artemian_auto_deterrent.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},physical_dent=dict(point=list(dent_point),normal=list(dent_normal)),fixed_ports=ports,emitter=dict(origin=list(emitter_origin),direction=list(direction),length=.95,bore_floor=.82*.95/.90),interpretation=['Own16sprite headings establish a small rotating bulb head/single emitter above fixed green two-hoop base/pale shoulder/two dark points. GenericPB17/ST19Terran counterpart does not override Artemian geometry.','Blind emitter bore,sections,bearing and metric dimensions are authored. Four-second azimuth preview is not recovered game timing or client aiming logic.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar17-concept-review.json',animation_clips=['AutoDeterrentAzimuth'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_AUTO_DETERRENT_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
