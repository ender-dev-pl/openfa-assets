"""Review every RI10 authored descriptor-pose render and make reference-only comparisons."""
import hashlib
import json
import sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/buildings/rigellian/ground-deck'
OUT=ROOT/'states'
REF=REPO/'artifacts/rigellian-building-reference-study/RI10'


def sha(path):
    data=path.read_bytes()
    if path.suffix in ['.json','.py']: data=data.replace(b'\r\n',b'\n')
    return hashlib.sha256(data).hexdigest()


def main():
    index=OUT/'state-exports.json';manifest=json.loads(index.read_text());meta=json.loads((ROOT/'model.json').read_text())
    assert manifest['source_blend_sha256']==meta['blend_sha256']==sha(ROOT/'model.blend')
    assert manifest['source_glb_sha256']==meta['glb_sha256']==sha(ROOT/'model.glb')
    assert [item['descriptor'] for item in manifest['states']]==list(range(2,18))
    gallery=Image.new('RGB',(2048,2048),(20,25,34));draw=ImageDraw.Draw(gallery);reviews=[]
    for i,item in enumerate(manifest['exports']):
        for key in ['glb','native_render','imported_render']: assert sha(OUT/item[key])==item[key+'_sha256']
        with Image.open(OUT/item['native_render']) as native,Image.open(OUT/item['imported_render']) as imported:
            margins=[]
            for image in [native,imported]:
                assert image.mode=='RGBA' and image.size==(900,900) and image.getextrema()[3]==(0,255)
                left,top,right,bottom=image.getchannel('A').getbbox();margin=min(left,top,900-right,900-bottom)
                assert margin>=24;margins.append(margin)
            difference=ImageChops.difference(native,imported);mask=native.getchannel('A').point(lambda x:255 if x else 0)
            mean=ImageStat.Stat(difference,mask).mean;alpha=difference.getchannel('A')
            count=sum(value!=0 for value in alpha.tobytes());maximum=alpha.getextrema()[1]
            a=native.getchannel('A').point(lambda x:255 if x>=128 else 0);b=imported.getchannel('A').point(lambda x:255 if x>=128 else 0)
            assert ImageChops.difference(a,b).getbbox() is None,('Binary silhouette changed',item['key'])
            assert max(mean[:3])<1.5 and count<=4 and maximum<=4,('Native/imported pose render mismatch',item['key'],mean,count,maximum)
        red_pixels=[0,0]
        with Image.open(OUT/item['imported_render']) as image:
            for pixel_index,(r,g,b,a) in enumerate(image.get_flattened_data()):
                if a>=128 and r>80 and r>g*1.7 and r>b*1.6:
                    red_pixels[int(pixel_index%image.width>=image.width/2)]+=1
        if item['key']=='covers-stowed': assert min(red_pixels)>=8,'Both red interior fittings must be visible'
        if item['key']=='descriptor-02': assert red_pixels==[0,0],'Closed covers must mask red interior fittings'
        gallery.paste(tile(OUT/item['imported_render'],(512,470)),(i%4*512,i//4*512+32))
        draw.text((i%4*512+12,i//4*512+10),item['key']+' | '+str(item['descriptors']),fill='white')
        reviews.append(dict(key=item['key'],red_pixels_by_image_half=red_pixels,margins=margins,mean_rgba_difference=mean,alpha_changed_pixels=count,
            maximum_alpha_difference=maximum,binary_silhouette_equal=True))
    gallery.save(OUT/'gallery.png')
    comparison=Image.new('RGB',(2048,2048),(20,25,34));draw=ImageDraw.Draw(comparison)
    for i,state in enumerate(manifest['states']):
        descriptor=state['descriptor'];item=next(x for x in manifest['exports'] if descriptor in x['descriptors'])
        source=REF/(f'layer-combination-{descriptor:02}.png' if descriptor not in [15,16] else 'surface-01.png')
        x=i%4*512;y=i//4*512
        draw.text((x+10,y+8),f'Descriptor {descriptor}: reference / authored full assembly',fill='white')
        if descriptor>=15: draw.text((x+10,y+27),'Empty cover layer' if descriptor<17 else 'Mixed lower layer: composition pending',fill='white')
        comparison.paste(tile(source,(256,440)),(x,y+55));comparison.paste(tile(OUT/item['imported_render'],(256,440)),(x+256,y+55))
    comparison.save(REF/'descriptor-pose-comparison.png')
    report=dict(issue=980,id=manifest['id'],revision=manifest['revision'],state_index_sha256=sha(index),reviewer_sha256=sha(Path(__file__)),
        exports=len(reviews),descriptors=16,reviews=reviews,gallery_sha256=sha(OUT/'gallery.png'),
        reference_comparison='artifacts/rigellian-building-reference-study/RI10/descriptor-pose-comparison.png',
        final_visual_acceptance=False,composition_calibration=False)
    (OUT/'render-review.json').write_text(json.dumps(report,indent=2)+'\n');print('RI10_DESCRIPTOR_RENDER_REVIEW_OK',len(reviews))


if __name__=='__main__': main()
