"""Verify all trade PNGs, source-bound provenance and shared gallery integration."""
import argparse,hashlib,json,re
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--baseline',type=Path);a=ap.parse_args();root=a.repo.resolve();coverage=json.loads((root/'docs/trading-goods/coverage.json').read_text());manifest=json.loads((root/'docs/trading-goods/gallery-validation.json').read_text());catalogue=json.loads((root/'gallery/catalogue.json').read_text());goods=[r for r in catalogue if r['category']=='trading-goods'];assert len(goods)==101;assert {r['id'] for r in goods}=={f'trade:TI{i:03d}' for i in range(1,102)};assert len(manifest['items'])==101
for item,evidence,row in zip(coverage['items'],manifest['items'],goods):
 assert row['id']=='trade:'+item['legacy_stem']== 'trade:'+evidence['legacy_stem'];assert row['studies'][0]['blend']==item['native'] and row['studies'][0]['glb']==item['static_glb'];image=root/evidence['image'];assert hashlib.sha256(image.read_bytes()).hexdigest()==evidence['image_sha256'];assert hashlib.sha256((root/item['native']).read_bytes()).hexdigest()==evidence['native_sha256'];assert evidence['renderer_sha256']==hashlib.sha256((root/'sources/tools/trading-goods/render_gallery.py').read_bytes()).hexdigest()
 with Image.open(image) as im:
  im.load();assert im.mode=='RGBA' and im.size==(768,576);alpha=im.getchannel('A');bbox=alpha.getbbox();assert bbox and alpha.getextrema()==(0,255);assert min(bbox[0],bbox[1],768-bbox[2],576-bbox[3])>4,(row['id'],bbox)
 assert row['studies'][0]['image']==evidence['image'];assert item['gallery_png']['status']=='rendered';assert item['gallery_png']['output']==evidence['image'];assert not row['studies'][0]['animations']
page=(root/'gallery/index.html').read_text();assert page.count('data-type="trading-goods"')==101;assert '<option value="trading-goods">Trading goods</option>' in page;assert 'trading-goods-shared.md' in (root/'gallery/README.md').read_text();assert (root/'gallery/trading-goods-shared.md').read_text().count('## ')==101
if a.baseline:
 before=json.loads(a.baseline.read_text());assert [r for r in catalogue if r['category']!='trading-goods']==before
print('TRADING_GALLERY_VERIFIED: 101 RGBA PNGs, current native/render hashes, unclipped content, 101 linked gallery cards')
