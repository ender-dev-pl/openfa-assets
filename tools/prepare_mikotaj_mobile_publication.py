"""Strip private native metadata before actual runtime checks, never after them."""
from pathlib import Path
import json,hashlib
from publication_support import clean_blend
ROOT=Path(__file__).resolve().parents[1]


def main():
    for folder in sorted((ROOT/'sources/objects/mikotaj').iterdir()):
        if not (folder/'model.json').exists():continue
        p=folder/'model.blend';data,edits,before,after=clean_blend(p.read_bytes(),lambda old:b'//');p.write_bytes(data)
        meta=json.loads((folder/'model.json').read_text());meta['blend_sha256']=hashlib.sha256(data).hexdigest();(folder/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
        (folder/'publication-preparation.json').write_text(json.dumps(dict(edits=edits,raw_before_sha256=before,raw_after_sha256=after,scope='Metadata only; runtime verification follows'),indent=2)+'\n')
        print('PREPARED',folder.name,edits)


if __name__=='__main__':main()
