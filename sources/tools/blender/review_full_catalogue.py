"""Check render coverage/alpha/bounds and create a filterable local catalogue with contact sheets."""
import argparse
import collections
import hashlib
import html
import json
from pathlib import Path

from PIL import Image,ImageDraw


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--partial',action='store_true',help='Create review sheets during generation without claiming full coverage')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]/'docs/assets/bootstrap-3d/full-catalogue'
    recipes=json.loads((root/'recipes.json').read_text(encoding='utf-8'))['buildings']
    models=[]
    failures=[]
    for recipe in recipes:
        directory=root/recipe['culture']/recipe['preview'].lower()
        if args.partial and not (directory/'model.json').is_file():
            continue
        metadata=json.loads((directory/'model.json').read_text(encoding='utf-8'))
        for view in metadata['views']:
            image=Image.open(directory/(view+'.png'))
            assert image.mode=='RGBA' and image.size==(512,512),(recipe['preview'],view,'format')
            alpha=image.getchannel('A')
            bounds=alpha.getbbox()
            if alpha.getextrema()!=(0,255) or bounds is None or not all(0<value<512 for value in bounds):
                failures.append([recipe['preview'],view,'alpha/bounds',bounds])
        metadata['files_sha256']={name:hashlib.sha256((directory/name).read_bytes()).hexdigest()
            for name in ['model.blend','model.glb']+[view+'.png' for view in metadata['views']]}
        models.append(metadata)
    if not args.partial:
        assert len(models)==177 and {model['global_type'] for model in models}==set(range(177))
    assert not failures,failures
    cards=[]
    for culture in sorted({model['culture'] for model in models}):
        subset=[model for model in models if model['culture']==culture]
        for start in range(0,len(subset),20):
            group=subset[start:start+20]
            sheet=Image.new('RGB',(1600,1280),(14,20,28))
            draw=ImageDraw.Draw(sheet)
            for slot,model in enumerate(group):
                relative=model['culture']+'/'+model['preview'].lower()
                image=Image.open(root/relative/'front-quarter.png')
                image=Image.alpha_composite(Image.new('RGBA',image.size,(14,20,28,255)),image).convert('RGB')
                x,y=slot%5*320,slot//5*320
                sheet.paste(image.resize((320,320),Image.Resampling.LANCZOS),(x,y))
                draw.text((x+8,y+301),f"{model['global_type']:03} {model['preview']} {model['name']}",fill=(220,225,232))
                title=html.escape(model['name'])
                links=' '.join(f'<button data-view="{view}.png">{view}</button>' for view in model['views'])
                if model.get('rotation_rig'):
                    links += '<button data-view="rotation.gif">Rotation</button><button data-view="directions.jpg">16 directions</button>'
                cards.append(f'<article data-culture="{culture}" data-search="{html.escape((title+" "+model["preview"]+" "+model["building_id"]).lower())}">'
                    f'<img loading="lazy" src="{relative}/front-quarter.png" data-root="{relative}/" alt="{title}">'
                    f'<h3>{model["global_type"]:03} · {model["preview"]} · {title}</h3><p>{culture} · {model["footprint"][0]}×{model["footprint"][1]}</p>'
                    f'<nav>{links}</nav><p><a href="{relative}/model.blend">Blend</a> <a href="{relative}/model.glb">GLB</a></p>'
                    f'<details><summary>Reference features</summary>{html.escape(model["observed_features"])}</details></article>')
            sheet.save(root/f'review-{culture}-{start:02}.jpg',quality=93)
    options=''.join(f'<option>{culture}</option>' for culture in sorted({item['culture'] for item in models}))
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenFA original building models</title><style>
body{margin:0;background:#0e141c;color:#dce4eb;font:15px system-ui}header{padding:24px;position:sticky;top:0;background:#16222ded;z-index:2;border-bottom:1px solid #435762}
h1{margin:0 0 12px;font-size:25px}input,select,button{background:#20323e;color:#e1e8ec;border:1px solid #536c79;padding:8px;border-radius:4px}input{width:300px;max-width:70vw}
main{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:18px;padding:20px}article{border:1px solid #304655;border-radius:8px;padding:12px;background:#14212b}
img{width:100%;aspect-ratio:1;object-fit:contain;background:#0e141c}h3{font-size:15px;margin:8px 0}p{color:#a9bcc7}nav{display:flex;gap:5px;flex-wrap:wrap}button{font-size:11px;cursor:pointer}a{color:#f2bf7a;margin-right:12px}details{font-size:13px;line-height:1.5}[hidden]{display:none!important}
</style><header><h1>OpenFA · COUNT original building models</h1><input id="search" placeholder="Name, resource or building ID"><select id="culture"><option value="">All cultures</option>OPTIONS</select><p>Editable Blender sources · GLB exports · three transparent review views per model</p><a href="../terran-refined/index.html">Refined Terran models · before / after</a></header><main>CARDS</main>
<script>const search=document.querySelector('#search'),culture=document.querySelector('#culture');function filter(){document.querySelectorAll('article').forEach(card=>card.hidden=!(card.dataset.search.includes(search.value.toLowerCase())&&(!culture.value||card.dataset.culture===culture.value)))}search.addEventListener('input',filter);culture.addEventListener('change',filter);document.addEventListener('click',event=>{const button=event.target.closest('button[data-view]');if(button){const image=button.closest('article').querySelector('img');image.src=image.dataset.root+button.dataset.view}});</script></html>'''
    (root/'index.html').write_text(page.replace('COUNT',str(len(models))).replace('OPTIONS',options).replace('CARDS','\n'.join(cards)),encoding='utf-8')
    report={'expected_count':177,'completed_count':len(models),'complete':len(models)==177,
            'culture_counts':dict(collections.Counter(model['culture'] for model in models)),
            'render_count':sum(len(model['views']) for model in models),'models':models}
    (root/'manifest.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('CATALOGUE_RENDER_REVIEW_OK',len(models),report['render_count'],'renders',report['culture_counts'])


if __name__=='__main__':
    main()
