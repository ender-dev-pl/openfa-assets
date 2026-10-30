"""Bind the applied UV-only repair to its unchanged baseline and current runtime reports."""
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/detail-uv-repair'
PROPOSAL = OUTPUT.with_name('detail-uv-proposal')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows = []
    for slug in ['strategic-bunker', 'ultrathermal-lance']:
        folder = REPO/'docs/assets/reconstruction/buildings/rigellian'/slug
        path = OUTPUT/(slug+'.json')
        repair = json.loads(path.read_text())
        proposal = json.loads((PROPOSAL/(slug+'.json')).read_text())
        meta = json.loads((folder/'model.json').read_text())
        technical = json.loads((folder/'technical-review.json').read_text())
        renders = json.loads((folder/'render-review.json').read_text())
        assert repair['before_source_files_sha256'] == proposal['source_files_sha256']
        assert repair['exact_native_geometry_before_and_after'] == proposal['exact_native_geometry_before_and_after']
        assert repair['packed_images_before_and_after'] == proposal['packed_images_before_and_after']
        assert repair['changes'] == proposal['changes']
        assert repair['revision'] == meta['revision'] == technical['revision'] == renders['revision']
        assert repair['saved_native_reopened'] and repair['idempotent'] and repair['final_visual_acceptance'] is False
        assert repair['repair_script_sha256'] == sha(REPO/'tools/blender/apply_detail_uv_repair.py')
        assert repair['helper_sha256'] == meta['helper_sha256']['repair_detail_uvs.py'] == sha(REPO/'tools/blender/repair_detail_uvs.py')
        for ext in ['blend', 'glb']:
            assert repair[ext+'_sha256'] == meta[ext+'_sha256'] == technical[ext+'_sha256'] == sha(folder/('model.'+ext))
        assert renders['blend_sha256'] == meta['blend_sha256']
        roundtrip_path = OUTPUT/(slug+'-roundtrip.json')
        roundtrip = json.loads(roundtrip_path.read_text())
        assert roundtrip['verifier_sha256'] == sha(REPO/'tools/blender/verify_detail_uv_roundtrip.py')
        assert roundtrip['blend_sha256'] == meta['blend_sha256'] and roundtrip['glb_sha256'] == meta['glb_sha256']
        assert roundtrip['source_assets_unchanged'] and roundtrip['details'] == list(repair['uv_checks'])
        for value in roundtrip['corner_uv_comparison'].values():
            assert value['bidirectional_shader_uv_material_corner_coverage']
            assert value['maximum_position_error'] <= 1e-5 and value['maximum_uv_error'] <= 1e-5
        detail_native_path = OUTPUT/(slug+'-detail-native.png')
        detail_imported_path = OUTPUT/(slug+'-detail-imported.png')
        assert sha(detail_native_path) == roundtrip['native_render_sha256']
        assert sha(detail_imported_path) == roundtrip['imported_render_sha256']
        with Image.open(detail_native_path) as a, Image.open(detail_imported_path) as b:
            delta = ImageChops.difference(a, b)
            detail_mean = ImageStat.Stat(delta, a.getchannel('A')).mean
            detail_alpha = delta.getchannel('A')
            a_mask = a.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
            b_mask = b.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
            detail_measurement = dict(foreground_mean_rgba_difference=detail_mean,
                alpha_different_pixels=sum(v != 0 for v in detail_alpha.tobytes()),
                maximum_alpha_difference=detail_alpha.getextrema()[1],
                threshold128_silhouette_different_pixels=sum(v != 0 for v in ImageChops.difference(a_mask, b_mask).tobytes()),
                scope='Diagnostic measurements of isolated detail shading, not a full shader/artistic equivalence claim')
        for name, digest in renders['view_hashes'].items():
            assert sha(folder/(name+'.png')) == digest
        for name, digest in repair['before_source_files_sha256'].items():
            if name.startswith('authored-'):
                assert sha(folder/name) == digest, 'Authored wear changed during UV repair'
        before = Image.open(PROPOSAL/'previews'/(slug+'-before.png')).convert('RGBA')
        after = Image.open(folder/'front-quarter.png').convert('RGBA')
        difference = ImageChops.difference(before, after)
        silhouette_before = before.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
        silhouette_after = after.getchannel('A').point(lambda v: 255 if v >= 128 else 0)
        assert ImageChops.difference(silhouette_before, silhouette_after).getbbox() is None
        sheet = Image.new('RGB', (1000, 550), (20, 25, 34))
        draw = ImageDraw.Draw(sheet)
        for index, (image, label) in enumerate([(before, 'Previous saved source'), (after, 'Applied UV-only repair')]):
            draw.text((index*500+12, 12), label, fill='white')
            background = Image.new('RGBA', image.size, (20, 25, 34, 255))
            background.alpha_composite(image)
            sheet.paste(background.convert('RGB').resize((500, 500)), (index*500, 35))
        gallery = OUTPUT/(slug+'-comparison.png')
        sheet.save(gallery)
        rows.append(dict(id=meta['id'], revision=meta['revision'], report=path.name, report_sha256=sha(path),
            model_json_sha256=sha(folder/'model.json'), technical_report_sha256=sha(folder/'technical-review.json'),
            render_report_sha256=sha(folder/'render-review.json'), comparison=gallery.name, comparison_sha256=sha(gallery),
            native_binary_silhouette_unchanged=True,
            native_before_after_foreground_mean_rgba_difference=ImageStat.Stat(difference, before.getchannel('A')).mean,
            native_imported_render_difference=renders['native_glb_foreground_mean_rgba_difference'],
            detail_roundtrip_report_sha256=sha(roundtrip_path), isolated_detail_render_measurement=detail_measurement,
            repaired_details=list(repair['uv_checks'])))
        before.close()
        after.close()
    (OUTPUT/'findings.json').write_text(json.dumps(dict(issue=1111, checker_sha256=sha(Path(__file__)), records=rows,
        applied=True, final_visual_acceptance=False,
        scope='UV-only technical repair with actual native/GLB checks. No artistic refining, new wear, state or game integration acceptance.'), indent=2)+'\n')
    print('DETAIL_UV_REPAIR_EVIDENCE_OK', len(rows), flush=True)


if __name__ == '__main__':
    main()
