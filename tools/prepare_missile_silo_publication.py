"""Clean source metadata only; actual corrected-silo validation follows."""
from pathlib import Path
import json
import hashlib
from publication_support import clean_blend

ROOT=Path(__file__).resolve().parents[1]


def main():
    folder=ROOT/'sources/docs/assets/bootstrap-3d/terran-refined/pb14';p=folder/'model.blend'
    data,edits,before,after=clean_blend(p.read_bytes(),lambda old:b'//');p.write_bytes(data)
    r=json.loads((folder/'correction-generation.json').read_text());r['source_sha256']=hashlib.sha256(data).hexdigest();(folder/'correction-generation.json').write_text(json.dumps(r,indent=2)+'\n')
    (folder/'publication-preparation.json').write_text(json.dumps(dict(metadata_edits=edits,raw_before_sha256=before,raw_after_sha256=after,scope='Metadata only, no geometry edit'),indent=2)+'\n')


if __name__=='__main__':main()
