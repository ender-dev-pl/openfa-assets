"""Package actual Blender renders into independent RGBA frontend layers and previews."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageFilter,ImageFont


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def read(p):return Image.open(p).convert('RGBA')


def iou(a,b):
    a=a.getchannel('A').point(lambda v:255 if v>=128 else 0);b=b.getchannel('A').point(lambda v:255 if v>=128 else 0)
    u=sum(v>0 for v in ImageChops.lighter(a,b).getdata());n=sum(v>0 for v in ImageChops.darker(a,b).getdata())
    return n/u if u else 0


def halo(image,color,strength,radius=10):
    out=Image.new('RGBA',image.size,tuple(round(c*255) for c in color)+(0,))
    alpha=image.getchannel('A').filter(ImageFilter.GaussianBlur(radius))
    multiplier=0 if strength==0 else min(.90,.18+strength*.22)
    out.putalpha(alpha.point(lambda v:round(v*multiplier)))
    return out


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workspace',required=True,type=Path);a=p.parse_args()
    work=a.workspace.resolve();raw=work/'renders';out=work/'delivery';out.mkdir(exist_ok=True)
    for size in ['native','hires']:(out/size).mkdir(exist_ok=True)
    info=json.loads((raw/'renders.json').read_text());proof={}
    for group,names in info['groups'].items():
        value=iou(read(raw/('layer-'+group+'.png')),read(raw/('imported-'+group+'.png')))
        if value<.995:raise RuntimeError(f'Independent import mismatch: {group} {value}')
        proof[group]={'objects':len(names),'silhouette_iou':value}
    bbox=read(raw/'layer-bezel.png').getbbox();crop=(bbox[0]-4,bbox[1]-4,bbox[2]+4,bbox[3]+4)
    records=[]

    def deliver(name,image,size,role,theme=None,state=None):
        for resolution,final in [('hires',image.size),('native',size)]:
            path=out/resolution/(name+'.png');image.resize(final,Image.Resampling.LANCZOS).save(path)
        records.append({'id':name,'role':role,'theme':theme,'state':state,'native_size':list(size),'hires_size':list(image.size),'files':{'native':'native/'+name+'.png','hires':'hires/'+name+'.png'}})

    for group in info['groups']:
        image=read(raw/('layer-'+group+'.png'))
        if group in ['panel','panel-neon','lettering']:size=(415,480)
        elif group=='menu-base':size=(320,480)
        elif group in ['menu-row','row-neon']:size=(211,48)
        else:image=image.crop(crop);size=(200,200)
        deliver('layer-'+group,image,size,'independent-layer')
    for theme,color in info['themes'].items():
        for state,strength in info['states'].items():
            image=read(raw/f'sphere-{theme}-{state}.png').crop(crop)
            emission=read(raw/f'emission-{theme}-{state}.png').crop(crop)
            glow=halo(emission,color,strength,10)
            full=glow.copy();full.alpha_composite(image)
            for part,im in [('sphere',full),('emission',emission),('glow',glow)]:
                deliver(f'{part}-{theme}-{state}',im,(200,200),part,theme,state)
            # Compatibility preserves the legacy logical canvas and visible-image offset.
            compat=Image.new('RGBA',(960,600));compat.alpha_composite(full.resize((591,597),Image.Resampling.LANCZOS),(6,0))
            deliver(f'dome-canvas-{theme}-{state}',compat,(320,200),'legacy-dome-canvas',theme,state)
            rail=read(raw/f'rail-{theme}-{state}.png')
            railglow=halo(rail,color,strength,7)
            railfull=railglow.copy();railfull.alpha_composite(rail)
            deliver(f'rail-{theme}-{state}',railfull,(415,480),'panel-neon',theme,state)
            deliver(f'rail-glow-{theme}-{state}',railglow,(415,480),'panel-neon-halo',theme,state)
            row=read(raw/f'row-{theme}-{state}.png')
            # Halo follows only the neon geometry, never the opaque row background.
            rowmask=read(raw/'layer-row-neon.png')
            rowglow=halo(rowmask,color,strength,5)
            rowfull=rowglow.copy();rowfull.alpha_composite(row)
            deliver(f'row-{theme}-{state}',rowfull,(211,48),'menu-row',theme,state)
            deliver(f'row-glow-{theme}-{state}',rowglow,(211,48),'menu-row-halo',theme,state)
        # Eight loop-ready halo frames. Pulsation is a composition extension, not legacy evidence.
        base=read(out/'hires'/f'glow-{theme}-selected.png')
        for frame in range(8):
            pulse=base.copy();gain=.62+.38*(.5+.5*math.sin(frame*math.tau/8))
            pulse.putalpha(pulse.getchannel('A').point(lambda v:round(v*gain)))
            deliver(f'pulse-{theme}-{frame:02}',pulse,(200,200),'pulse-halo',theme,str(frame))
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
    heading=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',27)
    preview=Image.new('RGBA',(1240,80+len(info['themes'])*215),(12,17,25,255));d=ImageDraw.Draw(preview)
    d.text((24,16),'Main-menu sphere | original-file-referenced geometry',font=heading,fill='white')
    for x,state in enumerate(info['states']):d.text((18+x*205,55),state,font=font,fill=(190,204,230))
    for y,theme in enumerate(info['themes']):
        for x,state in enumerate(info['states']):
            im=read(out/'native'/f'sphere-{theme}-{state}.png')
            preview.alpha_composite(im,(x*205,80+y*215))
            d.text((x*205+8,80+y*215+194),theme,font=font,fill='white')
    preview.convert('RGB').save(out/'sphere-states.png')
    # Composition proof uses the generated artwork, with illustrative labels only.
    for theme in ['ruby','cyan','amber']:
        screen=Image.new('RGBA',(640,480),(8,12,20,255))
        screen.alpha_composite(read(out/'native/layer-panel.png'))
        screen.alpha_composite(read(out/'native/layer-menu-base.png'),(320,0))
        screen.alpha_composite(read(out/'native/layer-lettering.png'))
        screen.alpha_composite(read(out/'native'/f'rail-{theme}-idle.png'))
        screen.alpha_composite(read(out/'native'/f'sphere-{theme}-idle.png'),(152,136))
        sd=ImageDraw.Draw(screen);label_font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
        for n,label in enumerate(['Intro','Tutorials','New Game','Saved Game','Multiplayer','Options','Quit']):
            state='selected' if n==2 else 'idle';screen.alpha_composite(read(out/'native'/f'row-{theme}-{state}.png'),(429,27+n*64))
            sd.text((543,51+n*64),label,font=label_font,anchor='mm',fill=(222,229,238))
        screen.convert('RGB').resize((1280,960),Image.Resampling.NEAREST).save(out/('composition-'+theme+'.png'))
    layers=Image.new('RGBA',(1200,410),(12,17,25,255));ld=ImageDraw.Draw(layers)
    ld.text((20,15),'Separate layers | chrome / glass / emblem / neon / glow',font=heading,fill='white')
    for i,name in enumerate(['layer-bezel','layer-sphere','layer-emblem','emission-cyan-selected','glow-cyan-selected']):
        image=read(out/'native'/(name+'.png'));layers.alpha_composite(image,(i*235+15,80));ld.text((i*235+10,295),name.replace('cyan-selected',''),font=font,fill='white')
    layers.convert('RGB').save(out/'layers.png')
    references={p.name:sha(p) for p in sorted((Path('../legacy')/'_MS').glob('FE_*.256'))}
    catalog={'themes':info['themes'],'states':info['states'],'items':records,'legacy_dome_frames':{'0':'native/dome-canvas-ruby-idle.png','1':'native/dome-canvas-ruby-pressed.png'},'sphere_anchor':[152,136],'halo_blend':'source-over RGBA; pulse/glow overlays may alternatively be added in linear light','legacy_evidence':'Only dark idle and brighter pressed are confirmed; extra hues, neon rails, hover, selected, dim, off and pulse are OpenFA extensions.'}
    (out/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    report={'source_hashes':info['source_hashes'],'packager_sha256':sha(Path(__file__)),'blender':info['blender'],'samples':info['samples'],'proof':proof,'reference_hashes':references,'artifacts':{n:sha(raw/n) for n in ['main-menu.blend','main-menu.glb']},'files':{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*.png'))}}
    for item in records:
        for resolution,file in item['files'].items():
            im=read(out/file);expected=item['native_size' if resolution=='native' else 'hires_size']
            if list(im.size)!=expected:raise RuntimeError('Bad size '+file)
            if item['role'] not in ['pulse-halo','glow','panel-neon-halo','menu-row-halo'] or item['state']!='off':
                if not im.getbbox():raise RuntimeError('Unexpected empty render '+file)
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MENU_PAYLOAD_VERIFIED',len(records),'records',len(report['files']),'PNGs')


if __name__=='__main__':main()
