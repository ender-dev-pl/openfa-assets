"""Ground-plane holdout for a real below-ground RI10 shaft, excluded from GLB geometry."""
import math
import bpy
from mathutils import Vector


def asset_meshes(scene):
    return [obj for obj in scene.objects if obj.type=='MESH' and not obj.get('preview_only')]


def surface_points(meshes):
    points=[]
    for obj in meshes:
        evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        points.extend(p for vertex in mesh.vertices if (p:=evaluated.matrix_world @ vertex.co).z>=-1e-5)
        evaluated.to_mesh_clear()
    return points


def ground_mask():
    existing=bpy.data.objects.get('RI10 preview ground holdout')
    if existing: return existing
    count=128;vertices=[]
    for rx,ry in [(.875,.695),(20,20)]:
        vertices.extend((rx*math.cos(i*math.tau/count),ry*math.sin(i*math.tau/count),0) for i in range(count))
    faces=[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    mesh=bpy.data.meshes.new('Preview ground with real shaft opening');mesh.from_pydata(vertices,[],faces);mesh.update()
    obj=bpy.data.objects.new('RI10 preview ground holdout',mesh);bpy.context.scene.collection.objects.link(obj)
    obj['preview_only']=True;obj.visible_shadow=False
    surface=bpy.data.materials.new('RI10 preview-only ground holdout');surface.use_nodes=True
    nodes=surface.node_tree.nodes;nodes.clear();holdout=nodes.new('ShaderNodeHoldout');output=nodes.new('ShaderNodeOutputMaterial')
    surface.node_tree.links.new(holdout.outputs[0],output.inputs['Surface']);mesh.materials.append(surface)
    return obj
