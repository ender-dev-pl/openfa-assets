"""Index and thumbnail existing renders; never invoke model generators or refinement."""
import collections
import html
import json
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]


def main():
    inventory = json.loads((ROOT / 'sources/docs/reconstruction/models/inventory.json').read_text())
    rows = []
    sheets = collections.defaultdict(list)
    for record in inventory['records']:
        studies = []
        for study in record['available_studies']:
            if not study['present']:
                continue
            blend = Path(study['blend'])
            folder = ROOT / 'gallery/media' / blend.parent
            names = ['front-quarter.png', 'front.png', 'render.png', blend.stem+'.png', 'gallery.png', 'top.png']
            image = next((folder / name for name in names if (folder / name).is_file()), None)
            if image is None:
                # Early generic samples have separate source/export/render folders.
                image = ROOT / 'gallery/media/docs/assets/bootstrap-3d/renders' / (blend.stem+'.png')
            assert image.is_file(), (record['id'], str(blend), 'No existing preview')
            glb = ROOT / 'sources' / blend.with_suffix('.glb')
            if not glb.is_file():
                glb = ROOT / 'sources/docs/assets/bootstrap-3d/exports' / (blend.stem+'.glb')
            studies.append(dict(stage=study['stage'], blend='sources/'+study['blend'],
                glb=glb.relative_to(ROOT).as_posix() if glb.is_file() else None,
                image=image.relative_to(ROOT).as_posix(), sha256=study['sha256']))
        assert studies, record['id']
        row = dict(id=record['id'], name=record['name'], category=record['category'],
                   culture=record['culture'], studies=studies)
        rows.append(row)
        sheets[(row['category'], row['culture'])].append(row)
    out = ROOT / 'gallery'
    (out / 'sheets').mkdir(exist_ok=True)
    (out / 'catalogue.json').write_text(json.dumps(rows, indent=2)+'\n', encoding='utf-8')
    lines = ['# Model gallery', '', 'Existing authored studies only. First run and available refined stages are shown separately. '
             'A technical study is not final artistic acceptance. No new refinement was generated.', '',
             '[Interactive catalogue](index.html) · [Machine-readable index](catalogue.json)', '']
    for (category, culture), group in sorted(sheets.items()):
        slug = category+'-'+culture
        page = ['# '+category.title()+' / '+culture.title(), '', '[All groups](README.md)', '']
        cells = []
        for row in group:
            page += ['## '+row['name'], '', '`'+row['id']+'`', '']
            for n, study in enumerate(row['studies']):
                label = ('First available iteration' if n == 0 else 'Additional iteration')+' — '+study['stage']
                img = '../'+quote(study['image'])
                page += ['**'+label+'**', '', '!['+row['name']+']('+img+')', '',
                         '[Blend](../'+quote(study['blend'])+')'+
                         (' · [GLB](../'+quote(study['glb'])+')' if study['glb'] else ''), '']
                cell = Image.new('RGB', (256, 288), '#161f2b')
                source = Image.open(ROOT / study['image']).convert('RGBA')
                source.thumbnail((240, 232))
                cell.paste(source, ((256-source.width)//2, (232-source.height)//2), source)
                draw = ImageDraw.Draw(cell)
                draw.text((8, 238), row['name'][:36], fill='white')
                draw.text((8, 259), study['stage'][:38], fill='#99cde8')
                cells.append(cell)
        sheet = Image.new('RGB', (256*5, 288*((len(cells)+4)//5)), '#101722')
        for n, cell in enumerate(cells):
            sheet.paste(cell, ((n%5)*256, (n//5)*288))
        sheet.save(out / 'sheets' / (slug+'.jpg'), quality=88)
        (out / (slug+'.md')).write_text('\n'.join(page).rstrip()+'\n', encoding='utf-8')
        lines += ['## '+category.title()+' / '+culture.title(), '',
                  '[Browse '+str(len(group))+' definitions]('+slug+'.md)', '',
                  '!['+slug+'](sheets/'+slug+'.jpg)', '']
    (out / 'README.md').write_text('\n'.join(lines).rstrip()+'\n', encoding='utf-8')
    cards = []
    for row in rows:
        images = []
        for n, study in enumerate(row['studies']):
            label = ('First available' if n == 0 else 'Additional')+' / '+study['stage']
            images.append('<figure><img loading="lazy" src="../'+quote(study['image'])+'" alt="'+html.escape(row['name'])+'"><figcaption>'+html.escape(label)+
                '<br><a href="../'+quote(study['blend'])+'">Blend</a>'+
                (' · <a href="../'+quote(study['glb'])+'">GLB</a>' if study['glb'] else '')+'</figcaption></figure>')
        search = ' '.join([row['name'],row['id'],row['category'],row['culture']]+[s['stage'] for s in row['studies']]).lower()
        cards.append('<article data-search="'+html.escape(search, quote=True)+'"><h2>'+html.escape(row['name'])+'</h2><p>'+html.escape(row['category']+' / '+row['culture']+' / '+row['id'])+'</p><div class="variants">'+''.join(images)+'</div></article>')
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>OpenFA asset catalogue</title><style>
body{margin:0;background:#101722;color:#e7eff7;font:16px system-ui}header{padding:24px;position:sticky;top:0;background:#162334;z-index:1}h1{margin:0 0 8px}input{padding:12px;width:min(90%,640px);font:inherit}main{padding:20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:20px}article{background:#192637;border-radius:12px;padding:20px}h2{margin:0 0 8px;font-size:21px}p,figcaption{color:#b3c7dc}.variants{display:flex;flex-wrap:wrap;gap:12px}figure{margin:0;flex:1;min-width:180px}img{display:block;width:100%;height:260px;object-fit:contain;background:#101722}figcaption{padding:8px 0}a{color:#80ccff}[hidden]{display:none!important}</style>
<header><h1>OpenFA asset catalogue</h1><p>303 definitions · existing first-run and refined studies · no final artistic acceptance implied</p><input id="search" type="search" placeholder="Filter by name, culture, category or stage" aria-label="Filter catalogue"><span id="count"></span></header><main>'''+''.join(cards)+'''</main><script>
const cards=[...document.querySelectorAll('article')],input=document.querySelector('#search'),count=document.querySelector('#count');function filter(){let n=0;for(const c of cards){c.hidden=!c.dataset.search.includes(input.value.toLowerCase());if(!c.hidden)n++}count.textContent=' '+n+' definitions'}input.addEventListener('input',filter);filter();</script></html>'''
    (out / 'index.html').write_text(page, encoding='utf-8')
    print('GALLERY_OK', len(rows), sum(len(r['studies']) for r in rows), len(sheets))


if __name__ == '__main__':
    main()
