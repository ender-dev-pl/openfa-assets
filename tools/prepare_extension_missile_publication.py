"""Remove local authoring metadata before saved-source runtime validation."""
from pathlib import Path
import json
import re
import hashlib
from publication_support import clean_blend,clean_png

ROOT=Path(__file__).resolve().parents[1]


def main():
    for name in ['interceptor','decoy']:
        out=ROOT/'sources/objects/extensions/munitions'/name;p=out/'model.blend'
        def resolve(old):
            leaf=re.split(rb'[\\/]',old)[-1]
            return b'//../../../../materials/extensions/munitions/'+leaf if leaf.endswith(b'.png') else b'//'
        data,edits,before,after=clean_blend(p.read_bytes(),resolve);p.write_bytes(data)
        r=json.loads((out/'generation.json').read_text());r['source_sha256']=hashlib.sha256(data).hexdigest();(out/'generation.json').write_text(json.dumps(r,indent=2)+'\n')
        (out/'publication-preparation.json').write_text(json.dumps(dict(metadata_edits=edits,raw_before_sha256=before,raw_after_sha256=after,geometry_unchanged=True),indent=2)+'\n')
        for p in (ROOT/'gallery/media/objects/extensions/munitions'/name).glob('*.png'):p.write_bytes(clean_png(p.read_bytes()))


if __name__=='__main__':main()
