"""Bind the inspected legacy/concept/actual-GLB feedback correction to its sources."""
from io import BytesIO
from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw, ImageOps

ROOT=Path(__file__).resolve().parents[1]
OBJECT='objects/achaean/dedicated-ore-transporter'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    out=ROOT/'sources'/OBJECT;media=ROOT/'gallery/media'/OBJECT
    baseline=json.loads((out/'feedback-baseline.json').read_text())
    runtime=json.loads((out/'runtime-verification.json').read_text())
    evidence=json.loads((out/'reference-evidence.json').read_text())
    for kind in ['blend','glb']:
        assert sha((out/('model.'+kind)).read_bytes())==runtime[kind+'_sha256']
    before_glb=subprocess.check_output(['git','show',baseline['source_commit']+':sources/'+OBJECT+'/model.glb'],cwd=ROOT)
    assert sha(before_glb)==baseline['glb_sha256']
    current=runtime['imported_crescent_proportions']
    assert current['tip_span_over_hull_height']<baseline['tip_span_over_hull_height']*.5
    assert runtime['maximum_bidirectional_world_position_error']==0
    assert runtime['imported_distal_fastener_contacts']['contacts']==8
    old_render=subprocess.check_output(['git','show',baseline['source_commit']+':gallery/media/'+OBJECT+'/verified-imported.png'],cwd=ROOT)
    board=Image.new('RGB',(1800,1100),(18,21,25));draw=ImageDraw.Draw(board)
    items=[('Reviewed artistic concept (not a model render)',Image.open(media/'concept.png'),(0,0,1800,530)),
           ('Previous independently imported GLB: flared arms',Image.open(BytesIO(old_render)),(0,550,900,550)),
           ('Corrected independently imported GLB: converging arms',Image.open(media/'verified-imported.png'),(900,550,900,550))]
    for label,image,(x,y,w,h) in items:
        im=image.convert('RGBA');im=im.crop(im.getbbox())
        im=ImageOps.contain(im,(w-24,h-60),Image.Resampling.LANCZOS)
        bg=Image.new('RGBA',im.size,(18,21,25,255));bg.alpha_composite(im)
        board.paste(bg.convert('RGB'),(x+(w-im.width)//2,y+40+(h-60-im.height)//2))
        draw.text((x+15,y+12),label,fill=(235,237,240))
    board.save(media/'feedback-comparison.jpg',quality=92)
    prior=subprocess.check_output(['git','show','3d235d5a:gallery/media/'+OBJECT+'/verified-imported.png'],cwd=ROOT)
    detail=Image.new('RGB',(1200,470),(18,21,25));draw=ImageDraw.Draw(detail)
    crops=[('Concept: broad leading shield',Image.open(media/'concept.png'),(850,330,1230,740)),
           ('Before: narrow leading shield',Image.open(BytesIO(prior)),(680,400,1020,760)),
           ('Corrected actual GLB',Image.open(media/'verified-imported.png'),(680,400,1020,760))]
    for i,(label,image,crop) in enumerate(crops):
        im=ImageOps.contain(image.convert('RGBA').crop(crop),(380,410))
        bg=Image.new('RGBA',im.size,(18,21,25,255));bg.alpha_composite(im)
        detail.paste(bg.convert('RGB'),(i*400+(400-im.width)//2,45))
        draw.text((i*400+12,15),label,fill=(235,237,240))
    detail.save(media/'wing-root-comparison.jpg',quality=92)
    frames=[f for f in evidence['legacy']['frames'] if f['index'] in [0,4,12,20]]
    report=dict(id=runtime['id'],model_render_review_passes=3,imagegen_iterations_this_correction=0,
        review_method='Human-readable visual review by authoring agent plus measured actual imported geometry; no automated perceptual score',
        feedback='Distal crescent arms too widely separated compared with concept and paletted legacy',
        legacy_source=evidence['legacy']['source'],legacy_sha256=evidence['legacy']['source_sha256'],
        principal_legacy_frames=frames,concept_sha256=sha((media/'concept.png').read_bytes()),
        previous_commit=baseline['source_commit'],previous_glb_sha256=baseline['glb_sha256'],
        current_glb_sha256=runtime['glb_sha256'],current_blend_sha256=runtime['blend_sha256'],
        before=baseline,after=current,
        change='Distal arms converge; leading shield around the hub widened without changing the mouth, lateral mounts or hull; eight fasteners seated on the tapered skin',
        root_width_correction=dict(previous_source_commit='3d235d5a',previous_authored_width_parameter=.64,
            current_measured_imported_width=current['root_fore_aft_width'],
            user_feedback='Leading crescent width around the hub must match the broad concept/legacy shield',
            comparison_sha256=sha((media/'wing-root-comparison.jpg').read_bytes())),
        imported_distal_fastener_contacts=runtime['imported_distal_fastener_contacts'],
        visual_review=dict(converging_open_crescents=True,pale_fore_tip_and_yellow_aft_marks_preserved=True,
            full_warm_hull_and_transverse_supports_preserved=True,empty_mouths_and_occupied_rims_verified=True,
            source_export_geometry_agrees=True),
        reviewed_current_views={name:digest for name,digest in runtime['renders'].items() if name.startswith('verified-')},
        comparison_sha256=sha((media/'feedback-comparison.jpg').read_bytes()),
        limitations=['No exact original camera or recovered physical dimensions',
                    'Concept microdetail and surface wear simplified for gameplay',
                    'Final user artistic approval and game integration remain separate'])
    (out/'visual-feedback.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('ACHAEAN_VISUAL_FEEDBACK_BOUND',baseline['tip_span_over_hull_height'],'->',current['tip_span_over_hull_height'])


if __name__=='__main__':
    main()
