"""BR08/17/21: recover six-spire wards, branched Forge equipment and extractor housing."""
import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
from refine_braccatian_vessels import band,disc,ring
from refine_braccatian_longhouse import arch
from refine_braccatian_clan_complexes import pyramid,blue_terminal
from refine_braccatian_mast_facilities import ball
from manufactured_vessels import vessel
from manufactured_annuli import annulus
from build_openfa_assets import setup_scene,box,beam
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={'br08':(70,'Field Hospital'),'br17':(79,'Forge'),'br21':(83,'Subterranean Extractor')}
VIEWS={'front-quarter':(6,-13,7),'front':(0,-16,4),'side':(16,0,4),'rear-quarter':(-7,12,7),'equipment-detail':(3,-13,4)}
WARD_X=[-.65,0,.65]
WARD_HEIGHTS=[(2.26,2.00),(2.50,1.80),(2.26,2.00)]
FORGE=[(0,.23),(.05,.30),(1.40,.30),(1.49,.36),(1.62,.36),(1.80,.28),(1.93,.13),(2.02,.06)]
SIDE_HALL=[(0,.31),(.06,.37),(.17,.36),(.26,.24),(.35,.23),(.45,.30),(.60,.30),(.68,.19),(.74,.18),(.85,.29),(.92,.27),(1.02,.10)]
EXTRACTOR=[(0,.26),(.06,.32),(.60,.32),(.69,.39),(.82,.39),(.88,.29),(1.42,.29),(1.47,.27)]


def source(key):return ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian'/key/'model.blend'


def folders(key):
    rel=Path('docs/assets/reconstruction/braccatian-refined')/key
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def selected(view):
    return [o for o in bpy.context.scene.objects if o.type=='MESH' and
      (view!='equipment-detail' or not any(s in o.name for s in ['single tip','upper tip']))]


def shift_new(before,xy):
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH' and obj.name not in before:obj.location+=Vector((*xy,0))


def hospital(m):
    p='BR08 '
    box(p+'rear ward connecting lintel',(0,.25,.36),(2.06,.30,.22),m['rose-casing'],.012)
    for i,(x,heights) in enumerate(zip(WARD_X,WARD_HEIGHTS)):
        n=p+f'ward {i} '
        box(n+'rear chamber',(x,.08,.23),(.64,.78,.46),m['gold-casting'],.012)
        box(n+'broad rose terrace',(x,-.16,.465),(.645,1.34,.09),m['rose-casing'],.013)
        box(n+'gold terrace inset',(x,-.13,.511),(.56,1.15,.035),m['gold-casting'],.009)
        arch(n+'open entrance arch',x,m['rose-casing'])
        for sign in [-1,1]:
            box(n+f'entrance gold jamb {sign}',(x+sign*.237,-.796,.115),(.052,.026,.14),m['pale-gold'],.005)
            for j,y in enumerate([-.16,.08,.32]):box(n+f'side pale face {sign} {j}',(x+sign*.322,y,.24),(.025,.085,.14),m['pale-gold'],.004)
        for j,(y,height) in enumerate(zip([.23,-.28],heights)):
            before={o.name for o in bpy.context.scene.objects};name=n+f'slim tower {j}'
            pyramid(name,[(.48,.175),(.60,.16),(height-.26,.028),(height-.24,.025)],m)
            blue_terminal(name,height,m);shift_new(before,(x,y))


def forge(m):
    p='BR17 '
    before={o.name for o in bpy.context.scene.objects}
    vessel(p+'tall main core',FORGE,m['rose-casing'],[(-1.8,.85,.003)])
    band(p+'main broad upper gold rim',FORGE,1.49,1.55,m['gold-casting'])
    authored.patch(p+'main gold service backing',FORGE,(-.17,.17),(.13,1.30),m['gold-casting'],.010)
    for i,x in enumerate([-.10,0,.10]):authored.patch(p+f'main long dark slot {i}',FORGE,(x-.023,x+.023),(.20,1.24),m['recess'],.022)
    for i,x in enumerate([-.035,.035]):beam(p+f'paired upper tip {i}',(x,0,1.96),(x,0,2.25),.022,m['gold-casting'])
    ball(p+'main upper gold face',(-.16,-.29,1.71),.14,m['gold-casting'])
    ball(p+'main rounded rose face',(.17,-.25,1.42),.14,m['rose-casing'])
    shift_new(before,(-.14,0))
    before={o.name for o in bpy.context.scene.objects}
    left=[(0,.11),(.05,.15),(1.34,.15),(1.44,.10),(1.48,.025)]
    vessel(p+'left equipment cylinder',left,m['rose-casing'],[(-1.8,.75,.002)])
    ball(p+'left equipment gold head',(0,0,1.48),.145,m['gold-casting'])
    authored.patch(p+'left dark service backing',left,(-.072,.072),(.20,1.20),m['recess'],.010)
    for i,z in enumerate([.33,.60,.87,1.10]):authored.patch(p+f'left red service field {i}',left,(-.045,.045),(z-.075,z+.075),m['red-field'],.025)
    shift_new(before,(-.56,-.07))
    beam(p+'external left gold link',(-.56,-.07,.95),(-.88,-.07,.95),.033,m['gold-casting'])
    ball(p+'external left gold terminal',(-.88,-.07,.95),.105,m['gold-casting'])
    beam(p+'external left small tip',(-.88,-.07,1.00),(-.88,-.07,1.23),.023,m['gold-casting'])
    before={o.name for o in bpy.context.scene.objects}
    vessel(p+'layered low side hall',SIDE_HALL,m['rose-casing'],[(-1.8,.52,.002)])
    ring(p+'side hall broad gold face rim',SIDE_HALL,.28,.145,.088,m['gold-casting'])
    disc(p+'side hall dark face',SIDE_HALL,.28,.094,m['recess'],relief=.010)
    disc(p+'side hall gold face centre',SIDE_HALL,.28,.045,m['gold-casting'],relief=.025)
    for i,(z0,z1) in enumerate([(.09,.13),(.48,.52),(.86,.90)]):band(p+f'side hall gold division {i}',SIDE_HALL,z0,z1,m['gold-casting'])
    shift_new(before,(.48,.05))
    beam(p+'tall gold service upright',(.40,-.02,.30),(.40,-.02,2.00),.043,m['gold-casting'])
    ball(p+'upper service gold globe',(.40,-.02,2.04),.13,m['gold-casting'])


def slope_height(x):return 1.23+(x+.12)*(.10-1.23)/(.56+.12)


def extractor(m):
    p='BR21 '
    # The rear/side housing is a closed wedge under a sloping equipment face.
    vertices=[(x,y,z) for z in [0,1] for x,y in [(-.12,-.30),(.56,-.30),(.56,.52),(-.12,.52)]]
    vertices=[(x,y,0 if i<4 else slope_height(x)) for i,(x,y,z) in enumerate(vertices)]
    faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    mesh(p+'sloping rear housing',vertices,faces,m['rose-casing'],smooth=False)
    # Keep all slot centres outside the broad cylindrical shoulder's projection.
    for i,x in enumerate([.28,.39,.50]):
        corners=[(x-.023,-.17),(x+.023,-.17),(x+.023,.34),(x-.023,.34)]
        verts=[(xx,y,slope_height(xx)+depth) for depth in [-.008,.012] for xx,y in corners]
        mesh(p+f'sloping dark equipment slot {i}',verts,faces,m['recess'],smooth=False)
    before={o.name for o in bpy.context.scene.objects}
    vessel(p+'tiered cylindrical machine',EXTRACTOR,m['rose-casing'],[(-1.8,.42,.002),(-1.8,1.15,.002)])
    band(p+'broad gold shoulder',EXTRACTOR,.70,.76,m['gold-casting'])
    for i,x in enumerate([-.25,-.055,.055]):authored.patch(p+f'lower gold vertical rail {i}',EXTRACTOR,(x-.018,x+.018),(.08,.61),m['gold-casting'],.019)
    authored.patch(p+'lower dark service field',EXTRACTOR,(.10,.24),(.17,.58),m['recess'],.010)
    authored.patch(p+'long red service field',EXTRACTOR,(.12,.148),(.24,.51),m['red-field'],.025)
    authored.patch(p+'short red service field',EXTRACTOR,(.175,.220),(.32,.40),m['red-field'],.025)
    for i,angle in enumerate([-.65,0,.65]):
        obj=authored.patch(p+f'upper dark equipment field {i}',EXTRACTOR,(-.060,.060),(.92,1.37),m['recess'],.008);obj.rotation_euler.z=angle
        obj=authored.patch(p+f'upper gold vertical fitting {i}',EXTRACTOR,(-.022,.022),(.94,1.35),m['gold-casting'],.019);obj.rotation_euler.z=angle
    annulus(p+'flat upper rose rim',(0,0),[(1.44,.285,.21),(1.50,.285,.21)],m['rose-casing'],(-1.8,1.47,.001))
    vessel(p+'upper inset gold plate',[(1.465,.22),(1.483,.22)],m['gold-casting'],[])
    shift_new(before,(-.12,-.13))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;number,name=CASES[key];output,media=folders(key)
    old=json.loads(source(key).with_suffix('.json').read_text());assert old['global_type']==number
    output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True);scene=setup_scene(768,32)
    collection=bpy.data.collections.new(name+' complete editable work facility');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined'/key;materials={}
    for style,colour,metal in [('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),('blue-collar',(.045,.09,.36),.62),
      ('red-field',(.42,.025,.018),.55),('recess',(.035,.028,.019),.48),('pale-gold',(.68,.51,.24),.60)]:
        materials[style]=authored.worn_material(style,colour,metal);materials[style].name=key.upper()+' | worn '+style
    {'br08':hospital,'br17':forge,'br21':extractor}[key](materials)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']=f'openfa:building/legacy/{number:03}';root['footprint_width'],root['footprint_height']=old['footprint']
    objects=[o for o in scene.objects if o.type=='MESH']
    for obj in objects:
        obj.parent=root;bpy.context.view_layer.objects.active=obj
        if obj.name not in collection.objects:collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();uv(obj)
        modifier=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');modifier.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=modifier.name)
    for mat in list(materials.values()):
        if not mat.users:bpy.data.materials.remove(mat)
    used={Path(n.image.filepath_raw) for mat in bpy.data.materials if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for path in authored.TEXTURES.glob('*.png'):
        if path not in used:path.unlink() # Only newly generated unused case maps.
    collection.asset_mark();collection.asset_data.description=name+' visible legacy construction; hidden sections authored'
    for view,direction in VIEWS.items():
        fit_camera(direction,selected(view));scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(VIEWS['front-quarter'],objects);bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    dependencies=['refine_braccatian_pithoi.py','refine_braccatian_vessels.py','refine_braccatian_longhouse.py','refine_braccatian_clan_complexes.py','refine_braccatian_public_facilities.py','refine_braccatian_mast_facilities.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    observed={'br08':['Six blue-collared slim towers over joined low wards with three open entrance arches and repeated edge faces; initial five-tower assumption corrected by focused body/phase review','Basic field hospital per functional narrative, without invented medical symbols/apparatus'],
      'br17':['Tall core with long front slots/rounded upper faces, left red equipment column/external gold fitting, low layered side hall and tall gold service globe','Weapons factory, slightly smaller than TechMech and described as a temple to warfare; no invented clan emblems or exposed manufacturing process'],
      'br21':['Tiered cylindrical equipment, broad shoulder, flat upper rim/plate, gold vertical fittings, red lower fields and sloping side housing/slots','Efficient power-hungry combined mine per functional narrative; no exposed drill or unobserved underground animation']}
    meta=dict(issue=190,id=root['catalogue_id'],name=name,culture='braccatian',stage='work-facility-structural-refinement',source_study=source(key).relative_to(ROOT).as_posix(),source_blend_sha256=sha(source(key)),
      blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},
      texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      observed=observed[key]+['All 41 paletted catalogue phases and body/shadow layers inspected; functional payload byte ranges/hashes checked and read'],inferred=['Exact profiles, placement/depth, repeated fitting counts, hidden rear construction and alloy identities'],
      geometry_policy='Separate new assembly; earlier generic source preserved unchanged',mesh_objects=len(objects),views=list(VIEWS),blender=bpy.app.version_string,acceptance='Actual reconstruction; final artistic/game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('BRACCATIAN_WORK_FACILITY_REFINED',key,len(objects),flush=True)


if __name__=='__main__':main()
