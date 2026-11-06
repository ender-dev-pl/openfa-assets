"""Metadata-only publication preparation, before fresh Blender validation."""
import argparse
import hashlib
import json
from pathlib import Path
import re

from PIL import Image
from publication_support import clean_blend, clean_png

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--variant', choices=['refined', 'construction'], required=True)
    args = parser.parse_args()
    folder = ROOT/'sources/objects/terran/space-dock'/args.variant
    meta_path = folder/'model.json'
    meta = json.loads(meta_path.read_text())
    source = folder/'model.blend'
    def resolver(old):
        name = re.split(rb'[\\/]', old)[-1]
        if name.startswith(b'PS7C ') and name.endswith(b'.png'):
            return b'//../../../../materials/terran/space-dock/refined/'+name
        return None
    cleaned, edits, before, after = clean_blend(source.read_bytes(), resolver)
    source.write_bytes(cleaned)
    paths = [ROOT/'gallery/media/objects/terran/space-dock'/args.variant/(name+'.png') for name in meta['views']]
    paths += list((ROOT/'sources/materials/terran/space-dock/refined').glob('*.png'))
    records = []
    for path in paths:
        pixels = sha(Image.open(path).convert('RGBA').tobytes())
        path.write_bytes(clean_png(path.read_bytes()))
        assert pixels == sha(Image.open(path).convert('RGBA').tobytes())
        records.append(dict(path=path.relative_to(ROOT).as_posix(), rgba_sha256=pixels))
    meta['blend_sha256'] = sha(source.read_bytes())
    meta_path.write_text(json.dumps(meta, indent=2)+'\n')
    report = dict(issue=216, variant=args.variant, removed_path_strings=edits,
                  uncompressed_before_sha256=before, uncompressed_after_sha256=after,
                  scope='Only path strings and PNG text/timestamps changed; clean_blend checks all other bytes unchanged. Fresh runtime verification follows.',
                  unchanged_pixels=records)
    (folder/'publication-preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PS7C_PUBLICATION_PREPARED', args.variant, edits, len(records))


if __name__ == '__main__':
    main()
