"""Issue242: in-place correction of the current PB14 iris and two status lamps.

The original eight curved leaves and their drop/50-degree motion are retained. Original ground datum and
first-half iris timing stay fixed. Lamp mode presets use shared geometry; no
unverified legacy blinking schedule is embedded in the iris clip.
"""
from pathlib import Path
import math
import json
import hashlib
import struct
import sys
import bpy
import bmesh
from mathutils import Vector,Quaternion,Matrix

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'sources/docs/assets/bootstrap-3d/terran-refined/pb14'
MEDIA=ROOT/'gallery/media/docs/assets/bootstrap-3d/terran-refined/pb14'
sys.path.insert(0,str(Path(__file__).parent))
from missile_silo_drive import linear_action

COLOURS={'Hybrid':(255,210,138),'AttackOnly':(194,93,93),'DefenceOnly':(150,170,210)}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def mesh_object(name,vertices,faces,mat,parent):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();mesh.materials.append(mat)
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.parent=parent
    for f in mesh.polygons:f.use_smooth=True
    return o


def box(name,centre,size,mat,parent):
    bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name;o.scale=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=parent;o.data.materials.append(mat)
    m=o.modifiers.new('Worn housing bevel','BEVEL');m.width=.009;m.segments=2
    return o


def linear(v):
    v=v/255;return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4


def lamps(root):
    dark=bpy.data.materials['Refined | dark'];edge=bpy.data.materials['Refined | edge']
    modes={}
    for mode,rgb in COLOURS.items():
        name='Silo lamp '+mode;mat=bpy.data.materials.get(name) or bpy.data.materials.new(name);mat.use_nodes=True;b=mat.node_tree.nodes.get('Principled BSDF')
        colour=tuple(linear(v) for v in rgb)+(1,);b.inputs['Base Color'].default_value=colour;b.inputs['Metallic'].default_value=.1;b.inputs['Roughness'].default_value=.28
        b.inputs['Emission Color'].default_value=colour;b.inputs['Emission Strength'].default_value=1
        mat['reference_srgb']=list(rgb);modes[mode]=mat
    for side,x in [('Left',-.20),('Right',.20)]:
        box('StatusLamp'+side+'Bezel',(x,-1.145,.25),(.15,.055,.16),edge,root)
        box('StatusLamp'+side+'Recess',(x,-1.177,.25),(.115,.025,.126),dark,root)
        holder=bpy.data.objects.new('StatusLamp'+side,None);bpy.context.collection.objects.link(holder);holder.parent=root;holder.location=(x,-1.196,.25)
        holder['channel']=side.lower();holder['off']='All three preset children have zero scale';holder['on']='Only selected mode child has unit scale'
        n=24;vertices=[(.037*math.cos(math.tau*i/n),y,.037*math.sin(math.tau*i/n)) for y in [-.005,.005] for i in range(n)]
        faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
        for mode,mat in modes.items():
            o=mesh_object('StatusLamp'+side+mode,vertices,faces,mat,holder);o['lamp_channel']=side.lower();o['launcher_mode']=mode
            o.scale=(1,1,1) if mode=='Hybrid' else (0,0,0)


def shaft(root):
    # Remove the old solid bunker bottom cap as well as the cosmetic well floor.
    # A real central launch tube must continue below the terrain plane.
    bunker=bpy.data.objects['Silo flared bunker'];bm=bmesh.new();bm.from_mesh(bunker.data)
    z=min(v.co.z for v in bm.verts);caps=[f for f in bm.faces if len(f.verts)>4 and all(abs(v.co.z-z)<1e-5 for v in f.verts)]
    if caps:bmesh.ops.delete(bm,geom=caps,context='FACES_ONLY')
    bm.to_mesh(bunker.data);bm.free()
    bottom=bpy.data.objects.get('Launch well bottom')
    if bottom:
        bottom.location.z=-3.2
        mat=bpy.data.materials.get('Silo black shaft floor') or bpy.data.materials.new('Silo black shaft floor');mat.use_nodes=True
        shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(0,0,0,1);shader.inputs['Metallic'].default_value=0;shader.inputs['Roughness'].default_value=1;shader.inputs['Specular IOR Level'].default_value=0
        bottom.data.materials.clear();bottom.data.materials.append(mat)
    for name in ['Launch well inner liner','Iris guide race','Iris outer drive cover','Lid pressure seal','Silo lid seam','Iris outer pocket wall']:
        o=bpy.data.objects.get(name)
        if o:bpy.data.objects.remove(o,do_unlink=True)
    def ring(name,profile,material):
        n=64;vs=[(r*math.cos(math.tau*i/n),r*math.sin(math.tau*i/n),z) for z,r in profile for i in range(n)]
        fs=[(j*n+i,j*n+(i+1)%n,((j+1)%len(profile))*n+(i+1)%n,((j+1)%len(profile))*n+i) for j in range(len(profile)) for i in range(n)]
        return mesh_object(name,vs,fs,bpy.data.materials['Refined | '+material],root)
    ring('Buried launch shaft',[(-3.2,.90),(0,.90),(0,.865),(-3.2,.865)],'dark')



    ring('Launch well inner liner',[(0,.925),(.61,.925),(.61,.905),(0,.905)],'dark')
    ring('Iris guide race',[(.60,.965),(.66,.965),(.66,.905),(.60,.905)],'edge')
    ring('Iris outer drive cover',[(.59,1.04),(.64,1.04),(.64,.965),(.59,.965)],'bronze')
    ring('Lid pressure seal',[(.62,.925),(.64,.925),(.64,.90),(.62,.90)],'dark')
    for o in bpy.context.scene.objects:
        if o.name.startswith('Launch guide rail'):
            v=Vector((o.location.x,o.location.y,0)).normalized();o.location.x=v.x*.94;o.location.y=v.y*.94
        elif o.name.startswith('Iris hinge axle'):
            v=Vector((o.location.x,o.location.y,0)).normalized();o.location.x=v.x*1.0;o.location.y=v.y*1.0;o.location.z=-.98
        elif o.name.startswith('Silo lid hinge'):
            v=Vector((o.location.x,o.location.y,0)).normalized();o.location.x=v.x*1.04;o.location.y=v.y*1.04


def iris():
    # Preserve the original eight curved leaves, including every mesh coordinate.
    # Restore the first model: drop 0.20, then turn 50 degrees; tube-only correction.
    root=bpy.data.objects['SiloPlacementRoot']
    for obj in list(bpy.context.scene.objects):
        if obj.name.startswith(('Iris curved leaf','Iris hinge axle','Silo lid hinge','Iris sliding guide','Iris mount','Iris lift carriage','Iris drive wheel','Iris coax','Iris internal mounting')):
            bpy.data.objects.remove(obj,do_unlink=True)
    for i in range(8):
        theta=i*math.tau/8;angle=theta+math.pi/8
        radial=Vector((math.cos(angle),math.sin(angle),0));pivot=radial*.82+Vector((0,0,.64))
        vertices=[];faces=[];rows=16;columns=10
        for row in range(rows+1):
            radius=.003+.88*row/rows;sweep=.48*(1-radius/.883)
            for col in range(columns+1):
                a=theta+sweep+(col/columns)*(math.tau/8+.08)-.04
                height=.64+.22*math.sqrt(max(0,1-(radius/.883)**2))+i*.0015
                vertices.append(tuple(Vector((radius*math.cos(a),radius*math.sin(a),height))-pivot))
        for row in range(rows):
            for col in range(columns):
                a=row*(columns+1)+col;faces.append((a,a+columns+1,a+columns+2,a+1))
        obj=mesh_object(f'Iris curved leaf {i+1:02}',vertices,faces,bpy.data.materials['Refined | bronze' if i%2==0 else 'Refined | gold'],root)
        obj.location=pivot;obj.rotation_mode='XYZ';obj['iris_leaf']=i
        modifier=obj.modifiers.new('Leaf metal thickness','SOLIDIFY');modifier.thickness=.012;modifier.offset=-1
        n=24;vs=[(.045*math.cos(math.tau*j/n),.045*math.sin(math.tau*j/n),z) for z in [-.04,.04] for j in range(n)]
        fs=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]
        axle=mesh_object(f'Iris hinge axle {i+1:02}',vs,fs,bpy.data.materials['Refined | edge'],root);axle.location=(pivot.x,pivot.y,.61)
        for frame,turn,drop in [(1,0,0),(5,0,.20),(17,50,.20),(29,0,.20),(33,0,0)]:
            obj.location=pivot-Vector((0,0,drop))
            obj.rotation_euler=(0,0,math.radians(turn))
            obj.keyframe_insert('location',frame=frame);obj.keyframe_insert('rotation_euler',frame=frame)
        obj.animation_data.action.name='IrisLeaf_'+str(i+1)
        linear_action(obj)
        obj['mechanism']='Original curved leaf: drop0.20, fixed-axis50-degree turn; original rim interference retained by user choice; no new actuators'



def set_lamps(mode='Hybrid',left=True,right=True):
    for side,on in [('Left',left),('Right',right)]:
        for preset in COLOURS:
            o=bpy.data.objects['StatusLamp'+side+preset];o.scale=(1,1,1) if on and mode==preset else (0,0,0)
    bpy.context.view_layer.update()


def merge_iris_clip(path):
    # Blender4.5 may emit one SCENE animation per animated object. The existing
    # client consumes one normalized iris clip, so merge sampler/channel tables.
    data=path.read_bytes();length=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+length]);merged=dict(name='Animation',samplers=[],channels=[])
    for clip in g['animations']:
        offset=len(merged['samplers']);merged['samplers']+=clip['samplers']
        merged['channels'] += [dict(c,sampler=c['sampler']+offset) for c in clip['channels']]
    # SCENE export can retain frame1/16 even with slide-to-zero enabled. A
    # normalized client fraction0.5 must reach the exact open pose at1second.
    rest=bytearray(data[20+length:]);inputs={s['input'] for s in merged['samplers']};start=min(g['accessors'][a]['min'][0] for a in inputs);done=set()
    for index in inputs:
        accessor=g['accessors'][index];view=g['bufferViews'][accessor['bufferView']]
        assert accessor['componentType']==5126 and accessor['type']=='SCALAR' and view.get('buffer',0)==0
        offset=8+view.get('byteOffset',0)+accessor.get('byteOffset',0);stride=view.get('byteStride',4)
        for i in range(accessor['count']):
            address=offset+i*stride
            if address not in done:
                value=struct.unpack_from('<f',rest,address)[0]-start;struct.pack_into('<f',rest,address,max(0,value));done.add(address)
        accessor['min']=[accessor['min'][0]-start];accessor['max']=[accessor['max'][0]-start]
    g['animations']=[merged];chunk=json.dumps(g,separators=(',',':')).encode();chunk+=b' '*((-len(chunk))%4)
    path.write_bytes(struct.pack('<4sII',b'glTF',2,20+len(chunk)+len(rest))+struct.pack('<II',len(chunk),0x4e4f534a)+chunk+rest)


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'model.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(1)
    bpy.context.preferences.filepaths.save_version=0
    for o in list(scene.objects):
        if o.name.startswith(('Launch status lamp','StatusLamp','Buried launch shaft','Buried iris chamber')):bpy.data.objects.remove(o,do_unlink=True)
    root=bpy.data.objects.get('SiloPlacementRoot')
    if not root:root=bpy.data.objects.new('SiloPlacementRoot',None);bpy.context.collection.objects.link(root)
    root['building_id']='terran:missile-silo';root['preserve_ground_origin']=True;root['ground_level']=0.0;root['animation_kind']='iris';root['lamp_control']='Set each StatusLamp{Left,Right}{Hybrid,AttackOnly,DefenceOnly} scale to 0 or 1; never multiple modes at once'
    hold=bpy.data.objects.get('LaunchPayloadHoldPoint')
    if not hold:hold=bpy.data.objects.new('LaunchPayloadHoldPoint',None);bpy.context.collection.objects.link(hold)
    hold.parent=root;hold.location=(0,0,-2.05);hold['status']='Authored payload-centre proposal for nominal WorldSize48; keep nose below iris until clear; not recovered calibration'
    for o in list(scene.objects):
        if o!=root and o.type=='MESH' and o.parent is None:o.parent=root
    shaft(root);iris();lamps(root);set_lamps();scene.frame_start=1;scene.frame_end=33;scene.render.fps=16;scene.frame_set(1)
    bpy.ops.object.select_all(action='DESELECT')
    for o in scene.objects:
        if o.type in {'MESH','EMPTY'}:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_extras=True,export_animations=True,export_animation_mode='SCENE',export_frame_range=True,export_apply=True,export_anim_slide_to_zero=True,export_merge_animation='NONE')
    merge_iris_clip(OUT/'model.glb')
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True,relative_remap=True)
    report=dict(id='terran:missile-silo',issue=242,drive_generator_sha256=sha(Path(__file__).with_name('missile_silo_drive.py')),source_sha256=sha(OUT/'model.blend'),glb_sha256=sha(OUT/'model.glb'),patcher_sha256=sha(Path(__file__)),closed_frame=1,open_frame=17,loop_end_frame=33,fps=16,normalized_glb_seconds=[0,2],full_open_seconds=1,ground_level=0,preserve_ground_origin=True,leaf_count=8,lift=0,drop=.20,radial_travel=0,turn_degrees=50,nominal_aperture_radius=.87,verified_passage_radius=.33,shaft_floor=-3.2,payload_hold_centre_z=-2.05,payload_contract='Keep payload below closed iris, then raise through fully clear aperture; no retracting carrier',lamp_colours_srgb=COLOURS,lamp_on_off='independent node visibility per lamp; original blink schedule not established',mechanism_status='Original eight curved leaves and original drop0.20/turn50 motion; tube-only correction; original leaf/rim interference explicitly retained')
    (OUT/'correction-generation.json').write_text(json.dumps(report,indent=2)+'\n');print('SILO_CORRECTED',json.dumps(report))


if __name__=='__main__':main()
