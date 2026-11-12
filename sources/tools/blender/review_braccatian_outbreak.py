"""Review first Braccatian Outbreak renders and compare matched-camera GLB pixels."""
import hashlib,json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile
REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/missiles/braccatian/outbreak'
REF=REPO/'artifacts/issue-1056-outbreak'


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
    REF.mkdir(parents=True,exist_ok=True);reference=json.loads((REPO/'docs/reconstruction/models/missile-reference-index.json').read_text());missile=next(r for r in reference['missiles'] if r['id']=='openfa:missile/braccatian/outbreak');record=missile['surface'];assert missile['management_preview'] is None and record['frame_count']==14
    for frame in record['frames']:
        path=REPO/frame['png'];assert hashlib.sha256(path.read_bytes()).hexdigest()==frame['png_sha256']
        with Image.open(path) as original:
            assert original.mode=='P' and original.info['transparency']==0 and hashlib.sha256(bytes(original.getpalette())).hexdigest()==record['palette_rgb_sha256']
            assert hashlib.sha256(original.tobytes()).hexdigest()==frame['indexed_canvas_sha256']
    sheet=Image.new('RGB',(1600,1200),(20,25,34));draw=ImageDraw.Draw(sheet)
    for i,index in enumerate([0,1,2,3,4,5,6,9,12]):
        frame=record['frames'][index];path=REPO/frame['png'];sheet.paste(tile(path,(320,260)),(i%5*320,i//5*300+30));draw.text((i%5*320+8,i//5*300+8),'Original BRM7 flight/launch '+str(index),fill='white')
    for i,name in enumerate(['front-quarter','rear-quarter','top','underside']):
        sheet.paste(tile(ROOT/(name+'.png'),(400,500)),(i*400,670));draw.text((i*400+8,640),'First interpretation '+name,fill='white')
    sheet.save(REF/'comparison.png')
    report=dict(issue=1056,reviewer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),blend_sha256=meta['blend_sha256'],view_hashes=hashes,margins=margins,matched_view_comparisons=comparisons,detail_views_intentionally_crop_body=True,reference_source_sha256=record['source_sha256'],reference_palette_rgb_sha256=record['palette_rgb_sha256'],reference_index_sha256=hashlib.sha256((REPO/'docs/reconstruction/models/missile-reference-index.json').read_bytes()).hexdigest(),reference_comparison='artifacts/issue-1056-outbreak/comparison.png',final_visual_acceptance=False)
    (ROOT/'render-review.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_OUTBREAK_RENDER_REVIEW_OK',len(names))


if __name__=='__main__':main()
