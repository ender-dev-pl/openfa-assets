"""Check refined renders and create a before/after gallery and culture sheets."""
import argparse
import hashlib
import html
import json
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ids')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]/'docs/assets/bootstrap-3d/terran-refined'
    ids=sorted(set(map(int,args.ids.split(',')))) if args.ids else list(range(40))
    records=[]
    for index in ids:
        folder=root/f'pb{index:02}'
        meta=json.loads((folder/'model.json').read_text(encoding='utf-8'))
        names=[view+'.png' for view in meta['views']]
        if meta.get('rotation_rig'):
            names += [f'directions/{i:02}.png' for i in range(16)]
        if meta.get('iris_rig'):
            names += [f'iris/{i:02}.png' for i in range(17)]
        for name in names:
            image=Image.open(folder/name)
            assert image.mode=='RGBA' and image.size==(768,768)
            bounds=image.getchannel('A').getbbox()
            assert bounds and all(0<value<768 for value in bounds),(index,name,bounds)
            assert image.getchannel('A').getextrema()==(0,255)
        if meta.get('rotation_rig'):
            frames=[]
            for heading in range(16):
                frame=Image.open(folder/'directions'/f'{heading:02}.png')
                composite=Image.alpha_composite(Image.new('RGBA',frame.size,(14,20,28,255)),frame).convert('RGB')
                frames.append(composite.resize((384,384),Image.Resampling.LANCZOS))
            frames[0].save(folder/'rotation.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
        if meta.get('iris_rig'):
            frames=[]
            for iris_frame in range(17):
                frame=Image.open(folder/'iris'/f'{iris_frame:02}.png')
                composite=Image.alpha_composite(Image.new('RGBA',frame.size,(14,20,28,255)),frame).convert('RGB')
                frames.append(composite.resize((384,384),Image.Resampling.LANCZOS))
            frames[0].save(folder/'iris.gif',save_all=True,append_images=frames[1:]+frames[-2:0:-1],duration=100,loop=0)
        meta['files_sha256']={name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in names+['model.blend','model.glb']}
        records.append(meta)
    for start in range(0,len(records),20):
        group=records[start:start+20]
        sheet=Image.new('RGB',(1600,1280),(14,20,28))
        draw=ImageDraw.Draw(sheet)
        for slot,record in enumerate(group):
            frame=Image.open(root/record['preview'].lower()/'front-quarter.png')
            image=Image.alpha_composite(Image.new('RGBA',frame.size,(14,20,28,255)),frame).convert('RGB')
            x,y=slot%5*320,slot//5*320
            sheet.paste(image.resize((320,320),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+7,y+301),record['preview']+' '+record['name'],fill=(225,230,235))
        sheet.save(root/f'review-terran-{start:02}.jpg',quality=94)
    cards=[]
    for record in records:
        key=record['preview'].lower()
        title=html.escape(record['preview']+' · '+record['name'])
        features='; '.join(record['detail_features'])
        buttons=''.join(f'<button data-view="{view}.png">{view}</button>' for view in record['views'])
        if record.get('rotation_rig'):
            buttons+='<button data-view="rotation.gif">Rotation</button>'
        if record.get('iris_rig'):
            buttons+='<button data-view="iris.gif">Iris dome</button><button data-view="iris/16.png">Open silo</button>'
        cards.append(f'<article data-search="{title.lower()}"><h2>{title}</h2><div class="pair">'
            f'<figure><img loading="lazy" src="../full-catalogue/terran/{key}/front-quarter.png"><figcaption>Previous study</figcaption></figure>'
            f'<figure><img class="refined" loading="lazy" src="{key}/front-quarter.png" data-root="{key}/"><figcaption>Refined model</figcaption></figure></div>'
            f'<nav>{buttons}</nav><p>{html.escape(features)}</p><p>{record["detail_objects"]} authored detail objects · '
            f'<a href="{key}/model.blend">Blend</a> · <a href="{key}/model.glb">GLB</a></p></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenFA refined Terran catalogue</title><style>
body{background:#0e141c;color:#dce4eb;font:15px system-ui;margin:0}header{padding:24px;background:#1b2b36;position:sticky;top:0;z-index:1}h1{font-size:26px;margin:0 0 12px}input,button{padding:8px;background:#233b49;border:1px solid #526876;color:#dce4eb;border-radius:4px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(540px,1fr));gap:20px;padding:20px}article{padding:16px;border:1px solid #344c5b;border-radius:8px;background:#14212b}h2{font-size:18px}.pair{display:grid;grid-template-columns:1fr 1fr}figure{margin:0}img{width:100%;aspect-ratio:1;object-fit:contain}figcaption{text-align:center;color:#9eb4c4}p{line-height:1.5;color:#9eb4c4}nav{display:flex;flex-wrap:wrap;gap:6px;margin-top:16px}a{color:#f2bf7a}[hidden]{display:none!important}@media(max-width:600px){main{display:block}article{margin-bottom:18px}}
</style><header><h1>Refined Terran buildings · COUNT/40</h1><input id="search" placeholder="PB code or building name"><p>Independent geometry and native PBR materials · previous studies preserved for comparison</p></header><main>CARDS</main>
<script>document.querySelector('#search').addEventListener('input',event=>document.querySelectorAll('article').forEach(card=>card.hidden=!card.dataset.search.includes(event.target.value.toLowerCase())));document.addEventListener('click',event=>{const button=event.target.closest('button[data-view]');if(button){const image=button.closest('article').querySelector('.refined');image.src=image.dataset.root+button.dataset.view}})</script></html>'''
    (root/'index.html').write_text(page.replace('COUNT',str(len(records))).replace('CARDS','\n'.join(cards)),encoding='utf-8')
    (root/'manifest.json').write_text(json.dumps(dict(expected_count=40,completed_count=len(records),
        complete=set(ids)==set(range(40)),buildings=records),indent=2)+'\n',encoding='utf-8')
    print('REFINED_RENDER_REVIEW_OK',len(records),sum(3+(16 if record.get('rotation_rig') else 0)+(17 if record.get('iris_rig') else 0) for record in records))


if __name__=='__main__':
    main()
