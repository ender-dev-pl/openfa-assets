"""Record actual RI20 paired render comparisons and legacy/concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/extractor'
MEDIA = ROOT/'gallery/media/objects/rigellian/extractor'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(legacy,out):
    metadata = json.loads((FOLDER/'model.json').read_bytes())
    runtime = json.loads((FOLDER/'runtime-review.json').read_bytes())
    assert metadata['binaries']==runtime['binaries']
    names = ['front-quarter','front','rear-quarter']
    comparisons = {}
    sheet = Image.new('RGB',(900,250),(20,23,26))
    draw = ImageDraw.Draw(sheet)
    for row,name in enumerate(names):
        images = [Image.open(MEDIA/(p+'-'+name+'.png')).convert('RGBA') for p in ['native','imported']]
        a,b = [np.asarray(im).astype(float) for im in images]
        difference = np.abs(a-b)
        mask = np.maximum(a[:,:,3],b[:,:,3])>127
        yy,xx = np.where(mask)
        margin = int(min(xx.min(),yy.min(),a.shape[1]-1-xx.max(),a.shape[0]-1-yy.max()))
        disagreement = float(np.count_nonzero((a[:,:,3]>127)!=(b[:,:,3]>127))/np.count_nonzero(mask))
        mean,foreground = difference.mean(axis=(0,1)).tolist(),difference[mask].mean(axis=0).tolist()
        assert max(mean)<1 and max(foreground)<2 and disagreement<.001 and margin>12,(name,mean,foreground,disagreement,margin)
        comparisons[name] = dict(mean_absolute_rgba_255=mean,foreground_mean_rgba_255=foreground,
            alpha_equal=bool(np.array_equal(a[:,:,3],b[:,:,3])),threshold_silhouette_equal=bool(np.array_equal(a[:,:,3]>127,b[:,:,3]>127)),
            threshold_silhouette_disagreement_fraction=disagreement,margin=margin)
        x,y = row*300,0
        draw.text((x+5,y+5),name+' native / GLB',fill='white')
        for i,im in enumerate(images):
            im.thumbnail((150,220))
            sheet.paste(im,(x+i*150,y+25),im)
    sheet.save(out)
    concept = ROOT/'gallery/media/concepts/rigellian/ri20-review-1.png'
    report = dict(issue=253,id=metadata['id'],concept_requests_used=1,concept_request_limit=3,
        concept=dict(tool='built-in ImageGen',image=concept.relative_to(ROOT).as_posix(),sha256=sha(concept),
                     prompt='sources/docs/reconstruction/models/ri20-concept-prompt-1.txt',
                     verdict='Broad lower shoulder, round upper housing, side pod, three lower ribs, two recessed slots and bronze/green details agree. Concept rounds slot ends and changes green-fitting layout; latest source geometry retained.'),
        concept_attempts=[dict(attempt=1,outcome='Image returned and inspected.')],
        legacy=dict(body_sha256=sha(legacy/'surface-01.png'),shadow_sha256=sha(legacy/'surface-00.png'),catalogue_phases_sheet_sha256=sha(legacy/'catalogue-phases.png'),
            reviewed_catalogue_phases=[0,10,20,30,40],functional_record=920,
            functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
            culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,
        feedback=[
            'Original functional record920 identifies one mining device handling all ores. Correctly paletted body/shadow and catalogue colour/outline phases reviewed. Current selector excludes this ID from directional body definitions. Two descriptors do not establish a cycle; RIS2 construction separate.',
            'One actual built-in ImageGen concept preserves the broad shoulder, rounded upper section, left side pod, front fittings, two vertical slots and three lower ribs. Rounded slot ends, enlarged upper fitting, rearranged green lower pieces and stronger natural patina are interpreted details and are not transferred automatically.',
            'All39 evaluated parts of the latest structural refinement are protected. Do not revert to the older smooth capsule/flat-inlay/green-loop study. Source stepped shoulder, true slot cavities/backing/rims, three lower ribs, segmented green blocks and existing bronze/green finish remain.',
            'Source and native UV corners match exactly; native/imported corresponding material corners and complete used colour/roughness pixels are checked. Two retained casing dents and one sampled39-part contact component supplement structural rays; not exhaustive solid-contact proof.',
            'Three paired actual saved-native/independent GLB views inspected. Export pixel equivalence is separate from legacy likeness. Existing wear/patina is more graphic and subtler than concept; material identity and ambiguous green marks do not establish external plumbing.',
            'Identity PlacementRoot, nominal2x2 footprint. Lowest physical surface remains at source Z0.02; do not silently assume it touches root Z0. Client ground/scale/state calibration and Android cost remain separate. No drill, operating cycle, glow or damage model invented; final user artistic acceptance remains open.'
        ],final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI20_PAIRED_PIXELS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
