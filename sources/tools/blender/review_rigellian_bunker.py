"""Check authored render framing and keep original reference pixels outside deliverables."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat

sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/strategic-bunker'
REF=REPO/'artifacts/rigellian-building-reference-study/RI06'


def main():
    meta=json.loads((ROOT/'model.json').read_text())
    gallery=Image.new('RGB',(1536,1536),(20,25,34));draw=ImageDraw.Draw(gallery)
    hashes={};margins={}
    for i,view in enumerate(meta['views']+['imported-glb-front-quarter']):
        path=ROOT/(view+'.png')
        with Image.open(path) as im:
            assert im.mode=='RGBA' and im.size==(900,900)
            assert im.getextrema()[3]==(0,255)
            x0,y0,x1,y1=im.getchannel('A').getbbox()
            margins[view]=min(x0,y0,900-x1,900-y1)
            assert margins[view]>=24,'Clipped view '+view
        gallery.paste(tile(path,(512,480)),(i%3*512,i//3*512+24))
        draw.text((i%3*512+12,i//3*512+6),view,fill='white')
        hashes[view]=hashlib.sha256(path.read_bytes()).hexdigest()
    gallery.save(ROOT/'gallery.png')
    sheet=Image.new('RGB',(1500,1000),(20,25,34));draw=ImageDraw.Draw(sheet)
    for i,(path,label) in enumerate([(REF/'surface-01.png','Legacy surface body'),
            (REF/'hologram/frames/020.png','Legacy hologram phase 20'),
            (REF/'hologram/frames/040.png','Legacy hologram phase 40')]):
        if i:
            with Image.open(path) as im:
                crop=REF/f'comparison-crop-{i}.png';im.crop((38,25,104,134)).save(crop)
            path=crop
        sheet.paste(tile(path,(500,420)),(i*500,50))
        draw.text((i*500+12,12),label+' (reference only)',fill='white')
    draw.text((12,475),'Hologram phases are not different spatial views; hidden geometry remains inferred.',fill='white')
    for i,view in enumerate(['front-quarter','front','imported-glb-front-quarter']):
        sheet.paste(tile(ROOT/(view+'.png'),(500,450)),(i*500,535))
        draw.text((i*500+12,510),'Authored '+view,fill='white')
    sheet.save(REF/'comparison.png')
    with Image.open(ROOT/'front-quarter.png') as native,Image.open(ROOT/'imported-glb-front-quarter.png') as imported:
        difference=ImageChops.difference(native,imported)
        mask=native.getchannel('A').point(lambda value:255 if value else 0)
        mean=ImageStat.Stat(difference,mask).mean
        alpha=difference.getchannel('A');alpha_count=sum(value!=0 for value in alpha.tobytes());alpha_max=alpha.getextrema()[1]
        native_mask=native.getchannel('A').point(lambda value:255 if value>=128 else 0)
        imported_mask=imported.getchannel('A').point(lambda value:255 if value>=128 else 0)
        assert ImageChops.difference(native_mask,imported_mask).getbbox() is None,'Imported binary silhouette differs'
        assert max(mean[:3])<1.5 and alpha_count<=4 and alpha_max<=4,'Imported render differs materially'
    report=dict(issue=975,revision=meta['revision'],blend_sha256=meta['blend_sha256'],view_hashes=hashes,
        alpha=True,margins=margins,reference_comparison='artifacts/rigellian-building-reference-study/RI06/comparison.png',
        native_glb_foreground_mean_rgba_difference=mean,
        native_glb_alpha_difference=dict(pixels=alpha_count,maximum=alpha_max,bounds=alpha.getbbox(),binary_silhouette_equal=True,
            tolerance='At most four antialiased edge pixels, each at most 4/255 alpha; threshold-128 silhouette must match exactly'),
        final_visual_acceptance=False)
    (ROOT/'render-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RIGELLIAN_BUNKER_RENDER_REVIEW_OK',len(hashes))


if __name__=='__main__': main()
