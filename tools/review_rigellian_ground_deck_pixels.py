"""Recompute RI10 paired pixels after actual source/export verification."""
import hashlib
import json
import struct
from pathlib import Path
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'sources/objects/rigellian/ground-deck'
MEDIA=ROOT/'gallery/media/objects/rigellian/ground-deck'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    meta=json.loads((FOLDER/'model.json').read_bytes())
    runtime=json.loads((FOLDER/'runtime-review.json').read_bytes())
    assert meta['binaries']==runtime['binaries']
    raw=(FOLDER/'model.glb').read_bytes()
    document=json.loads(raw[20:20+struct.unpack_from('<I',raw,12)[0]])
    assert sum(document['accessors'][p['indices']]['count']//3 for mesh in document['meshes'] for p in mesh['primitives'])==meta['triangles']==19010
    assert runtime['protected_surface_error']<1e-6
    comparisons={}
    for name in runtime['renders']:
        if not name.startswith('imported-'):
            continue
        native='native-'+name.removeprefix('imported-')
        a,b=[np.asarray(Image.open(MEDIA/path).convert('RGBA'),dtype=np.int16) for path in [native,name]]
        assert a.shape==b.shape
        difference=np.abs(a-b)
        mask=np.maximum(a[:,:,3],b[:,:,3])>127
        yy,xx=np.where(mask)
        margin=int(min(xx.min(),yy.min(),a.shape[1]-1-xx.max(),a.shape[0]-1-yy.max()))
        mean=difference.mean(axis=(0,1)).tolist()
        foreground=difference[mask].mean(axis=0).tolist()
        assert max(mean)<1 and max(foreground)<2 and margin>12,(name,mean,foreground,margin)
        assert np.array_equal(a[:,:,3],b[:,:,3])
        comparisons[name.removeprefix('imported-').removesuffix('.png')]=dict(mean_absolute_rgba_255=mean,
            foreground_mean_rgba_255=foreground,alpha_equal=True,threshold_silhouette_equal=True,margin=margin)
    assert len(comparisons)==20
    # Concept/reference feedback is preserved; only verified regenerated render
    # comparisons and their current source bindings replace the old evidence.
    review=json.loads((FOLDER/'visual-review.json').read_bytes())
    review['binaries']=meta['binaries']
    review['runtime_report_sha256']=sha(FOLDER/'runtime-review.json')
    review['comparisons']=comparisons
    review['feedback']=[text for text in review['feedback'] if not text.startswith('Final budget audit:')]
    review['feedback'].append('Final budget audit: 13,170 raw pre-modifier triangles had understated the runtime budget. Evaluated native/imported geometry and actual GLB index accessors now agree at19,010. No source anatomy or mechanism change; all40actual renders and both imported-GLB previews regenerated before rebinding.')
    (FOLDER/'visual-review.json').write_bytes((json.dumps(review,indent=2)+'\n').encode())
    print('RI10_CURRENT_PAIRED_PIXELS_VERIFIED',len(comparisons),max(max(r['foreground_mean_rgba_255']) for r in comparisons.values()))


if __name__=='__main__':
    main()
