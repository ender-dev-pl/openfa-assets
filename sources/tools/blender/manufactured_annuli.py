"""Closed editable annular castings with independent inner/outer profiles."""
import math
import bpy
from build_openfa_assets import finish


def annulus(name,centre,rows,surface,dent):
    cx,cy=centre;count=128;vertices=[]
    refined=[rows[0]]
    for left,right in zip(rows,rows[1:]):
        steps=max(1,math.ceil((right[0]-left[0])/.025))
        for step in range(1,steps+1):
            t=step/steps;refined.append(tuple(a+(b-a)*t for a,b in zip(left,right)))
    rows=refined;size=len(rows)*count
    angle,height,depth=dent
    for inside in [False,True]:
        for z,outer,inner in rows:
            for i in range(count):
                phi=i*math.tau/count;delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle))
                wear=0 if inside else depth*math.exp(-2*((delta/.10)**2+((z-height)/.07)**2))
                r=(inner if inside else outer)-wear;vertices.append((cx+r*math.cos(phi),cy+r*math.sin(phi),z))
    faces=[]
    for row in range(len(rows)-1):
        for i in range(count):
            j=(i+1)%count;a=row*count+i;b=row*count+j;c=b+count;d=a+count
            faces += [(a,b,c,d),(a+size,d+size,c+size,b+size)]
    for row in [0,len(rows)-1]:
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;faces.append((a,a+size,b+size,b))
    mesh=bpy.data.meshes.new(name+' closed annular casting');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    for face in mesh.polygons:
        zs=[mesh.vertices[index].co.z for index in face.vertices];face.use_smooth=max(zs)-min(zs)>1e-6
    return obj
