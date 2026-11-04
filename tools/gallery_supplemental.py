"""Index published UI records and all nineteen scaffold families."""
import ast
import html
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def supplemental_records():
    rows=[]
    base='gallery/media/ui/legacy-icon-set/'
    for item in json.loads((ROOT/base/'catalog.json').read_text())['items']:
        views=[dict(label=kind+' / '+state,image=base+name) for kind,files in item['files'].items() for state,name in files.items() if state.startswith('hires/')]
        rows.append(dict(id='ui:'+item['id'],name=item['motif'],category='ui',culture='shared',views=views,detail='sources/ui/legacy-icon-set/README.md'))
    tree=ast.parse((ROOT/'tools/build_ui_gallery.py').read_text(encoding='utf-8'))
    cards=next(ast.literal_eval(n.value) for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cards' for t in n.targets))
    for title,image,source,description in cards[2:]:
        stem='interactive-sphere' if source=='interactive-menu-sphere' else 'main-menu'
        view=dict(label=description,image='gallery/media/ui/'+image,blend='sources/ui/'+source+'/'+stem+'.blend',glb='sources/ui/'+source+'/'+stem+'.glb')
        if image.endswith('spin-37.png'):view['video']='gallery/media/ui/interactive-menu-sphere/sphere-spin.webm'
        rows.append(dict(id='ui:'+image,name=title,category='ui',culture='shared',views=[view],detail='sources/ui/'+source+'/README.md'))
    families=ROOT/'sources/docs/assets/reconstruction/scaffolds/culture-kits/families'
    for folder in sorted(families.iterdir()):
        if not (folder/'model.json').is_file():continue
        model=json.loads((folder/'model.json').read_text());rows.append(scaffold(folder,model['family'],model['culture'],'gallery/scaffolds-cultures.md#'+model['family'].lower()))
    folder=ROOT/'sources/docs/assets/reconstruction/scaffolds/rigellian/size-2-refined'
    rows.append(scaffold(folder,'RIS2','rigellian','gallery/scaffolds-ris2.md'))
    assert sum(r['category']=='scaffolds' for r in rows)==19
    assert len({r['id'] for r in rows})==len(rows)
    for row in rows:
        assert (ROOT/row['detail'].split('#')[0]).is_file()
        for view in row['views']:
            for key in ['image','blend','glb','video']:
                if view.get(key):assert (ROOT/view[key]).is_file(),view[key]
    return rows

def scaffold(folder,family,culture,detail):
    views=[]
    for stage in sorted(folder.glob('stage-*')):
        if not (stage/'model.blend').is_file():continue
        rel=stage.relative_to(ROOT).as_posix()
        views.append(dict(label=stage.name,image='gallery/media/'+rel.removeprefix('sources/')+'/front-quarter.png',blend=rel+'/model.blend',glb=rel+'/model.glb'))
    assert views,family
    return dict(id='scaffold:'+family,name=family+' construction scaffold',category='scaffolds',culture=culture,views=views,detail=detail)

def supplemental_cards(rows):
    cards=[]
    for row in rows:
        e=html.escape
        view=row['views'][-1] if row['category']=='scaffolds' else row['views'][0]
        preview='<img loading="lazy" src="../'+view['image']+'" alt="'+e(row['name'])+'">'
        if view.get('video'):preview='<video controls loop muted playsinline preload="none" poster="../'+view['image']+'"><source src="../'+view['video']+'" type="video/webm"></video>'
        links=[]
        for v in row['views']:
            values=['<a href="../'+v['image']+'">Preview</a>']
            values += ['<a href="../'+v[k]+'">'+k.upper()+'</a>' for k in ['blend','glb'] if v.get(k)]
            links.append('<li>'+e(v['label'])+' · '+' · '.join(values)+'</li>')
        search=' '.join([row['id'],row['name'],row['category'],row['culture']]+[v['label'] for v in row['views']]).lower()
        cards.append('<article data-search="'+e(search,quote=True)+'" data-race="'+row['culture']+'" data-type="'+row['category']+'"><h2>'+e(row['name'])+'</h2><p>'+row['category']+' / '+row['culture']+'</p>'+preview+'<p><a href="../'+row['detail']+'">Source and evidence</a></p><details><summary>All stages / variants ('+str(len(links))+')</summary><ul>'+''.join(links)+'</ul></details></article>')
    return cards
