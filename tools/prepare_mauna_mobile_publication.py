"""Sanitize one deliberately selected source before actual runtime verification."""
from pathlib import Path
import argparse,hashlib,json
from publication_support import clean_blend
ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--ship',required=True);key=parser.parse_args().ship
    root=ROOT/'sources/objects/mauna';folder=(root/key).resolve();assert folder.parent==root.resolve()
    p=folder/'model.blend';data,edits,before,after=clean_blend(p.read_bytes(),lambda old:b'//');p.write_bytes(data)
    meta_path=folder/'model.json';meta=json.loads(meta_path.read_text());meta['blend_sha256']=hashlib.sha256(data).hexdigest();meta_path.write_text(json.dumps(meta,indent=2)+'\n')
    (folder/'publication-preparation.json').write_text(json.dumps(dict(edits=edits,raw_before_sha256=before,raw_after_sha256=after,scope='Metadata only; actual runtime verification follows'),indent=2)+'\n');print('MAUNA_PREPARED',key,edits)


if __name__=='__main__':main()
