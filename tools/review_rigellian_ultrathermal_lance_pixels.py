"""Record actual RI23 paired render comparisons and legacy/concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/ultrathermal-lance'
MEDIA = ROOT/'gallery/media/objects/rigellian/ultrathermal-lance'


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
    concept = ROOT/'gallery/media/concepts/rigellian/ri23-review-1.png'
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
            prompt='sources/docs/reconstruction/models/ri23-concept-prompt-1.txt',
            verdict='Paired bronze projections, green bell body, tapered segmented foot and side fittings broadly agree. Extra root collars/pitch articulation, simplified groove count and omitted front strip are not transferred.'),
        concept_attempts=[dict(attempt=1,outcome='Image returned and inspected; selected with explicit deviations retained as feedback.',
            prompt='sources/docs/reconstruction/models/ri23-concept-prompt-1.txt',image='gallery/media/concepts/rigellian/ri23-review-1.png',sha256=sha(concept))],
        source_comparisons=source_comparisons,
        legacy=dict(surface_payload_sha256=sha(legacy/'RI23.256'),static_base_descriptor_empty=False,complete_directional_building_frames=False,shadow_sha256=sha(legacy/'surface-00.png'),assembled_descriptor_sha256={str(d):sha(legacy/f'layer-combination-{d:02}.png') for d in range(2,18)},
            reviewed_catalogue_phases=[0,10,20,30,40],functional_record=923,
            functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
            culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,
        feedback=['Actual function record923 identifies an effective anti-ship weapon. All16 paletted directional upper overlays2..17, persistent base1, shadow and catalogue phases reviewed. Current selector uses2+(((heading+8)>>4)&15); fixed base remains present.', 'One actual ImageGen request used. Selected concept broadly agrees with two bronze lances, green bell body, tapered segmented foot, side spur and fitting. Invented root collars/pitch articulation, altered groove count and omitted bronze front strip are not copied.', 'Nine evaluated upper/detail components retained without reduction. Thirteen foot components retain12segments, taper, grooves, dents, positive closed surfaces and contact samples. Near-coplanar tessellation dissolved with material/UV boundaries preserved; source and candidate surfaces measured bidirectionally below1e-4 model units. This is tolerance-bounded simplification, not exact geometry identity.', 'Actual saved native and independent GLB retain three moving parts,19fixed parts and two independent lance-tip sockets. All16 authored yaw poses check positions, local+Z forwards,0.36tip separation and fixed-base invariance. Sampled contacts and poses do not prove continuous collision freedom.', 'Three source/native appearance comparisons and19native/imported pairs evaluated. Full decoded maps retained; UV corner projections compared bidirectionally against corresponding material surfaces, including degenerate triangulation edges. This is sampled correspondence, not a continuous UV-field proof or numerical legacy-fidelity percentage.', 'No pitch/firing/glow clip or operating timing recovered. Model yaw phase/sign relative to game remains uncalibrated. RIS3construction remains separate. Socket references are authored geometry attachments, not recovered ballistic origins.', 'One canonical editable model and GLB serve gameplay, build menu, SciTek and derived wireframes. Client placement/scale/damage/state integration, Android performance and final user artistic acceptance remain separate.'],final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI23_PAIRED_PIXELS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
