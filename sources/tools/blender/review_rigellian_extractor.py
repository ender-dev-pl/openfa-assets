"""Check authored render framing and keep original reference pixels outside deliverables."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat

sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/extractor'
REF=REPO/'artifacts/rigellian-building-reference-study/RI20'


def main():
    meta=json.loads((ROOT/'model.json').read_text())
    gallery=Image.new('RGB',(1536,2048),(20,25,34));draw=ImageDraw.Draw(gallery)
    hashes={};margins={}
    for i,view in enumerate(meta['views']+['imported-glb-front-quarter','front-detail','imported-glb-front-detail','base-detail','imported-glb-base-detail']):
        path=ROOT/(view+'.png')
        with Image.open(path) as im:
            assert im.mode=='RGBA' and im.size==(900,900)
            alpha_range=im.getextrema()[3]
            assert alpha_range[1]==255 and ('-detail' in view or alpha_range[0]==0),'Whole-object views need transparent background; macro crops may fill the frame'
            x0,y0,x1,y1=im.getchannel('A').getbbox()
            margins[view]=min(x0,y0,900-x1,900-y1)
            if '-detail' not in view: assert margins[view]>=24,'Clipped view '+view
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
                crop=REF/f'comparison-crop-{i}.png';im.crop((42,36,104,126)).save(crop)
            path=crop
        sheet.paste(tile(path,(500,420)),(i*500,50))
        draw.text((i*500+12,12),label+' (reference only)',fill='white')
    draw.text((12,475),'Hologram phases are not different spatial views; hidden geometry remains inferred.',fill='white')
    for i,view in enumerate(['front-quarter','front','imported-glb-front-quarter']):
        sheet.paste(tile(ROOT/(view+'.png'),(500,450)),(i*500,535))
        draw.text((i*500+12,510),'Authored '+view,fill='white')
    sheet.save(REF/'comparison.png')
    differences={}
    for native_name,imported_name in [('front-quarter','imported-glb-front-quarter'),('front-detail','imported-glb-front-detail'),('base-detail','imported-glb-base-detail')]:
        with Image.open(ROOT/(native_name+'.png')) as native,Image.open(ROOT/(imported_name+'.png')) as imported:
            difference=ImageChops.difference(native,imported)
            mask=native.getchannel('A').point(lambda value:255 if value else 0)
            mean=ImageStat.Stat(difference,mask).mean
            alpha=difference.getchannel('A');alpha_count=sum(value!=0 for value in alpha.tobytes());alpha_max=alpha.getextrema()[1]
            native_mask=native.getchannel('A').point(lambda value:255 if value>=128 else 0)
            imported_mask=imported.getchannel('A').point(lambda value:255 if value>=128 else 0)
            assert ImageChops.difference(native_mask,imported_mask).getbbox() is None,'Imported binary silhouette differs'
            assert max(mean[:3])<1.5 and alpha_count<=4 and alpha_max<=4,'Imported render differs materially'
        differences[native_name]=dict(mean_rgba=mean,alpha_pixels=alpha_count,alpha_maximum=alpha_max,alpha_bounds=alpha.getbbox(),binary_silhouette_equal=True)
    report=dict(issue=992,reviewer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),revision=meta['revision'],blend_sha256=meta['blend_sha256'],view_hashes=hashes,
        alpha=True,margins=margins,detail_views_intentionally_crop_body=True,matched_view_comparisons=differences,reference_comparison='artifacts/rigellian-building-reference-study/RI20/comparison.png',
        native_glb_foreground_mean_rgba_difference=differences['front-quarter']['mean_rgba'],
        native_glb_alpha_difference=dict(pixels=differences['front-quarter']['alpha_pixels'],maximum=differences['front-quarter']['alpha_maximum'],bounds=differences['front-quarter']['alpha_bounds'],binary_silhouette_equal=True,
            tolerance='At most four antialiased edge pixels, each at most 4/255 alpha; threshold-128 silhouette must match exactly'),
        final_visual_acceptance=False)
    (ROOT/'render-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('RIGELLIAN_EXTRACTOR_RENDER_REVIEW_OK',len(hashes))


if __name__=='__main__': main()
