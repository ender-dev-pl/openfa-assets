"""Record actual RI22 paired render comparisons and legacy/concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/ex-fang'
MEDIA = ROOT/'gallery/media/objects/rigellian/ex-fang'


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
    concept = ROOT/'gallery/media/concepts/rigellian/ri22-review-2.png'
    report = dict(issue=253,id=metadata['id'],concept_requests_used=2,concept_request_limit=3,
        concept=dict(tool='built-in ImageGen',image=concept.relative_to(ROOT).as_posix(),sha256=sha(concept),
                     prompt='sources/docs/reconstruction/models/ri22-concept-prompt-2.txt',
                     verdict='Second iteration preserves a single shallow green collector, central copper projection, four bronze fittings and narrow inclined support. Extra linkages/collars and changed base proportions remain artistic interpretation; retain simpler source geometry.'),
        concept_attempts=[dict(attempt=1,outcome='Image returned and rejected: invented extra green plate behind collector.',
            prompt='sources/docs/reconstruction/models/ri22-concept-prompt-1.txt',image='gallery/media/concepts/rigellian/ri22-review-1.png',
            sha256=sha(ROOT/'gallery/media/concepts/rigellian/ri22-review-1.png')),
            dict(attempt=2,outcome='Image returned and inspected: one-dish silhouette corrected; selected.',prompt='sources/docs/reconstruction/models/ri22-concept-prompt-2.txt')],
        legacy=dict(surface_payload_sha256=sha(legacy/'RI22.256'),static_base_descriptor_empty=True,complete_directional_building_frames=True,shadow_sha256=sha(legacy/'surface-00.png'),assembled_descriptor_sha256={str(d):sha(legacy/f'layer-combination-{d:02}.png') for d in range(2,18)},
            reviewed_catalogue_phases=[0,10,20,30,40],functional_record=922,
            functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
            culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,
        feedback=[
            'Actual function record922 describes energy draining with uncertain operating means. Correctly paletted all16complete directional building frames, empty descriptor1, shadow and catalogue phases reviewed. Current selector/rules use2+(((heading+8)>>4)&15); do not treat these as separate base-plus-turret layers.',
            'First actual ImageGen attempt invented a second plate and was rejected. Second attempt used a single actual legacy heading and corrected the one-dish silhouette. Exact prompts, both outputs and explicit feedback retained; two of at most three requests used.',
            'Selected concept agrees with the shallow round green collector, central copper projection, four bronze fittings and inclined support. Elaborate new linkages/collars, deeper rim and altered base proportions are not recovered details and are not transferred automatically.',
            'All16 evaluated source components protected exactly, including shallow concavity, shell thickness, three profile dents and one collector dent, full authored maps and UVs. Source-derived11-part yaw assembly and physical supports retained; no reduction or unrelated restyling claimed.',
            'Actual native and independent GLB checks cover collector profile/thickness, feed embedment, support/head/shell/yoke/fitting/inset contacts, one sampled contact graph, all16authored yaw poses, collector-axis socket position/forward and fixed-base invariance. Contact samples are not exhaustive solid or continuous-sweep proof.',
            'Nineteen paired actual renders cover three whole-object views and16authored yaw poses. Full shader-bound UV corners and decoded colour/roughness maps match source/native/import. Export pixel equivalence is distinct from a numerical legacy-fidelity percentage.',
            'Exact fixed/moving division, pivot/elevation sections and concavity are authored interpretation. Model yaw phase/sign relative to game heading remains uncalibrated. CollectorAxisSocket is an axis reference, not proof of a firing origin. No pitch/firing/glow/operating clip invented; RIS4 construction separate.',
            'One current model supports gameplay, build menu, SciTek and derived technical views. Client placement/scale/damage/state integration, Android performance and final user artistic acceptance remain separate.'
        ],final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI22_PAIRED_PIXELS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
