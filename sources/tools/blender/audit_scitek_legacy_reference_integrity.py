"""Verify current actual legacy bytes against all36 subject reference bindings."""
from pathlib import Path
import json,sys,hashlib
assets,legacy,out=map(lambda p:Path(p).resolve(),sys.argv[1:]);sys.path.insert(0,str(legacy/'tools'));import fragile256
audit=json.loads((assets/'sources/docs/reconstruction/scitek/menu-audit.json').read_text());_,raw,entries=fragile256.read_archive(legacy/'_MA/_MA');records=[]
for rec in audit['records']:
 entry=next(e for e in entries if e.name==rec['preview']['file']);digest=hashlib.sha256(raw[entry.offset:entry.offset+entry.length]).hexdigest();assert digest==rec['preview']['sha256'];row=dict(id=rec['research_id'],index=rec['index'],tile=entry.name,tile_sha256=digest,videos=[])
 for key in ['preview_animation','information']:
  spec=rec[key]['source'];path=legacy/spec['directoryName']/spec['fileName'];digest=hashlib.sha256(path.read_bytes()).hexdigest();assert digest==rec[key]['source_sha256'];row['videos'].append(dict(role=key,directory=spec['directoryName'],file=spec['fileName'],sha256=digest))
 records.append(row)
out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(dict(scope='Current source-byte integrity for all36 research tiles,36 _MA colour films and36 _SCITEK information films. Complements prior actual-palette/decoded-frame/caption visual reviews; not a fresh original-codec decode or independent fidelity measurement.',records=records,counts=dict(subjects=len(records),tiles=len(records),videos=sum(len(x['videos']) for x in records))),indent=2)+'\n',encoding='utf-8');print('SCITEK_LEGACY_REFERENCES_VERIFIED',len(records))
