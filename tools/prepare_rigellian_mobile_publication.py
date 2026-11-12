"""Strip metadata-only local paths before fresh native/GLB runtime checks."""
from pathlib import Path
import argparse
import hashlib
import json
import re
from publication_support import clean_blend, clean_png

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ship');args=parser.parse_args()
    style=json.loads((ROOT/'sources/objects/rigellian/fleet-style.json').read_text())
    for ship in style['ships']:
        if args.ship and args.ship!=ship['slug']:continue
        folder=ROOT/ship['canonical_directory'];path=folder/'model.blend'
        def resolve(old):
            name=re.split(rb'[\\/]',old)[-1]
            return b'//../../../materials/rigellian-mobile-fleet/'+name if name.endswith(b'.png') else b'//'
        cleaned,edits,before,after=clean_blend(path.read_bytes(),resolve);path.write_bytes(cleaned)
        report=json.loads((folder/'generation.json').read_text())
        report['blend_sha256']=hashlib.sha256(cleaned).hexdigest()
        (folder/'generation.json').write_text(json.dumps(report,indent=2)+'\n')
        preparation={'fixed_width_path_strings_removed':edits,'raw_before_sha256':before,'raw_after_sha256':after,
                     'method':'Byte changes restricted to fixed-width path metadata; fresh Blender verification follows.'}
        (folder/'publication-preparation.json').write_text(json.dumps(preparation,indent=2)+'\n')
        for png in (ROOT/'gallery/media/objects/rigellian'/ship['slug']).glob('*.png'):
            png.write_bytes(clean_png(png.read_bytes()))
        print('RIGELLIAN_PUBLICATION_PREPARED',ship['slug'],edits)


if __name__=='__main__':main()
