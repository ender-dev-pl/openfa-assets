"""Check current provenance, native alpha/palette and negative control cases."""
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image,ImageEnhance

ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def image_contract(image,size,colour=True):
    assert image.mode=='RGBA' and image.size==size,'RGBA dimensions'
    alpha=image.getchannel('A');assert alpha.getextrema()[0]==0,'transparent exterior required'
    box=alpha.point(lambda value:255 if value>=64 else 0).getbbox()
    assert box and box[0]>1 and box[1]>1 and box[2]<size[0]-1 and box[3]<size[1]-1,'clear border required'
    get_pixels=getattr(image,'get_flattened_data',image.getdata)
    pixels=[p for p in get_pixels() if p[3]>=128]
    assert len(pixels)>size[0]*size[1]*.08,'empty or unreadable glyph'
    if colour:
        assert sum(b>r*1.25 and b>g*1.15 for r,g,b,a in pixels)>=3,'blue yaw axis missing'
        assert sum(r>b*1.35 and g>b*1.1 and r>g for r,g,b,a in pixels)>=3,'gold pitch axis missing'


def main():
    report=json.loads((SOURCE/'catalog.json').read_text())
    for relative,digest in report['inputs'].items():assert sha(ROOT/relative)==digest,relative
    for key in ['blend','glb','preview']:
        row=report[key];assert sha(ROOT/row['path'])==row['sha256'],key
    for name,digest in report['renders'].items():
        path=ROOT/'gallery/media/ui/camera-mode-icon'/name
        assert sha(path)==digest,name
        image_contract(Image.open(path),(384,320))
    for resolution,files in report['files'].items():
        assert set(files)=={'normal','hover','selected','pressed','disabled'}
        size=tuple(report['native_size' if resolution=='native' else 'hires_size'])
        for state,row in files.items():
            assert sha(ROOT/row['path'])==row['sha256'],row['path']
            image_contract(Image.open(ROOT/row['path']),size,colour=state!='disabled')
    native=Image.open(ROOT/report['files']['native']['normal']['path'])
    # Recheck the actual semantic contract, independent of a checksum update.
    rejected=0
    for image in [Image.new('RGBA',(48,40),'white'),native.resize((40,40)),ImageEnhance.Color(native).enhance(0)]:
        try:image_contract(image,(48,40))
        except AssertionError:rejected+=1
    assert rejected==3
    print('CAMERA_ICON_CONTRACT_OK 10 PNG states; opaque, wrong-size and lost-axis-colour negative controls rejected')


if __name__=='__main__':main()
