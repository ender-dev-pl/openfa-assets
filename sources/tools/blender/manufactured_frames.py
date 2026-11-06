"""Editable closed rounded-rectangle retaining frames with continuous tube geometry."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import finish


def rounded_frame(name,centre,width,height,corner,tube,surface):
    x,y,z=centre;path=[]
    for cx,cz,angle in [(x+width/2-corner,z+height/2-corner,0),
            (x-width/2+corner,z+height/2-corner,math.pi/2),
            (x-width/2+corner,z-height/2+corner,math.pi),
            (x+width/2-corner,z-height/2+corner,3*math.pi/2)]:
        for i in range(9):
            phi=angle+i*math.pi/16;path.append(Vector((cx+corner*math.cos(phi),y,cz+corner*math.sin(phi))))
    vertices=[];count=16
    for i,point in enumerate(path):
        tangent=(path[(i+1)%len(path)]-path[(i-1)%len(path)]).normalized();normal=Vector((tangent.z,0,-tangent.x))
        for n in range(count):
            phi=n*math.tau/count;vertices.append(point+tube*(Vector((0,1,0))*math.cos(phi)+normal*math.sin(phi)))
    faces=[(i*count+n,i*count+(n+1)%count,((i+1)%len(path))*count+(n+1)%count,((i+1)%len(path))*count+n)
        for i in range(len(path)) for n in range(count)]
    mesh=bpy.data.meshes.new(name+' continuous solid');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    for face in mesh.polygons: face.use_smooth=True
    return obj
