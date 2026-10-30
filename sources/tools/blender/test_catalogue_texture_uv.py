"""Controlled graph and UV buffer-layout checks without game asset mutation."""
import sys
from pathlib import Path
import struct
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
from audit_catalogue_texture_uv import reachable_images,coordinate_sources,uv_accessor


def main():
    material=bpy.data.materials.new('Texture audit test');material.use_nodes=True
    nodes=material.node_tree.nodes;links=material.node_tree.links
    image=nodes.new('ShaderNodeTexImage');shader=nodes.get('Principled BSDF')
    assert reachable_images(material)[0]==[],'Unused image must not create a dependency'
    links.new(image.outputs['Color'],shader.inputs['Base Color'])
    assert reachable_images(material)[0]==[image]
    assert coordinate_sources(image.inputs['Vector'])=={('uv','')}
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map='Explicit chart';links.new(uv.outputs[0],image.inputs['Vector'])
    assert coordinate_sources(image.inputs['Vector'])=={('uv','Explicit chart')}
    coordinates=nodes.new('ShaderNodeTexCoord');links.new(coordinates.outputs['Generated'],image.inputs['Vector'])
    assert coordinate_sources(image.inputs['Vector'])=={('non_uv','Generated')}
    document=dict(accessors=[dict(bufferView=0,componentType=5126,type='VEC2',count=2)],
                  bufferViews=[dict(buffer=0,byteOffset=0,byteLength=32,byteStride=16)])
    binary=struct.pack('<8f',0,1,0,0,1,0,0,0)
    assert uv_accessor(document,binary,0)['nonfinite']==0
    invalid=struct.pack('<8f',float('nan'),1,0,0,1,0,0,0)
    assert uv_accessor(document,invalid,0)['nonfinite']==1
    document['accessors'][0]['sparse']={}
    assert uv_accessor(document,binary,0)['status'].startswith('uninspected')
    del document['accessors'][0]['sparse'];document['bufferViews'][0]['byteLength']=16
    try: uv_accessor(document,binary,0)
    except AssertionError: pass
    else: raise AssertionError('Truncated accessor must be rejected')
    print('CATALOGUE_TEXTURE_UV_TEST_OK',flush=True)


if __name__=='__main__': main()
