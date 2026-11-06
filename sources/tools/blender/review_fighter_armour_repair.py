"""Bind original framing checks and current before/after/native/import fighter pixels."""
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from review_assault_fighter import main as original_review, tile
import hashlib

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO/'docs/assets/reconstruction/ships/terran/assault-fighter'
OUTPUT = REPO/'docs/assets/reconstruction/evidence/fighter-armour-repair'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compare(a_path, b_path):
    with Image.open(a_path).convert('RGBA') as a, Image.open(b_path).convert('RGBA') as b:
        assert a.size == b.size == (768, 768)
        delta = ImageChops.difference(a, b)
        mask_a = a.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
        mask_b = b.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
        return dict(foreground_mean_rgba_difference=ImageStat.Stat(delta, a.getchannel('A')).mean,
            binary_silhouette_different_pixels=sum(v != 0 for v in ImageChops.difference(mask_a, mask_b).tobytes()),
            alpha_difference_maximum=delta.getchannel('A').getextrema()[1])


def main():
    original_review()
    meta = json.loads((SOURCE/'model.json').read_text())
    proposal = json.loads((OUTPUT/'proposal.json').read_text())
    applied = json.loads((OUTPUT/'applied.json').read_text())
    technical = json.loads((SOURCE/'technical-review.json').read_text())
    assert meta['blend_sha256'] == applied['blend_sha256'] == technical['blend_sha256'] == sha(SOURCE/'model.blend')
    assert meta['glb_sha256'] == applied['glb_sha256'] == technical['glb_sha256'] == sha(SOURCE/'model.glb')
    before_after, roundtrip, hashes, margins = {}, {}, {}, {}
    names = meta['views'] + ['imported-glb-'+view for view in meta['views']] + ['directions/'+f'{i:02}' for i in range(32)]
    for name in names:
        path = SOURCE/(name+'.png')
        with Image.open(path) as image:
            assert image.size == (768, 768) and image.mode == 'RGBA' and image.getextrema()[3] == (0, 255)
            box = image.getchannel('A').getbbox()
            margins[name] = min(box[0], box[1], 768-box[2], 768-box[3])
            assert margins[name] >= 20
        hashes[name] = sha(path)
    for view in ['front-quarter', 'top', 'side', 'belly']:
        before = OUTPUT/('proposal-'+view+'-before.png')
        assert sha(before) == proposal['renders'][before.name]
        before_after[view] = compare(before, SOURCE/(view+'.png'))
        assert before_after[view]['binary_silhouette_different_pixels'] == 0, 'Technical repair changed silhouette: '+view
    for view in meta['views']:
        roundtrip[view] = compare(SOURCE/(view+'.png'), SOURCE/('imported-glb-'+view+'.png'))
        assert roundtrip[view]['binary_silhouette_different_pixels'] == 0
        assert max(roundtrip[view]['foreground_mean_rgba_difference'][:3]) < 1.5
    sheet = Image.new('RGB', (1536, 1024), (20, 25, 34))
    draw = ImageDraw.Draw(sheet)
    for index, view in enumerate(['front-quarter', 'top']):
        for column, (path, label) in enumerate([(OUTPUT/('proposal-'+view+'-before.png'), 'Previous'),
                                               (SOURCE/(view+'.png'), 'Connectivity repair'),
                                               (SOURCE/('imported-glb-'+view+'.png'), 'Actual GLB import')]):
            x, y = column*512, index*512
            draw.text((x+12, y+6), view+' / '+label, fill='white')
            sheet.paste(tile(path, (512, 480)), (x, y+24))
    sheet.save(OUTPUT/'comparison.png')
    report = dict(issue=1108, id=meta['id'], revision=meta['revision'], blend_sha256=meta['blend_sha256'],
        glb_sha256=meta['glb_sha256'], reviewer_sha256=sha(Path(__file__)),
        original_reviewer_sha256=sha(Path(__file__).with_name('review_assault_fighter.py')),
        view_hashes=hashes, margins=margins, alpha=True, before_after=before_after, native_imported=roundtrip,
        final_visual_acceptance=False,
        scope='Current source/import framing and measured image differences. No final art, calibrated heading or game integration acceptance.')
    (SOURCE/'render-review.json').write_text(json.dumps(report, indent=2)+'\n')
    print('FIGHTER_ARMOUR_RENDER_REVIEW_OK', len(hashes), flush=True)


if __name__ == '__main__':
    main()
