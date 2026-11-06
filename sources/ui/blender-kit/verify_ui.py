"""Verify native/imported rendered silhouettes and UI deliverable states (Pillow)."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--renders', required=True, type=Path)
args = parser.parse_args()
source = Path(__file__).resolve().parent
metadata = json.loads((source/'ui-kit.json').read_text(encoding='utf-8'))
native = Image.open(args.renders/'source-contact.png').convert('RGBA')
imported = Image.open(args.renders/'imported-contact.png').convert('RGBA')
assert native.size == imported.size
left = list(native.getchannel('A').point(lambda a: 255 if a >= 128 else 0).tobytes())
right = list(imported.getchannel('A').point(lambda a: 255 if a >= 128 else 0).tobytes())
intersection = sum(a > 0 and b > 0 for a,b in zip(left,right))
union = sum(a > 0 or b > 0 for a,b in zip(left,right))
iou = intersection / union
assert iou > .995, f'Imported geometry diverged: silhouette IoU={iou}'
for index in range(64):
    image = Image.open(args.renders/f'icon-{index:02}.png').convert('RGBA')
    assert image.size == (192,192)
    occupied = sum(alpha > 128 for alpha in image.getchannel('A').tobytes())
    assert 200 < occupied < 192*192*.85, (index,occupied)
for name,size in metadata['panel_states'].items():
    image = Image.open(args.renders/(name+'.png'))
    assert image.size == (size[0]*4,size[1]*4), (name,image.size)
for family in ['gameplay','frontend','control']:
    fingerprints = {hashlib.sha256((args.renders/(family+'-'+state+'.png')).read_bytes()).hexdigest()
                    for state in ['normal','selected','pressed','disabled','hover']}
    # Hover and selected deliberately share the same lit plate geometry/material.
    assert len(fingerprints) >= 4, (family,len(fingerprints))
report = {
    'silhouette_iou':iou,'occupied_native':sum(a>0 for a in left),'occupied_imported':sum(b>0 for b in right),
    'symbols_checked':64,'panel_renders_checked':len(metadata['panel_states']),
    'source_sha256':{name:hashlib.sha256((source/name).read_bytes()).hexdigest()
                     for name in ['build_ui.py','verify_ui.py','ui-kit.blend','ui-kit.glb','ui-kit.json']},
    'proof_sha256':{name:hashlib.sha256((args.renders/name).read_bytes()).hexdigest()
                    for name in ['source-contact.png','imported-contact.png']},
}
(args.renders/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('UI_KIT_VERIFIED',json.dumps(report))
