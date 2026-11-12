"""Render the full original-frame-referenced UI icon set in actual Blender.

blender -b --factory-startup --python-exit-code 1 --python FILE -- --output DIR
Original pixels are never loaded. Sources and independent GLB proof are saved.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
import legacy_shapes as g
import icon_recipes as r

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',required=True,type=Path)
p.add_argument('--samples',default=40,type=int)
p.add_argument('--only',help='Render one named group for diagnosis (no complete-set claim)')
a=p.parse_args(sys.argv[sys.argv.index('--')+1:])
out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
source_paths=[Path(__file__).resolve(),Path(g.__file__).resolve(),Path(r.__file__).resolve()]
source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}
g.scene.cycles.samples=a.samples
groups={};catalog=[]
STATES=['normal','hover','selected','pressed','disabled']


def group(name,make):
    g.parts=[];make()
    if not g.parts:raise RuntimeError('Empty group: '+name)
    groups[name]=list(g.parts)
    for o in g.parts:o.hide_render=True


for i,name in enumerate(r.NAMES):
    key=f'gameplay-{i:03}'
    group(key,lambda i=i:r.icon(i))
    catalog.append({'id':key,'family':'gameplay','frame':i,'motif':name,'group':key,'reference':'ICONS.256','reference_frame':i,'palette':'BLUE.256','icon_size':[48,38],'button_size':[48,40]})
for family,recipes,source in [('controls',r.CONTROLS,'CICONS.256'),('scroll',r.SCROLL,'SCROLL.256')]:
    for i,(name,make) in enumerate(recipes):
        key=f'{family}-{i:03}'
        group(key,make)
        catalog.append({'id':key,'family':family,'frame':i,'motif':name,'group':key,'reference':source,'reference_frame':i*3+1,'palette':'BLUE.256','icon_size':[30,30],'button_size':[32,32],
                        'original_frames':{'mask':i*3,'normal':i*3+1,'pressed':i*3+2}})

# FE_ICONS contains player-colour swatches, not the modern frontend menu symbols.
# Preserve all 17 indices including intentionally repeated neutral swatches.
swatch_colors=[(.65,.025,.025),(.75,.36,.03),(.65,.58,.025),(.025,.38,.025),(.05,.24,.58),(.055,.03,.58),(.36,.025,.55),(.52,.52,.52),(.52,.52,.52),(.52,.52,.52)]
swatch_colors+=swatch_colors[:7]
for i,color in enumerate(swatch_colors):
    key=f'frontend-{i:03}'
    mat=g.material('Player colour '+str(i),color,.25,.40)
    radius=.72 if i<10 else .38
    group(key,lambda mat=mat,radius=radius:g.uv('Player colour lens',(0,0,.1),(radius,radius,.18),mat))
    catalog.append({'id':key,'family':'frontend','frame':i,'motif':'player-colour-swatch','group':key,'reference':'FE_ICONS.256','reference_frame':i,'palette':'BLUE.256','icon_size':[40,40],'button_size':[48,40]})

group('brand-scitek',lambda:r.text('SCI-TEK',g.red,.44))
catalog.append({'id':'brand-scitek','family':'brand','frame':2,'motif':'sci-tek','group':'brand-scitek','reference':'BUTTONS.256','reference_frame':2,'palette':'embedded','icon_size':[84,27],'button_size':[84,27]})


def chrome(state,brand=False):
    if brand:
        g.uv('Oval badge outer rim',(0,0,-.24),(1.78,.55,.17),g.rim)
        g.uv('Oval badge inner face',(0,0,-.16),(1.62,.42,.14),g.silver)
    else:g.button()
    if state in ('hover','selected'):
        r.ellipse(rx=1.73 if not brand else 1.65,ry=1.16 if not brand else .45,
                  mat=g.blue if state=='selected' else g.white,r=.022 if state=='hover' else .04,z=-.055)
    if state=='pressed':
        for obj in g.parts:obj.location.z-=.07
        # Depression catches a narrower, darker upper bevel.
        if not brand:
            r.ellipse(rx=1.68,ry=1.11,mat=g.dark,r=.04,z=-.04)
    if state=='disabled':
        for obj in g.parts:
            if obj.data.materials:obj.data.materials[0]=g.rim if 'rim' in obj.name else g.dark


for state in STATES:
    group('chrome-'+state,lambda state=state:chrome(state))
    group('badge-'+state,lambda state=state:chrome(state,True))

# Silhouettes differ by physical parts, not a texture- or pixel-derived contour.
group_names={name:[o.name for o in objects] for name,objects in groups.items()}
group_sizes={item['group']:tuple(n*8 for n in item['icon_size']) for item in catalog}


def render(name,objects,proof=False):
    selected=set(objects)
    for obj in g.scene.objects:
        if obj.type in {'MESH','CURVE','FONT'}:obj.hide_render=obj not in selected
    width,height=group_sizes.get(name,(384,304))
    g.scene.render.resolution_x=width;g.scene.render.resolution_y=height
    g.scene.render.resolution_percentage=100
    g.scene.render.filepath=str(out/(name+('-imported' if proof else '')+'.png'))
    bpy.ops.render.render(write_still=True)


if a.only:
    if a.only not in groups:raise ValueError(a.only)
    render(a.only,groups[a.only])
    print('DIAGNOSTIC_GROUP_RENDERED',a.only)
    raise SystemExit(0)

for name,objects in groups.items():render(name,objects)

for name,objects in groups.items():
    col=bpy.data.collections.new(name);g.scene.collection.children.link(col)
    for obj in objects:
        for old in list(obj.users_collection):old.objects.unlink(obj)
        col.objects.link(obj)
        obj.hide_render=name!='gameplay-017';obj.hide_set(name!='gameplay-017')
bpy.ops.wm.save_as_mainfile(filepath=str(out/'legacy-ui-full.blend'))

for obj in g.scene.objects:
    obj.hide_set(False)
    obj.select_set(obj.type in {'MESH','CURVE','FONT'})
bpy.ops.export_scene.gltf(filepath=str(out/'legacy-ui-full.glb'),use_selection=True,export_format='GLB',export_apply=True)
for objects in groups.values():
    for obj in objects:bpy.data.objects.remove(obj,do_unlink=True)
before=set(g.scene.objects)
bpy.ops.import_scene.gltf(filepath=str(out/'legacy-ui-full.glb'))
imported={o.name:o for o in g.scene.objects if o not in before and o.type=='MESH'}
proof={}
for name,names in group_names.items():
    if not all(n in imported for n in names):raise RuntimeError('Incomplete GLB group: '+name)
    objects=[imported[n] for n in names]
    render(name,objects,True)
    proof[name]={'source_objects':len(names),'imported_objects':len(objects)}
if source_hashes!={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths}:
    raise RuntimeError('Generator source changed during rendering')
(out/'catalog.json').write_text(json.dumps({'schema':1,'items':catalog,'states':STATES,'source_hashes':source_hashes},indent=2)+'\n')
(out/'runtime-proof.json').write_text(json.dumps({'blender':bpy.app.version_string,'engine':g.scene.render.engine,'samples':a.samples,'view_transform':g.scene.view_settings.view_transform,'groups':proof},indent=2)+'\n')
print('FULL_ICON_SET_RENDERED',len(catalog),'icons',len(groups),'groups',out)
