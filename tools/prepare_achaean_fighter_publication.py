"""Clean metadata in the fighter's new outputs, preserving portable shared maps."""
from pathlib import Path
import hashlib
import json
import re
from publication_support import clean_blend,clean_png

ROOT=Path(__file__).resolve().parents[1]


def main():
    out=ROOT/'sources/objects/achaean/dedicated-fighter'
    def resolve(old):
        name=re.split(rb'[\\/]',old)[-1]
        return b'//../../../materials/achaean/dedicated-ore-transporter/'+name if name.endswith(b'.png') else b'//'
    source=out/'model.blend';data,edits,before,after=clean_blend(source.read_bytes(),resolve);source.write_bytes(data)
    report=json.loads((out/'generation.json').read_text());report['blend_sha256']=hashlib.sha256(data).hexdigest()
    (out/'generation.json').write_text(json.dumps(report,indent=2)+'\n')
    (out/'publication-preparation.json').write_text(json.dumps(dict(path_strings_removed=edits,raw_before_sha256=before,raw_after_sha256=after,scope='Metadata only; actual runtime verification follows'),indent=2)+'\n')
    for path in (ROOT/'gallery/media/objects/achaean/dedicated-fighter').glob('*.png'):path.write_bytes(clean_png(path.read_bytes()))
    print('FIGHTER_PUBLICATION_PREPARED',edits)


if __name__=='__main__':main()
