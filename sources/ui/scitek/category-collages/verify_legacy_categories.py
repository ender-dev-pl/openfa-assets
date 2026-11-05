"""Optional six-frame category decode check using the runtime BUTTONS palette."""
from pathlib import Path
import sys,json,hashlib
from PIL import Image,ImageChops
legacy=Path(sys.argv[1]).resolve();cache=Path(sys.argv[2]).resolve();out=Path(sys.argv[3]).resolve()
sys.path.insert(0,str(legacy/'tools'));import fragile256
source=legacy/'_MS/SCITEKC.256';buttons=legacy/'_MS/BUTTONS.256'
data,frames,_,_=fragile256.read_sprites(source);_,palette=fragile256.find_palette(buttons.read_bytes(),32);assert palette and len(frames)==6
results=[]
for f in frames:
 pixels=fragile256.decode_sprite(data[32+f.stream_offset:32+f.stream_offset+f.stream_length],f.width,f.height)
 im=Image.new('P',(f.canvas_width,f.canvas_height),0);im.putpalette(fragile256.palette_to_png(palette));im.paste(Image.frombytes('P',(f.width,f.height),pixels),(f.x,f.y));im.info['transparency']=0;im=im.convert('RGBA')
 cached=cache/f'SCITEKC-{f.index:03}.png';assert not ImageChops.difference(im,Image.open(cached).convert('RGBA')).getbbox(alpha_only=False)
 results.append(dict(frame=f.index,canvas=list(im.size),occupied_box=list(im.getchannel('A').getbbox()),cached_sha256=hashlib.sha256(cached.read_bytes()).hexdigest(),fresh_decoded_rgba_sha256=hashlib.sha256(im.tobytes()).hexdigest()))
out.write_text(json.dumps(dict(source='_MS/SCITEKC.256',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),palette='_MS/BUTTONS.256',palette_source_sha256=hashlib.sha256(buttons.read_bytes()).hexdigest(),decoder_sha256=hashlib.sha256((legacy/'tools/fragile256.py').read_bytes()).hexdigest(),frames=results,source_pixels_published=False),indent=2)+'\n')
print('LEGACY_CATEGORIES_VERIFIED',len(results))
