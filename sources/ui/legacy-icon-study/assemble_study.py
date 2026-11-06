"""Assemble original-file references and Blender study without modifying game assets."""
import json
import hashlib
import argparse
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageEnhance,ImageChops


def portable_font(size):
    """Resolve installed fonts without a machine-specific filesystem path."""
    for name in ('arial.ttf', 'segoeui.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('workspace',type=Path)
parser.add_argument('--legacy-root',required=True,type=Path)
args=parser.parse_args()
ROOT=args.workspace.resolve()
OUT=ROOT/'preview';OUT.mkdir(exist_ok=True)
RENDERS=ROOT/'renders'
font=portable_font(19)
small=portable_font(14)
title=portable_font(28)
items=[('missile','Rakieta',17),('fleet','Flota',16),('funds','Finanse',21),('construction','Budowa',10),('scitek','Sci-Tek',None)]


def keyed(path):
    im=Image.open(path).convert('RGBA')
    im.putdata([(r,g,b,0 if r>230 and b>230 and g<25 else a) for r,g,b,a in im.getdata()])
    return im


def original(name,frame):
    if frame is None:
        return keyed(ROOT/'reference/BUTTONS/002.png').crop((4,3,88,30))
    base=keyed(ROOT/'reference/BUTTONS/000.png').crop((0,0,49,36))
    icon=Image.open(ROOT/f'reference/ICONS/{frame:03}.png').convert('RGBA').crop((0,0,48,36))
    base.alpha_composite(icon,(0,0))
    return base


def paste_center(canvas,im,x,y,w,h):
    canvas.alpha_composite(im,(x+(w-im.width)//2,y+(h-im.height)//2))


board=Image.new('RGBA',(1160,840),(18,22,31,255));draw=ImageDraw.Draw(board)
draw.text((30,22),'OpenFA3D | proba ikon na podstawie oryginalnych plikow legacy',font=title,fill='white')
draw.text((30,62),'Referencje: _MS/ICONS.256 + BLUE.256; przyciski: _MS/BUTTONS.256. Bez wzorow z porownania starego HUD.',font=small,fill=(172,183,201))
draw.text((30,111),'ORYGINAL LEGACY - powiekszenie x4 (Sci-Tek x2)',font=font,fill=(224,192,124))
draw.text((30,330),'PROBA Z BLENDERA - sprite powiekszony x4 (Sci-Tek x2)',font=font,fill=(157,184,255))
draw.text((30,550),'ROZMIAR NATYWNY - normal / hover / selected / pressed / disabled',font=font,fill='white')
records=[]
gallery=Image.new('RGBA',(1160,590),(18,22,31,255));gd=ImageDraw.Draw(gallery)
gd.text((30,22),'Legacy UI icon study | new Blender geometry',font=title,fill='white')
gd.text((30,65),'Missile / fleet / funds / construction / Sci-Tek. Original-file references; no legacy textures.',font=small,fill=(172,183,201))
button_art=Image.open(RENDERS/'button.png').convert('RGBA')
button_art=button_art.crop(button_art.getbbox()).resize((48,36),Image.Resampling.LANCZOS)
button=Image.new('RGBA',(48,40));button.alpha_composite(button_art,(0,2))
for i,(name,label,frame) in enumerate(items):
    x=30+i*225
    draw.text((x,150),label,font=font,fill='white')
    ref=original(name,frame)
    if frame is None:
        ref_large=ref.resize((168,54),Image.Resampling.NEAREST)
    else:ref_large=ref.resize((196,144),Image.Resampling.NEAREST)
    paste_center(board,ref_large,x,180,210,140)
    art=Image.open(RENDERS/(name+'.png')).convert('RGBA')
    detail=art.copy();detail.thumbnail((210,190),Image.Resampling.LANCZOS)
    paste_center(gallery,detail,x,110,210,190)
    gd.text((x,305),name.capitalize(),font=font,fill='white')
    imported=Image.open(RENDERS/(name+'-imported.png')).convert('RGBA')
    a=art.getchannel('A').point(lambda v:255 if v>=128 else 0)
    b=imported.getchannel('A').point(lambda v:255 if v>=128 else 0)
    intersection=sum(v>0 for v in ImageChops.darker(a,b).getdata())
    union=sum(v>0 for v in ImageChops.lighter(a,b).getdata())
    iou=intersection/union if union else 0
    if iou<.995:raise RuntimeError(f'GLB silhouette mismatch {name}: {iou}')
    if frame is None:
        bbox=art.getbbox();art=art.crop((bbox[0]-3,bbox[1]-3,bbox[2]+3,bbox[3]+3))
        normal=art.resize((84,27),Image.Resampling.LANCZOS)
    else:
        icon=art.resize((48,38),Image.Resampling.LANCZOS)
        icon.save(OUT/(name+'-icon.png'))
        normal=button.copy();normal.alpha_composite(icon,(0,1))
    normal.save(OUT/(name+'-normal.png'))
    factor=4 if frame is not None else 2
    large=normal.resize((normal.width*factor,normal.height*factor),Image.Resampling.NEAREST)
    paste_center(board,large,x,374,210,164)
    for j,state in enumerate(['normal','hover','selected','pressed','disabled']):
        image=normal.copy()
        if state=='hover':image=ImageEnhance.Brightness(image).enhance(1.17)
        elif state=='selected':
            dr=ImageDraw.Draw(image);dr.rounded_rectangle((1,1,image.width-2,image.height-2),radius=image.height//2,outline=(112,136,255,255),width=1)
        elif state=='pressed':
            shifted=Image.new('RGBA',image.size);shifted.alpha_composite(ImageEnhance.Brightness(image).enhance(.76),(0,1));image=shifted
        elif state=='disabled':image=ImageEnhance.Brightness(ImageEnhance.Color(image).enhance(.1)).enhance(.43)
        image.save(OUT/f'{name}-{state}.png')
        if image.size!=normal.size or not image.getbbox():raise RuntimeError(f'Invalid state {name}/{state}')
        # Keep true native pixel sizes; use two rows for the wider Sci-Tek badge.
        px=x+(j%3)*68 if frame is not None else x+(j%2)*106
        py=600+(j//3)*65 if frame is not None else 594+(j//2)*48
        board.alpha_composite(image,(px,py))
        gallery.alpha_composite(image,(px,py-215))
    ref.save(OUT/(name+'-legacy-reference.png'))
    records.append({'name':name,'reference':f'ICONS.256/{frame:03}' if frame is not None else 'BUTTONS.256/002','palette':'BLUE.256' if frame is not None else 'BUTTONS.256 embedded','native_size':list(normal.size),'source_import_silhouette_iou':iou})
draw.text((30,767),'Nowa geometria i materialy; legacy sluzy wylacznie jako referencja. Scena .blend + niezalezny import .glb.',font=small,fill=(172,183,201))
draw.text((30,795),'Studium graficzne: stany sklada skrypt PNG; brak podmiany assetow lub testu integracji w grze.',font=small,fill=(172,183,201))
board.convert('RGB').save(OUT/'comparison.png')
gd.text((30,535),'Native 48 x 40 controls; Sci-Tek 84 x 27. Five PNG interaction states. Art study, not integrated into game.',font=small,fill=(172,183,201))
gallery.convert('RGB').save(OUT/'authored-contact.png')
delivered=[p for p in OUT.glob('*.png') if not p.name.endswith('-legacy-reference.png') and p.name!='comparison.png']
records={'samples':records,'states':25,'files':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(list((ROOT/'renders').glob('*'))+delivered) if p.is_file() and p.suffix!='.blend1'},'reference_files':{str(p.name):hashlib.sha256(p.read_bytes()).hexdigest() for p in [args.legacy_root/'_MS'/n for n in ['ICONS.256','BLUE.256','BUTTONS.256']]}}
(OUT/'verification.json').write_text(json.dumps(records,indent=2)+'\n')
print('STUDY_VERIFIED',len(records['samples']))
