"""Record actual RI02 paired render comparisons and legacy/concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/filtration-plant'
MEDIA = ROOT/'gallery/media/objects/rigellian/filtration-plant'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(legacy,out):
    metadata = json.loads((FOLDER/'model.json').read_bytes())
    runtime = json.loads((FOLDER/'runtime-review.json').read_bytes())
    assert metadata['binaries']==runtime['binaries']
    names = ['front-quarter','front','rear-quarter']
    comparisons = {}
    sheet = Image.new('RGB',(1500,500),(20,23,26))
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
        x,y = row*500,0
        draw.text((x+5,y+5),name+' native / GLB',fill='white')
        for i,im in enumerate(images):
            im.thumbnail((250,440))
            sheet.paste(im,(x+i*250,y+25),im)
    sheet.save(out)
    concept = ROOT/'gallery/media/concepts/rigellian/ri02-review-1.png'
    source_comparisons = {}
    for name in names[:3]:
        a,b = [np.asarray(Image.open(MEDIA/(prefix+'-'+name+'.png')).convert('RGBA')).astype(float) for prefix in ['source','native']]
        mask = np.maximum(a[:,:,3],b[:,:,3])>127
        error = np.abs(a-b)[mask].mean(axis=0).tolist()
        silhouette = float(np.count_nonzero((a[:,:,3]>127)!=(b[:,:,3]>127))/np.count_nonzero(mask))
        assert max(error)<5 and silhouette<.001,(name,error,silhouette)
        source_comparisons[name] = dict(foreground_mean_rgba_255=error,threshold_silhouette_disagreement_fraction=silhouette)
    report = dict(issue=253,id=metadata['id'],concept_requests_used=1,concept_request_limit=3,
        concept=dict(tool='built-in ImageGen',image=concept.relative_to(ROOT).as_posix(),sha256=sha(concept),
            prompt='sources/docs/reconstruction/models/ri02-concept-prompt-1.txt',
            verdict='Rounded body, narrowed capped tower, six gold front fittings, upper fitting and side recess agree broadly. Taller tower, fewer visible lower slots, different fitting rims and stronger mottling remain interpretation; assessed model retained.'),
        concept_attempts=[dict(attempt=1,outcome='Selected after inspection, with proportion/slot/rim/finish deviations recorded rather than transferred.',
            prompt='sources/docs/reconstruction/models/ri02-concept-prompt-1.txt',image='gallery/media/concepts/rigellian/ri02-review-1.png',sha256=sha(concept))],
        source_comparisons=source_comparisons,
        legacy=dict(surface_payload_sha256=sha(legacy/'RI02.256'),
            ground_sha256=sha(legacy/'surface-00.png'),complete_body_sha256=sha(legacy/'surface-01.png'),
            reviewed_catalogue_phases=[0,10,20,30,40],functional_record=902,
            functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
            culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,
        feedback=['Actual function902 defines clean-water production and removal of excess atmospheric oxygen. CDB18 architecture context reviewed. Paletted surface ground0/completebody1 and catalogue0/10/20/30/40 reviewed. Reveal/highlight is a fixed view, not rotation or operating timing.', 'One actual ImageGen request used. Concept preserves broad rounded lower body, narrow capped tower, six brass front fittings, smaller upper fitting, lower slots and tall side recess. Concept tower height, lower-slot count, rim forms and mottled finish differ; retain assessed geometry and authored maps rather than adopting these deviations.', 'All83evaluated components and65,890triangles preserved without reduction or new wear. Existing recessed lower slots, side channel, two measurable dents, six face/body contacts and authored wear retained.', 'Actual saved-native and independent GLB checks cover every protected component, positive closed surfaces, one sampled contact component and prior anatomy ray checks. Complete decoded used texture channels and scalar material values compared at8-bit quantization. Known glTF material variants for different UV indices normalized only after shading equality checks; other material identity retained.', 'All used UV corners projected bidirectionally by material, retaining per-object shader-selected UV maps. Nine actual renders compare source/native/import at three corresponding angles. Pixel export equivalence does not establish a numerical legacy-fidelity percentage or final user artistic acceptance.', 'Static body1 overground0,RIS2construction separate; no invented mechanism, operating animation or glow. Client scale/placement/state/damage integration, exhaustive solid contacts and Android frame rate remain separate.', 'One canonical editable Blend/GLB selection for gameplay, build menu and SciTek. Technical diagrams derive from the same geometry. Earlier studies remain historical evidence, excluded from current payload selection. Programme248 remains unfinished.'],final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI02_PAIRED_PIXELS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
