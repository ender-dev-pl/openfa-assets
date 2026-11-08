"""Check actual final render/export integrity and canonical selection for issue 234."""
from pathlib import Path
import hashlib
import json
import struct
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OBJECT = 'objects/achaean/dedicated-ore-transporter'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'sources'/OBJECT
    media = ROOT/'gallery/media'/OBJECT
    runtime = json.loads((out/'runtime-verification.json').read_text())
    for ext in ['blend', 'glb']:
        assert sha(out/('model.'+ext)) == runtime[ext+'_sha256']
    for name, digest in runtime['renders'].items():
        assert sha(media/name) == digest, name
    native = np.array(Image.open(media/'verified-native.png').convert('RGBA')).astype(float)
    imported = np.array(Image.open(media/'verified-imported.png').convert('RGBA')).astype(float)
    a, b = native[:,:,3] > 128, imported[:,:,3] > 128
    iou = float(np.logical_and(a,b).sum()/np.logical_or(a,b).sum())
    error = float(np.abs(native[:,:,:3]-imported[:,:,:3])[a & b].mean())
    assert iou > .999 and error < .5, (iou, error)
    framing = {}
    for name in ['front-quarter', 'rear-quarter', 'front', 'side', 'top', 'underside']:
        alpha = np.array(Image.open(media/(name+'.png')).convert('RGBA'))[:,:,3] > 128
        ys, xs = np.where(alpha)
        margin = int(min(xs.min(), ys.min(), alpha.shape[1]-1-xs.max(), alpha.shape[0]-1-ys.max()))
        assert margin >= 1, (name, margin)
        framing[name] = margin
    data = (out/'model.glb').read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    gltf = json.loads(data[20:20+length])
    assert len(gltf['materials']) == 1 and len(gltf['images']) == 2
    assert all('bufferView' in image and 'uri' not in image for image in gltf['images'])
    triangles = sum(gltf['accessors'][p['indices']]['count']//3 for mesh in gltf['meshes'] for p in mesh['primitives'])
    assert triangles == runtime['triangles'] == 44856
    for key in ['native_witnesses', 'imported_witnesses']:
        assert runtime[key] == dict(empty_mouth_witnesses=8, occupied_rim_witnesses=8)
    inventory = json.loads((ROOT/'sources/docs/reconstruction/models/inventory.json').read_text())
    record = next(r for r in inventory['records'] if r['id'] == runtime['id'])
    assert len(record['available_studies']) == 1
    assert record['available_studies'][0]['blend'] == OBJECT+'/model.blend'
    historical = {}
    for study in record['superseded_studies']:
        assert study['historical_not_for_packaging']
        assert sha(ROOT/'sources'/study['blend']) == study['sha256']
        historical[study['blend']] = study['sha256']
    gallery = json.loads((ROOT/'gallery/catalogue.json').read_text())
    row = next(r for r in gallery if r['id'] == runtime['id'])
    assert len(row['studies']) == 1 and len(row['studies'][0]['views']) == 10
    assert row['studies'][0]['sha256'] == runtime['blend_sha256']
    review = dict(native_imported_alpha_iou=iou, foreground_rgb_mean_error_255=error,
        framing_margin_pixels=framing, embedded_images=2, materials=1, triangles=triangles,
        one_current_canonical_study=True, historical_sources_unchanged=historical,
        blend_sha256=runtime['blend_sha256'], glb_sha256=runtime['glb_sha256'],
        scope='Delivery integrity, not final artistic or client acceptance')
    (out/'delivery-review.json').write_bytes((json.dumps(review,indent=2)+'\n').encode())
    print('ACHAEAN_DELIVERY_REVIEWED', iou, error, 'RGB/255; all six full views unclipped')


if __name__ == '__main__':
    main()
