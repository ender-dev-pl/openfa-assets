"""Review first Type 5 renders and compare matched-camera GLB pixels."""
import hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile
REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/ships/mauna/surveillance-craft-type-5'
REF=REPO/'artifacts/issue-1023-surveillance-craft-type-5'


def main():
    meta=json.loads((ROOT/'model.json').read_text());names=meta['views']+['hull-detail','imported-glb-front-quarter','imported-glb-hull-detail']
    gallery=Image.new('RGB',(1536,1536),(20,25,34));draw=ImageDraw.Draw(gallery);hashes={};margins={}
    for i,name in enumerate(names):
        path=ROOT/(name+'.png')
        with Image.open(path) as im:
            assert im.mode=='RGBA' and im.size==(900,900);bounds=im.getchannel('A').getbbox();assert bounds and im.getextrema()[3][1]==255
            margin=min(bounds[0],bounds[1],900-bounds[2],900-bounds[3]);margins[name]=margin
            if 'detail' not in name:assert margin>=24 and im.getextrema()[3][0]==0
        gallery.paste(tile(path,(512,480)),(i%3*512,i//3*512+26));draw.text((i%3*512+10,i//3*512+6),name,fill='white');hashes[name]=hashlib.sha256(path.read_bytes()).hexdigest()
    gallery.save(ROOT/'gallery.png');comparisons={}
    for a,b in [('front-quarter','imported-glb-front-quarter'),('hull-detail','imported-glb-hull-detail')]:
        with Image.open(ROOT/(a+'.png')) as native,Image.open(ROOT/(b+'.png')) as imported:
            delta=ImageChops.difference(native,imported);alpha=delta.getchannel('A');count=sum(v!=0 for v in alpha.tobytes());maximum=alpha.getextrema()[1]
            mean=ImageStat.Stat(delta,native.getchannel('A').point(lambda v:255 if v else 0)).mean
            mask=ImageChops.difference(native.getchannel('A').point(lambda v:255 if v>=128 else 0),imported.getchannel('A').point(lambda v:255 if v>=128 else 0));assert mask.getbbox() is None,'Binary silhouette mismatch'
            assert max(mean[:3])<1.5 and count<=4 and maximum<=4,'Export render mismatch'
            comparisons[a]=dict(mean_rgba=mean,alpha_pixels=count,alpha_maximum=maximum,binary_silhouette_equal=True)
    REF.mkdir(parents=True,exist_ok=True);reference=json.loads((REPO/'docs/reconstruction/models/ship-reference-index.json').read_text());record=next(r for r in reference['ships'] if r['id']=='openfa:ship/mauna/surveillance-craft-type-5')
    # Small heading sprites are the only located visual reference. Do not invent a large rotation source.
    legacy=REPO.parent/'legacy/_S/png';metadata_path=legacy/'MN0A.json';assert hashlib.sha256(metadata_path.read_bytes()).hexdigest()==record['decoded_metadata_sha256']
    metadata=json.loads(metadata_path.read_text());assert metadata['palette']['embedded'];assert not record['runtime_even_heading_only'] and len(metadata['frames'])==32 and all(m['width']>0 and m['height']>0 for m in metadata['frames']);reference_hashes={}
    for sample in record['frames']: assert hashlib.sha256((legacy/sample['png']).read_bytes()).hexdigest()==sample['png_sha256']
    sheet=Image.new('RGB',(1600,1320),(20,25,34));draw=ImageDraw.Draw(sheet)
    for i,index in enumerate([0,4,8,12,16,20,24,28]):
        m=metadata['frames'][index];path=legacy/m['png'];reference_hashes[str(index)]=hashlib.sha256(path.read_bytes()).hexdigest()
        # The canonical index binds 0/8/16/24; original archive/metadata bind other decoded headings.
        with Image.open(path) as im:
            crop=REF/('heading-'+str(index)+'.png');im.crop((m['x'],m['y'],m['x']+m['width'],m['y']+m['height'])).save(crop)
        sheet.paste(tile(crop,(400,290)),(i%4*400,i//4*320+30));draw.text((i%4*400+10,i//4*320+8),'Original MN0A heading '+str(index)+'; small surface sprite',fill='white')
    draw.text((8,650),'No catalogue video located; all depth and fine detail are independent interpretations.',fill='white')
    for i,name in enumerate(['front-quarter','rear-quarter','top','underside']):
        sheet.paste(tile(ROOT/(name+'.png'),(400,450)),(i*400,710));draw.text((i*400+10,680),'First authored '+name,fill='white')
    sheet.save(REF/'comparison.png')
    report=dict(issue=1023,reviewer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),blend_sha256=meta['blend_sha256'],view_hashes=hashes,margins=margins,matched_view_comparisons=comparisons,detail_views_intentionally_crop_body=True,reference_heading_png_sha256=reference_hashes,reference_decoded_metadata_sha256=record['decoded_metadata_sha256'],reference_comparison='artifacts/issue-1023-surveillance-craft-type-5/comparison.png',final_visual_acceptance=False)
    (ROOT/'render-review.json').write_text(json.dumps(report,indent=2)+'\n');print('MAUNA_SURVEILLANCE_CRAFT_TYPE_5_RENDER_REVIEW_OK',len(names))


if __name__=='__main__':main()
