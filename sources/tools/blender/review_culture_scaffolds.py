"""Render comparison, framing and reproducible family/style galleries."""
import hashlib
import json
import math
from pathlib import Path
import sys
from PIL import Image,ImageChops,ImageDraw,ImageStat
sys.path.insert(0,str(Path(__file__).resolve().parent))
from scaffold_render_coverage import compare_coverage

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/scaffolds/culture-kits'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def tile(path,size=(512,512)):
    with Image.open(path) as image:
        image=image.convert('RGBA');image.thumbnail(size)
        result=Image.new('RGBA',size,(20,25,34,255))
        result.alpha_composite(image,((size[0]-image.width)//2,(size[1]-image.height)//2))
        return result.convert('RGB')


def main():
    wear=json.loads((ROOT/'authored-wear.json').read_text())
    assert sha(Path(__file__).with_name('author_culture_scaffold_wear.py'))==wear['generator_sha256']
    for path,digest in wear['images'].items():assert sha(ROOT/path)==digest,path
    index=json.loads((ROOT/'index.json').read_text())
    overview=Image.new('RGB',(1536,math.ceil(len(index['families'])/3)*570),(20,25,34));labels=ImageDraw.Draw(overview)
    maximum_overview=Image.new('RGB',overview.size,(20,25,34));maximum_labels=ImageDraw.Draw(maximum_overview)
    culture_overview=Image.new('RGB',(1536,1080),(20,25,34));culture_labels=ImageDraw.Draw(culture_overview)
    styles=['PBS2','BRS2','MKS2','ARS2','MNS2','ACS2'];results=[]
    for i,family in enumerate(index['families']):
        folder=ROOT/Path(family['manifest']).parent
        manifest=json.loads((folder/'model.json').read_text())
        assert sha(folder/'model.json')==family['sha256']
        technical=json.loads((folder/'technical-review.json').read_text())
        assert technical['model_manifest_sha256']==family['sha256']
        cases=[]
        for case in manifest['cases']:
            stage=folder/f"stage-{case['stage']:02}"
            margins={};hashes={}
            views=['front-quarter','imported-front-quarter']+(['rear-quarter'] if case['rear_view'] else [])
            for view in views:
                path=stage/(view+'.png')
                with Image.open(path) as image:
                    assert image.size==(512,512) and image.mode=='RGBA'
                    bounds=image.getchannel('A').getbbox();assert bounds
                    margin=min(bounds[0],bounds[1],512-bounds[2],512-bounds[3])
                    assert margin>=5,(family['family'],case['stage'],view,margin)
                    margins[view]=margin
                hashes[view]=sha(path)
            with Image.open(stage/'front-quarter.png') as native,Image.open(stage/'imported-front-quarter.png') as imported:
                delta=ImageChops.difference(native,imported)
                try:coverage=compare_coverage(native,imported)
                except AssertionError as error:raise AssertionError((family['family'],case['stage'],str(error))) from error
                mask=native.getchannel('A').point(lambda value:255 if value else 0)
                mean=ImageStat.Stat(delta,mask).mean
                assert max(mean[:3])<1.5,(family['family'],case['stage'],mean)
            cases.append(dict(stage=case['stage'],view_sha256=hashes,margins=margins,mean_rgba_difference=mean,**coverage))
        representative=min(manifest['capacity'],manifest['required_max_stage'])
        x=i%3*512;y=i//3*570
        overview.paste(tile(folder/f'stage-{representative:02}/front-quarter.png'),(x,y+35))
        labels.text((x+12,y+10),family['family']+' / '+manifest['style']['kind'],fill='white')
        labels.text((x+12,y+548),f"stages 1..{manifest['required_max_stage']} / {manifest['required_max_tiers']} tiers maximum",fill='white')
        maximum=manifest['required_max_stage']
        maximum_overview.paste(tile(folder/f'stage-{maximum:02}/front-quarter.png'),(x,y+35))
        maximum_labels.text((x+12,y+10),f"{family['family']} / stage {maximum} / {manifest['required_max_tiers']} tiers",fill='white')
        if family['family'] in styles:
            k=styles.index(family['family']);x=k%3*512;y=k//3*540
            culture_overview.paste(tile(folder/f'stage-{representative:02}/front-quarter.png'),(x,y+25))
            culture_labels.text((x+12,y+8),family['family']+' / '+manifest['style']['kind'],fill='white')
        report=dict(issue=188,family=family['family'],model_manifest_sha256=sha(folder/'model.json'),technical_review_sha256=sha(folder/'technical-review.json'),reviewer_sha256=sha(Path(__file__)),coverage_checker_sha256=sha(Path(__file__).with_name('scaffold_render_coverage.py')),cases=cases,scope='Native/imported equivalence and framing with bounded stochastic edge coverage; authored OpenFA3D culture interpretation, not exact legacy pixel-mask fidelity')
        (folder/'render-review.json').write_text(json.dumps(report,indent=2)+'\n')
        results.append(dict(family=family['family'],states=len(cases),views=sum(len(c['view_sha256']) for c in cases),max_rgb_mean=max(max(c['mean_rgba_difference'][:3]) for c in cases),max_alpha=max(c['alpha_maximum'] for c in cases),render_review_sha256=sha(folder/'render-review.json')))
    overview.save(ROOT/'family-overview.png');culture_overview.save(ROOT/'culture-overview.png')
    maximum_overview.save(ROOT/'maximum-stacks.png')
    (ROOT/'render-review.json').write_text(json.dumps(dict(issue=188,reviewer_sha256=sha(Path(__file__)),families=results,states=sum(r['states'] for r in results),views=sum(r['views'] for r in results)),indent=2)+'\n')
    print('CULTURE_RENDER_REVIEW_OK',sum(r['states'] for r in results),sum(r['views'] for r in results))


if __name__=='__main__':main()
