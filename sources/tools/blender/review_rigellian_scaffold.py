"""RIS2 scaffold framing, native/imported comparisons and reference-only sheet."""
import hashlib,json,math,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageChops,ImageStat
sys.path.insert(0,str(Path(__file__).resolve().parent))
from review_assault_fighter import tile
REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/scaffolds/rigellian/size-2'
SOURCE=json.loads((REPO/'docs/reconstruction/models/shared-construction-references.json').read_text())
SOURCE_FAMILY=next(f for f in SOURCE['families'] if f['key']=='RIS2')
LAYERS={layer['index']:layer for layer in SOURCE_FAMILY['descriptors']}
ORDER_PATH=REPO/'docs/reconstruction/models/scaffold-composition-evidence.json'
ORDER=json.loads(ORDER_PATH.read_text())
assert ORDER['body_order_verified'] and not ORDER['full_pixel_composition_verified']


def reference_stack(frames,reference,reverse=False):
    # Diagnostic body-only stack: preserve original offsets and recovered 8px pitch.
    # Lower-first body dispatch is backed by the original-instruction fixture; reverse is a diagnostic contrast.
    placements=[]
    for level,frame in enumerate(frames):
        with Image.open(reference/f'descriptor-{frame:02}.png') as image:
            x,y=LAYERS[frame]['offset'];placements.append((image.convert('RGBA'),x,y-level*8))
    left=min(x for _,x,_ in placements);top=min(y for _,_,y in placements)
    right=max(x+image.width for image,x,_ in placements);bottom=max(y+image.height for image,_,y in placements)
    result=Image.new('RGBA',(right-left,bottom-top))
    for image,x,y in reversed(placements) if reverse else placements:
        result.alpha_composite(image,(x-left,y-top))
    return result


def main():
    meta=json.loads((ROOT/'model.json').read_text());gallery=Image.new('RGB',(2048,math.ceil(len(meta['cases'])/4)*512),(20,25,34));draw=ImageDraw.Draw(gallery);results=[]
    reference=REPO/'artifacts/shared-construction-reference-study/RIS2'
    comparison=Image.new('RGB',(1800,6*440),(20,25,34));comparison_labels=ImageDraw.Draw(comparison);selected=[1,2,3,6,16,17]
    for row,case in enumerate(meta['cases']):
        folder=ROOT/f"stage-{case['total_stage']:02}";margins={};hashes={}
        for col,view in enumerate(['front-quarter','rear-quarter','imported-front-quarter']):
            path=folder/(view+'.png')
            with Image.open(path) as image:
                assert image.mode=='RGBA' and image.size==(900,900) and image.getextrema()[3]==(0,255)
                x0,y0,x1,y1=image.getchannel('A').getbbox();margins[view]=min(x0,y0,900-x1,900-y1);assert margins[view]>=24
            if col==0:
                gallery.paste(tile(path,(512,480)),(row%4*512,row//4*512+30));draw.text((row%4*512+10,row//4*512+8),f"stage {case['total_stage']} / {len(case['frames'])} tiers / top {case['frames'][-1]}",fill='white')
            hashes[view]=hashlib.sha256(path.read_bytes()).hexdigest()
        with Image.open(folder/'front-quarter.png') as native,Image.open(folder/'imported-front-quarter.png') as imported:
            difference=ImageChops.difference(native,imported);mask=native.getchannel('A').point(lambda v:255 if v else 0);mean=ImageStat.Stat(difference,mask).mean
            binary=lambda im:im.getchannel('A').point(lambda v:255 if v>=128 else 0)
            assert ImageChops.difference(binary(native),binary(imported)).getbbox() is None,'Changed silhouette'
            alpha=difference.getchannel('A');count=sum(v!=0 for v in alpha.tobytes());maximum=alpha.getextrema()[1]
            assert max(mean[:3])<1.5 and count<=4 and maximum<=4,(case['total_stage'],mean,count,maximum)
        stacks=[]
        for reverse in [False,True]:
            stack=reference_stack(case['frames'],reference,reverse)
            name=reference/f"stack-{case['total_stage']:02}-{'upper-first' if reverse else 'lower-first'}.png";stack.save(name);stacks.append(name)
        with Image.open(stacks[0]) as stacked,Image.open(folder/'front-quarter.png') as native:
            source_box=stacked.getchannel('A').getbbox();native_box=native.getchannel('A').point(lambda v:255 if v>=128 else 0).getbbox()
            source_ratio=(source_box[3]-source_box[1])/(source_box[2]-source_box[0])
            native_ratio=(native_box[3]-native_box[1])/(native_box[2]-native_box[0])
        with Image.open(stacks[0]) as stacked,Image.open(folder/'front-quarter.png') as native:
            source_alpha=stacked.getchannel('A');source_alpha=source_alpha.crop(source_alpha.getbbox())
            native_alpha=native.getchannel('A');native_alpha=native_alpha.crop(native_box).resize(source_alpha.size,Image.Resampling.BOX)
            occupancy=dict(source=sum(v>=128 for v in source_alpha.tobytes())/len(source_alpha.tobytes()),
                authored=sum(v>=128 for v in native_alpha.tobytes())/len(native_alpha.tobytes()),
                method='Crop to alpha bounds, BOX-resize authored alpha to source dimensions, threshold at 128; diagnostic opacity occupancy, not geometric reconstruction acceptance')
        extent=dict(reference_height_over_width=source_ratio,native_height_over_width=native_ratio,
                    height_difference_at_reference_width=(native_ratio-source_ratio)*(source_box[2]-source_box[0]),scope='Diagnostic body extent only; not pixel-mask fidelity or recovered runtime world pitch')
        if case['total_stage'] in selected:
            index=selected.index(case['total_stage'])
            for col,(path,label) in enumerate([(stacks[0],'Legacy recovered body order'),(stacks[1],'Reverse order diagnostic'),(folder/'front-quarter.png','Authored native')]):
                comparison.paste(tile(path,(600,400)),(col*600,index*440+35));comparison_labels.text((col*600+10,index*440+8),f"stage {case['total_stage']} / {label}; full pixel compositor not reproduced",fill='white')
        results.append(dict(total_stage=case['total_stage'],view_sha256=hashes,margins=margins,reference_extent_comparison=extent,reference_occupancy_comparison=occupancy,mean_rgba_difference=mean,alpha_differences=count,alpha_maximum=maximum,binary_silhouette_equal=True))
    gallery.save(ROOT/'gallery.png')
    comparison.save(reference/'stack-comparison.png')
    reference=REPO/'artifacts/shared-construction-reference-study/RIS2';sheet=Image.new('RGB',(1400,1000),(20,25,34));labels=ImageDraw.Draw(sheet)
    for col,stage in enumerate([1,2]):
        sheet.paste(tile(reference/f'descriptor-{stage:02}.png',(700,440)),(col*700,40));labels.text((col*700+10,10),f'Legacy RIS2 descriptor {stage}; reference only',fill='white')
        sheet.paste(tile(ROOT/f'stage-{stage:02}/front-quarter.png',(700,440)),(col*700,550));labels.text((col*700+10,510),f'Authored stage {stage}; exact pitch/profile still provisional',fill='white')
    sheet.save(reference/'authored-comparison.png')
    (ROOT/'render-review.json').write_text(json.dumps(dict(issue=983,model_manifest_sha256=hashlib.sha256((ROOT/'model.json').read_bytes()).hexdigest(),reviewer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=results,reference_stack_comparison='artifacts/shared-construction-reference-study/RIS2/stack-comparison.png',source_composition_order_verified=False,body_descriptor_order_verified=True,body_order_evidence_sha256=hashlib.sha256(ORDER_PATH.read_bytes()).hexdigest(),final_visual_acceptance=False),indent=2)+'\n');print('RIS2_RENDER_REVIEW_OK',len(results)*3)


if __name__=='__main__': main()
