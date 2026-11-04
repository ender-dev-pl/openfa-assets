"""Attach independently authored, packed exportable RI02 wear images and UVs."""
import math
from pathlib import Path
import bpy

ROOT=Path(__file__).resolve().parents[2]/'docs/assets/reconstruction/buildings/rigellian/filtration-plant'


def apply(meshes):
    material=bpy.data.materials['RI02 | aged jade shell'];nodes=material.node_tree.nodes;links=material.node_tree.links
    shader=nodes.get('Principled BSDF')
    coordinates=nodes.new('ShaderNodeUVMap');coordinates.uv_map='Authored cylindrical wear'
    for name,input_name,space in [('authored-shell-colour.png','Base Color','sRGB'),('authored-shell-roughness.png','Roughness','Non-Color')]:
        image=bpy.data.images.load(str(ROOT/name));image.colorspace_settings.name=space;image.pack()
        texture=nodes.new('ShaderNodeTexImage');texture.image=image;texture.interpolation='Linear'
        texture.label='Independent analytic wear; no legacy pixels';links.new(texture.outputs['Color'],shader.inputs[input_name])
        links.new(coordinates.outputs['UV'],texture.inputs['Vector'])
    for obj in meshes:
        if obj.name not in ['RI02 rounded filtration pressure body','RI02 capped upper tower']: continue
        uv=obj.data.uv_layers.new(name='Authored cylindrical wear')
        obj.data.uv_layers.active=uv;uv.active_render=True
        for face in obj.data.polygons:
            if face.material_index<4: face.material_index=0
            coords=[obj.data.vertices[obj.data.loops[index].vertex_index].co for index in face.loop_indices]
            values=[(math.atan2(v.y,v.x)+math.pi)/math.tau for v in coords]
            wraps=max(values)-min(values)>.5
            for index,v,u in zip(face.loop_indices,coords,values):
                uv.data[index].uv=(u+1 if wraps and u<.5 else u,v.z/2.5)
        obj['wear']='Packed independent 1024x1024 colour/roughness maps and actual shallow dents'
