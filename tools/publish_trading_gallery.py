"""Validate completed render journals and install authored colour PNGs into the asset gallery."""
import argparse,hashlib,json,shutil,struct
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser();ap.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--renders',type=Path,required=True);a=ap.parse_args();root=a.repo.resolve();coverage_path=root/'docs/trading-goods/coverage.json';coverage=json.loads(coverage_path.read_text());items=[];renderer=root/'sources/tools/trading-goods/render_gallery.py';renderer_sha=hashlib.sha256(renderer.read_bytes()).hexdigest()
for item in coverage['items']:
 ident=item['legacy_stem'];png=a.renders/(ident+'.png');journal=json.loads((a.renders/(ident+'.json')).read_text());assert journal['legacy_stem']==ident and journal['item_id']==item['id'];assert journal['renderer_sha256']==renderer_sha;assert journal['model_source_unchanged'];assert hashlib.sha256((root/item['native']).read_bytes()).hexdigest()==journal['native_sha256'];assert hashlib.sha256(png.read_bytes()).hexdigest()==journal['image_sha256']
 with Image.open(png) as im:
  im.load();assert im.size==(768,576) and im.mode=='RGBA';alpha=im.getchannel('A');bbox=alpha.getbbox();assert bbox and alpha.getextrema()==(0,255);assert min(bbox[0],bbox[1],768-bbox[2],576-bbox[3])>4,(ident,bbox)
 out=root/'gallery/media/docs/assets/reconstruction/trading-goods'/ident/'front-quarter.png';out.parent.mkdir(parents=True,exist_ok=True);raw=png.read_bytes();clean=raw[:8];pos=8
 while pos<len(raw):
  length=struct.unpack_from('>I',raw,pos)[0];kind=raw[pos+4:pos+8];chunk=raw[pos:pos+12+length]
  if kind in {b'IHDR',b'PLTE',b'tRNS',b'IDAT',b'IEND',b'sRGB',b'gAMA',b'cHRM',b'pHYs'}:clean+=chunk
  pos+=12+length
 out.write_bytes(clean)
 with Image.open(png) as before, Image.open(out) as after:assert before.tobytes()==after.tobytes()
 entry={**journal,'render_output_sha256':journal['image_sha256'],'image_sha256':hashlib.sha256(clean).hexdigest(),'png_metadata_removed':True,'image':out.relative_to(root).as_posix()};items.append(entry);item['gallery_png']=dict(status='rendered',resolution=[768,576],transparent=True,output=entry['image'])
assert len(items)==101;coverage['gallery_png_delivery']='101 colour PNGs rendered and integrated into the asset gallery';coverage['gallery_png_count']=101;coverage_path.write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+'\n');(root/'docs/trading-goods/gallery-validation.json').write_text(json.dumps(dict(count=101,resolution=[768,576],samples=32,transparent_background=True,model_sources_preserved=True,legacy_ui_images='separate scope; gallery PNGs are not legacy-size UI outputs',items=items),indent=2)+'\n');print('GALLERY_PNGS_INSTALLED 101')
