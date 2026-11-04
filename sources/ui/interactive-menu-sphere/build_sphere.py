"""Derive a rotatable, double-sided sphere from the verified legacy menu study."""
import bpy, bmesh, math, json, random, sys
from pathlib import Path
from mathutils import Matrix, Vector, Quaternion
out=Path(sys.argv[sys.argv.index('--')+1]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(out.parent.parent/'issue-176-menu-refinement/source/main-menu.blend'))
scene=bpy.context.scene
keep={'bezel','sphere','emblem','sphere-neon'}
for o in list(scene.objects):
    if o.type not in {'LIGHT','CAMERA'} and not any(c.name in keep for c in o.users_collection):bpy.data.objects.remove(o,do_unlink=True)
def empty(name):
    o=bpy.data.objects.new(name,None);scene.collection.objects.link(o);return o
root=empty('SphereControlRoot');rotor=empty('SphereRotor');bezel=empty('SphereBezel');rotor.parent=root;bezel.parent=root
inverse=Matrix.Diagonal((1/.66,1/.66,1/.66,1)) @ Matrix.Translation((.68,-.04,0))
logos=[]
for o in list(scene.objects):
    if o.type not in {'MESH','CURVE'}:continue
    o.hide_render=False;o.hide_set(False)
    if o.type=='CURVE':
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    o.data.transform(inverse @ o.matrix_world);o.matrix_world=Matrix.Identity(4)
    iscore=o.name.startswith('Convex smoked');islogo=o.name.startswith('Continuous welded')
    for v in o.data.vertices:
        if iscore:v.co.z=.04+(v.co.z-.04)*2
        if islogo:v.co.z+=.62*math.sqrt(max(.02,1-(v.co.x*v.co.x+v.co.y*v.co.y)/1.24**2))
        v.co.z-=.04
    o.parent=rotor if iscore or islogo else bezel
    if iscore:o.name='Full spherical smoked core'
    if islogo:o.name='Front continuous emblem';logos.append(o)
front=logos[0];rear=front.copy();rear.data=front.data.copy();scene.collection.objects.link(rear);rear.name='Rear mirrored continuous emblem';rear.parent=rotor
for v in rear.data.vertices:v.co.z=-v.co.z
bm=bmesh.new();bm.from_mesh(rear.data);bmesh.ops.reverse_faces(bm,faces=list(bm.faces));bm.to_mesh(rear.data);bm.free()
for o in [front,rear]:
    bm=bmesh.new();bm.from_mesh(o.data);assert all(e.is_manifold for e in bm.edges);bm.free()
# Keep editable procedural wear in .blend; export stable PBR colors for glTF.
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if not bs:continue
    if mat.name.startswith('Used smoked'):color=(.025,.007,.055,1)
    elif 'ruby' in mat.name.lower():color=(.65,.008,.006,1)
    else:color=tuple(bs.inputs['Base Color'].default_value)
    mat.diffuse_color=color
    for node in mat.node_tree.nodes:
        if node.type=='VALTORGB' and 'ruby' not in mat.name.lower():
            color=tuple(node.color_ramp.elements[-1].color);mat.diffuse_color=color
camera=scene.camera;camera.location=(0,0,12);camera.data.ortho_scale=3.3
scene.render.resolution_x=400;scene.render.resolution_y=400;scene.cycles.samples=16
scene.render.fps=60;scene.frame_start=1;scene.frame_end=73
axis=Vector((.62,.76,.19)).normalized();rotor.rotation_mode='QUATERNION'
emission=bpy.data.materials['Emblem luminous ruby'].node_tree.nodes.get('Principled BSDF').inputs['Emission Strength']
for f in range(1,74,3):
    t=(f-1)/72;s=t*t*(3-2*t)
    rotor.rotation_quaternion=Quaternion(axis,math.tau*s);rotor.keyframe_insert(data_path='rotation_quaternion',frame=f)
    emission.default_value=.331+3*math.sin(math.pi*t)**2;emission.keyframe_insert(data_path='default_value',frame=f)
scene.frame_set(1)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'interactive-sphere.blend'))
# glTF cannot serialize procedural shader graphs. Export explicit PBR values.
for mat in bpy.data.materials:
    if not mat.use_nodes:continue
    bs=mat.node_tree.nodes.get('Principled BSDF')
    if not bs:continue
    color=(.025,.007,.055,1) if mat.name.startswith('Used smoked') else (.65,.008,.006,1) if 'ruby' in mat.name.lower() else tuple(mat.diffuse_color)
    for socket in ['Base Color','Normal','Roughness','Metallic']:
        for link in list(bs.inputs[socket].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=color
    if 'ruby' in mat.name.lower():bs.inputs['Emission Color'].default_value=color
bpy.ops.object.select_all(action='DESELECT')
for o in [root,rotor,bezel]+list(rotor.children)+list(bezel.children):o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(out/'interactive-sphere.glb'),use_selection=True,export_format='GLB',export_animations=True,export_apply=True)
for name,q in [('front',Quaternion()),('rear',Quaternion((0,1,0),math.pi)),('side',Quaternion((0,1,0),math.pi/2))]:
    scene.frame_set(1);rotor.animation_data_clear();rotor.rotation_quaternion=q
    scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
# Reopen the authored animation for proof frames and saved-source runtime verification.
bpy.ops.wm.open_mainfile(filepath=str(out/'interactive-sphere.blend'));scene=bpy.context.scene
for f in [1,19,37,55,73]:
    scene.frame_set(f);scene.render.filepath=str(out/f'spin-{f:02}.png');bpy.ops.render.render(write_still=True)
for o in list(scene.objects):
    if o.type not in {'LIGHT','CAMERA'}:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.import_scene.gltf(filepath=str(out/'interactive-sphere.glb'))
assert bpy.data.objects.get('SphereRotor')
scene.frame_set(1);scene.render.filepath=str(out/'imported-front.png');bpy.ops.render.render(write_still=True)
(out/'manifest.json').write_text(json.dumps({'scope':'models only; client click handling remains to implement','rotor':'SphereRotor','stationary':'SphereBezel','pivot':[0,0,0],'radius':1.24,'front_normal':[0,0,1],'rear':'mirrored same continuous logo, reflected through XY plane with reversed winding','preview_axis':list(axis),'duration_seconds':1.2,'rotation':'quaternion(normalize(random_axis), 2*pi*smoothstep(progress))','light':'emblem emission strength = 0.331 + 3*sin(pi*progress)^2; glTF material animation is not portable, drive intensity in client','logo_meshes':2,'logo_nonmanifold_edges':0,'runtime_verified':'Blender source reopen and independent GLB import render'},indent=2)+'\n')
print('INTERACTIVE_SPHERE_VERIFIED')
