"""Verify category composition, monochrome output and runtime rasters."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageChops,ImageStat,ImageFilter,ImageOps
out=Path(sys.argv[1]);proof=json.loads((out/'provenance.json').read_text());checks={}
native=Image.open(out/'native.png').convert('RGBA');reload=Image.open(out/'reload.png').convert('RGBA');assert not ImageChops.difference(native,reload).getbbox(alpha_only=False)
for subject in [{'subject':None}]+proof['subjects']:
 key=subject['subject'];a=Image.open(out/((key if key else 'native')+'.png')).convert('RGBA');b=Image.open(out/(('imported-'+key if key else 'imported')+'.png')).convert('RGBA');assert a.size==b.size==(800,640)
 aa=a.getchannel('A').point(lambda v:255 if v>128 else 0);bb=b.getchannel('A').point(lambda v:255 if v>128 else 0)
 inter=sum(v>0 for v in ImageChops.darker(aa,bb).tobytes());union=sum(v>0 for v in ImageChops.lighter(aa,bb).tobytes());iou=inter/union;assert iou>.985,(key,iou)
 mean=ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean;assert max(mean)<8,(key,mean)
 pixels=a.tobytes();assert max(max(pixels[i:i+3])-min(pixels[i:i+3]) for i in range(0,len(pixels),4))<=1,'Only1LSB of view-transform quantisation is allowed'
 if key:
  box=aa.getbbox();x0,y0,x1,y1=subject['target_box'];assert box and box[0]>=10*x0-3 and box[1]>=10*y0-3 and box[2]<=10*x1+3 and box[3]<=10*y1+3,(key,box,subject['target_box'])
  assert sum(v>0 for v in aa.tobytes())>2000,(key,'empty subject')
 checks[key or 'composition']=dict(native_import_alpha_iou=iou,mean_rgb_difference=mean,bbox=list(aa.getbbox()))
alpha=native.getchannel('A');native=ImageOps.grayscale(native).convert('RGBA');native.putalpha(alpha)
native.resize((80,64),Image.Resampling.LANCZOS).save(out/'category-native.png');native.resize((320,256),Image.Resampling.LANCZOS).save(out/'category-4x.png')
for name,size in [('category-native.png',(80,64)),('category-4x.png',(320,256))]:
 im=Image.open(out/name);pixels=im.convert('RGBA').tobytes();assert all(pixels[i]==pixels[i+1]==pixels[i+2] for i in range(0,len(pixels),4));assert im.size==size;assert im.getchannel('A').getextrema()==(0,255)
(out/'raster-verification.json').write_text(json.dumps(dict(variants=checks,saved_reload_pixels_identical=True,monochrome=True,raw_view_transform_channel_tolerance=1,derived_exact_monochrome=True,native_canvas=[80,64],hires_canvas=[320,256],derived_sha256={n:hashlib.sha256((out/n).read_bytes()).hexdigest() for n in ['category-native.png','category-4x.png']}),indent=2)+'\n')
print('SCITEK_CATEGORY_RASTERS_VERIFIED',min(x['native_import_alpha_iou'] for x in checks.values()))
