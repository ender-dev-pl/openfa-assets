"""Closed editable radial vessels with explicitly supplied shallow geometric dents."""
import math
import bpy
from build_openfa_assets import finish


def profile_radius(profile,z):
    return next(ra+(rb-ra)*(z-za)/(zb-za) for (za,ra),(zb,rb) in zip(profile,profile[1:]) if za<=z<=zb)


def vessel(name,profile,surface,dents):
    heights=[profile[0][0]]
    for (za,_),(zb,_) in zip(profile,profile[1:]):
        steps=max(1,math.ceil((zb-za)/.03));heights += [za+(zb-za)*i/steps for i in range(1,steps+1)]
    count=128;vertices=[]
    for z in heights:
        for i in range(count):
            phi=i*math.tau/count
            dent=sum(depth*math.exp(-2*((math.atan2(math.sin(phi-angle),math.cos(phi-angle))/.11)**2+((z-height)/.09)**2))
                for angle,height,depth in dents)
            r=profile_radius(profile,z)-dent;vertices.append((r*math.cos(phi),r*math.sin(phi),z))
    faces=[tuple(reversed(range(count)))]
    faces += [(row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i)
        for row in range(len(heights)-1) for i in range(count)]
    faces.append(tuple((len(heights)-1)*count+i for i in range(count)))
    mesh=bpy.data.meshes.new(name+' editable dented shell');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,name,surface,0)
    for face in mesh.polygons: face.use_smooth=len(face.vertices)==4
    return obj
