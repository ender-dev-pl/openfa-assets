"""Record actual RI19 paired render comparisons and legacy/concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/thermal-lance'
MEDIA = ROOT/'gallery/media/objects/rigellian/thermal-lance'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(legacy,out):
    metadata = json.loads((FOLDER/'model.json').read_bytes())
    runtime = json.loads((FOLDER/'runtime-review.json').read_bytes())
    assert metadata['binaries']==runtime['binaries']
    names = ['front-quarter','front','rear-quarter']+['yaw-'+str(i).zfill(2) for i in range(16)]
    comparisons = {}
    sheet = Image.new('RGB',(1200,5*250),(20,23,26))
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
        x,y = (row%4)*300,(row//4)*250
        draw.text((x+5,y+5),name+' native / GLB',fill='white')
        for i,im in enumerate(images):
            im.thumbnail((150,220))
            sheet.paste(im,(x+i*150,y+25),im)
    sheet.save(out)
    concept = ROOT/'gallery/media/concepts/rigellian/ri19-review-1.png'
    report = dict(issue=253,id=metadata['id'],concept_requests_used=1,concept_request_limit=3,
        concept=dict(tool='built-in ImageGen',image=concept.relative_to(ROOT).as_posix(),sha256=sha(concept),
                     prompt='sources/docs/reconstruction/models/ri19-concept-prompt-1.txt',
                     verdict='Bell pedestal, lower slots, bronze front strip/base fitting, single green tapered lance and small upper fitting agree. Concept enlarges head/fuses lance root; source-derived proportions and independent yaw rig retained.'),
        concept_attempts=[dict(attempt=1,outcome='Image returned and inspected.')],
        legacy=dict(body_sha256=sha(legacy/'surface-01.png'),assembled_descriptor_sha256={str(d):sha(legacy/f'layer-combination-{d:02}.png') for d in range(2,18)},
            reviewed_catalogue_phases=[0,10,20,30,40],functional_record=919,
            functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
            culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,
        feedback=[
            'Original function record919 identifies the least effective anti-ship weapon. Paletted fixed body and all16 assembled head directions reviewed; current selector and rules preserve frame1 plus2+(((heading+8)>>4)&15). Catalogue reveal/highlight is not operating motion.',
            'Concept broadly preserves the original green bell pedestal, short rounded head, upward-diagonal single tapered lance, lower dark slots and bronze strip/fittings. Enlarged head/fused lance root, stronger floor lip, thickened strip and stronger wear are artistic interpretations and not transferred automatically.',
            'All12 evaluated source components are retained geometrically with no reduction or restyling; three existing geometric dents, full authored green colour/roughness maps and six local planar caps plus cylindrical UVs are preserved. Existing wear is subtler than concept.',
            'Only four upper meshes plus LanceTipSocket inherit YawPivot; fixed pedestal/bearing/lower fittings remain under PlacementRoot. Actual socket endpoint/forward axis and all moving matrices agree in16native and16imported yaw samples. Legacy-to-model yaw phase/sign remains uncalibrated.',
            'Nineteen paired actual renders cover three whole-body views and all16authored yaw samples. Their close pixel agreement verifies export equivalence, not a numerical percentage of legacy likeness. Same canonical geometry supports technical diagrams rather than a separately remodelled diagram mesh.',
            'No timed operating/firing/pitch clip or invented glow. Fixed lance elevation/socket axis/pivot sections remain authored interpretation. Shared RIS3 construction separate. Continuous collision sweep, game scale/state effects, Android performance and final user artistic acceptance remain unproved.'
        ],final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI19_PAIRED_PIXELS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
