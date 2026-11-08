"""Metadata-only cleanup before reopening the final editable/remastered source."""
from pathlib import Path
import hashlib
import json
import re
from publication_support import clean_blend,clean_png

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'sources/objects/achaean/dedicated-ore-transporter';source=out/'model.blend'
    def resolve(old):
        name=re.split(rb'[\\/]',old)[-1]
        return b'//../../../materials/achaean/dedicated-ore-transporter/'+name if name.endswith(b'.png') else b'//'
    data,edits,before,after=clean_blend(source.read_bytes(),resolve);source.write_bytes(data)
    report=json.loads((out/'generation.json').read_text());report['blend_sha256']=hashlib.sha256(data).hexdigest()
    (out/'generation.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'publication-preparation.json').write_text(json.dumps(dict(path_strings_removed=edits,raw_before_sha256=before,raw_after_sha256=after,scope='Fixed-width metadata only; fresh native/GLB verification follows'),indent=2)+'\n')
    for path in (ROOT/'gallery/media/objects/achaean/dedicated-ore-transporter').glob('*.png'):
        path.write_bytes(clean_png(path.read_bytes()))
    print('ACHAEAN_PUBLICATION_PREPARED',edits,'metadata strings')


if __name__=='__main__':main()
