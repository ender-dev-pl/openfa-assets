"""Closed pressure bezels with a planar face and body-fitted embedded cast root."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import finish


def cast_bezel(name,body,point,normal,radius,surface):
    bpy.context.view_layer.update();point=Vector(point);normal=Vector(normal).normalized()
    rotation=normal.to_track_quat('Z','Y').to_matrix();x_axis=rotation @ Vector((1,0,0));y_axis=rotation @ Vector((0,1,0))
    count=64;rings=6;size=1+rings*count;vertices=[]
    samples=[point]+[point+radius*row/rings*(x_axis*math.cos(i*math.tau/count)+y_axis*math.sin(i*math.tau/count))
        for row in range(1,rings+1) for i in range(count)]
    vertices += [p+normal*.025 for p in samples]
    inverse=body.matrix_world.inverted()
    for p in samples:
        hit,where,_,_=body.ray_cast(inverse @ (p+normal*2),(inverse.to_3x3() @ -normal).normalized())
        assert hit,'Cast bezel has no supporting body beneath a root sample'
        back=body.matrix_world @ where-normal*.020
        assert (vertices[len(vertices)-size]-back).dot(normal)>0
        vertices.append(back)
    faces=[]
    for i in range(count):
        a=1+i;b=1+(i+1)%count;faces += [(0,a,b),(size,b+size,a+size)]
    for row in range(rings-1):
        for i in range(count):
            a=1+row*count+i;b=1+row*count+(i+1)%count;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for i in range(count):
        a=1+(rings-1)*count+i;b=1+(rings-1)*count+(i+1)%count;faces.append((a,a+size,b+size,b))
    mesh=bpy.data.meshes.new(name+' body-fitted closed cast root');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,.003)
    obj['construction']='Planar pressure face, sampled curved embedded root; exact hidden casting is authored inference'
    return obj
