"""BR07/09/10: source-visible hall entrances, slotted tower supports and shipyard modules."""
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
from refine_braccatian_longhouse import square_loft
from build_openfa_assets import setup_scene,box,cylinder,beam
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={'br07':(69,'Sports Hall'),'br09':(71,'Glasshouse'),'br10':(72,'TechMech')}
VIEWS={'front-quarter':(6,-13,7),'front':(0,-16,4),'side':(16,0,4),'rear-quarter':(-7,12,7),'equipment-detail':(3,-13,4)}
HALL=[(.34,.92),(.42,1.04),(.53,1.06),(.73,1.02),(1.0,.90),(1.30,.76),(1.60,.52),(1.78,.22),(1.82,.03)]
PILLAR=[(0,.16),(.04,.205),(.11,.20),(.60,.18),(.72,.14),(.78,.10)]
HEAD=[(.70,.075),(.76,.17),(.84,.225),(.92,.23),(1.02,.17),(1.08,.07)]
MECH=[(0,.28),(.05,.36),(.28,.42),(.48,.40),(.63,.32),(.80,.28),(.87,.32),
      (1.82,.32),(1.94,.23),(2.02,.07)]


def source(key):return ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian'/key/'model.blend'


def folders(key):
    rel=Path('docs/assets/reconstruction/braccatian-refined')/key
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def selected(view):
    return [o for o in bpy.context.scene.objects if o.type=='MESH' and
      (view!='equipment-detail' or not any(word in o.name for word in ['terminal','tip','handle']))]


def move_new(before,xy):
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH' and obj.name not in before:obj.location+=Vector((*xy,0))


def sports(m):
    p='BR07 '
    obj=vessel(p+'rear supporting foot',[(0,.65),(.05,.78),(.24,.80),(.40,.84),(.48,.80)],m['gold-casting'],[(-1.8,.23,.003)])
    obj.location.y=.20
    vessel(p+'broad domed hall',HALL,m['rose-casing'],[(-1.8,.85,.004)])
    band(p+'hall lower gold cornice',HALL,.40,.47,m['gold-casting'])
    vessel(p+'single upper terminal',[(1.78,.065),(1.85,.10),(1.96,.07),(2.05,.015)],m['gold-casting'],[])
    for i,angle in enumerate([-.95,.95]):
        obj=authored.patch(p+f'hall curved gold division {i}',HALL,(-.014,.014),(.58,1.44),m['gold-casting'],.016)
        obj.rotation_euler.z=angle
    for i,(xr,zr) in enumerate([((-.12,.12),(.53,.60)),((-.54,-.40),(.91,.97)),((.40,.54),(.91,.97)),
          ((-.57,-.46),(1.10,1.16)),((.46,.57),(1.10,1.16))]):
        authored.patch(p+f'hall broad gold face division {i}',HALL,xr,zr,m['gold-casting'],.016)
    for i,(x,z,r) in enumerate([(0,1.59,.10),(-.30,1.30,.105),(.30,1.30,.105),(0,1.16,.14)]):
        ring(p+f'hall face gold rim {i}',HALL,z,r,r*.63,m['gold-casting'],xcentre=x)
        disc(p+f'hall dark face {i}',HALL,z,r*.68,m['recess'],xcentre=x,relief=.012)
    disc(p+'upper pale fitting',HALL,1.59,.037,m['pale-gold'],relief=.023)
    box(p+'front rose connecting lintel',(0,-.84,.67),(1.20,.24,.15),m['rose-casing'],.018)
    for i,x in enumerate([-.40,.40]):
        before={o.name for o in bpy.context.scene.objects}
        vessel(p+f'front pillar {i}',PILLAR,m['gold-casting'],[(-1.6,.33,.002)])
        vessel(p+f'front gold globe {i}',HEAD,m['gold-casting'],[])
        authored.patch(p+f'pillar rose field {i}',PILLAR,(-.063,.063),(.04,.59),m['rose-casing'],.012)
        for j,z in enumerate([.10,.20,.30]):
            authored.patch(p+f'pillar red band {i} {j}',PILLAR,(-.030,.030),(z-.033,z+.033),m['red-field'],.024)
        for j,z in enumerate([.15,.25]):
            authored.patch(p+f'pillar pale band {i} {j}',PILLAR,(-.030,.030),(z-.014,z+.014),m['pale-gold'],.030)
        move_new(before,(x,-.86))


def pyramid_fitting(name,z,radius,height,half0,half1,material,inner=0,relief=.025):
    # A fitting conforming to a sloping square face, not a radial cylinder skin.
    count=64;verts=[]
    rings=[radius,inner] if inner else [radius,0]
    for depth in [-relief,.012]:
        for r in rings:
            for i in range(count):
                a=i*math.tau/count;x=r*math.cos(a);zz=z+r*math.sin(a)
                half=half0+(half1-half0)*zz/height
                verts.append((x,-half+depth,zz))
    # A tiny inner radius avoids duplicated degenerate centre rings.
    if not inner:
        # Rebuild as a closed fan with one centre per depth plane.
        verts=[]
        for depth in [-relief,.012]:
            verts.append((0,-(half0+(half1-half0)*z/height)+depth,z))
            for i in range(count):
                a=i*math.tau/count;x=radius*math.cos(a);zz=z+radius*math.sin(a)
                verts.append((x,-(half0+(half1-half0)*zz/height)+depth,zz))
        n=count+1;faces=[]
        for i in range(count):
            a,b=i+1,(i+1)%count+1;faces += [(0,a,b),(n,n+b,n+a),(a,n+a,n+b,b)]
    else:
        faces=[]
        for i in range(count):
            j=(i+1)%count
            faces += [(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),
              (i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)]
    return mesh(name,verts,faces,material)


def glasshouse(m):
    p='BR09 '
    vessel(p+'central lower neck',[(0,.12),(.66,.16),(.82,.21),(1.10,.21)],m['gold-casting'],[(-1.8,.75,.002)])
    for i,(x,y) in enumerate([(-.27,-.18),(.27,-.18),(0,.30)]):
        before={o.name for o in bpy.context.scene.objects}
        square_loft(p+f'pyramidal support {i}',[(0,.255),(.72,.060)],m['rose-casing'])
        if i<2:
            pyramid_fitting(p+f'foot gold fitting {i}',.27,.122,.72,.255,.060,m['gold-casting'],.080)
            pyramid_fitting(p+f'foot dark backing {i}',.27,.085,.72,.255,.060,m['recess'],relief=.008)
            if i==0:
                for j,(xx,z) in enumerate([(0,.33),(-.042,.24),(.042,.24)]):
                    obj=pyramid_fitting(p+f'foot blue fitting {j}',z,.032,.72,.255,.060,m['pale-blue'],relief=.040);obj.location.x=xx
            else:pyramid_fitting(p+'foot gold centre',.27,.047,.72,.255,.060,m['gold-casting'],relief=.035)
        move_new(before,(x,y))
    lower=[(.68,.16),(.80,.21),(1.10,.21)]
    authored.patch(p+'neck dark equipment field',lower,(-.16,.16),(.83,.98),m['recess'],.009)
    for i,x in enumerate([-.12,0,.12]):authored.patch(p+f'neck pale field {i}',lower,(x-.025,x+.025),(.85,.96),m['pale-gold'],.018)
    annulus(p+'lower open cage ring',(0,0),[(1.03,.30,.19),(1.13,.30,.19)],m['rose-casing'],(-1.8,1.08,.002))
    vessel(p+'inner gold cylinder',[(1.07,.13),(1.97,.13)],m['gold-casting'],[(-1.8,1.50,.002)])
    for i in range(8):
        a=i*math.tau/8
        obj=box(p+f'upper cage upright {i}',(.266*math.cos(a),.266*math.sin(a),1.54),(.056,.072,.87),m['rose-casing'],.006)
        obj.rotation_euler.z=a
    annulus(p+'upper open cage ring',(0,0),[(1.95,.30,.17),(2.02,.30,.17)],m['rose-casing'],(-1.8,1.98,.001))
    vessel(p+'rounded rose cap',[(1.98,.28),(2.05,.28),(2.13,.19),(2.18,.07)],m['rose-casing'],[])
    vessel(p+'small upper tip',[(2.14,.05),(2.24,.065),(2.33,.012)],m['rose-casing'],[])


def mech(m):
    p='BR10 '
    vessel(p+'layered central body',MECH,m['rose-casing'],[(-1.8,1.30,.003)])
    for i,(z0,z1) in enumerate([(.25,.31),(.58,.64),(.83,.89)]):band(p+f'gold shoulder band {i}',MECH,z0,z1,m['gold-casting'])
    for i,(z,y,width) in enumerate([(.06,-.40,1.14),(.12,-.35,1.06),(.18,-.30,.98)]):
        box(p+f'access step {i}',(0,y,z),(width,.46,.12),m['gold-casting'],.010)
    for i,x in enumerate([-.59,.59]):
        before={o.name for o in bpy.context.scene.objects}
        square_loft(p+f'side pyramidal module {i}',[(0,.28),(.95,.035)],m['rose-casing'])
        if i==1:
            pyramid_fitting(p+'side gold port rim',.27,.115,.95,.28,.035,m['gold-casting'],.08)
            pyramid_fitting(p+'side dark port backing',.27,.085,.95,.28,.035,m['recess'],relief=.008)
            for j,(xx,z) in enumerate([(0,.33),(-.042,.24),(.042,.24)]):
                obj=pyramid_fitting(p+f'side blue port {j}',z,.031,.95,.28,.035,m['pale-blue'],relief=.040);obj.location.x=xx
        move_new(before,(x,.03))
    fitting=[(0,.08),(.055,.14),(.12,.145),(.19,.09),(.42,.075),(.46,.035)]
    for i,x in enumerate([-.38,0,.38]):
        before={o.name for o in bpy.context.scene.objects}
        vessel(p+f'front gold fitting {i}',fitting,m['gold-casting'],[])
        authored.patch(p+f'front fitting red field {i}',fitting,(-.023,.023),(.21,.37),m['red-field'],.015)
        move_new(before,(x,-.48))
    authored.patch(p+'upper dark service field',MECH,(-.20,-.06),(1.12,1.71),m['recess'],.010)
    for i,x in enumerate([-.16,-.09]):
        for j,z in enumerate([1.22,1.40,1.58]):authored.patch(p+f'upper pale service face {i} {j}',MECH,(x-.020,x+.020),(z-.033,z+.033),m['pale-blue'],.023)
    authored.patch(p+'upper gold louver backing',MECH,(.005,.085),(1.11,1.72),m['gold-casting'],.010)
    for i,z in enumerate([1.20,1.35,1.50,1.65]):authored.patch(p+f'upper dark louver {i}',MECH,(.020,.070),(z-.025,z+.025),m['recess'],.020)
    ring(p+'upper gold face rim',MECH,1.56,.075,.044,m['gold-casting'],xcentre=.20)
    disc(p+'upper red face',MECH,1.56,.048,m['red-field'],xcentre=.20,relief=.016)
    for i,x in enumerate([-.36,.36]):
        beam(p+f'waist gold upright {i}',(x,-.06,.43),(x,-.06,1.06),.026,m['gold-casting'])
    vessel(p+'single gold terminal',[(1.98,.05),(2.10,.065),(2.13,.025),(2.40,.021)],m['gold-casting'],[])


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;number,name=CASES[key];output,media=folders(key)
    original=json.loads(source(key).with_suffix('.json').read_text());assert original['global_type']==number
    output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    scene=setup_scene(768,32)
    collection=bpy.data.collections.new(name+' complete editable structural refinement');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined'/key
    materials={}
    for style,colour,metal in [('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),('red-field',(.42,.025,.018),.55),
          ('recess',(.035,.028,.019),.48),('pale-gold',(.68,.51,.24),.60),('pale-blue',(.48,.61,.72),.62)]:
        materials[style]=authored.worn_material(style,colour,metal);materials[style].name=key.upper()+' | worn '+style
    {'br07':sports,'br09':glasshouse,'br10':mech}[key](materials)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']=f'openfa:building/legacy/{number:03}';root['footprint_width'],root['footprint_height']=original['footprint']
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
        if path not in used:path.unlink() # Only unused newly generated case maps.
    collection.asset_mark();collection.asset_data.description=name+' visible legacy structure; hidden construction authored'
    for view,direction in VIEWS.items():
        fit_camera(direction,selected(view));scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(VIEWS['front-quarter'],objects);bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    dependencies=['refine_braccatian_pithoi.py','refine_braccatian_vessels.py','refine_braccatian_longhouse.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    observations={'br07':['Single broad domed hall, paired substantial front pillars with gold globes and red/pale foot fields, front circular fittings','Semi-ritualised communal exercise per functional narrative; no invented clan emblem or ritual machinery'],
      'br09':['Slotted upper cylinder, rounded rose cap/small tip, lower neck fields and three pyramidal supports with blue/gold fittings','Security practically non-existent per honour-culture narrative; cage divisions are visible structure, not invented defensive machinery'],
      'br10':['Practical cylindrical core with shoulder bands, access steps, side pyramidal modules, front fittings and upper service fields','Extensive practical ship construction yard with some heavy-metal-type decor per functional narrative; no invented exposed assembly animation']}
    meta=dict(issue=190,id=root['catalogue_id'],name=name,culture='braccatian',stage='public-facility-structural-refinement',source_study=source(key).relative_to(ROOT).as_posix(),
      source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},
      texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),
      reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      observed=observations[key]+['All 41 correctly paletted catalogue phases and both surface descriptors inspected'],inferred=['Exact profiles, dimensions, hidden construction, division/fitting counts and material identities'],
      geometry_policy='New case-specific assembly; earlier generic study preserved separately',mesh_objects=len(objects),views=list(VIEWS),blender=bpy.app.version_string,acceptance='Actual reconstruction; final artistic/game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('BRACCATIAN_PUBLIC_FACILITY_REFINED',key,len(objects),flush=True)


if __name__=='__main__':main()
