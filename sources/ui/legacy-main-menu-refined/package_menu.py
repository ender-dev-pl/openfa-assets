"""Package actual Blender renders into independent RGBA frontend layers and previews."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageEnhance,ImageFilter,ImageFont


def portable_font(size):
    """Resolve installed fonts without a machine-specific filesystem path."""
    for name in ('arial.ttf', 'segoeui.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)



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
    # Shared world registration: the 600px dome view is exactly a native 200px
    # square. Never recrop each silhouette, which changes its projected scale.
    crop=(0,0,600,600)
    records=[]

    def deliver(name,image,size,role,theme=None,state=None,native_override=None):
        for resolution,final in [('hires',image.size),('native',size)]:
            path=out/resolution/(name+'.png')
            result=native_override if resolution=='native' and native_override is not None else image.resize(final,Image.Resampling.LANCZOS)
            result.save(path)
        records.append({'id':name,'role':role,'theme':theme,'state':state,'native_size':list(size),'hires_size':list(image.size),'files':{'native':'native/'+name+'.png','hires':'hires/'+name+'.png'}})

    for group in info['groups']:
        native_override=None
        image=read(raw/('layer-'+group+'.png'))
        if group=='panel':
            native_override=read(raw/'layer-panel.png').resize((640,480),Image.Resampling.LANCZOS).crop((0,0,415,480))
            image=read(raw/'layer-panel.png').crop((0,0,830,960));size=(415,480)
        elif group=='menu-base':
            native_override=read(raw/'layer-panel.png').resize((640,480),Image.Resampling.LANCZOS).crop((320,0,640,480))
            image=read(raw/'layer-panel.png').crop((640,0,1280,960));size=(320,480)
        elif group in ['panel-neon','lettering']:image=image.crop((0,0,830,960));size=(415,480)
        elif group in ['menu-row','row-neon']:size=(211,48)
        else:image=image.crop(crop);size=(200,200)
        deliver('layer-'+group,image,size,'independent-layer',native_override=native_override)
    shared=read(raw/'layer-panel.png');shared_native=shared.resize((640,480),Image.Resampling.LANCZOS)
    deliver('layer-shared-console',shared,(640,480),'registered-console',native_override=shared_native)
    deliver('layer-panel-left-320',shared.crop((0,0,640,960)),(320,480),'registered-left-half',native_override=shared_native.crop((0,0,320,480)))
    for theme,color in info['themes'].items():
        for state,strength in info['states'].items():
            image=read(raw/f'sphere-{theme}-{state}.png').crop(crop)
            emission=read(raw/f'emission-{theme}-{state}.png').crop(crop)
            glow=halo(emission,info['themes']['ruby'],strength,10)
            full=glow.copy();full.alpha_composite(image)
            for part,im in [('sphere',full),('emission',emission),('glow',glow)]:
                deliver(f'{part}-{theme}-{state}',im,(200,200),part,theme,state)
            # Compatibility preserves the legacy logical canvas and visible-image offset.
            compat=Image.new('RGBA',(960,600));compat.alpha_composite(full.resize((591,597),Image.Resampling.LANCZOS),(6,0))
            deliver(f'dome-canvas-{theme}-{state}',compat,(320,200),'legacy-dome-canvas',theme,state)
            rail=read(raw/f'rail-{theme}-{state}.png').crop((0,0,830,960))
            # Preserve the strong neon chroma seen in the supplied captures after
            # AgX and native-size reduction. Alpha/registration stay unchanged.
            rail=ImageEnhance.Color(rail).enhance(2.6)
            rail=ImageEnhance.Brightness(rail).enhance(.35+1.1*min(strength/.45,1)+.2*max(0,strength-.45))
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
    font=portable_font(17)
    heading=portable_font(27)
    preview=Image.new('RGBA',(1240,80+len(info['themes'])*215),(12,17,25,255));d=ImageDraw.Draw(preview)
    d.text((24,16),'Contextual neon profiles | continuous red dome emblem',font=heading,fill='white')
    for x,state in enumerate(info['states']):d.text((18+x*205,55),state,font=font,fill=(190,204,230))
    for y,theme in enumerate(info['themes']):
        for x,state in enumerate(info['states']):
            im=read(out/'native'/f'sphere-{theme}-{state}.png')
            preview.alpha_composite(im,(x*205,80+y*215))
            d.text((x*205+8,80+y*215+194),theme,font=font,fill='white')
            d.line((x*205+70,80+y*215+204,x*205+190,80+y*215+204),fill=tuple(round(c*255) for c in info['themes'][theme]),width=3)
    preview.convert('RGB').save(out/'sphere-states.png')
    # Composition proof uses the generated artwork, with illustrative labels only.
    for theme in ['ruby','cyan','amber','green']:
        screen=Image.new('RGBA',(640,480),(8,12,20,255))
        screen.alpha_composite(read(out/'native/layer-panel.png'))
        screen.alpha_composite(read(out/'native/layer-menu-base.png'),(320,0))
        screen.alpha_composite(read(out/'native/layer-lettering.png'))
        screen.alpha_composite(read(out/'native'/f'rail-{theme}-idle.png'))
        screen.alpha_composite(read(out/'native'/f'sphere-{theme}-idle.png'),(152,136))
        sd=ImageDraw.Draw(screen);label_font=portable_font(12)
        if theme=='green':
            sd.text((554,46),'PRESET GAMES',font=label_font,anchor='mm',fill=(222,229,238))
            labels=["Beginner's Luck",'Encounters','Getting Serious',"Three's A Crowd",'Raising The Stakes','The Void','Crowded House','Knowledge Is Power','Full On','Getting Tight','The Ultimate']
            circle=read(out/'native'/f'row-{theme}-idle.png').crop((18,5,55,43)).resize((23,23),Image.Resampling.LANCZOS)
            mask=Image.new('L',(92,92));ImageDraw.Draw(mask).ellipse((0,0,91,91),fill=255)
            mask=mask.resize((23,23),Image.Resampling.LANCZOS);circle.putalpha(ImageChops.multiply(circle.getchannel('A'),mask))
            for n,label in enumerate(labels):
                screen.alpha_composite(circle,(430,63+n*28));sd.text((554,75+n*28),label,font=label_font,anchor='mm',fill=(222,229,238))
            screen.alpha_composite(read(out/'native'/f'row-{theme}-idle.png'),(429,405));sd.text((554,429),'CUSTOM GAME',font=label_font,anchor='mm',fill=(222,229,238))
        else:
            for n,label in enumerate(['Intro','Tutorials','New Game','Saved Game','Multiplayer','Options','Quit']):
                state='selected' if n==2 else 'idle';screen.alpha_composite(read(out/'native'/f'row-{theme}-{state}.png'),(429,27+n*64))
                sd.text((554,51+n*64),label,font=label_font,anchor='mm',fill=(222,229,238))
        screen.convert('RGB').resize((1280,960),Image.Resampling.NEAREST).save(out/('composition-'+theme+'.png'))
    layers=Image.new('RGBA',(1200,410),(12,17,25,255));ld=ImageDraw.Draw(layers)
    ld.text((20,15),'Separate layers | chrome / glass / emblem / neon / glow',font=heading,fill='white')
    for i,name in enumerate(['layer-bezel','layer-sphere','layer-emblem','emission-cyan-selected','glow-cyan-selected']):
        image=read(out/'native'/(name+'.png'));layers.alpha_composite(image,(i*235+15,80));ld.text((i*235+10,295),name.replace('cyan-selected',''),font=font,fill='white')
    layers.convert('RGB').save(out/'layers.png')
    references={p.name:sha(p) for p in sorted((Path('../legacy')/'_MS').glob('FE_*.256'))}
    bindings={'main-menu':'amber','intro':'amber','tutorials':'amber','preset-games':'green','custom-game':'green','scenario-details':'green','saved-games':'blue','multiplayer':'blue','game-options':'blue','sound-options':'blue','mouse-options':'blue','time-options':'cyan','quit-confirmation':'amber'}
    catalog={'themes':info['themes'],'states':info['states'],'items':records,'legacy_dome_frames':{'0':'native/dome-canvas-ruby-idle.png','1':'native/dome-canvas-ruby-pressed.png'},'sphere_anchor':[152,136],'registration':info['registration'],'emblem':info['emblem'],'screen_neon_bindings':bindings,'color_contract':'Screen context changes the panel neon; the red dome emblem remains invariant for the same interaction state. Bind to the existing presenter theme, not pointer position.','halo_blend':'source-over RGBA; pulse/glow overlays may alternatively be added in linear light','legacy_evidence':'Attached main and preset captures confirm orange/green console neon while the sphere remains red. Dark idle and bright pressed are established legacy dome states; additional light levels are authored variants.'}
    (out/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    whole=read(raw/'layer-panel.png').resize((640,480),Image.Resampling.LANCZOS)
    joined=Image.new('RGBA',(640,480));joined.alpha_composite(read(out/'native/layer-panel.png'));joined.alpha_composite(read(out/'native/layer-menu-base.png'),(320,0))
    difference=ImageChops.difference(joined.crop((4,4,636,476)),whole.crop((4,4,636,476)))
    seam_error=max(hi for lo,hi in difference.getextrema())
    overlap=ImageChops.difference(read(out/'native/layer-panel.png').crop((320,0,415,480)),read(out/'native/layer-menu-base.png').crop((0,0,95,480)))
    overlap_error=max(hi for lo,hi in overlap.getextrema())
    gap_pixels=sum(v<255 for v in joined.getchannel('A').crop((4,4,636,476)).getdata())
    if seam_error or overlap_error or gap_pixels:raise RuntimeError(f'Panel registration failure: {seam_error}/{overlap_error}/{gap_pixels}')
    for state in info['states']:
        reference=read(raw/f'sphere-ruby-{state}.png').tobytes()
        for theme in info['themes']:
            if read(raw/f'sphere-{theme}-{state}.png').tobytes()!=reference:raise RuntimeError(f'Context recolored the dome: {theme}/{state}')
            if read(out/'native'/f'sphere-{theme}-{state}.png').tobytes()!=read(out/'native'/f'sphere-ruby-{state}.png').tobytes():raise RuntimeError('Context recolored the finished sphere')
    report={'source_hashes':info['source_hashes'],'packager_sha256':sha(Path(__file__)),'blender':info['blender'],'samples':info['samples'],'proof':proof,'reference_hashes':references,'panel_registration':{'max_channel_error':seam_error,'overlap_channel_error':overlap_error,'interior_gap_pixels':gap_pixels},'emblem':info['emblem'],'sphere_context_invariance':True,'artifacts':{n:sha(raw/n) for n in ['main-menu.blend','main-menu.glb']},'files':{p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*.png'))}}
    for item in records:
        for resolution,file in item['files'].items():
            im=read(out/file);expected=item['native_size' if resolution=='native' else 'hires_size']
            if list(im.size)!=expected:raise RuntimeError('Bad size '+file)
            if item['role'] not in ['pulse-halo','glow','panel-neon-halo','menu-row-halo'] or item['state']!='off':
                if not im.getbbox():raise RuntimeError('Unexpected empty render '+file)
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('MENU_PAYLOAD_VERIFIED',len(records),'records',len(report['files']),'PNGs')


if __name__=='__main__':main()
