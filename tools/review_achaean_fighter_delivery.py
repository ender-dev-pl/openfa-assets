"""Check bound actual outputs and create a concept/current-export comparison."""
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import numpy as np
from PIL import Image,ImageOps,ImageDraw

ROOT=Path(__file__).resolve().parents[1]
OBJECT='objects/achaean/dedicated-fighter'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out=ROOT/'sources'/OBJECT;media=ROOT/'gallery/media'/OBJECT;r=json.loads((out/'runtime-verification.json').read_text())
    for kind in ['blend','glb']:assert sha(out/f'model.{kind}')==r[kind+'_sha256']
    for name,digest in r['renders'].items():assert sha(media/name)==digest,name
    a=np.array(Image.open(media/'verified-native.png').convert('RGBA')).astype(float)
    b=np.array(Image.open(media/'verified-imported.png').convert('RGBA')).astype(float)
    ma,mb=a[:,:,3]>128,b[:,:,3]>128;iou=float((ma&mb).sum()/(ma|mb).sum());error=float(abs(a[:,:,:3]-b[:,:,:3])[ma&mb].mean())
    assert iou>.999 and error<.5,(iou,error)
    framing={}
    for name in ['front-quarter','rear-quarter','front','side','top','underside']:
        im=np.array(Image.open(media/(name+'.png')).convert('RGBA'));ys,xs=np.where(im[:,:,3]>128)
        margin=int(min(xs.min(),ys.min(),im.shape[1]-1-xs.max(),im.shape[0]-1-ys.max()));assert margin>0,(name,margin);framing[name]=margin
    data=(out/'model.glb').read_bytes();g=json.loads(data[20:20+struct.unpack_from('<I',data,12)[0]])
    assert len(g['materials'])==1 and len(g['images'])==2 and all('bufferView' in im for im in g['images'])
    assert sum(g['accessors'][p['indices']]['count']//3 for m in g['meshes'] for p in m['primitives'])==r['triangles']<60000
    assert not g.get('animations')
    subprocess.run(['git','diff','--exit-code','75d68fc7','--','sources/objects/achaean/dedicated-ore-transporter',
                    'sources/tools/blender/remaster_achaean_transporter.py','sources/materials/achaean/dedicated-ore-transporter'],cwd=ROOT,check=True,capture_output=True)
    board=Image.new('RGB',(1600,650),(18,21,25));draw=ImageDraw.Draw(board)
    for i,(name,label) in enumerate([('concept.png','Artistic concept3 - inset proportions unresolved'),('verified-imported.png','Actual independently imported GLB')]):
        im=Image.open(media/name).convert('RGBA');im=im.crop(im.getchannel('A').getbbox());im=ImageOps.contain(im,(770,580));bg=Image.new('RGBA',im.size,(18,21,25,255));bg.alpha_composite(im);board.paste(bg.convert('RGB'),(i*800+(800-im.width)//2,45+(580-im.height)//2));draw.text((i*800+12,15),label,fill=(235,237,240))
    board.save(media/'concept-model-comparison.jpg',quality=92)
    report=dict(id=r['id'],blend_sha256=r['blend_sha256'],glb_sha256=r['glb_sha256'],alpha_iou=iou,
        mean_foreground_rgb_error_255=error,framing_margin_pixels=framing,triangles=r['triangles'],materials=1,packed_maps=2,
        prior_transporter_unchanged=True,visual_feedback='Legacy end/side views corrected hull fullness, distal arm flare and excessive lateral wing spacing; concept3 inset remains unresolved and is excluded from geometric authority',
        concept_model_comparison_sha256=sha(media/'concept-model-comparison.jpg'),
        acceptance='Agent-reviewed characteristic silhouette/colour/negative spaces; final user/client acceptance separate')
    (out/'delivery-review.json').write_bytes((json.dumps(report,indent=2)+'\n').encode());print('FIGHTER_DELIVERY_REVIEWED',iou,error)


if __name__=='__main__':main()
