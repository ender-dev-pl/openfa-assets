"""Expose authored trading models and source-bound colour PNGs to the shared asset gallery."""
import hashlib,json
from pathlib import Path

def trading_records(root):
    coverage=root/'docs/trading-goods/coverage.json'
    if not coverage.is_file():return []
    report=root/'docs/trading-goods/gallery-validation.json'
    if not report.is_file():return []
    manifest=json.loads(report.read_text());images={i['legacy_stem']:i for i in manifest['items']};rows=[]
    for item in json.loads(coverage.read_text())['items']:
        ident=item['legacy_stem'];image=images[ident];native=root/item['native'];png=root/image['image']
        assert hashlib.sha256(native.read_bytes()).hexdigest()==image['native_sha256'],ident
        assert hashlib.sha256(png.read_bytes()).hexdigest()==image['image_sha256'],ident
        rows.append(dict(id='trade:'+ident,name=item['name'],category='trading-goods',culture='shared',studies=[dict(stage='coloured-reconstruction',blend=item['native'],glb=item['static_glb'],image=image['image'],sha256=image['native_sha256'],animations=[])]))
    assert len(rows)==101 and len({r['id'] for r in rows})==101
    return rows
