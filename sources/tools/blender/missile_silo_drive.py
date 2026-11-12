"""Compact lift cylinders coaxial with the eight fixed iris rotation axes."""
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def linear_action(obj):
    for layer in obj.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'


def mount_ring(root,mesh_object):
    n=64;profile=[(.50,.765),(.54,.765),(.54,.955),(.50,.955)]
    vertices=[(r*math.cos(math.tau*i/n),r*math.sin(math.tau*i/n),z) for z,r in profile for i in range(n)]
    faces=[(j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i) for j in range(4) for i in range(n)]
    return mesh_object('Iris internal mounting ring',vertices,faces,bpy.data.materials['Refined | dark'],root)


def drive(root,index,radial,angle,leaf,box,mesh_object):
    number=f'{index+1:02}';dark=bpy.data.materials['Refined | dark'];edge=bpy.data.materials['Refined | edge']
    for name,radius,depth,z,material in [('Iris coax barrel ',.055,.14,.525,dark),('Iris coax gland ',.061,.025,.60,edge)]:
        bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=radius,depth=depth)
        obj=bpy.context.object;obj.name=name+number;obj.parent=root;obj.location=radial*.82+Vector((0,0,z));obj.data.materials.append(material)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=.026,depth=.20)
    rod=bpy.context.object;rod.name='Iris coax rod '+number;rod.parent=leaf;rod.location=(0,0,-.09);rod.data.materials.append(edge)
    # Bearing saddle conforms to the evaluated underside, including leaf thickness.
    bpy.context.view_layer.update();evaluated=leaf.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
    tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],[list(f.vertices) for f in mesh.polygons]);evaluated.to_mesh_clear()
    n=32;vertices=[(.045*math.cos(math.tau*j/n),.045*math.sin(math.tau*j/n),-.045) for j in range(n)]
    for j in range(n):
        x=.045*math.cos(math.tau*j/n);y=.045*math.sin(math.tau*j/n)
        point,*_=tree.ray_cast(Vector((x,y,-.12)),Vector((0,0,1)),.6);assert point is not None
        vertices.append((x,y,point.z+.001))
    point,*_=tree.ray_cast(Vector((0,0,-.12)),Vector((0,0,1)),.6);assert point is not None
    vertices.append((0,0,point.z+.001))
    faces=[tuple(range(n-1,-1,-1))]+[(j,(j+1)%n,(j+1)%n+n,j+n) for j in range(n)]+[(2*n,n+j,n+(j+1)%n) for j in range(n)]
    saddle=mesh_object('Iris hinge axle '+number,vertices,faces,dark,leaf)
    saddle['attachment']='Conformal saddle meets leaf underside; cylinder and spindle share fixed rotation axis'
