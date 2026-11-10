"""Record actual RI21 paired render comparisons and legacy/concept feedback."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'sources/objects/rigellian/storage-racks'
MEDIA = ROOT/'gallery/media/objects/rigellian/storage-racks'


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
    concept = ROOT/'gallery/media/concepts/rigellian/ri21-review-1.png'
    report = dict(issue=253,id=metadata['id'],concept_requests_used=1,concept_request_limit=3,
        concept=dict(tool='built-in ImageGen',image=concept.relative_to(ROOT).as_posix(),sha256=sha(concept),
                     prompt='sources/docs/reconstruction/models/ri21-concept-prompt-1.txt',
                     verdict='Two tiers, five opaque green ovals and two grey front guides agree. Concept adds top handles, side collars, denser seams and massive supports; retain source-derived housings and tested cradle architecture.'),
        concept_attempts=[dict(attempt=1,outcome='Image returned and inspected.')],
        legacy=dict(body_sha256=sha(legacy/'surface-01.png'),shadow_sha256=sha(legacy/'surface-00.png'),catalogue_phases_sheet_sha256=sha(legacy/'catalogue-phases.png'),
            reviewed_catalogue_phases=[0,10,20,30,40],functional_record=921,
            functional_source_sha256='559e835dbd4fd058310fed6ef643600a09b95e5a7c6d86f0dc153c96b9e0a449',
            culture_record=18,culture_source_sha256='767991db2dd69ffc182b80ea7f4a1a872935fbaa308f8778244a6b0e5fb3b4e4',original_pixels_published=False),
        binaries=metadata['binaries'],runtime_report_sha256=sha(FOLDER/'runtime-review.json'),comparisons=comparisons,
        feedback=[
            'Original functional record921 identifies ore storage. Actual paletted body/shadow, catalogue colour/outline phases and current selector reviewed. ID060 is not a directional body. Catalogue reveal/highlight does not establish loading motion; shared RIS3 construction separate.',
            'One actual built-in ImageGen concept preserves two tiers, five visible green oval faces and two grey front guides. Added top handles, side collars, denser casing divisions and heavy feet/cradles are not established by legacy and are not copied automatically.',
            'Six housings and hidden triangular cradles/rear spines remain source-guided authored interpretations. Preserve32 evaluated source components, six measured dents, twelve planar caps and full used bronze colour/roughness pixels. Existing wear is subtler than concept; no tessellation reduction or material restyling claimed.',
            'Actual containment/ray checks retain housing/cradle, spine/tie, guide/foot-tie connections plus160oval bezel-root and25face attachment samples. One sampled contact component connects the rack; this is not exhaustive solid-intersection proof.',
            'Source/native and native/import material-bound UV corners match bidirectionally, including seams and export triangulation. Directed corner counts may differ after triangulation; full coverage and error bounds are checked rather than assuming equal counts.',
            'Three paired actual whole-object renders inspected against legacy and concept. Export pixel equivalence is separate from a numerical measure of legacy likeness. Ovals remain opaque, rough and non-emissive; no glass, lamps, loading cycle or unseen sixth green face invented.',
            'One current model serves gameplay, build menu, SciTek and derived technical views. Client placement/orientation/scale, construction/damage states, Android cost and final user artistic acceptance remain separate.'
        ],final_user_artistic_acceptance=False,game_client_integration=False)
    (FOLDER/'visual-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('RI21_PAIRED_PIXELS_OK',len(comparisons),max(max(c['foreground_mean_rgba_255']) for c in comparisons.values()))


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--legacy-directory',type=Path,required=True)
    parser.add_argument('--contact-sheet',type=Path,required=True)
    args = parser.parse_args()
    main(args.legacy_directory,args.contact_sheet)
