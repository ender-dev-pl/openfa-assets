"""Inspect actual native/import images and make a public authored-only review sheet."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    source = ROOT/'sources/objects/shared/federal-transporter/refined'
    media = ROOT/'gallery/media/objects/shared/federal-transporter/refined'
    proof = json.loads((source/'runtime-verification.json').read_text())
    for filename, digest in proof['renders'].items():
        assert sha(media/filename) == digest
    a = np.asarray(Image.open(media/'verified-native-side.png').convert('RGBA')).astype(float)
    b = np.asarray(Image.open(media/'verified-imported-side.png').convert('RGBA')).astype(float)
    first, second = a[:, :, 3] >= 128, b[:, :, 3] >= 128
    overlap, union = first & second, first | second
    iou = float(overlap.sum()/union.sum())
    assert iou > .999, iou
    mean = float(np.abs(a[:, :, :3]-b[:, :, :3])[overlap].mean())
    assert np.isfinite(mean)
    views = ['front-quarter', 'legacy-side', 'rear-quarter', 'top', 'underside', 'rear',
             'cargo-detail', 'bridge-detail', 'verified-native-side', 'verified-imported-side']
    sheet = Image.new('RGB', (1400, 5*330), '#10161d')
    draw = ImageDraw.Draw(sheet)
    for index, name in enumerate(views):
        picture = Image.open(media/(name+'.png')).convert('RGBA')
        alpha = picture.getchannel('A')
        assert alpha.getbbox(), name
        crop = picture.crop(alpha.getbbox())
        thumb = ImageOps.contain(crop, (670, 292), Image.Resampling.LANCZOS)
        x, y = (index % 2)*700+(700-thumb.width)//2, (index//2)*330
        sheet.paste(thumb, (x, y), thumb)
        draw.text(((index % 2)*700+12, y+303), name, fill='#c2d2df')
    sheet.save(media/'review.jpg', quality=94)
    report = dict(issue=215, blend_sha256=sha(source/'model.blend'), glb_sha256=sha(source/'model.glb'),
                  mean_foreground_rgb_absolute_difference_255=mean, alpha_maximum_difference=float(np.abs(a[:, :, 3]-b[:, :, 3]).max()),
                  threshold_128_silhouette_iou=iou, view_count=len(views), review_sha256=sha(media/'review.jpg'),
                  interpretation='Geometry silhouette comparison and actual rendered colour difference; not an original-game fidelity percentage. Native and imported shading can differ.')
    (source/'pixel-review.json').write_text(json.dumps(report, indent=2)+'\n')
    print('FEDERAL_PIXEL_REVIEW', json.dumps(report))


if __name__ == '__main__':
    main()
