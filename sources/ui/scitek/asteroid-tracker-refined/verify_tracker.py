"""Verify actual native/imported renders and named Sci-Tek component coverage."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();o=a.output
proof={}
for name in ['solid','wireframe','highlight-user-interface','highlight-cooling-fans','highlight-data-storage','highlight-calibration-device']:
    x=Image.open(o/(name+'.png')).convert('RGBA');y=Image.open(o/('imported-'+name+'.png')).convert('RGBA')
    assert x.size==y.size
    aa=x.getchannel('A').point(lambda v:255 if v>127 else 0);bb=y.getchannel('A').point(lambda v:255 if v>127 else 0)
    intersection=sum(v>0 for v in ImageChops.darker(aa,bb).tobytes());union=sum(v>0 for v in ImageChops.lighter(aa,bb).tobytes())
    assert union>1000;assert intersection/union>.98,(name,intersection/union)
    if name.startswith('highlight'):
        data=x.tobytes();red=sum(data[i]>data[i+1]*2 and data[i]>100 and data[i+3]>128 for i in range(0,len(data),4));assert red>30,name
    proof[name]={'native_import_silhouette_iou':intersection/union}
assert ImageChops.difference(Image.open(o/'solid.png'),Image.open(o/'reload-solid.png')).getbbox() is None
m=json.loads((o/'model.json').read_text());assert len(m['phases'])==4 and set(m['components'])=={'chassis','user-interface','cooling-fans','data-storage','calibration-device'}
proof['source_hashes']=json.loads((o/'source-hashes.json').read_text());proof['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.suffix in ['.blend','.glb','.png']}
(o/'verification.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print('TRACKER_VERIFIED',len(proof['files']),'files')
