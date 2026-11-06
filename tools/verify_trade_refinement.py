"""Check refined delivery hashes, PBR evidence and both gallery iterations."""
import hashlib,json
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((root/'docs/trading-goods/refinement-validation.json').read_text())
rows={r['id']:r for r in json.loads((root/'gallery/catalogue.json').read_text())}
coverage=json.loads((root/'docs/trading-goods/coverage.json').read_text());assert coverage['refined_gallery_png_count']==101
items={i['legacy_stem']:i for i in coverage['items']}
tools=root/'sources/tools/trading-goods/refining'
assert len(manifest['items'])==manifest['count']==101
for e in manifest['items']:
 ident=e['legacy_stem'];review=manifest['visual_review']['reviewed_images'][ident];assert review['native_sha256']==e['native_sha256'] and review['image_sha256']==e['render_output_sha256'];row=rows['trade:'+ident];assert len(row['studies'])==2
 selected=items[ident]['refined_variant'];assert selected['native']==e['native'] and selected['glb']==e['glb'] and selected['image']==e['image'] and selected['status']=='material_refined_png_verified'
 initial,refined=row['studies'];assert initial['stage']=='coloured-reconstruction' and refined['stage']=='material-refined'
 for key,hkey in [('native','native_sha256'),('glb','glb_sha256'),('image','image_sha256')]:assert sha(root/e[key])==e[hkey],(ident,key)
 assert sha(root/initial['blend'])==e['baseline_native_sha256'],ident
 for prefix in ['geometry','revision']:
  if prefix+'_builder' in e:
   assert sha(root/e[prefix+'_builder'])==e[prefix+'_builder_sha256'] and sha(root/e['prior_refined_native'])==e['prior_refined_native_sha256']
 assert sha(tools/'refine.py')==e['builder_sha256'] and sha(root/e.get('renderer','sources/tools/trading-goods/refining/render.py'))==e['renderer_sha256']
 assert refined['blend']==e['native'] and refined['glb']==e['glb'] and refined['image']==e['image']
 folder=(root/e['native']).parent
 runtime=json.loads((folder/'runtime-validation.json').read_text())
 assert runtime['independent_glb_import'] and runtime['base_colours_roundtrip_verified'] and runtime['native_sha256']==e['native_sha256'] and runtime['glb_sha256']==e['glb_sha256']
 with Image.open(root/e['image']) as im:
  im.load();assert im.size==(1024,768) and im.mode=='RGBA' and not im.getexif()
  alpha=im.getchannel('A');assert alpha.getextrema()==(0,255)
  b=alpha.point(lambda p:255 if p>245 else 0).getbbox();assert b and min(b[0],b[1],1024-b[2],768-b[3])>4,(ident,b)
assert set(manifest['visual_review']['reviewed_items'])=={f'TI{i:03d}' for i in range(1,102)}
print('REFINED_TRADING_GOODS_VERIFIED: 101 natives, independent GLBs, source-bound RGBA images and preserved gallery comparisons')
