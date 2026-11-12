"""Package native/8x transparent HUD states and verify actual Blender imports."""
import hashlib
import json
from pathlib import Path
import sys
from PIL import Image,ImageDraw

ROOT=Path(__file__).resolve().parents[3]
SOURCE=Path(__file__).resolve().parent
MEDIA=ROOT/'gallery/media/ui/camera-mode-icon'
sys.path.insert(0,str(SOURCE.parent/'legacy-icon-set'))
from assemble_icon_set import variant,alpha_iou
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_png


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report=json.loads((SOURCE/'runtime-proof.json').read_text(encoding='utf-8'))
    for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
    for name,digest in report['renders'].items():assert sha(MEDIA/name)==digest,name
    native=Image.open(MEDIA/'native-render.png').convert('RGBA')
    for name in ['imported-glb.png','reopened-blend.png']:
        iou=alpha_iou(native,Image.open(MEDIA/name).convert('RGBA'))
        assert iou>.995,(name,iou)
        report['runtime'][name+'_alpha_iou']=iou
    files={}
    for size,multiplier in [('native',1),('hires',8)]:
        directory=MEDIA/'icons'/size;directory.mkdir(parents=True,exist_ok=True);files[size]={}
        for state in ['normal','hover','selected','pressed','disabled']:
            image=variant(native,state).resize((48*multiplier,40*multiplier),Image.Resampling.LANCZOS)
            if state=='pressed':
                shifted=Image.new('RGBA',image.size);shifted.alpha_composite(image,(multiplier,multiplier));image=shifted
            path=directory/('camera-mode-icon'+('' if state=='normal' else '-'+state)+'.png')
            image.save(path);path.write_bytes(clean_png(path.read_bytes()))
            box=image.getchannel('A').point(lambda value:255 if value>=64 else 0).getbbox()
            assert box and box[0]>1 and box[1]>1 and box[2]<image.width-1 and box[3]<image.height-1,box
            assert image.getpixel((0,0))[3]==0 and image.mode=='RGBA'
            files[size][state]=dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path),alpha_bounds=box)
    report['files']=files
    board=Image.new('RGBA',(660,280),(16,23,34,255));draw=ImageDraw.Draw(board)
    board.alpha_composite(native,(10,-20))
    for index,state in enumerate(files['native']):
        image=Image.open(ROOT/files['native'][state]['path']).convert('RGBA')
        board.alpha_composite(image,(390+(index%3)*82,35+(index//3)*100))
        draw.text((380+(index%3)*82,80+(index//3)*100),state,fill='white')
    path=MEDIA/'preview.png';board.save(path);path.write_bytes(clean_png(path.read_bytes()))
    report['preview']=dict(path=path.relative_to(ROOT).as_posix(),sha256=sha(path))
    report['inputs'][Path(__file__).relative_to(ROOT).as_posix()]=sha(Path(__file__))
    reference=ROOT/'gallery/media/ui/legacy-icon-set/verification.json'
    provenance=json.loads(reference.read_text())['reference_provenance']
    report['style_reference']['original_source_sha256']={name:provenance['sources'][name]['sha256'] for name in ['ICONS','BLUE']}
    report['inputs'][reference.relative_to(ROOT).as_posix()]=sha(reference)
    (SOURCE/'catalog.json').write_bytes((json.dumps(report,indent=2)+'\n').encode())
    print('CAMERA_MODE_ICON_VERIFIED',report['runtime'],flush=True)


if __name__=='__main__':main()
