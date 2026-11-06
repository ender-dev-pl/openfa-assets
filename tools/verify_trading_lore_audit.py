"""Check lore-audit coverage and evidence freshness; do not infer semantic acceptance."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--game-repo',type=Path);a=ap.parse_args();root=Path(__file__).resolve().parents[1];d=json.loads((root/'docs/trading-goods/lore-audit.json').read_text());m=json.loads((root/'docs/trading-goods/refinement-validation.json').read_text());images={e['legacy_stem']:e for e in m['items']};sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert d['count']==len(d['entries'])==len(images)==101;assert d['image_manifest_sha256']==sha(root/'docs/trading-goods/refinement-validation.json');assert {e['legacy_stem'] for e in d['entries']}==set(images)
assert d['counts']==dict(Counter(e['assessment'] for e in d['entries']))
if d.get('schema_version',1)>=2:
 assert d['manual_notes_sha256']==sha(root/'docs/trading-goods/lore-review-notes.tsv')
 inspection_path=root/'docs/trading-goods/lore-corrections-validation.json'
 assert d['correction_inspections_sha256']==sha(inspection_path)
 inspections=json.loads(inspection_path.read_text())
 assert len(inspections['items'])==inspections['count']==7
 assert inspections['inspector_sha256']==sha(root/inspections['inspector'])
 for row in inspections['items']:assert row['native_sha256']==images[row['legacy_stem']]['native_sha256']==sha(root/row['native'])
strings=json.loads((a.game_repo/d['lore_source']['path']).read_text())['strings'] if a.game_repo else None
for e in d['entries']:
 image=images[e['legacy_stem']];assert e['assessment'] in d['assessment_meanings'] and e['priority'] in ['P1','P2','P3'];assert e['lore_requirement'] and e['current_finding'] and e['next_action']
 for key in ['native','image']:
  assert e[key]==image[key] and e[key+'_sha256']==image[key+'_sha256']==sha(root/e[key]),(e['legacy_stem'],key)
 if strings is not None:assert hashlib.sha256(strings[e['description_key']].encode()).hexdigest()==e['description_sha256'],e['legacy_stem']
print('LORE_AUDIT_EVIDENCE_CURRENT 101 items; semantic judgements are manual; open findings preserved')
