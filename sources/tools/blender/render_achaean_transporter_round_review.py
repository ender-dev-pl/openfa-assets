"""Two focused review renders from the existing verified export; never rebuild."""
from pathlib import Path
import hashlib
import json
import sys
import bpy

sys.path.insert(0,str(Path(__file__).parent))
import remaster_achaean_transporter as author
sys.path.insert(0,str(author.ROOT/'tools'))
from publication_support import clean_png


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    before={kind:sha(author.OUT/f'model.{kind}') for kind in ['blend','glb']}
    verified=json.loads((author.OUT/'runtime-verification.json').read_text())
    assert before['glb']==verified['glb_sha256'] and before['blend']==verified['blend_sha256']
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene=author.studio();bpy.ops.import_scene.gltf(filepath=str(author.OUT/'model.glb'))
    meshes=[o for o in scene.objects if o.type=='MESH'];assert len(meshes)==16
    domes=[o for o in meshes if o.name in {'BridgeGlass','BridgeFrames'}]
    author.aim(scene,(1,-1,1.7),domes,margin=1.30)
    scene.render.filepath=str(author.MEDIA/'verified-bridge-detail.png');bpy.ops.render.render(write_still=True)
    body_names={'PressureHull','FormedHullSkins','BellyCargoHatches','OchreAftMarks',
                'DorsalStructure','ForeTerminal','AftTerminal','BridgeGlass','BridgeFrames'}
    visible=[o for o in meshes if o.name in body_names]
    for obj in meshes:obj.hide_render=obj.name not in body_names
    author.aim(scene,(1,0,0),visible,margin=1.20)
    scene.render.filepath=str(author.MEDIA/'verified-hull-profile.png');bpy.ops.render.render(write_still=True)
    renders={}
    for name in ['verified-bridge-detail.png','verified-hull-profile.png']:
        path=author.MEDIA/name;path.write_bytes(clean_png(path.read_bytes()));renders[name]=sha(path)
    assert before=={kind:sha(author.OUT/f'model.{kind}') for kind in before}
    result=dict(id=author.ID,blend_sha256=before['blend'],glb_sha256=before['glb'],
        renderer_sha256=sha(Path(__file__)),blender=bpy.app.version_string,renders=renders,
        source_unchanged=True,hull_profile='Actual imported hull geometry; wing/support/service assemblies hidden for diagnosis',
        bridge_detail='Actual four glazed shells, user-directed crew/bridge interpretation; not hardpoints')
    (author.OUT/'round-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print('ACHAEAN_FOCUSED_ROUND_REVIEW',json.dumps(result))


if __name__=='__main__':
    main()
