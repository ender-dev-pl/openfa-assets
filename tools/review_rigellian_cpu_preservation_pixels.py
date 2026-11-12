"""Record actual RI01 paired render comparisons and legacy/concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/central-unit'
MEDIA = ROOT/'gallery/media/objects/rigellian/central-unit'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(legacy,out):
    metadata = json.loads((FOLDER/'model.json').read_bytes())
    runtime = json.loads((FOLDER/'runtime-review.json').read_bytes())
    assert metadata['binaries']==runtime['binaries']
    names = ['front-quarter','front','rear-quarter']
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
    concept = ROOT/'gallery/media/concepts/rigellian/ri01-review-2.png'
    source_comparisons = {}
    for name in names[:3]:
        a,b = [np.asarray(Image.open(MEDIA/(prefix+'-'+name+'.png')).convert('RGBA')).astype(float) for prefix in ['source','native']]
        mask = np.maximum(a[:,:,3],b[:,:,3])>127
        error = np.abs(a-b)[mask].mean(axis=0).tolist()
        silhouette = float(np.count_nonzero((a[:,:,3]>127)!=(b[:,:,3]>127))/np.count_nonzero(mask))
        assert max(error)<5 and silhouette<.001,(name,error,silhouette)
        source_comparisons[name] = dict(foreground_mean_rgba_255=error,threshold_silhouette_disagreement_fraction=silhouette)
    report = dict(issue=253,id=metadata['id'],concept_requests_used=2,concept_request_limit=3,
        concept=dict(tool='built-in ImageGen',image=concept.relative_to(ROOT).as_posix(),sha256=sha(concept),
            prompt='sources/docs/reconstruction/models/ri01-concept-prompt-2.txt',
            verdict='Second concept corrects invented central ring opening and crescent well. Broad saucer, waisted base, three-prong crown and green/brass palette agree. Altered grille division, neck proportions and feature sizes remain interpretation; assessed geometry retained.'),
        concept_attempts=[dict(attempt=1,outcome='Rejected: invented central roof opening and crescent side cutout.',
            prompt='sources/docs/reconstruction/models/ri01-concept-prompt-1.txt',image='gallery/media/concepts/rigellian/ri01-review-1.png',sha256=sha(ROOT/'gallery/media/concepts/rigellian/ri01-review-1.png')),
            dict(attempt=2,outcome='Selected with explicit limitations: solid crown seating and small round side well restored.',
            prompt='sources/docs/reconstruction/models/ri01-concept-prompt-2.txt',image='gallery/media/concepts/rigellian/ri01-review-2.png',sha256=sha(concept))],
        source_comparisons=source_comparisons,
        legacy=dict(surface_payload_sha256=sha(legacy/'RI01.256'),
            ground_sha256=sha(legacy/'surface-00.png'),complete_body_sha256=sha(legacy/'surface-01.png'),
            reviewed_catalogue_phases=[0,10,20,30,40],functional_record=901,
            functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
            culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,
        feedback=['Actual function901 defines essential colony supplies until dedicated facilities are constructed. CDB18 architecture context reviewed. RI01surface ground0 and complete body1 plus catalogue phases0/10/20/30/40 reviewed. The catalogue reveals/highlights a fixed object, not multiple headings or operating motion.', 'Two actual ImageGen attempts. First rejected for invented central crown opening and crescent well. Second corrects these, broadly preserving green/brass palette, broad saucer, waisted base and three-prong crown. Changed grille division/proportions and fitting sizes are not automatically transferred.', 'All75evaluated components,40,636triangles and seven authored materials retained. No tessellation reduction, new wear or body restyling. The pre-existing CPU body is exempt from later wear retrofit; existing crown finish also retained.', 'Actual saved-native and independent GLB checks cover roof well/sleeve/floor/fin seating, crown socket/rim clearance, conformal roof cap, open neck grille, broad tapered crown arms and sampled contact graph. UV corner projections and decoded used map channels plus scalar material properties compared. Scalar values quantized to8bits for source/export equivalence; not an exact float shader identity.', 'Nine actual renders include three source/native appearance comparisons and three native/import pairs. Full source geometry retained within measured tolerance; export pixel agreement is separate from legacy fidelity and final user artistic acceptance.', 'No moving mechanism, operational timing or special glow recovered. Static body1,ground0,RIS3construction separate. Client placement/scale/state/damage integration, continuous solid contacts and Android frame rate remain separate.', 'One canonical editable Blend and GLB serve gameplay, build menu and SciTek; technical diagrams derive from the same model. Earlier studies remain historical evidence, excluded from current payload selection.'],final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI01_PAIRED_PIXELS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
