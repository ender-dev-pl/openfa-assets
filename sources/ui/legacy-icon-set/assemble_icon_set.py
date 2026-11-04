"""Package standalone RGBA icons and oval buttons; verify full source-frame coverage."""
import argparse
import hashlib
import json
import math
from pathlib import Path
from PIL import Image,ImageChops,ImageDraw,ImageEnhance,ImageFont

STATES=['normal','hover','selected','pressed','disabled']
SCALE=8


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    im=Image.open(path).convert('RGBA')
    if not im.getbbox():raise ValueError('Empty render: '+str(path))
    return im


def alpha_iou(a,b):
    a=a.getchannel('A').point(lambda x:255 if x>=128 else 0)
    b=b.getchannel('A').point(lambda x:255 if x>=128 else 0)
    intersect=sum(v>0 for v in ImageChops.darker(a,b).getdata())
    union=sum(v>0 for v in ImageChops.lighter(a,b).getdata())
    return intersect/union if union else 0


def variant(image,state):
    if state=='disabled':return ImageEnhance.Brightness(ImageEnhance.Color(image).enhance(.08)).enhance(.43)
    if state=='hover':return ImageEnhance.Brightness(image).enhance(1.16)
    if state=='selected':return ImageEnhance.Brightness(image).enhance(1.08)
    if state=='pressed':return ImageEnhance.Brightness(image).enhance(.78)
    return image.copy()


def fit(image,size):
    im=image.copy();im.thumbnail(size,Image.Resampling.LANCZOS)
    return im


def center(canvas,image,offset=(0,0)):
    canvas.alpha_composite(image,((canvas.width-image.width)//2+offset[0],(canvas.height-image.height)//2+offset[1]))


def sheet(path,items,images,title,columns=8):
    w=170;h=155;top=70
    canvas=Image.new('RGBA',(columns*w,math.ceil(len(items)/columns)*h+top),(16,20,29,255))
    d=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    heading=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25)
    d.text((22,18),title,font=heading,fill='white')
    for k,item in enumerate(items):
        x=(k%columns)*w;y=(k//columns)*h+top
        im=fit(images[item['id']],(150,112))
        canvas.alpha_composite(im,(x+(w-im.width)//2,y+(112-im.height)//2))
        d.text((x+8,y+116),item['id'],font=font,fill=(191,206,235))
        d.text((x+8,y+135),item['motif'][:23],font=font,fill=(151,164,186))
    canvas.convert('RGB').save(path)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--workspace',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--references',type=Path,help='Optional local original-pixel reference directory (never published)')
    a=p.parse_args();work=a.workspace.resolve();renders=work/'renders';out=a.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    for kind in ['icons','buttons','chrome']:
        for size in ['native','hires']:(out/kind/size).mkdir(parents=True,exist_ok=True)
    (out/'masks').mkdir(exist_ok=True)
    catalog=json.loads((renders/'catalog.json').read_text())
    items=catalog['items'];ids={i['id'] for i in items}
    expected={f'gameplay-{i:03}' for i in range(75)}|{f'controls-{i:03}' for i in range(4)}|{f'scroll-{i:03}' for i in range(14)}|{f'frontend-{i:03}' for i in range(17)}|{'brand-scitek'}
    if ids!=expected or len(items)!=111:raise ValueError('Incomplete or duplicate semantic icon catalogue')
    runtime=json.loads((renders/'runtime-proof.json').read_text())
    groups=runtime['groups']
    if len(groups)!=121:raise ValueError('Incomplete source or chrome group coverage')
    proofs={};manifest=[];normal_icons={};normal_buttons={};frame_map=[]
    for label,size,is_brand in [('button',(48,40),False),('small',(32,32),False),('scitek',(84,27),True)]:
        for state in STATES:
            raw=read(renders/(('badge-' if is_brand else 'chrome-')+state+'.png'))
            for resolution,multiplier in [('native',1),('hires',SCALE)]:
                target=(size[0]*multiplier,size[1]*multiplier)
                margin=0 if is_brand else 2*multiplier
                panel=raw.crop(raw.getbbox()).resize((target[0],target[1]-2*margin),Image.Resampling.LANCZOS)
                background=Image.new('RGBA',target);center(background,panel)
                background.save(out/'chrome'/resolution/(label+'-'+state+'.png'))
    for name,proof in groups.items():
        if proof['source_objects']!=proof['imported_objects'] or proof['source_objects']==0:raise ValueError('Incomplete import: '+name)
        src=read(renders/(name+'.png'));imp=read(renders/(name+'-imported.png'))
        iou=alpha_iou(src,imp)
        if iou<.995:raise ValueError(f'GLB silhouette mismatch {name}: {iou}')
        # Verify border clearance on actual source renders, before any resizing.
        alpha=src.getchannel('A');w,h=src.size
        for edge in [(0,0,w,1),(0,h-1,w,h),(0,0,1,h),(w-1,0,w,h)]:
            if alpha.crop(edge).getextrema()[1]>32:raise ValueError('Clipped source render: '+name)
        proofs[name]={'silhouette_iou':iou,'source_objects':proof['source_objects'],'imported_objects':proof['imported_objects']}
    for item in items:
        key=item['id'];raw=read(renders/(item['group']+'.png'))
        native_icon=tuple(item['icon_size']);native_button=tuple(item['button_size'])
        hi_icon=tuple(n*SCALE for n in native_icon);hi_button=tuple(n*SCALE for n in native_button)
        if item['family']=='brand':
            glyph=raw.crop(raw.getbbox())
            factor=min((hi_icon[0]-16*SCALE)/glyph.width,(hi_icon[1]-9*SCALE)/glyph.height)
            glyph=glyph.resize((round(glyph.width*factor),round(glyph.height*factor)),Image.Resampling.LANCZOS)
            raw_icon=Image.new('RGBA',hi_icon);center(raw_icon,glyph)
        else:raw_icon=raw.resize(hi_icon,Image.Resampling.LANCZOS)
        record=dict(item);record['files']={'icons':{},'buttons':{}}
        for state in STATES:
            icon=variant(raw_icon,state)
            icon_name=key+('' if state=='normal' else '-'+state)+'.png'
            for label,size in [('hires',hi_icon),('native',native_icon)]:
                rel=Path('icons')/label/icon_name
                icon.resize(size,Image.Resampling.LANCZOS).save(out/rel)
                record['files']['icons'][label+'/'+state]=rel.as_posix()
            chrome_name=('badge-' if item['family']=='brand' else 'chrome-')+state
            chrome=read(renders/(chrome_name+'.png'))
            margin_y=2*SCALE if item['family']!='brand' else 0
            chrome=chrome.crop(chrome.getbbox()).resize((hi_button[0],hi_button[1]-margin_y*2),Image.Resampling.LANCZOS)
            button=Image.new('RGBA',hi_button);center(button,chrome)
            glyph=fit(icon,(hi_button[0]-4*SCALE,hi_button[1]-4*SCALE))
            center(button,glyph,(0,SCALE if state=='pressed' else 0))
            for label,size in [('hires',hi_button),('native',native_button)]:
                rel=Path('buttons')/label/(key+'-'+state+'.png')
                button.resize(size,Image.Resampling.LANCZOS).save(out/rel)
                record['files']['buttons'][label+'/'+state]=rel.as_posix()
            if state=='normal':normal_icons[key]=raw_icon;normal_buttons[key]=button
        manifest.append(record)
        if 'original_frames' in item:
            for role,index in item['original_frames'].items():
                target={'source':item['reference'],'frame':index,'id':key,'role':role}
                if role=='mask':
                    base=read(out/record['files']['buttons']['native/normal'])
                    mask=Image.new('RGBA',base.size,(0,0,0,0));mask.putalpha(base.getchannel('A'))
                    rel=Path('masks')/(item['reference'].split('.')[0].lower()+f'-{index:03}.png')
                    mask.save(out/rel);target['mask']=rel.as_posix()
                else:
                    target['icon']=record['files']['icons']['native/'+role]
                    target['button']=record['files']['buttons']['native/'+role]
                frame_map.append(target)
        else:frame_map.append({'source':item['reference'],'frame':item['reference_frame'],'id':key,'role':'normal','icon':record['files']['icons']['native/normal'],'button':record['files']['buttons']['native/normal']})
    if len(frame_map)!=147 or len({(i['source'],i['frame']) for i in frame_map})!=147:raise ValueError('Incomplete original-frame map')
    expected_frames={'ICONS.256':75,'CICONS.256':12,'SCROLL.256':42,'FE_ICONS.256':17}
    for source,count in expected_frames.items():
        actual={i['frame'] for i in frame_map if i['source']==source}
        if actual!=set(range(count)):raise ValueError('Incomplete original family: '+source)
        if a.references:
            original=json.loads((a.references/(source.split('.')[0]+'.json')).read_text())
            if len(original['frames'])!=count:raise ValueError('Original file frame count differs: '+source)
    for family in ['gameplay','controls','scroll','frontend','brand']:
        subset=[i for i in items if i['family']==family]
        sheet(out/(family+'-icons.png'),subset,normal_icons,'Standalone RGBA icons | '+family)
        sheet(out/(family+'-buttons.png'),subset,normal_buttons,'Oval buttons | '+family)
    native=Image.new('RGBA',(1000,70+math.ceil(len(items)/10)*100),(16,20,29,255))
    nd=ImageDraw.Draw(native);nf=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',12)
    nd.text((20,20),'Native pixel sizes | standalone icons above oval buttons',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22),fill='white')
    for k,item in enumerate(items):
        x=(k%10)*100;y=70+(k//10)*100
        glyph=read(out/'icons/native'/(item['id']+'.png'))
        button=read(out/'buttons/native'/(item['id']+'-normal.png'))
        native.alpha_composite(glyph,(x+(100-glyph.width)//2,y))
        native.alpha_composite(button,(x+(100-button.width)//2,y+40))
        nd.text((x+4,y+84),item['id'],font=nf,fill=(170,191,223))
    native.convert('RGB').save(out/'native-contact.png')
    examples=['gameplay-001','gameplay-010','gameplay-016','gameplay-017','gameplay-021','gameplay-024','gameplay-051','gameplay-057','gameplay-058','controls-002','scroll-011','brand-scitek']
    states=Image.new('RGBA',(960,90+len(examples)*86),(16,20,29,255));sd=ImageDraw.Draw(states)
    sf=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    sd.text((20,15),'Oval controls | native states x2; Sci-Tek x1',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',25),fill='white')
    for j,state in enumerate(STATES):sd.text((160+j*158,60),state,font=sf,fill='white')
    for row,key in enumerate(examples):
        y=90+row*86;sd.text((10,y+25),key,font=sf,fill=(170,191,223))
        for j,state in enumerate(STATES):
            image=read(out/'buttons/native'/(key+'-'+state+'.png'))
            image=image.resize((image.width*2,image.height*2),Image.Resampling.NEAREST)
            # The wide brand uses its native pixel size to keep the table readable.
            if image.width>150:image=read(out/'buttons/native'/(key+'-'+state+'.png'))
            states.alpha_composite(image,(160+j*158+(148-image.width)//2,y+(80-image.height)//2))
    states.convert('RGB').save(out/'interaction-states.png')
    # Local original/new evidence is deliberately kept outside the deliverable directory.
    if a.references:
        comparison=work/'comparisons';comparison.mkdir(exist_ok=True)
        for start in [0,25,50]:
            subset=[i for i in items if i['family']=='gameplay'][start:start+25]
            evidence=[];images={}
            base=read(a.references/'BUTTONS/000.png').crop((0,0,49,36))
            base.putdata([(r,g,b,0 if r>230 and b>230 and g<25 else al) for r,g,b,al in base.getdata()])
            for item in subset:
                old=base.copy();old.alpha_composite(read(a.references/f'ICONS/{item["frame"]:03}.png').crop((0,0,48,36)))
                native=read(out/'buttons/native'/(item['id']+'-normal.png'))
                image=Image.new('RGBA',(156,122))
                image.alpha_composite(old.resize((147,108),Image.Resampling.NEAREST),(4,7))
                old_id=item['id']+'-original';new_id=item['id']+'-new'
                evidence.extend([{'id':old_id,'motif':'Original '+str(item['frame'])},{'id':new_id,'motif':item['motif']}])
                images[old_id]=image
                images[new_id]=native.resize((144,120),Image.Resampling.NEAREST)
            sheet(comparison/f'gameplay-{start:03}-{start+24:03}.png',evidence,images,'Original legacy (left) / Blender (right)',columns=10)
    (out/'catalog.json').write_text(json.dumps({'schema':1,'scale':SCALE,'states':STATES,'items':manifest},indent=2)+'\n')
    (out/'frame-map.json').write_text(json.dumps({'schema':1,'frames':frame_map},indent=2)+'\n')
    for record in manifest:
        for kind in ['icons','buttons']:
            for key,rel in record['files'][kind].items():
                im=read(out/rel);expected=record['icon_size' if kind=='icons' else 'button_size']
                if key.startswith('hires'):expected=[n*SCALE for n in expected]
                if list(im.size)!=expected or im.getchannel('A').getextrema()[0]!=0:raise ValueError('Invalid RGBA geometry: '+rel)
    files={p.relative_to(out).as_posix():sha(p) for p in sorted(out.rglob('*.png'))}
    report={'icons':len(items),'icon_pngs':len(list((out/'icons').rglob('*.png'))),'button_pngs':len(list((out/'buttons').rglob('*.png'))),'mapped_original_frames':len(frame_map),'blender':runtime,'source_hashes':catalog['source_hashes'],'source_artifacts':{n:sha(renders/n) for n in ['legacy-ui-full.blend','legacy-ui-full.glb']},'render_hashes':{p.name:sha(p) for p in sorted(renders.glob('*.png'))},'proofs':proofs,'files':files,'packager_sha256':sha(Path(__file__).resolve())}
    if a.references:report['reference_provenance']=json.loads((a.references/'provenance.json').read_text())
    if (work/'reopened-source.json').is_file():
        reload=json.loads((work/'reopened-source.json').read_text())
        if reload['source_sha256']!=report['source_artifacts']['legacy-ui-full.blend']:raise ValueError('Saved-scene reload used another source')
        if reload['render_sha256']!=sha(work/'reopened-source.png'):raise ValueError('Saved-scene render changed')
        reload['silhouette_iou']=alpha_iou(read(work/'reopened-source.png'),read(renders/'gameplay-017.png'))
        if reload['silhouette_iou']<.995:raise ValueError('Saved-scene render differs from native geometry')
        report['saved_scene_reload']=reload
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('FULL_SET_VERIFIED',len(items),'icons',len(files),'PNGs',len(frame_map),'original frames')


if __name__=='__main__':main()
