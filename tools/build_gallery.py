"""Index and thumbnail existing renders; never invoke model generators or refinement."""
import argparse
import collections
import html
import json
from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parents[1]
CATEGORY_LABELS = {'buildings': 'Buildings', 'ships': 'Ships / vehicles',
                   'hardpoints': 'Hardpoints', 'missiles': 'Missiles / rockets',
                   'ui': 'UI / HUD / menu', 'scaffolds': 'Scaffolds',
                   'trading-goods': 'Trading goods'}


def write_page(path, text):
    previous=path.read_bytes() if path.exists() else b''
    newline='\r\n' if b'\r\n' in previous else '\n'
    path.write_bytes(text.replace('\r\n','\n').replace('\n',newline).encode('utf-8'))


def culture_label(value):
    return 'Shared / all races' if value == 'shared' else value.title()


def index_table(groups, cultures, categories, interactive=False):
    if not interactive:
        lines = ['## Index by race and asset type', '',
                 '| Race | '+' | '.join(CATEGORY_LABELS[c] for c in categories)+' |',
                 '| --- | '+' | '.join('---:' for _ in categories)+' |']
        for culture in cultures:
            cells = []
            for category in categories:
                count = len(groups.get((category, culture), []))
                cells.append(f'[{count}]({category}-{culture}.md)' if count else '—')
            lines.append('| '+culture_label(culture)+' | '+' | '.join(cells)+' |')
        return lines+['']
    def link(text, culture='', category=''):
        from urllib.parse import urlencode
        return '<a href="#'+html.escape(urlencode({k:v for k,v in [('race',culture),('type',category)] if v}), quote=True)+'">'+html.escape(text)+'</a>'
    headings = '<th scope="col">Race</th>'+''.join('<th scope="col">'+link(CATEGORY_LABELS[c],category=c)+'</th>' for c in categories)
    body = []
    for culture in cultures:
        cells = []
        for category in categories:
            count = len(groups.get((category, culture), []))
            cells.append('<td>'+link(str(count),culture,category)+'</td>' if count else '<td>—</td>')
        body.append('<tr><th scope="row">'+link(culture_label(culture),culture=culture)+'</th>'+''.join(cells)+'</tr>')
    return '<table><caption>Choose a race, asset type or a count to filter the catalogue.</caption><thead><tr>'+headings+'</tr></thead><tbody>'+''.join(body)+'</tbody></table>'


def inventory_records():
    from gallery_animation_assets import animation_previews
    inventory = json.loads((ROOT / 'sources/docs/reconstruction/models/inventory.json').read_text(encoding='utf-8'))
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
            previews=animation_previews('sources/'+study['blend'],glb.relative_to(ROOT).as_posix(),folder)
            studies.append(dict(stage=study['stage'], blend='sources/'+study['blend'],
                glb=glb.relative_to(ROOT).as_posix() if glb.is_file() else None,
                image=image.relative_to(ROOT).as_posix(), sha256=study['sha256'],animations=previews))
        assert studies, record['id']
        row = dict(id=record['id'], name=record['name'], category=record['category'],
                   culture=record['culture'], studies=studies)
        rows.append(row)
        sheets[(row['category'], row['culture'])].append(row)
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--from-catalogue',action='store_true',help='Preserve indexed baseline studies without requiring their media locally; update trading goods and the shared index.')
    args=parser.parse_args()
    rows=json.loads((ROOT/'gallery/catalogue.json').read_text()) if args.from_catalogue else inventory_records()
    from gallery_trading_goods import trading_records
    rows=[r for r in rows if r['category']!='trading-goods']+trading_records(ROOT)
    sheets=collections.defaultdict(list)
    for row in rows:sheets[(row['category'],row['culture'])].append(row)
    out = ROOT / 'gallery'
    (out / 'sheets').mkdir(exist_ok=True)
    write_page(out / 'catalogue.json',json.dumps(rows, indent=2)+'\n')
    lines = ['# Model gallery', '', 'Existing authored studies only. First run and available refined stages are shown separately. '
             'A technical study is not final artistic acceptance.', '',
             '[Interactive catalogue](index.html) · [Machine-readable index](catalogue.json) · '
               '[RIS2 scaffold refinement](scaffolds-ris2.md) · [Culture scaffold kits](scaffolds-cultures.md) · '
               '[Game-rendered construction videos](construction-animations.html)', '']
    categories = [c for c in CATEGORY_LABELS if any(key[0] == c for key in sheets)]
    cultures = sorted({r['culture'] for r in rows}, key=lambda c:(c == 'shared', c))
    lines += index_table(sheets, cultures, categories)
    for (category, culture), group in sorted(sheets.items()):
        slug = category+'-'+culture
        if args.from_catalogue and category!='trading-goods':
            lines += ['## '+category.title()+' / '+culture.title(), '',
                      '[Browse '+str(len(group))+' definitions]('+slug+'.md)', '',
                      '!['+slug+'](sheets/'+slug+'.jpg)', '']
            continue
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
                for clip in study['animations']:
                    page += ['[Play animation: '+clip['name']+'](../'+quote(clip['video'])+')', '']
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
        encoded = BytesIO()
        sheet.save(encoded, format='JPEG', quality=88)
        target = out / 'sheets' / (slug+'.jpg')
        if not target.exists() or target.read_bytes() != encoded.getvalue():
            target.write_bytes(encoded.getvalue())
        write_page(out / (slug+'.md'),'\n'.join(page).rstrip()+'\n')
        lines += ['## '+category.title()+' / '+culture.title(), '',
                  '[Browse '+str(len(group))+' definitions]('+slug+'.md)', '',
                  '!['+slug+'](sheets/'+slug+'.jpg)', '']
    write_page(out / 'README.md','\n'.join(lines).rstrip()+'\n')
    cards = []
    for row in rows:
        images = []
        for n, study in enumerate(row['studies']):
            label = ('First available' if n == 0 else 'Additional')+' / '+study['stage']
            if study['animations']:
                clips=study['animations']
                preview='<video controls loop muted playsinline preload="none" poster="../'+quote(study['image'])+'" aria-label="'+html.escape(row['name']+' — '+study['stage']+' animation',quote=True)+'"><source src="../'+quote(clips[0]['video'])+'" type="video/webm">Your browser does not support WebM video.</video>'
                if len(clips)>1:
                    options=''.join('<option value="../'+quote(c['video'])+'">'+html.escape(c['name'])+'</option>' for c in clips)
                    preview+='<label>Animation clip<select class="animation-clip">'+options+'</select></label>'
                preview+='<p class="animation-label">Animated model · '+str(len(clips))+' clip'+('s' if len(clips)!=1 else '')+'</p>'
            else:
                preview='<img loading="lazy" src="../'+quote(study['image'])+'" alt="'+html.escape(row['name'])+'">'
            images.append('<figure>'+preview+'<figcaption>'+html.escape(label)+
                '<br><a href="../'+quote(study['blend'])+'">Blend</a>'+
                (' · <a href="../'+quote(study['glb'])+'">GLB</a>' if study['glb'] else '')+'</figcaption></figure>')
        search = ' '.join([row['name'],row['id'],row['category'],row['culture']]+[s['stage'] for s in row['studies']]).lower()
        cards.append('<article data-search="'+html.escape(search, quote=True)+'" data-race="'+html.escape(row['culture'],quote=True)+'" data-type="'+html.escape(row['category'],quote=True)+'"><h2>'+html.escape(row['name'])+'</h2><p>'+html.escape(CATEGORY_LABELS[row['category']]+' / '+culture_label(row['culture'])+' / '+row['id'])+'</p><div class="variants">'+''.join(images)+'</div></article>')
    from gallery_supplemental import supplemental_records, supplemental_cards
    extra = json.loads((out/'supplemental-catalogue.json').read_text()) if args.from_catalogue else supplemental_records()
    write_page(out / 'supplemental-catalogue.json',json.dumps(extra, indent=2)+'\n')
    cards += supplemental_cards(extra)
    index_groups = collections.defaultdict(list, {k:list(v) for k,v in sheets.items()})
    for row in extra:
        index_groups[(row['category'], row['culture'])].append(row)
    categories += ['ui', 'scaffolds']
    cultures = sorted(set(cultures) | {row['culture'] for row in extra}, key=lambda c:(c == 'shared', c))
    template = Path(__file__).with_name('gallery_template.html').read_text(encoding='utf-8')
    race_options = ''.join('<option value="'+c+'">'+html.escape(culture_label(c))+'</option>' for c in cultures)
    type_options = ''.join('<option value="'+c+'">'+html.escape(CATEGORY_LABELS[c])+'</option>' for c in categories)
    page = template.replace('{{CARDS}}', ''.join(cards)).replace('{{RACES}}', race_options).replace('{{TYPES}}', type_options).replace('{{INDEX}}', index_table(index_groups,cultures,categories,interactive=True)).replace('{{COUNT}}',str(len(rows)+len(extra)))
    write_page(out / 'index.html',page)
    if not args.from_catalogue:
        from build_ui_gallery import build
        build()
    print('GALLERY_OK', len(rows), sum(len(r['studies']) for r in rows), len(sheets))


if __name__ == '__main__':
    main()
