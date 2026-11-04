"""An original articulated iris dome, informed by the PB14 opening overlay frames."""
import math

import bmesh
import bpy
from mathutils import Vector


def build_iris(d):
    # Remove the coarse solid lid and the bunker's top n-gon, exposing a real launch well.
    for obj in list(d.collection.objects):
        if obj.name.startswith('Silo armoured lid'):
            bpy.data.objects.remove(obj,do_unlink=True)
    bunker=next(obj for obj in d.collection.objects if obj.name.startswith('Silo flared bunker'))
    mesh=bmesh.new()
    mesh.from_mesh(bunker.data)
    top=max(vertex.co.z for vertex in mesh.verts)
    caps=[face for face in mesh.faces if len(face.verts)>4 and all(abs(vertex.co.z-top)<.0001 for vertex in face.verts)]
    assert len(caps)==1
    bmesh.ops.delete(mesh,geom=caps,context='FACES_ONLY')
    mesh.to_mesh(bunker.data)
    mesh.free()
    d.shell('Launch well inner liner',[(.06,.87),(.35,.87),(.64,.87)],32,'dark')
    d.disc('Launch well bottom',(0,0,.045),.87,.04,'dark')
    d.ring('Iris guide race',(0,0,.64),.89,.045,'edge')
    d.ring('Iris outer drive cover',(0,0,.60),.98,.065,'bronze')
    for i in range(4):
        angle=i*math.tau/4
        d.rod('Launch guide rail',(.65*math.cos(angle),.65*math.sin(angle),.10),
            (.65*math.cos(angle),.65*math.sin(angle),.57),.022,'edge')
    leaves=[]
    count=8
    for index in range(count):
        theta=index*math.tau/count
        angle=theta+math.pi/count
        pivot=Vector((.82*math.cos(angle),.82*math.sin(angle),.64))
        vertices,faces=[],[]
        radial_steps,angular_steps=16,10
        for row in range(radial_steps+1):
            radius=.003+.88*row/radial_steps
            sweep=.48*(1-radius/.883)
            for column in range(angular_steps+1):
                a=theta+sweep+(column/angular_steps)*(math.tau/count+.08)-.04
                height=.64+.22*math.sqrt(max(0,1-(radius/.883)**2))+index*.0015
                point=Vector((radius*math.cos(a),radius*math.sin(a),height))
                vertices.append(tuple(point-pivot))
        for row in range(radial_steps):
            for column in range(angular_steps):
                a=row*(angular_steps+1)+column
                faces.append((a,a+angular_steps+1,a+angular_steps+2,a+1))
        data=bpy.data.meshes.new(f'Iris curved leaf {index+1:02}')
        data.from_pydata(vertices,[],faces)
        data.update()
        obj=bpy.data.objects.new(data.name,data)
        d.collection.objects.link(obj)
        obj.location=pivot
        data.materials.append(d.m['gold' if index%2 else 'bronze'])
        for face in data.polygons:
            face.use_smooth=True
        solid=obj.modifiers.new('Leaf metal thickness','SOLIDIFY')
        solid.thickness=.012
        solid.offset=-1
        obj['iris_leaf']=index
        # A rigid curved leaf around its own rim pivot, never a scaled fake aperture.
        for frame,turn,drop in [(1,0,0),(5,0,.20),(17,50,.20),(29,0,.20),(33,0,0)]:
            obj.rotation_euler.z=math.radians(turn)
            obj.location.z=pivot.z-drop
            obj.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
            obj.keyframe_insert(data_path='location',index=2,frame=frame)
        obj.animation_data.action.name=f'IrisLeaf_{index+1:02}_OpenClose'
        for layer in obj.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:
                            key.interpolation='LINEAR'
        d.keep(obj)
        leaves.append(obj.name)
        d.disc('Iris hinge axle',(pivot.x,pivot.y,.61),.045,.08,'edge')
    scene=bpy.context.scene
    scene.frame_start,scene.frame_end=1,33
    scene.render.fps=16
    scene.frame_set(1)
    d.collection['iris_leaves']=leaves
    d.feature('Articulated overlapping curved iris leaves, rim pivots, guide race and open launch well')
    return leaves
