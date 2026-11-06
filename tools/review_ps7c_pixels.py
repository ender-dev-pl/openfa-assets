"""Read real renders, compare native/imported silhouettes and assemble authored review."""
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    cells, reports = [], []
    for variant in ['refined', 'construction']:
        folder = ROOT/'sources/objects/terran/space-dock'/variant
        media = ROOT/'gallery/media/objects/terran/space-dock'/variant
        proof = json.loads((folder/'runtime-verification.json').read_text())
        for suffix in ['blend', 'glb']:
            assert sha(folder/('model.'+suffix)) == proof[suffix+'_sha256']
        for name, digest in proof['renders'].items():
            assert sha(media/name) == digest
        native = np.asarray(Image.open(media/'verified-native.png').convert('RGBA')).astype(float)
        imported = np.asarray(Image.open(media/'verified-imported.png').convert('RGBA')).astype(float)
        a, b = native[:, :, 3] >= 128, imported[:, :, 3] >= 128
        overlap, union = a & b, a | b
        iou = float(overlap.sum()/union.sum())
        assert iou > .998, (variant, iou)
        mean = float(np.abs(native[:, :, :3]-imported[:, :, :3])[overlap].mean())
        report = dict(issue=216, variant=variant, blend_sha256=proof['blend_sha256'], glb_sha256=proof['glb_sha256'],
                      silhouette_iou_threshold_128=iou, mean_foreground_rgb_difference_255=mean,
                      alpha_maximum_difference=float(np.abs(native[:, :, 3]-imported[:, :, 3]).max()),
                      interpretation='Render comparison, not a measured legacy-fidelity percentage; native/import shader differences reported honestly')
        (folder/'pixel-review.json').write_text(json.dumps(report, indent=2)+'\n')
        reports.append(report)
        for view in ['front-quarter', 'legacy-front', 'rear-quarter', 'top', 'underside', 'verified-imported']:
            picture = Image.open(media/(view+'.png')).convert('RGBA')
            crop = picture.crop(picture.getchannel('A').getbbox())
            crop.thumbnail((488, 568), Image.Resampling.LANCZOS)
            cell = Image.new('RGB', (512, 608), '#111821')
            cell.paste(crop, ((512-crop.width)//2, (568-crop.height)//2), crop)
            ImageDraw.Draw(cell).text((12, 582), variant+' / '+view, fill='#d0dce7')
            cells.append(cell)
    sheet = Image.new('RGB', (512*4, 608*3), '#111821')
    for i, cell in enumerate(cells):
        sheet.paste(cell, ((i%4)*512, (i//4)*608))
    output = ROOT/'gallery/media/objects/terran/space-dock/refined/review.jpg'
    sheet.save(output, quality=94)
    print('PS7C_PIXEL_REVIEW', json.dumps(reports))


if __name__ == '__main__':
    main()
