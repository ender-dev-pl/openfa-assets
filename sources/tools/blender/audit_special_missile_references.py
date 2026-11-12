"""Audit filename-bound PM11/PM12 reference availability without inventing previews."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO=Path(__file__).resolve().parents[2]
LEGACY=REPO.parent/'legacy'
TARGET=REPO/'docs/reconstruction/models/special-missile-reference-audit.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    sys.path.insert(0,str(LEGACY/'tools'))
    from fragile256 import read_archive
    refs=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text())['missiles']
    archives=[]
    for directory in ['_MA','_M']:
        path=LEGACY/directory/directory;_,_,entries=read_archive(path)
        names=sorted(e.name for e in entries if e.name.upper().startswith('PM'))
        archives.append(dict(path='../legacy/'+directory+'/'+directory,sha256=sha(path),entry_count=len(entries),pm_entries=names))
    standalone=sorted(str(p.relative_to(LEGACY)) for p in LEGACY.glob('**/PM1[12]*') if p.is_file() and p.suffix.upper() in ['.256','.VID'])
    definitions=[]
    for name in ['bug-hunter','meat-eater']:
        ref=next(r for r in refs if r['id']=='openfa:missile/terran/'+name)
        definitions.append(dict(id=ref['id'],global_type=ref['global_type'],management_preview=ref['management_preview'],
            source_directory=ref['surface']['source_directory'],source_entry=ref['surface']['source_entry'],
            source_sha256=ref['surface']['source_sha256'],frame_count=ref['surface']['frame_count'],
            canonical_reference_frame=9,flight_reference_frames=list(range(7))))
    result=dict(issue=968,scope='Bound catalogue references, PM filename entries in _MA/_M, standalone PM11/PM12 sprite/video files; unidentified images not exhaustively searched',
        reference_index_sha256=sha(REPO/'docs/reconstruction/models/missile-reference-index.json'),archives=archives,
        filename_matched_standalone_files=standalone,definitions=definitions,
        conclusions=['Current _MA contains PM00..PM10 only; PM11/PM12 exist in _M',
                     'Neither catalogue definition has a bound management preview',
                     'High-detail geometry is an authored interpretation, not proven high-resolution reconstruction'])
    if args.check:
        assert json.loads(TARGET.read_text())==result,'Reference audit has stale source evidence'
    else:
        TARGET.write_text(json.dumps(result,indent=2)+'\n')
    print('SPECIAL_MISSILE_REFERENCE_AUDIT_OK',len(definitions),'definitions; limited availability scope')


if __name__=='__main__': main()
