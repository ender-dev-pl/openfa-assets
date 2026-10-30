"""Bind an in-memory proposal to exact unchanged sources and compare actual render pixels."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/detail-uv-proposal'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = []
    for slug in ['strategic-bunker', 'ultrathermal-lance']:
        path = OUTPUT/(slug+'.json')
        report = json.loads(path.read_text())
        folder = REPO/'docs/assets/reconstruction/buildings/rigellian'/slug
        assert report['saved_source_files_unchanged'] and not report['exported_or_saved_model']
        assert report['final_visual_acceptance'] is False
        assert report['proposal_script_sha256'] == sha(Path(__file__).with_name('audit_detail_uv_proposal.py'))
        current_helper = Path(__file__).with_name('repair_detail_uvs.py')
        if report['helper_sha256'] != sha(current_helper):
            assert report['helper_sha256'] == sha(OUTPUT/'repair_detail_uvs-baseline.py')
        baseline_current = report['source_files_sha256'] == {p.name: sha(p) for p in folder.iterdir() if p.is_file()}
        superseded = None
        if not baseline_current:
            # A historical proposal is not current-source verification. Its replacement must
            # bind both the complete recorded baseline and the exact repaired native/export.
            repair_path = REPO/'docs/assets/reconstruction/evidence/detail-uv-repair'/(slug+'.json')
            repair = json.loads(repair_path.read_text())
            assert repair['before_source_files_sha256'] == report['source_files_sha256']
            assert repair['exact_native_geometry_before_and_after'] == report['exact_native_geometry_before_and_after']
            assert repair['packed_images_before_and_after'] == report['packed_images_before_and_after']
            assert repair['blend_sha256'] == sha(folder/'model.blend')
            assert repair['glb_sha256'] == sha(folder/'model.glb')
            assert repair['saved_native_reopened'] and repair['idempotent']
            superseded = str(repair_path.relative_to(REPO)).replace('\\', '/')
        for name, digest in report['preview_files'].items():
            assert sha(REPO/name) == digest
        images = [Image.open(OUTPUT/'previews'/(slug+'-'+kind+'.png')).convert('RGBA')
                  for kind in ['before', 'proposed']]
        before, after = images
        assert before.size == after.size == (900, 900)
        difference = ImageChops.difference(before, after)
        assert difference.getchannel('A').getbbox() is None, 'UV-only proposal changed silhouette/alpha'
        rgb = difference.convert('RGB')
        box = rgb.getbbox()
        assert box is not None, 'Expected texture-coordinate appearance change is invisible'
        sheet = Image.new('RGB', (1000, 550), (20, 25, 34))
        draw = ImageDraw.Draw(sheet)
        for index, (image, label) in enumerate(zip(images, ['Current saved source', 'In-memory UV proposal'])):
            draw.text((index*500+12, 12), label, fill='white')
            background = Image.new('RGBA', image.size, (20, 25, 34, 255))
            background.alpha_composite(image)
            sheet.paste(background.convert('RGB').resize((500, 500)), (index*500, 35))
        gallery = OUTPUT/(slug+'-comparison.png')
        sheet.save(gallery)
        rows.append(dict(id=report['id'], report=path.name, report_sha256=sha(path),
                         alpha_identical=True, rgb_difference_bounds=box,
                         foreground_mean_rgb_difference=ImageStat.Stat(rgb, before.getchannel('A')).mean,
                         comparison=gallery.name, comparison_sha256=sha(gallery),
                         baseline_source_files_unchanged_at_proposal=True,
                         current_sources_match_baseline=baseline_current,
                         superseded_by_repair=superseded, exported_or_saved_model=False))
        for image in images:
            image.close()
    summary = dict(issue=1111, checker_sha256=sha(Path(__file__)), records=rows,
                   final_visual_acceptance=False, applied=False,
                   scope='Historical read-only native Blender proposal. Separately bound repaired sources are identified explicitly; these proposal renders do not verify the repaired GLB.')
    (OUTPUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print('DETAIL_UV_PROPOSAL_EVIDENCE_OK', len(rows))


if __name__ == '__main__':
    main()
