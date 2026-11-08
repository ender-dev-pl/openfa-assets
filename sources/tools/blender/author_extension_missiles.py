"""Issue240: user-artwork Interceptor and four-instance Decoy; no legacy pixels.

Native forward -Y, up Z. Geometry and material details not shown by the artwork
are authored. Menu separation timing is a presentation enhancement, not simulation.
"""
from pathlib import Path
import math
import json
import hashlib
import bpy
import bmesh
from mathutils import Vector, Quaternion

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'sources/objects/extensions/munitions'
MEDIA=ROOT/'gallery/media/objects/extensions/munitions'
GROUPS={}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def emit(name,vertices,faces,tile):
    row=GROUPS.setdefault(name,dict(v=[],f=[],t=[]));n=len(row['v'])
    row['v']+=vertices;row['f'] += [tuple(n+i for i in f) for f in faces];row['t'] += [tile]*len(faces)


def lathe(name,profile,tile=0,centre=(0,0,0),n=48,closed_ring=False):
    # profile is (axial Y, radius); repeated end stations form annular nozzle.
    c=Vector(centre);vs=[tuple(c+Vector((r*math.cos(math.tau*i/n),y,r*math.sin(math.tau*i/n)))) for y,r in profile for i in range(n)]
    fs=[] if closed_ring else [tuple(range(n-1,-1,-1)),tuple((len(profile)-1)*n+i for i in range(n))]
    fs += [(j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,((j+1)%len(profile))*n+i)
           for j in range(len(profile) if closed_ring else len(profile)-1) for i in range(n)]
    emit(name,vs,fs,tile)


def box(name,c,size,tile=2,angle=0):
    bpy.ops.mesh.primitive_cube_add(size=1);o=bpy.context.object;o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    mod=o.modifiers.new('Manufactured rounded edges','BEVEL');mod.width=min(size)*.18;mod.segments=2
    bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    rot=Quaternion((0,1,0),angle);vertices=[tuple(Vector(c)+rot@v.co) for v in o.data.vertices]
    emit(name,vertices,[tuple(f.vertices) for f in o.data.polygons],tile);bpy.data.objects.remove(o,do_unlink=True)


def radial_box(name,r,y,width,length,depth,tile,a):
    box(name,(r*math.sin(a),y,r*math.cos(a)),(width,length,depth),tile,a)


def detail_latch(y,r,scale=1):
    box('Mechanical recess',(0,y,r),(.36*scale,1.5*scale,.045),3)
    box('Machined latch',(0,y+.06*scale,r+.034),(.25*scale,1.2*scale,.045),2)
    for x in [-.052,.052]:box('Latch slots',(x*scale,y+.19*scale,r+.062),(.025*scale,.57*scale,.012),3)
    for yy in [-.48,-.31]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=.047*scale,depth=.014,location=(0,y+yy*scale,r+.065))
        o=bpy.context.object;emit('Latch holes',[tuple(o.matrix_world@v.co) for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons],3);bpy.data.objects.remove(o,do_unlink=True)


def interceptor():
    for lo,hi,r in [(-3.0,-1.1,.58),(-1.08,.15,.50),(.17,1.0,.49),(1.02,2.0,.47),(2.02,2.9,.46),(2.92,3.9,.45),(3.92,4.35,.43)]:
        lathe('Blue body',[(lo,r*.97),(lo+.035,r),(hi-.035,r),(hi,r*.97)],0)
    lathe('Blue pointed forebody',[(-5.03,.08),(-4.6,.20),(-4,.34),(-3.4,.49),(-3.0,.58)],0)
    lathe('Golden nose',[(-5.3,.015),(-5.22,.07),(-4.83,.15),(-4.78,.14)],1)
    for a in [0,math.pi/2,math.pi,math.pi*1.5]:
        radial_box('Gold shoulder armour',.53,-2.1,.31,1.65,.12,1,a)
        radial_box('Gold midbody markers',.50,-.35,.07,.68,.035,1,a)
        # Closed swept fins with a visible gold inset; no paper-thin planes.
        profile=[(.43,1.32),(.68,1.7),(1.01,2.85),(1.01,3.95),(.60,4.50),(.43,4.32)]
        q=Quaternion((0,1,0),a);vs=[tuple(q@Vector((x,y,z))) for z in [-.085,.085] for x,y in profile]
        n=len(profile);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        emit('Four swept blue fins',vs,fs,0)
        for sign in [-1,1]:
            inset=[(.61,2.03),(.91,2.94),(.91,3.86),(.62,4.22)]
            gold=[tuple(q@Vector((x,y,sign*.097+z))) for z in [-.009,.009] for x,y in inset]
            emit('Gold fin plates',gold,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],1)
        radial_box('Fin vent slots',.83,3.60,.05,.29,.025,3,a+math.pi/2)
    detail_latch(-2.18,.59)
    lathe('Hollow dark nozzle',[(4.25,.39),(4.5,.43),(4.90,.36),(5.08,.32),(5.08,.25),(4.64,.22),(4.25,.27)],3,closed_ring=True)
    lathe('Gold nozzle lip',[(4.98,.33),(5.10,.33),(5.10,.28),(4.98,.28)],1,closed_ring=True)


def decoy():
    for lo,hi in [(-3.18,-2.35),(-2.33,-.60),(-.58,.35),(.37,1.72),(1.74,2.90),(2.92,4.00)]:
        lathe('Silver segment shell',[(lo,.405),(lo+.025,.42),(hi-.025,.42),(hi,.405)],2)
    lathe('Blue rounded forebody',[(-5.25,.012),(-5.16,.12),(-4.99,.24),(-4.76,.34),(-4.35,.425),(-3.75,.45),(-3.18,.44)],4)
    for y,r in [(-4.91,.28),(-4.47,.405),(-3.78,.452)]:
        lathe('Nose alloy joints',[(y-.018,r),(y+.018,r),(y+.018,r-.025),(y-.018,r-.025)],2,closed_ring=True)
    detail_latch(-3.1,.45,.75)
    for a in [0,math.pi/2,math.pi,math.pi*1.5]:
        radial_box('Blue status insets',.422,-1.7,.07,.64,.018,4,a)
        for y in [.3,2.4]:
            radial_box('Blue coupling locks',.43,y,.17,.25,.10,4,a)
            radial_box('Coupling contact pads',.52,y,.12,.17,.10,3,a)
        lathe('Blue aft pods',[(2.7,.015),(2.85,.09),(3.05,.12),(4.15,.12),(4.35,.085),(4.44,.015)],4,
              centre=(.43*math.cos(a),0,.43*math.sin(a)),n=24)
    for y in [.30,2.4]:
        lathe('Coupling collars',[(y-.23,.42),(y-.20,.46),(y+.20,.46),(y+.23,.42)],3)
        lathe('Collar alloy rims',[(y-.22,.465),(y-.17,.465),(y-.17,.435),(y-.22,.435)],2,closed_ring=True)
    lathe('Aft mount',[(4.0,.40),(4.25,.40),(4.48,.31),(4.62,.21)],3)
    lathe('Hollow nozzle',[(4.59,.21),(4.85,.23),(5.2,.34),(5.22,.34),(5.22,.27),(4.86,.17),(4.59,.16)],3,closed_ring=True)
    lathe('Blue nozzle lip',[(5.12,.337),(5.24,.35),(5.24,.30),(5.12,.29)],4,closed_ring=True)


def material():
    mat=bpy.data.materials.new('OpenFA extension worn blue gold alloy');mat.use_nodes=True;t=mat.node_tree;b=t.nodes.get('Principled BSDF');nodes=[]
    for name in ['base-colour','orm']:
        im=bpy.data.images.load(str(ROOT/'sources/materials/extensions/munitions'/f'{name}.png'));im.pack()
        if name=='orm':im.colorspace_settings.name='Non-Color'
        node=t.nodes.new('ShaderNodeTexImage');node.image=im;nodes.append(node)
    t.links.new(nodes[0].outputs['Color'],b.inputs['Base Color']);sep=t.nodes.new('ShaderNodeSeparateColor');t.links.new(nodes[1].outputs['Color'],sep.inputs['Color'])
    t.links.new(sep.outputs['Green'],b.inputs['Roughness']);t.links.new(sep.outputs['Blue'],b.inputs['Metallic']);return mat


def finish(parent,mat):
    objects=[]
    for name,row in GROUPS.items():
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(row['v'],[],row['f']);mesh.update();uv=mesh.uv_layers.new(name='Authored atlas')
        low=Vector(tuple(min(v.co[a] for v in mesh.vertices) for a in range(3)));high=Vector(tuple(max(v.co[a] for v in mesh.vertices) for a in range(3)))
        for f,tile in zip(mesh.polygons,row['t']):
            axis=max(range(3),key=lambda a:abs(f.normal[a]));axes=[a for a in range(3) if a!=axis]
            for i in f.loop_indices:
                p=mesh.vertices[mesh.loops[i].vertex_index].co;u,v=[(p[a]-low[a])/max(.00001,high[a]-low[a]) for a in axes]
                uv.data[i].uv=((tile%4+.02+.96*u)/4,1-(tile//4+.02+.96*v)/4)
            f.use_smooth=not any(s in name.lower() for s in ['plate','slot','latch','recess','fins','locks','pads','marker'])
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();mesh.update();mesh.set_sharp_from_angle(angle=.7);mesh.materials.append(mat)
        o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.parent=parent;objects.append(o)
    return objects


def empty(name,parent=None):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.parent=parent;return o


def studio():
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=700;scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
    scene.world=bpy.data.worlds.new('Neutral studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.16,.18,.22,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    for p,power,size in [((-5,-3,10),1800,6),((6,1,6),1100,5),((0,7,-5),1800,5)]:
        bpy.ops.object.light_add(type='AREA',location=p);o=bpy.context.object;o.data.energy=power;o.data.size=size;o.rotation_euler=(-o.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.object.camera_add(location=(5,0,14));scene.camera=bpy.context.object;aim(scene);return scene


def aim(scene,front=False,wide=False):
    cam=scene.camera;cam.location=(0,0,20) if front else (5,0,14)
    cam.rotation_mode='QUATERNION';cam.rotation_quaternion=Quaternion((0,1,0),0 if front else math.atan2(5,14))@Quaternion((0,0,1),math.pi)
    cam.data.type='ORTHO';cam.data.ortho_scale=14 if wide else 12.6


def export(path,objects,animated=False):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_extras=True,
        export_animations=animated,export_animation_mode='NLA_TRACKS',export_frame_range=True)


def main():
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    reports=[]
    for name,build in [('interceptor',interceptor),('decoy',decoy)]:
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0;GROUPS.clear()
        root=empty('PlacementRoot');root['catalogue_id']='openfa:missile/'+name;root['forward_axis']='-Y';root['up_axis']='+Z';root['proposed_world_size']=48
        mat=material();build();first=empty('DecoySegment0',root) if name=='decoy' else root;meshes=finish(first,mat)
        bpy.ops.object.select_all(action='DESELECT')
        for o in meshes:
            group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();meshes=[bpy.context.object]
        meshes[0].name='InterceptorBody' if name=='interceptor' else 'DecoySegmentMesh'
        if name=='interceptor':
            # Source artwork's fin span/length is about0.29; the first loft was
            # too slender. Widen the full radial section without changing length.
            for v in meshes[0].data.vertices:v.co.x*=1.45;v.co.z*=1.45
            meshes[0].data.update()
        for mesh in list(bpy.data.meshes):
            if mesh.users==0:bpy.data.meshes.remove(mesh)
        objects=[root]+meshes
        scene=studio();scene.render.fps=30;scene.frame_start=0;scene.frame_end=180
        folder=OUT/name;folder.mkdir(exist_ok=True);media=MEDIA/name;media.mkdir(exist_ok=True)
        if name=='decoy':
            # Export individual segment from precisely the same meshes, not a second authored copy.
            first['segment_model_id']='openfa:missile/decoy-segment';export(folder/'segment.glb',[first]+meshes)
            objects += [first];roots=[first]
            for i in range(1,4):
                child=empty('DecoySegment'+str(i),root);child['segment_model_id']='openfa:missile/decoy-segment';roots.append(child);objects.append(child)
                for source in meshes:
                    clone=bpy.data.objects.new(source.name+'.'+str(i),source.data);bpy.context.collection.objects.link(clone);clone.parent=child;objects.append(clone)
            for i,child in enumerate(roots):
                sx,sz=[(-1,-1),(-1,1),(1,-1),(1,1)][i]
                for frame,spread in [(0,.57),(15,.57),(90,1.85),(120,1.85),(180,.57)]:
                    child.location=(sx*spread,0,sz*spread);child.keyframe_insert('location',frame=frame)
                action=child.animation_data.action;action.name='Decoy separation segment '+str(i)
                track=child.animation_data.nla_tracks.new();track.name='DecoyMenuSeparation';track.strips.new('DecoyMenuSeparation',0,action);child.animation_data.action=None
            scene.frame_set(0)
        exhaust=empty('ExhaustOrigin',root);exhaust.location=(0,5.24 if name=='decoy' else 5.1,0);exhaust['status']='authored optional origin, not calibrated';objects.append(exhaust)
        export(folder/'model.glb',objects,name=='decoy');bpy.ops.wm.save_as_mainfile(filepath=str(folder/'model.blend'),compress=True,relative_remap=True)
        for view,front in [('front-quarter',False),('front',True)]:
            aim(scene,front);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
        report=dict(id=root['catalogue_id'],package='openfa.interceptor-missle' if name=='interceptor' else 'openfa.advanced-munitions',
            meshes=sum(o.type=='MESH' for o in objects),triangles=sum(sum(len(f.vertices)-2 for f in o.data.polygons) for o in objects if o.type=='MESH'),
            unique_meshes=len(meshes),materials=1,packed_maps=2,map_size=1024,native_forward='-Y',native_up='+Z',world_size_proposal=48,
            scale_status='generic runtime fitting assumption, not recovered physical dimensions',source_sha256=sha(folder/'model.blend'),glb_sha256=sha(folder/'model.glb'),
            generator_sha256=sha(Path(__file__)),animation='DecoyMenuSeparation:0-6s; separation0.5-3s; hold3-4s; menu-only return4-6s' if name=='decoy' else None)
        if name=='decoy':report['segment_sha256']=sha(folder/'segment.glb')
        (folder/'generation.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report)
    print('EXTENSION_MODELS_AUTHORED',json.dumps(reports))


if __name__=='__main__':main()
