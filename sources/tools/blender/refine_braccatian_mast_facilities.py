"""Recover BR03/13/16 visible head, column and mast assemblies from paletted references."""
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
from refine_braccatian_vessels import disc,ring,band
from manufactured_vessels import vessel,profile_radius
from build_openfa_assets import setup_scene,cylinder,beam
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={'br03':(65,'Radiation Shield'),'br13':(75,'Eyes-and-Ears'),'br16':(78,'Aegis')}
VIEWS={'front-quarter':(6,-13,7),'front':(0,-16,4),'side':(16,0,4),
       'rear-quarter':(-7,12,7),'equipment-detail':(3,-13,4)}
SHIELD_CENTRES=[(-.62,-.35),(0,.60),(.62,-.35)]
SHIELD_BELL=[(0,.47),(.025,.54),(.075,.54),(.10,.50),(.16,.44),(.24,.36),
             (.33,.29),(.43,.24),(.52,.22),(.59,.18),(.64,.105),(.68,.065)]
SHIELD_HANDLE=[(.64,.045),(.70,.042),(.76,.045),(.80,.036),(1.05,.036),
               (1.08,.052),(1.24,.050),(1.29,.025),(1.31,.012)]
SENSOR_MAIN=(.18,.08)
SENSOR_SIDE=(-.34,-.14)
SENSOR_LOWER=[(0,.17),(.035,.23),(.10,.22),(1.65,.12),(1.77,.09),(1.84,.09)]
SENSOR_HEAD=[(1.78,.085),(1.84,.14),(1.90,.17),(2.18,.17),(2.25,.12),(2.31,.07),(2.35,.06)]
SENSOR_COLLAR=[(2.31,.055),(2.34,.08),(2.40,.08),(2.43,.033)]
SENSOR_MAST=[(2.39,.032),(2.50,.04),(2.91,.032),(3.00,.009)]
SENSOR_SIDE_BASE=[(0,.14),(.035,.19),(.10,.19),(.72,.18),(.81,.13),(.88,.10)]
SENSOR_SIDE_HEAD=[(.81,.09),(.86,.17),(.94,.21),(1.06,.22),(1.17,.17),(1.25,.07)]
SENSOR_SIDE_CAP=[(1.21,.06),(1.25,.075),(1.33,.075),(1.36,.025)]
AEGIS_FOOT=[(0,.34),(.035,.53),(.12,.64),(.22,.64),(.34,.50),(.41,.27),(.46,.15)]
AEGIS_COLUMN=[(.42,.14),(.48,.20),(.55,.21),(.99,.21),(1.06,.15),(1.12,.13)]
AEGIS_ORB=[(1.07,.06),(1.12,.15),(1.20,.235),(1.31,.245),(1.40,.20),(1.47,.10),(1.50,.02)]
AEGIS_MAST=[(.60,.036),(.67,.027),(2.02,.027),(2.04,.055),(2.16,.055),(2.19,.028),(2.26,.028)]


def source(key):return ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian'/key/'model.blend'


def folders(key):
    relative=Path('docs/assets/reconstruction/braccatian-refined')/key
    return ROOT/'sources'/relative,ROOT/'gallery/media'/relative


def new_objects(before):return [o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in before]


def offset(objects,xy):
    for obj in objects:obj.location+=Vector((*xy,0))


def ball(name,centre,radius,material):
    profile=[]
    for i in range(25):
        angle=-math.pi/2+math.pi*i/24
        profile.append((centre[2]+radius*math.sin(angle),max(.001,radius*math.cos(angle))))
    obj=vessel(name,profile,material,[]);obj.location.x,obj.location.y=centre[:2]
    return obj


def selected(view):
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    return [o for o in objects if 'mast' not in o.name and 'handle' not in o.name] if view=='equipment-detail' else objects


def radiation_shield(prefix,m):
    for i,xy in enumerate(SHIELD_CENTRES):
        before={o.name for o in bpy.context.scene.objects};name=prefix+f' unit {i}'
        vessel(name+' continuous flared bell',SHIELD_BELL,m['gold-casting'],[(-1.9,.15,.002),(-1.8,.45,.002)])
        vessel(name+' banded handle',SHIELD_HANDLE,m['gold-casting'],[])
        band(name+' rose hem trim',SHIELD_BELL,.075,.11,m['rose-casing'])
        for j,z in enumerate([.75,1.02]):
            band(name+f' blue handle band {j}',SHIELD_HANDLE,z,z+.045,m['blue-collar'])
        ring(name+' front gold rim',SHIELD_BELL,.46,.075,.048,m['gold-casting'])
        disc(name+' red front field',SHIELD_BELL,.46,.054,m['red-field'],relief=.016)
        obj=disc(name+' pale side field',SHIELD_BELL,.48,.045,m['pale-blue'],relief=.015)
        obj.rotation_euler.z=-math.pi/3
        offset(new_objects(before),xy)


def eyes_and_ears(prefix,m):
    before={o.name for o in bpy.context.scene.objects}
    vessel(prefix+' main tapered body',SENSOR_LOWER,m['rose-casing'],[(-1.8,.80,.002)])
    vessel(prefix+' main gold capsule',SENSOR_HEAD,m['gold-casting'],[(-1.9,2.00,.002)])
    vessel(prefix+' main blue collar',SENSOR_COLLAR,m['blue-collar'],[])
    vessel(prefix+' main single mast',SENSOR_MAST,m['gold-casting'],[])
    authored.patch(prefix+' main dark equipment backing',SENSOR_LOWER,(-.046,.046),(1.02,1.62),m['recess'],.009)
    for i,z in enumerate([1.12,1.32,1.52]):
        authored.patch(prefix+f' main pale face {i}',SENSOR_LOWER,(-.030,.030),(z-.045,z+.045),m['pale-blue'],.018)
    authored.patch(prefix+' main lower gold service field',SENSOR_LOWER,(-.046,.046),(.30,.94),m['gold-casting'],.018)
    for i,z in enumerate([.37,.50,.63,.76,.89]):
        authored.patch(prefix+f' main service dark division {i}',SENSOR_LOWER,(-.027,.027),(z-.022,z+.022),m['recess'],.021)
    offset(new_objects(before),SENSOR_MAIN)
    before={o.name for o in bpy.context.scene.objects}
    vessel(prefix+' side lower cylinder',SENSOR_SIDE_BASE,m['gold-casting'],[(-1.8,.40,.002)])
    vessel(prefix+' side gold globe',SENSOR_SIDE_HEAD,m['gold-casting'],[(-1.8,1.05,.001)])
    vessel(prefix+' side blue cap',SENSOR_SIDE_CAP,m['blue-collar'],[])
    authored.patch(prefix+' side dark service field',SENSOR_SIDE_BASE,(-.055,.055),(.13,.69),m['recess'],.009)
    for i,z in enumerate([.20,.34,.48,.62]):
        authored.patch(prefix+f' side gold field division {i}',SENSOR_SIDE_BASE,(-.033,.033),(z-.022,z+.022),m['gold-casting'],.019)
    offset(new_objects(before),SENSOR_SIDE)
    start=Vector((*SENSOR_SIDE,1.31));elbow=Vector((*SENSOR_SIDE,1.75));end=Vector((*SENSOR_MAIN,1.89))
    beam(prefix+' visible link upright',start,elbow,.019,m['gold-casting'])
    beam(prefix+' visible link crosspiece',elbow,end,.019,m['gold-casting'])
    ball(prefix+' visible link elbow',elbow,.029,m['gold-casting'])


def aegis(prefix,m):
    vessel(prefix+' rose dome foot',AEGIS_FOOT,m['rose-casing'],[(-1.8,.24,.003)])
    vessel(prefix+' central gold column',AEGIS_COLUMN,m['gold-casting'],[(-1.8,.75,.002)])
    vessel(prefix+' upper gold globe',AEGIS_ORB,m['gold-casting'],[(-1.8,1.30,.001)])
    ring(prefix+' foot broad gold fitting',AEGIS_FOOT,.22,.135,.085,m['gold-casting'])
    disc(prefix+' foot dark fitting backing',AEGIS_FOOT,.22,.090,m['recess'])
    disc(prefix+' foot central gold fitting',AEGIS_FOOT,.22,.044,m['gold-casting'],relief=.027)
    authored.patch(prefix+' column dark field backing',AEGIS_COLUMN,(-.145,.145),(.53,1.00),m['recess'],.008)
    for i,x in enumerate([-.10,0,.10]):
        authored.patch(prefix+f' red vertical field {i}',AEGIS_COLUMN,(x-.023,x+.023),(.56,.97),m['red-field'],.018)
    for i in range(8):
        phi=math.tau*i/8
        ball(prefix+f' upper globe lobe {i}',(.19*math.cos(phi),-.085,1.29+.19*math.sin(phi)),.055,m['gold-casting'])
    for sign in [-1,1]:
        x=sign*.48
        obj=vessel(prefix+' straight side mast '+str(sign),AEGIS_MAST,m['gold-casting'],[])
        obj.location.x=x
        beam(prefix+' gold mast crossarm '+str(sign),(0,0,.65),(x,0,.65),.042,m['gold-casting'])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model
    number,name=CASES[key];prefix=key.upper();output,media=folders(key)
    original=json.loads(source(key).with_suffix('.json').read_text())
    assert original['global_type']==number
    output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    scene=setup_scene(768,32)
    collection=bpy.data.collections.new(name+' refined complete editable source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined'/key
    styles=[('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),('recess',(.035,.028,.019),.48),
            ('pale-blue',(.48,.61,.72),.62),('blue-collar',(.045,.09,.36),.62),('red-field',(.42,.025,.018),.55)]
    materials={}
    for style,colour,metal in styles:
        materials[style]=authored.worn_material(style,colour,metal);materials[style].name=prefix+' | worn '+style
    {'br03':radiation_shield,'br13':eyes_and_ears,'br16':aegis}[key](prefix,materials)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']=f'openfa:building/legacy/{number:03}'
    root['footprint_width'],root['footprint_height']=original['footprint']
    objects=[o for o in scene.objects if o.type=='MESH']
    for obj in objects:
        obj.parent=root
        if obj.name not in collection.objects:collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        uv(obj)
        modifier=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');modifier.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    for material in list(materials.values()):
        if not material.users:bpy.data.materials.remove(material)
    used={Path(n.image.filepath_raw) for mat in bpy.data.materials if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for path in authored.TEXTURES.glob('*.png'):
        if path not in used:path.unlink() # Only generated unused maps in this new case directory.
    collection.asset_mark();collection.asset_data.description=name+' source-supported construction; hidden geometry/calibration authored'
    for view,direction in VIEWS.items():
        fit_camera(direction,selected(view));scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(VIEWS['front-quarter'],objects)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    observed={
      'br03':['Three bell-shaped continuous gold casings with flared lower hems and slender gold/blue banded handles, red front and pale side fields','User clarified the handbell silhouette; no marshmallow cylinders, separate globular heads or invented acoustic/clapper mechanism','Original arrangement is three separate grounded units; no invented common platform'],
      'br13':['Tall tapered main body with upper gold capsule/blue collar and lower side cylinder/globe/cap','Visible upper link and separate front equipment fields; no generic free-standing sensor spindle'],
      'br16':['Rose dome foot, central gold column/red vertical fields and lobed gold upper globe','Two straight separated gold masts and lower crossarms, not kite-shaped wire loops']}
    dependencies=['refine_braccatian_pithoi.py','refine_braccatian_vessels.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=190,id=root['catalogue_id'],name=name,culture='braccatian',stage='visible-mast-facility-refinement',
      source_study=source(key).relative_to(ROOT).as_posix(),source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),
      dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},
      lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      observed=observed[key]+['All 41 correctly paletted catalogue phases and surface parts inspected'],inferred=['Exact profiles, layout/depth and repeated equipment/lobe counts','Visible link/support interpretation and hidden rear details; no alloy or operating timing recovered'],
      geometry_policy='New case-specific assembly; earlier generic source preserved separately with no retained-geometry claim',mesh_objects=len(objects),views=list(VIEWS),blender=bpy.app.version_string,
      acceptance='Source-led structural refinement; final artistic acceptance and gameplay calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('BRACCATIAN_MAST_FACILITY_REFINED',key,len(objects),flush=True)


if __name__=='__main__':main()
