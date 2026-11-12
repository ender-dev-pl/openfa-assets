"""Bound deliverable regression: source hashes, decoded renders, clip and instancing."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def gltf(p):
    data=p.read_bytes();assert data[:4]==b'glTF';return json.loads(data[20:20+struct.unpack_from('<I',data,12)[0]])


def main():
    for name in ['interceptor','decoy']:
        folder=ROOT/'sources/objects/extensions/munitions'/name;media=ROOT/'gallery/media/objects/extensions/munitions'/name;r=json.loads((folder/'runtime-verification.json').read_text())
        for n,digest in r['binaries'].items():assert sha(folder/n)==digest
        assert r['generator_sha256']==sha(ROOT/'sources/tools/blender/author_extension_missiles.py')
        assert r['verifier_sha256']==sha(ROOT/'sources/tools/blender/verify_extension_missiles.py')
        for n,digest in r['renders'].items():assert sha(media/n)==digest
        a=np.asarray(Image.open(media/'verified-native.png').convert('RGBA')).astype(float);b=np.asarray(Image.open(media/'verified-imported.png').convert('RGBA')).astype(float)
        ma=a[:,:,3]>128;mb=b[:,:,3]>128;iou=float((ma&mb).sum()/(ma|mb).sum());error=float(abs(a[:,:,:3]-b[:,:,:3])[ma&mb].mean());assert iou>.999 and error<.5,(name,iou,error)
        for n in ['verified-imported.png','verified-front.png']+(['separated.png','segment.png'] if name=='decoy' else []):
            im=np.asarray(Image.open(media/n).convert('RGBA'));yy,xx=np.where(im[:,:,3]>128);assert min(xx.min(),yy.min(),im.shape[1]-1-xx.max(),im.shape[0]-1-yy.max())>8,(name,n,'clipped')
        g=gltf(folder/'model.glb');mesh_nodes=[n for n in g['nodes'] if 'mesh' in n];assert len(g['materials'])==1 and len(g['images'])==2 and all('bufferView' in i for i in g['images'])
        if name=='decoy':
            assert len(mesh_nodes)==4 and len({n['mesh'] for n in mesh_nodes})==1
            assert len(g['animations'])==1 and g['animations'][0]['name']=='DecoyMenuSeparation'
            translations=[c for c in g['animations'][0]['channels'] if c['target']['path']=='translation'];assert len(translations)==4
            segment=gltf(folder/'segment.glb');assert len([n for n in segment['nodes'] if 'mesh' in n])==1 and not segment.get('animations')
            clip=r['animation_preview'];assert sha(ROOT/clip['video'])==clip['sha256'] and clip['distinct_pose_count']>100
            result=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate,nb_read_frames','-of','json',str(ROOT/clip['video'])]));stream=result['streams'][0]
            assert stream['nb_read_frames']=='144' and stream['r_frame_rate']=='24/1' and stream['width']==stream['height']==512
        else:
            assert len(mesh_nodes)==1 and not g.get('animations')
            bounds=r['native_bounds'];ratio=(bounds[0][1]-bounds[0][0])/(bounds[1][1]-bounds[1][0])
            assert .27<ratio<.31,('Reference artwork fin span/length approximately0.29',ratio)
        (folder/'delivery-review.json').write_text(json.dumps(dict(alpha_iou=iou,mean_rgb_error_255=error,binaries=r['binaries'],review='Actual imported renders, reference identity and continuous clip phases reviewed; user/client acceptance separate'),indent=2)+'\n')
        print('EXTENSION_DELIVERY_OK',name,iou,error)


if __name__=='__main__':main()
