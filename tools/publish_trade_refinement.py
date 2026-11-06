"""Publish independently verified, visually reviewed refined trading-good sources and PNGs."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib
from PIL import Image


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_png(path):
    raw = path.read_bytes()
    clean, pos = raw[:8], 8
    while pos < len(raw):
        length = struct.unpack_from('>I', raw, pos)[0]
        kind = raw[pos+4:pos+8]
        if kind in {b'IHDR', b'PLTE', b'tRNS', b'IDAT', b'IEND', b'sRGB', b'gAMA', b'cHRM', b'pHYs'}:
            clean += raw[pos:pos+12+length]
        pos += 12+length
    # Recompress the identical filtered scanline stream when this saves space.
    chunks = []
    pos = 8
    while pos < len(clean):
        length = struct.unpack_from('>I', clean, pos)[0]
        chunks.append((clean[pos+4:pos+8], clean[pos:pos+length+12]))
        pos += length+12
    original = b''.join(chunk[8:-4] for kind, chunk in chunks if kind == b'IDAT')
    packed = zlib.compress(zlib.decompress(original), 9)
    if len(packed) < len(original):
        assert zlib.decompress(packed) == zlib.decompress(original)
        replacement = struct.pack('>I', len(packed))+b'IDAT'+packed+struct.pack('>I', zlib.crc32(b'IDAT'+packed))
        first = True
        clean = clean[:8]
        for kind, chunk in chunks:
            if kind != b'IDAT':
                clean += chunk
            elif first:
                clean += replacement
                first = False
    return clean


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument('--renders', type=Path, required=True)
    ap.add_argument('--review', type=Path, required=True)
    ap.add_argument('--consume', action='store_true', help='Remove raw PNG duplicates after pixel-preserving installation; retain journals and receipts')
    a = ap.parse_args()
    root = a.repo.resolve()
    tools = root/'sources/tools/trading-goods/refining'
    coverage = json.loads((root/'docs/trading-goods/coverage.json').read_text())
    review = json.loads(a.review.read_text())
    assert set(review['reviewed_items']) == {f'TI{i:03d}' for i in range(1, 102)}
    selections_path = root/'docs/trading-goods/refinement-selections.json'
    selection_data = json.loads(selections_path.read_text()) if selections_path.exists() else {}
    selections = selection_data.get('overrides', {})
    renderers = selection_data.get('renderer_overrides', {})
    entries = []
    for item in coverage['items']:
        ident = item['legacy_stem']
        folder = root/selections[ident]['folder'] if ident in selections else root/'sources/docs/assets/reconstruction/trading-goods-refined'/ident
        native, glb = folder/(ident+'.blend'), folder/(ident+'.glb')
        built = json.loads((folder/'refinement.json').read_text())
        assert built['legacy_stem'] == ident and built['item_id'] == item['id'] and built['baseline_native'] == item['native'], ident
        verified = json.loads((folder/'runtime-validation.json').read_text())
        png = a.renders/(ident+'.png')
        rendered = json.loads(png.with_suffix('.json').read_text())
        out = root/'gallery/media/docs/assets/reconstruction/trading-goods-refined'/ident/'front-quarter.png'
        receipt_path = a.renders/(ident+'.published.json')
        raw_present = png.is_file()
        if not raw_present:
            receipt = json.loads(receipt_path.read_text())
            assert receipt['render_output_sha256'] == rendered['image_sha256'] and receipt['native_sha256'] == rendered['native_sha256'], ident
            assert receipt['image_sha256'] == sha(out), ident
            png = out
        assert built['baseline_native_sha256'] == sha(root/item['native']), ident
        assert built['builder_sha256'] == sha(tools/'refine.py'), ident
        for prefix in ['geometry','revision']:
            if prefix+'_builder' in built:
                assert built[prefix+'_builder_sha256'] == sha(root/built[prefix+'_builder']), ident
                assert built['prior_refined_native_sha256'] == sha(root/built['prior_refined_native']), ident
        assert built['refined_native_sha256'] == verified['native_sha256'] == rendered['native_sha256'] == sha(native), ident
        assert built['glb_sha256'] == verified['glb_sha256'] == sha(glb), ident
        assert verified['independent_glb_import'] and verified['base_colours_roundtrip_verified'], ident
        renderer = root/renderers[ident] if ident in renderers else tools/'render.py'
        reviewed = review['reviewed_images'][ident]
        assert reviewed['native_sha256'] == rendered['native_sha256'] and reviewed['image_sha256'] == rendered['image_sha256'], ident
        assert rendered['source_unchanged'] and rendered['renderer_sha256'] == sha(renderer), ident
        assert rendered['resolution'] == [1024, 768] and rendered['samples'] in [32,64], ident
        if raw_present:
            assert rendered['image_sha256'] == sha(png), ident
        with Image.open(png) as im:
            im.load()
            assert im.mode == 'RGBA' and im.size == (1024, 768)
            alpha = im.getchannel('A')
            assert alpha.getextrema() == (0, 255), ident
            # Faint shadows may cross frame edges; solid geometry must have a margin.
            box = alpha.point(lambda p: 255 if p > 245 else 0).getbbox()
            assert box and min(box[0], box[1], 1024-box[2], 768-box[3]) > 4, (ident, box)
            pixels = im.tobytes()
        out.parent.mkdir(parents=True, exist_ok=True)
        if raw_present:
            out.write_bytes(clean_png(png))
        else:
            # The receipt already proves this exact installed file preserves pixels.
            assert png == out
        with Image.open(out) as im:
            assert im.tobytes() == pixels
        entry = dict(legacy_stem=ident, item_id=item['id'], native=native.relative_to(root).as_posix(),
                     glb=glb.relative_to(root).as_posix(), image=out.relative_to(root).as_posix(),
                     **rendered, glb_sha256=sha(glb), baseline_native_sha256=built['baseline_native_sha256'],
                     builder_sha256=built['builder_sha256'], png_metadata_removed=True,
                     render_output_sha256=rendered['image_sha256'],
                     renderer=renderer.relative_to(root).as_posix(),material_roles=dict(Counter(m['role'] for m in built['materials'])))
        for key in ['geometry_builder','geometry_builder_sha256','revision_builder','revision_builder_sha256','prior_refined_native','prior_refined_native_sha256']:
            if key in built:
                entry[key] = built[key]
        entry['image_sha256'] = sha(out)
        receipt_path.write_text(json.dumps(dict(native_sha256=rendered['native_sha256'],render_output_sha256=rendered['image_sha256'],image_sha256=entry['image_sha256'],image=entry['image'],decoded_pixels_preserved=True),indent=2)+'\n')
        if a.consume and raw_present:
            png.unlink()
        entries.append(entry)
        item['refined_variant'] = dict(status='material_refined_png_verified',native=entry['native'],glb=entry['glb'],image=entry['image'],runtime_validation=(folder/'runtime-validation.json').relative_to(root).as_posix())
    coverage['refined_gallery_png_count'] = len(entries)
    coverage['material_refinement_delivery'] = '101 reviewed native-material variants and source-bound gallery PNGs; first pass preserved'
    (root/'docs/trading-goods/coverage.json').write_text(json.dumps(coverage,indent=2,ensure_ascii=False)+'\n')
    manifest = dict(count=len(entries), resolution=[1024, 768], sampling='32 samples for opaque goods; 64 for glass/gems; adaptive threshold 0.05 and denoising', original_sources_preserved=True,
                    material_delivery='Procedural PBR in editable natives; scalar/base-colour GLB fallback, not baked textures',
                    visual_review=review, items=entries)
    (root/'docs/trading-goods/refinement-validation.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('REFINED_TRADE_PUBLISHED', len(entries))


if __name__ == '__main__':
    main()
