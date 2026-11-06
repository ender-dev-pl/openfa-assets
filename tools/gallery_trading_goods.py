"""Expose authored trading models and source-bound colour PNGs to the shared asset gallery."""
import hashlib,json
from pathlib import Path

def trading_records(root):
    coverage=root/'docs/trading-goods/coverage.json'
    if not coverage.is_file():return []
    report=root/'docs/trading-goods/gallery-validation.json'
    if not report.is_file():return []
    refined_path=root/'docs/trading-goods/refinement-validation.json'
    refined={e['legacy_stem']:e for e in json.loads(refined_path.read_text())['items']} if refined_path.exists() else {}
    manifest=json.loads(report.read_text());images={i['legacy_stem']:i for i in manifest['items']};rows=[]
    for item in json.loads(coverage.read_text())['items']:
        ident=item['legacy_stem'];image=images[ident];native=root/item['native'];png=root/image['image']
        assert hashlib.sha256(native.read_bytes()).hexdigest()==image['native_sha256'],ident
        assert hashlib.sha256(png.read_bytes()).hexdigest()==image['image_sha256'],ident
        rows.append(dict(id='trade:'+ident,name=item['name'],category='trading-goods',culture='shared',studies=[dict(stage='coloured-reconstruction',blend=item['native'],glb=item['static_glb'],image=image['image'],sha256=image['native_sha256'],animations=[])]))
        if refined:
            e=refined[ident]
            for key,hashkey in [('native','native_sha256'),('glb','glb_sha256'),('image','image_sha256')]:
                assert hashlib.sha256((root/e[key]).read_bytes()).hexdigest()==e[hashkey],(ident,key)
            rows[-1]['studies'].append(dict(stage='material-refined',blend=e['native'],glb=e['glb'],image=e['image'],sha256=e['native_sha256'],animations=[]))
    assert len(rows)==101 and len({r['id'] for r in rows})==101
    return rows
