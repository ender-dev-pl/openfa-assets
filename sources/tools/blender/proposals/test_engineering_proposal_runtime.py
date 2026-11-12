"""Mutation tests: reject frozen tool exports and disconnected attachments."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from verify_engineering_refinement import ROOT,motion_samples,snapshot
import json
folder=ROOT/'sources/proposals/engineering-ships/terran/repair'
meta=json.loads((folder/'model.json').read_text())
def load():bpy.ops.wm.open_mainfile(filepath=str(folder/'model.blend'),load_ui=False,use_scripts=False)
def rejected(fn,text):
    try:fn()
    except AssertionError as e:
        assert text in str(e),str(e)
    else:raise AssertionError('Defective fixture was accepted: '+text)
load();motion_samples(meta)
for o in bpy.context.scene.objects:
    if o.animation_data:
        for track in o.animation_data.nla_tracks:track.mute=True
rejected(lambda:motion_samples(meta),'No geometry moves')
load();o=bpy.data.objects['GripShoulderPivot'];o.location.x+=10;bpy.context.view_layer.update()
rejected(lambda:snapshot(meta),'Unsupported geometry')
load();bpy.data.objects['ProposalRoot']['runtime_integration']=True
rejected(lambda:snapshot(meta),'')
load();m=next(m for m in bpy.data.materials if m.use_nodes and m.node_tree.nodes.get('Principled BSDF'));shader=m.node_tree.nodes.get('Principled BSDF')
for link in list(shader.inputs['Normal'].links):m.node_tree.links.remove(link)
rejected(lambda:snapshot(meta),'Missing portable PBR map')
load();_,before=snapshot(meta)
materials=[m for m in bpy.data.materials if m.use_nodes and m.node_tree.nodes.get('Principled BSDF')]
nodes=[m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].links[0].from_node for m in materials]
a,b=nodes[:2];a.image,b.image=b.image,a.image
_,after=snapshot(meta)
assert before['images']==after['images'] and before['bindings']!=after['bindings'],'Swapped material image assignment was not detected'
print('ENGINEERING_MUTATIONS_OK frozen_animation detached_arm runtime_flag missing_normal_map swapped_image_bindings')
