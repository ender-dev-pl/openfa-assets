"""Measure matched unchanged-equipment renders without hiding export differences."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw, ImageStat

BASE = Path(__file__).resolve().parents[2] / 'docs/assets/reconstruction/evidence/early-equipment-runtime'


def main():
    evidence = json.loads((ROOT / 'runtime-audit.json').read_text())
    results = {}
    sheet = Image.new('RGB', (1536, 1600), (20, 25, 34))
    draw = ImageDraw.Draw(sheet)
    for row, view in enumerate(['front-quarter', 'rear-quarter']):
        images = []
        for column, kind in enumerate(['native', 'imported']):
            name = kind + '-' + view + '.png'
            path = ROOT / name
            assert hashlib.sha256(path.read_bytes()).hexdigest() == evidence['render_sha256'][name]
            image = Image.open(path).convert('RGBA')
            assert image.size == (768, 768)
            bounds = image.getchannel('A').getbbox()
            assert bounds and min(bounds[0], bounds[1], 768-bounds[2], 768-bounds[3]) >= 16
            sheet.paste(image, (column*768, row*800+24), image)
            draw.text((column*768+12, row*800+5), kind + ' ' + view, fill='white')
            images.append(image)
        a, b = images
        delta = ImageChops.difference(a, b)
        silhouette = ImageChops.difference(a.getchannel('A').point(lambda p: 255 if p >= 128 else 0),
                                         b.getchannel('A').point(lambda p: 255 if p >= 128 else 0))
        results[view] = dict(alpha_pixels_different=sum(v != 0 for v in delta.getchannel('A').tobytes()),
                             binary_silhouette_pixels_different=sum(v != 0 for v in silhouette.tobytes()),
                             foreground_mean_rgba_difference=ImageStat.Stat(delta, a.getchannel('A')).mean)
    sheet.save(ROOT / 'comparison.png')
    report = dict(issue=1103, reviewer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  runtime_audit_sha256=hashlib.sha256((ROOT/'runtime-audit.json').read_bytes()).hexdigest(),
                  comparisons=results, final_visual_acceptance=False,
                  scope='Actual matched-camera pixel differences; no final artistic or technical acceptance promotion.')
    (ROOT/'pixel-review.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(results, indent=2))


if __name__ == '__main__':
    for slug in ['photon-cannon', 'plasma-cannon', 'shield-x10', 'shield-x20', 'shield-x30', 'shield-x40', 'shield-x50']:
        ROOT = BASE / slug
        print(slug)
        main()

    slugs = ['photon-cannon', 'plasma-cannon', 'shield-x10', 'shield-x20', 'shield-x30', 'shield-x40', 'shield-x50']
    sheet = Image.new('RGB', (1536, 7*420), (20,25,34));draw = ImageDraw.Draw(sheet)
    for row, slug in enumerate(slugs):
        for col, name in enumerate(['native-front-quarter','imported-front-quarter','native-rear-quarter','imported-rear-quarter']):
            im = Image.open(BASE/slug/(name+'.png')).convert('RGBA').resize((384,384))
            sheet.paste(im,(col*384,row*420+30),im)
            draw.text((col*384+5,row*420+5),slug+' '+name,fill='white')
    sheet.save(BASE/'comparison-catalogue.png')
