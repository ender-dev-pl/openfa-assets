"""Verify every delivered solid/wire/highlight import, not just one representative."""
import sys,json,hashlib
from pathlib import Path
from PIL import Image,ImageChops
o=Path(sys.argv[1]);m=json.loads((o/'model.json').read_text());names=['solid','wireframe']+['highlight-'+p['component'] for p in m['phases']];proof={}
assert len(m['phases'])==3 and m['information_timeline_frames']==423
for i,p in enumerate(m['phases']):assert (p['first_legacy_frame'],p['last_legacy_frame'])==(29+141*i,139+141*i)
for name in names:
    x=Image.open(o/(name+'.png')).convert('RGBA');y=Image.open(o/('imported-'+name+'.png')).convert('RGBA');assert x.size==y.size
    a=x.getchannel('A').point(lambda v:255 if v>127 else 0);b=y.getchannel('A').point(lambda v:255 if v>127 else 0)
    inter=sum(v>0 for v in ImageChops.darker(a,b).tobytes());union=sum(v>0 for v in ImageChops.lighter(a,b).tobytes());assert inter/union>.98,(name,inter/union)
    if name.startswith('highlight'):
        raw=x.tobytes();assert sum(raw[i]>2*raw[i+1] and raw[i]>100 and raw[i+3]>127 for i in range(0,len(raw),4))>30
        if name=='highlight-cooling-cylinders':
            mask=Image.frombytes('L',x.size,bytes(255 if raw[i]>raw[i+1]*2 and raw[i]>100 and raw[i+3]>127 else 0 for i in range(0,len(raw),4)))
            bounds=mask.getbbox();assert bounds and bounds[3]-bounds[1]>x.height*.2 and bounds[2]-bounds[0]>x.width*.15,'Coolant bodies must remain visible, not only their top valves'
    proof[name]={'native_import_silhouette_iou':inter/union}
assert ImageChops.difference(Image.open(o/'solid.png'),Image.open(o/'reload-solid.png')).getbbox() is None
proof['source_hashes']=json.loads((o/'source-hashes.json').read_text());proof['files']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in o.iterdir() if p.suffix in ['.blend','.glb','.png']};(o/'verification.json').write_text(json.dumps(proof,indent=2)+'\n',newline='\n');print('SCITEK_DEVICE_VERIFIED',m['id'],len(names),'variants')
