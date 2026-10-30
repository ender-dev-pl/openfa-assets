"""Closed strips fitted to a supplied radial profile, independently authored geometry."""
import math
import bpy
from build_openfa_assets import finish
from manufactured_vessels import profile_radius


def strip(name,profile,phi,low,high,width,surface):
    vertices=[];count=25
    for row in range(count):
        z=low+(high-low)*row/(count-1);r=profile_radius(profile,z)
        for radial,angle in [(r-.008,phi-width/(2*r)),(r+.006,phi-width/(2*r)),(r+.006,phi+width/(2*r)),(r-.008,phi+width/(2*r))]:
            vertices.append((radial*math.cos(angle),radial*math.sin(angle),z))
    faces=[(3,2,1,0)]
    for row in range(count-1):
        a=row*4;b=a+4
        faces += [(a+j,a+(j+1)%4,b+(j+1)%4,b+j) for j in range(4)]
    faces.append(tuple((count-1)*4+j for j in range(4)))
    mesh=bpy.data.meshes.new(name+' fitted closed casting');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    return obj
