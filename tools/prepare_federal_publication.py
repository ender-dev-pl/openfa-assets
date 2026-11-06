"""Remove metadata-only local paths and PNG timestamps; verify pixels are unchanged.

Run after generation and BEFORE a fresh native/import runtime verification.
"""
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
    folder = ROOT/'sources/objects/shared/federal-transporter/refined'
    source = folder/'model.blend'
    def resolve(old):
        name = re.split(rb'[\\/]', old)[-1]
        if name.endswith(b'.png'):
            return b'//../../../../materials/shared/federal-transporter/'+name
        return b'//'
    cleaned, edits, original_raw, cleaned_raw = clean_blend(source.read_bytes(), resolve)
    source.write_bytes(cleaned)
    records = []
    paths = list((ROOT/'sources/materials/shared/federal-transporter').glob('*.png'))
    model = json.loads((folder/'model.json').read_text())
    paths += [ROOT/'gallery/media/objects/shared/federal-transporter/refined'/(name+'.png')
              for name in model['views']]
    for path in paths:
        before = sha(Image.open(path).convert('RGBA').tobytes())
        path.write_bytes(clean_png(path.read_bytes()))
        after = sha(Image.open(path).convert('RGBA').tobytes())
        assert before == after
        records.append(dict(path=path.relative_to(ROOT).as_posix(), rgba_sha256=after))
    meta_path = folder/'model.json'
    meta = json.loads(meta_path.read_text())
    meta['blend_sha256'] = sha(source.read_bytes())
    meta_path.write_text(json.dumps(meta, indent=2)+'\n')
    report = dict(issue=215, fixed_width_path_strings_removed=edits,
                  uncompressed_before_sha256=original_raw, uncompressed_after_sha256=cleaned_raw,
                  preservation='Existing clean_blend verifies every byte outside path strings is unchanged. Fresh runtime verification must follow.',
                  unchanged_rgba_pixels=records)
    (folder/'publication-preparation.json').write_text(json.dumps(report, indent=2)+'\n')
    print('FEDERAL_PUBLICATION_PREPARED', edits, 'path strings;', len(records), 'pixel-identical PNGs')


if __name__ == '__main__':
    main()
