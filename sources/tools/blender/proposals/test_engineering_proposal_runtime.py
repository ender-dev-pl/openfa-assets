"""Mutation tests: reject frozen tool exports and disconnected attachments."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from verify_engineering_proposal import ROOT,motion_samples,snapshot
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
print('ENGINEERING_MUTATIONS_OK frozen_animation detached_arm runtime_flag')
