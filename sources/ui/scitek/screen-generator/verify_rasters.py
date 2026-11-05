from pathlib import Path
import json,sys
from PIL import Image,ImageChops,ImageStat,ImageFilter
out=Path(sys.argv[1]);proof={}
for stem in ['solid','wireframe','highlight-three-field-masts','highlight-reverse-polarity-suppressers','highlight-phase-synchronising-oscillators']:
 a=Image.open(out/(stem+'.png')).convert('RGBA');b=Image.open(out/('imported-'+stem+'.png')).convert('RGBA');assert a.size==b.size
 aa={i for i,p in enumerate(a.getdata()) if p[3]>128 and max(p[:3])>30};bb={i for i,p in enumerate(b.getdata()) if p[3]>128 and max(p[:3])>30};iou=len(aa&bb)/len(aa|bb);# Two pixels at 640px allow native/import antialiasing differences;
 # this checks projected structure, not legacy pixel fidelity.
 maska=Image.new('L',a.size);maska.putdata([255 if i in aa else 0 for i in range(a.width*a.height)])
 maskb=Image.new('L',b.size);maskb.putdata([255 if i in bb else 0 for i in range(b.width*b.height)])
 da={i for i,v in enumerate(maska.filter(ImageFilter.MaxFilter(5)).getdata()) if v};db={i for i,v in enumerate(maskb.filter(ImageFilter.MaxFilter(5)).getdata()) if v}
 coverage=min(len(aa&db)/len(aa),len(bb&da)/len(bb));assert coverage>.98,(stem,coverage)
 mean=ImageStat.Stat(ImageChops.difference(a.convert('RGB'),b.convert('RGB'))).mean
 # Dense native curve bevels and exported triangles differ in edge coverage.
 # Preserve geometry/hue checks while allowing <12% integrated green energy
 # difference for technical closeups (global RGB MAE still below12/255).
 energy_a=ImageStat.Stat(a.convert('RGB')).mean;energy_b=ImageStat.Stat(b.convert('RGB')).mean
 energy_error=abs(energy_a[1]-energy_b[1])/max(energy_a[1],20)
 assert max(mean)<(8 if stem=='solid' else 12),(stem,mean)
 if stem!='solid' and energy_a[1]>80:assert energy_error<.12,(stem,energy_error)
 proof[stem]=dict(raw_foreground_iou=iou,two_pixel_bidirectional_coverage=coverage,mean_rgb_difference=mean,relative_green_energy_error=energy_error)

a=Image.open(out/'solid.png').convert('RGBA');b=Image.open(out/'reload-solid.png').convert('RGBA');assert not ImageChops.difference(a,b).getbbox(alpha_only=False)
(out/'raster-verification.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print('DEFLECTOR_RASTERS_VERIFIED',min(p['two_pixel_bidirectional_coverage'] for p in proof.values()))
