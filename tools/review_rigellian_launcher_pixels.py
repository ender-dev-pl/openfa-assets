"""Compare actual RI18 native/import renders; keep original pixels private."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/missile-launcher'
MEDIA = ROOT/'gallery/media/objects/rigellian/missile-launcher'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(legacy,contact_sheet):
    metadata = json.loads((FOLDER/'model.json').read_bytes())
    runtime = json.loads((FOLDER/'runtime-review.json').read_bytes())
    assert runtime['binaries']==metadata['binaries']
    concept = json.loads((FOLDER/'concept-review.json').read_bytes())
    comparisons = {}
    sheet = Image.new('RGB',(1024,8*280),(20,23,26))
    draw = ImageDraw.Draw(sheet)
    for row,name in enumerate(['front-quarter','front','rear-quarter','half-open','open','open-top','descriptor09','descriptor16']):
        images = [Image.open(MEDIA/(prefix+'-'+name+'.png')).convert('RGBA') for prefix in ['native','imported']]
        a,b = [np.asarray(image).astype(float) for image in images]
        difference = np.abs(a-b)
        mask = np.maximum(a[:,:,3],b[:,:,3])>127
        silhouette_a,silhouette_b = a[:,:,3]>127,b[:,:,3]>127
        yy,xx = np.where(mask)
        margin = int(min(xx.min(),yy.min(),a.shape[1]-1-xx.max(),a.shape[0]-1-yy.max()))
        mean = difference.mean(axis=(0,1)).tolist()
        foreground = difference[mask].mean(axis=0).tolist()
        disagreement = float(np.count_nonzero(silhouette_a!=silhouette_b)/max(1,np.count_nonzero(mask)))
        assert max(mean)<1 and max(foreground)<2 and disagreement<.001 and margin>12,(name,mean,foreground,disagreement,margin)
        comparisons[name] = dict(mean_absolute_rgba_255=mean,foreground_mean_rgba_255=foreground,
            alpha_equal=bool(np.array_equal(a[:,:,3],b[:,:,3])),threshold_silhouette_equal=bool(np.array_equal(silhouette_a,silhouette_b)),
            threshold_silhouette_disagreement_fraction=disagreement,margin=margin)
        for column,image in enumerate(images):
            image.thumbnail((256,256))
            sheet.paste(image,(column*512+128,row*280+24),image)
            draw.text((column*512+12,row*280+5),name+' / '+['native','independent GLB'][column],fill='white')
    sheet.save(contact_sheet)
    feedback = [
        'Correctly paletted source/layer combinations 2..17 and catalogue phases preserve green stepped upper casing, bronze ribbed drum, two front bands, angled fitting and outward two-half dome family. Existing refined silhouette retained.',
        'Concept adds a third front band, stronger rings and fitting details; these are not adopted. Concept hollow halves do not establish hidden wall thickness. Source-derived solid half geometry and outer UVs retained; interior split faces receive explicit YZ mapping.',
        'Compact axle/bearing/root brackets are authored engineering. Actual own-axis seat contacts are bounded in 61 native and independent-import cycle samples, with opposite hardware and old-body contacts excluded. Contacts are triangle surface/envelope checks, not measured penetration volumes or continuous-time proof.',
        'Proportional collar compression only above Z1.62 preserves nonzero-height rim profile; preserved components and lower casing match the latest source. Recessed floor radius overlaps existing low ring. Six cosmetic scuffs gain 0.0001 thickness. No unrelated source redesign.',
        'Source bronze/green colour and roughness maps and fixed planar/cylindrical UVs verified after independent import. New hardware reuses these worn maps with explicit UVs. Existing wear is subtler than ImageGen artwork.',
        'Angles through descriptors 2..16 and cycle duration are authored monotonic calibration, not recovered physical measurements or timers. Descriptor17 uses the open pose while its extra lower/shadow composition remains unverified. Shared RIS3 construction and missile entity remain separate.',
        'Eight paired native/import renders agree within the recorded image metrics and retain framing margins. This is export equivalence, not a numerical measure of legacy likeness. Client scale, missile swept volume, Android cost and final user artistic acceptance remain separate.'
    ]
    report = dict(issue=253,id=metadata['id'],concept_requests_used=2,concept_request_limit=3,
        concept=concept['concept'],concept_attempts=concept['attempts'],
        legacy=dict(body_sha256=sha(legacy/'surface-01.png'),closed_composite_sha256=sha(legacy/'layer-combination-02.png'),
                    reviewed_surface_descriptors=list(range(18)),reviewed_composite_descriptors=list(range(2,18)),
                    functional_record=918,functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
                    culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,feedback=feedback,
        final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    concept['feedback'] = feedback[:6]
    concept['candidate_motion_report_sha256'] = sha(FOLDER/'candidate-motion-review.json')
    concept.pop('canonical_delivery_ready',None)
    concept['delivery_authority'] = 'Current runtime/visual proofs and canonical inventory registration'
    (FOLDER/'concept-review.json').write_bytes((json.dumps(concept,indent=2)+'\n').encode())
    print('RI18_RENDER_COMPARISONS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
