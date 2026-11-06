"""Preserved-parent corrections for seven explicit trade-description conflicts.

Fictional metals, lunar/arcana motifs and material colours are authored readings,
not recovered canonical textures. Native shaders remain unbaked in the GLB.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
import bpy
import bmesh

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo', type=Path, required=True)
ap.add_argument('--out', type=Path, required=True)
a = ap.parse_args(sys.argv[sys.argv.index('--') + 1:])
ident = a.out.parent.name
assert ident in {'TI016','TI018','TI019','TI020','TI021','TI045','TI053'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
parent = a.repo/'sources/docs/assets/reconstruction/trading-goods-refined'/ident
if ident in {'TI016','TI018','TI019','TI020','TI021'}:
    parent /= 'optical'
source = parent/(ident+'.blend')
before = sha(source)
bpy.ops.wm.open_mainfile(filepath=str(source))
sys.path.insert(0, str(a.repo/'sources/tools/trading-goods'))
import modelling as M
M.ID = ident
M.COL = bpy.context.scene.collection
s = bpy.context.scene
checks = {}

def obj(fragment):
    return next(o for o in s.objects if fragment in o.name)

def material(fragment):
    return next(m for o in s.objects if o.type in {'MESH','CURVE','FONT'}
                for m in o.data.materials if fragment in m.name)

def remove(fragment):
    for o in list(s.objects):
        if fragment in o.name:
            bpy.data.objects.remove(o, do_unlink=True)

def surface(name, colour, role='metal', rough=.25, transmission=0, ior=1.5):
    m = M.mat(name, colour, metal=.94 if role=='metal' else 0,
              rough=rough, glass=transmission)
    m['physical_surface_role'] = role
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['IOR'].default_value = ior
    for n in m.node_tree.nodes:
        if n.type=='BUMP':
            n.inputs['Distance'].default_value = .00015 if role in {'gem','glass'} else .0008
            n.inputs['Strength'].default_value = .08
    return m

def assign(o, m):
    o.data = o.data.copy()
    o.data.materials.clear()
    o.data.materials.append(m)
    for p in getattr(o.data, 'polygons', []):
        p.material_index = 0

def gem_material(name, colour, ior=1.76, density=2):
    m = surface(name, colour, 'gem', .045, 1, ior)
    absorption = m.node_tree.nodes.new('ShaderNodeVolumeAbsorption')
    absorption.inputs['Color'].default_value = (*colour,1)
    absorption.inputs['Density'].default_value = density
    m.node_tree.links.new(absorption.outputs[0], m.node_tree.nodes['Material Output'].inputs['Volume'])
    return m

def closed_normals(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), o.name
    bm.to_mesh(o.data)
    bm.free()

if ident=='TI016':
    metal = surface('metachrome setting and chain', (.61,.65,.67), rough=.22)
    opal = surface('raw opal / milky natural colour play', (.63,.71,.65), 'gem', .19, .28, 1.45)
    bs = opal.node_tree.nodes['Principled BSDF']
    bs.inputs['Subsurface Weight'].default_value = .15
    bs.inputs['Subsurface Radius'].default_value = (.08,.12,.10)
    bs.inputs['Thin Film Thickness'].default_value = 420
    bs.inputs['Thin Film IOR'].default_value = 1.35
    noise = opal.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=9
    ramp = opal.node_tree.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[0].color=(.20,.40,.38,1)
    ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(.78,.70,.56,1)
    opal.node_tree.links.new(noise.outputs['Fac'],ramp.inputs[0]);opal.node_tree.links.new(ramp.outputs[0],bs.inputs['Base Color'])
    placements=[]
    for fragment,scale in [('tiara central opal',(.16,.12,.18)),('bracelet brilliant',(.23,.19,.14))]:
        old=obj(fragment);placements.append((old.parent,tuple(old.location),scale));bpy.data.objects.remove(old,do_unlink=True)
    for o in s.objects:
        if o.type in {'MESH','CURVE'}:assign(o,metal)
    for j,(p,loc,scale) in enumerate(placements):
        o=M.ball('unfaceted raw opal '+str(j),loc,scale,opal,p,sub=4)
        for v in o.data.vertices:
            v.co *= 1+.026*math.sin(v.co.x*13+v.co.z*7)*math.cos(v.co.y*11)
        closed_normals(o)
    checks.update(raw_opals=2,frame_material='metachrome',introduced_diamonds=0)

elif ident=='TI018':
    p=obj('square cut solitaire');emerald=material('emerald jewel');remove('octagonal square emerald');remove('white gold bezel')
    gold=surface('white gold square solitaire setting',(.67,.69,.66),rough=.19)
    outline=[(1,.82),(.82,1),(-.82,1),(-1,.82),(-1,-.82),(-.82,-1),(.82,-1),(1,-.82)]
    rings=[(.20,-.45),(.92,-.02),(1,.02),(1,.07),(.89,.19),(.74,.30),(.60,.36)]
    verts=[(x*r,y*r,z+.10) for r,z in rings for x,y in outline]
    faces=[tuple(range(7,-1,-1))]
    for j in range(len(rings)-1):
        for k in range(8):faces.append((j*8+k,j*8+(k+1)%8,(j+1)*8+(k+1)%8,(j+1)*8+k))
    faces.append(tuple((len(rings)-1)*8+k for k in range(8)))
    o=M.mesh('square emerald / chamfered step cut',verts,faces,emerald,p);closed_normals(o)
    points=[(x*1.015,y*1.015,.12) for x,y in outline];points.append(points[0])
    M.polyline('white gold square bezel',points,.038,gold,p)
    for x,y in [outline[j] for j in [0,2,4,6]]:
        M.rod('small white gold corner claw',(x*.98,y*.98,.06),(x*.94,y*.94,.23),.028,gold,p)
    checks.update(square_step_cut=True,setting_material='white gold',centre_stones=1)

elif ident=='TI019':
    p=obj('four-point ruby brooch');remove('raised ruby centre')
    ruby=gem_material('ruby / smooth cabochon',(.56,.008,.023),density=1.7)
    redgold=surface('red gold brooch petals',(.55,.22,.12),rough=.26)
    copper=surface('copper contrasting brooch petals',(.43,.17,.074),rough=.35)
    for j,o in enumerate(sorted([o for o in s.objects if 'pointed brooch petal' in o.name],key=lambda o:o.name)):
        assign(o,redgold if j%2 else copper)
        q=o.modifiers.new('Actual sheet thickness','SOLIDIFY');q.thickness=.045
        q=o.modifiers.new('Soft hand-worked petal rim','BEVEL');q.width=.012;q.segments=3
    profile=[(.365,.075),(.38,.105)]+[(.38*math.cos(t*math.pi/2),.105+.25*math.sin(t*math.pi/2)) for t in [j/24 for j in range(1,24)]]+[(.0001,.355)]
    o=M.lathe('nine-carat ruby / rounded unfaceted cabochon',profile,ruby,p,segments=96);closed_normals(o)
    M.ring('red gold cabochon seat',(0,0,.095),.375,.025,redgold,p)
    checks.update(cabochon_smooth=True,setting_materials=['red gold','copper'],carat_weight='lore identity; display-normalised scale')

elif ident=='TI020':
    gold=surface('white gold astramarine bezels',(.67,.69,.66),rough=.20)
    titanium=surface('titanium necklace links',(.30,.33,.35),rough=.33)
    for o in s.objects:
        if 'stone gold bezel' in o.name:o.name=o.name.replace('stone gold bezel','white gold bezel');assign(o,gold)
        elif 'necklace link' in o.name:assign(o,titanium)
    checks.update(astramarines=sum('individual astramarine ' in o.name for o in s.objects),setting_materials=['white gold','titanium'])
    assert checks['astramarines']==23

elif ident=='TI021':
    ultropaz=gem_material('ultropaz / warm amber transparent gem',(.73,.30,.018),1.63,2.2)
    alexandrite=gem_material('alexandrite / violet studio-light appearance',(.25,.035,.38),1.75,2.0)
    stones=sorted([o for o in s.objects if 'set ultropaz alexandrite' in o.name],key=lambda o:o.name)
    assert len(stones)==8
    for j,o in enumerate(stones):
        assign(o,ultropaz if j%2==0 else alexandrite);o.name=ident+' / inset '+('ultropaz' if j%2==0 else 'alexandrite')+' '+str(j)
    checks.update(gem_identities=['ultropaz','alexandrite'],intact_pearls=0,setting_material='24ct yellow gold',colour_change='One violet lighting state shown; dynamic spectral colour change not implemented')

elif ident=='TI045':
    remove('undissolved pearl');old=obj('bottle body');p=old.parent;bpy.data.objects.remove(old,do_unlink=True)
    glass=surface('clear hollow brandy flask glass',(.96,.98,1),'glass',.045,1,1.46)
    outer=[(.52,0),(.65,.06),(.65,1.425),(.585,1.65),(.1625,1.95),(.143,2.425),(.182,2.45),(.182,2.5)]
    inner=[(.152,2.5),(.152,2.46),(.113,2.425),(.1325,1.95),(.555,1.65),(.62,1.425),(.62,.09),(.50,.055)]
    o=M.lathe('hollow glass / open neck and thick base',outer+inner,glass,p,segments=96);closed_normals(o)
    liquid=surface('brandy with dissolved pearl / amber opalescent liquid',(.83,.43,.12),'glass',.07,1,1.36)
    nodes=liquid.node_tree.nodes;links=liquid.node_tree.links
    absorb=nodes.new('ShaderNodeVolumeAbsorption');absorb.inputs['Color'].default_value=(.74,.37,.09,1);absorb.inputs['Density'].default_value=.9
    scatter=nodes.new('ShaderNodeVolumeScatter');scatter.inputs['Color'].default_value=(.84,.79,.63,1);scatter.inputs['Density'].default_value=.045;scatter.inputs['Anisotropy'].default_value=.15
    add=nodes.new('ShaderNodeAddShader');links.new(absorb.outputs[0],add.inputs[0]);links.new(scatter.outputs[0],add.inputs[1]);links.new(add.outputs[0],nodes['Material Output'].inputs['Volume'])
    o=M.lathe('brandy fill / dissolved nacre, no intact pearls',[(.49,.06),(.614,.095),(.614,1.42),(.588,1.535),(.575,1.545),(.56,1.532),(.0001,1.53)],liquid,p,segments=96);closed_normals(o)
    checks.update(intact_pearl_objects=0,liquid_ior=1.36,product_state='Pearls dissolved in brandy; subtle nacre suspension is an authored appearance')

elif ident=='TI053':
    p=obj('multi-level Ortok game');ivory=material('ivory small pieces');dark=material('aged black base');brass=material('antiqued artifact brass')
    remove('miniature mansion');remove('mansion doorway')
    deceit=surface('deceit mansions / oxblood enamel',(.18,.026,.019),'paint',.32)
    bs=deceit.node_tree.nodes['Principled BSDF'];bs.inputs['Coat Weight'].default_value=.25
    # Earlier generator duplicated the same four columns once for every level.
    columns=sorted([o for o in s.objects if 'board support column' in o.name],key=lambda o:o.name)
    for o in columns[4:]:bpy.data.objects.remove(o,do_unlink=True)
    counts=[4,4,4,4,3,1];truth=deceit_count=0
    for tier,count in enumerate(counts):
        z=.2+tier*.45
        locations=[(-1.1,-.45),(-.4,-.65),(.4,-.65),(1.1,-.45)] if count==4 else [(-.88,-.55),(0,-.7),(.88,-.55)] if count==3 else [(0,-.20)]
        for k,(x,y) in enumerate(locations):
            is_truth=(k%2==0) if tier<4 else (k==0 if tier==4 else True)
            # On level five, one truth and two deceit; top goal is the tenth truth.
            kind='truth' if is_truth else 'deceit';truth+=is_truth;deceit_count+=not is_truth
            o=M.cube('mansion of '+kind,(x,y,z+.13),(.105,.08,.10),ivory if is_truth else deceit,p,bevel=.009)
            o['mansion_kind']=kind;o['board_tier']=tier;o['ultimate_truth']=tier==5
            M.cube('carved mansion doorway',(x,y-.085,z+.12),(.024,.007,.053),dark,p,bevel=.004)
            roof=M.mesh('pitched mansion roof',[(x-.125,y-.10,z+.23),(x+.125,y-.10,z+.23),(x,y-.10,z+.29),(x-.125,y+.10,z+.23),(x+.125,y+.10,z+.23),(x,y+.10,z+.29)],[(0,1,2),(5,4,3),(0,3,4,1),(1,4,5,2),(2,5,3,0)],brass,p);closed_normals(roof)
            if tier==5:
                M.ring('ultimate truth goal halo',(x,y,z+.32),.13,.013,brass,p)
    # Four authored character tokens evoke arcana roles; neither count nor glyphs
    # are asserted to reproduce the historical game's complete rule set.
    for j,x in enumerate([-.90,-.30,.30,.90]):
        y=-.89;z=.17
        token=M.root('arcana-like character token '+str(j),(x,y,z));token.parent=p;token['illustrative_role']=['crown','staff','scales','star'][j]
        M.lathe('turned character pedestal',[(.065,0),(.07,.025),(.035,.05),(.045,.16),(.032,.19)],ivory,token,segments=32)
        M.ball('carved character head',(0,0,.225),(.035,.033,.037),ivory,token,sub=2)
        if j==0:
            M.ring('crowned character',(0,0,.25),.035,.009,brass,token)
            for k in range(3):M.rod('crown point',((k-1)*.02,-.023,.25),((k-1)*.02,-.023,.285),.006,brass,token)
        elif j==1:M.rod('character staff',(.07,0,.04),(.07,0,.32),.007,brass,token)
        elif j==2:
            M.rod('character balance beam',(-.08,0,.26),(.08,0,.26),.006,brass,token)
            for dx in [-.07,.07]:M.ring('balance pan',(dx,0,.22),.025,.005,brass,token)
        else:
            pts=[]
            for k in range(10):
                t=k*math.tau/10;r=.065 if k%2==0 else .028;pts.append((r*math.sin(t),-.035,.30+r*math.cos(t)))
            M.mesh('star character emblem',pts,[tuple(range(10))],brass,token)
    checks.update(mansion_locations=sum(counts),truth=truth,deceit=deceit_count,board_tiers=6,top_goal='ultimate truth',illustrative_character_tokens=4)
    assert truth==deceit_count==10

s['lore_reconciliation']=json.dumps(checks,sort_keys=True)
s.render.filepath='//renders/'
bpy.context.preferences.filepaths.save_version=0
a.out.mkdir(parents=True,exist_ok=True)
native=a.out/(ident+'.blend')
bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
used={m for o in s.objects if o.type in {'MESH','CURVE','FONT'} for m in o.data.materials}
materials=[dict(name=m.name,role=m.get('physical_surface_role','metal'),base_colour=list(m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value)) for m in sorted(used,key=lambda m:m.name)]
for m in used:
    bs=m.node_tree.nodes.get('Principled BSDF')
    for key in ['Base Color','Roughness','Normal']:
        for link in list(bs.inputs[key].links):m.node_tree.links.remove(link)
for o in list(s.objects):
    if o.type in {'CURVE','FONT'}:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
bpy.ops.export_scene.gltf(filepath=str(a.out/(ident+'.glb')),export_format='GLB',export_apply=True,export_animations=False,export_cameras=False,export_lights=False)
record=json.loads((parent/'refinement.json').read_text())
record.update(refined_native_sha256=sha(native),glb_sha256=sha(a.out/(ident+'.glb')),geometry_builder='sources/tools/trading-goods/refining/reconcile_lore.py',geometry_builder_sha256=sha(Path(__file__)),prior_refined_native=source.relative_to(a.repo).as_posix(),prior_refined_native_sha256=before,lore_reconciliation=checks,materials=materials,glb_materials='Unbaked scalar/base-colour fallback; procedural native material appearance is not claimed for GLB')
(a.out/'refinement.json').write_text(json.dumps(record,indent=2)+'\n')
assert sha(source)==before
print('LORE_RECONCILED',ident,checks,flush=True)
