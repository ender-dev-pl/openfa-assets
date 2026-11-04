"""Recover distinct BR04/14/15 source-visible vessels, fittings and equipment regions."""
import argparse
import json
import math
from pathlib import Path
import sys

import bmesh
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
from build_openfa_assets import setup_scene,cylinder
from manufactured_vessels import vessel,profile_radius
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={
 'br04':dict(number=66,name='Source',footprint=2,
  lower=[(0,.30),(.035,.38),(.10,.40),(.85,.40),(.96,.37),(1.08,.29),(1.18,.15),(1.25,.095),(1.34,.095)],
  upper=[(1.29,.08),(1.37,.21),(1.47,.34),(1.60,.43),(1.75,.47),(1.88,.43),(2.00,.31),(2.09,.16),(2.16,.08)],
  neck=[(2.11,.075),(2.14,.12),(2.22,.12),(2.25,.055)],
  mast=[(2.22,.045),(2.30,.055),(2.39,.045),(2.46,.012)],
  body_style='gold-casting',inset_style='pale-blue',
  observed=['Slender gold lower cylinder and rounded upper vessel joined by a narrow neck','Rose horizontal regions, front equipment, blue upper collar and single gold terminal','Functional narrative: nutrition provision with a secondary ceremonial role; no invented ritual apparatus']),
 'br14':dict(number=76,name='Anchor',footprint=2,
  lower=list(authored.BASE),upper=[(z,r) for z,r in authored.JAR if z<1.96]+[(1.96,.464),(2.06,.36),(2.115,.272),(2.15,.187),(2.175,.077),(2.18,.008)],
  body_style='rose-casing',inset_style='red-field',
  observed=['Low rose double-shoulder housing over a ribbed gold cylinder; no separate mast/globe','Broad upper circular gold fitting, dark middle vertical fields, lower red service column','Functional narrative establishes gravity-nullifier role, not exposed internal machinery']),
 'br15':dict(number=77,name='Heart-of-the-Sun',footprint=2,
  lower=[(0,.24),(.035,.40),(.12,.52),(.28,.58),(.47,.56),(.65,.45),(.78,.30),(.85,.13),(.97,.12)],
  upper=[(.92,.10),(1.02,.29),(1.15,.43),(1.32,.50),(1.47,.49),(1.62,.39),(1.76,.22),(1.84,.07)],
  neck=[(1.80,.06),(1.84,.105),(1.92,.105),(1.95,.045)],
  mast=[(1.92,.040),(2.03,.050),(2.10,.038),(2.25,.032),(2.32,.055),(2.39,.025),(2.43,.008)],
  body_style='rose-casing',inset_style='red-field',
  observed=['Two rounded rose chambers, narrow gold waist, blue collar and stepped single gold terminal','Broad gold upper face grille, circular lower fitting and two separate front upright fittings','Functional text explicitly states fusion power; no exposed reactor internals or operating loop established'])}
VIEWS={'front-quarter':(6,-13,7),'front':(0,-16,4),'side':(16,0,4),
       'rear-quarter':(-7,12,7),'equipment-detail':(3,-13,4)}


def folders(key):
    rel=Path('docs/assets/reconstruction/braccatian-refined')/key
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def source(key):
    return ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian'/key/'model.blend'


def disc(name,profile,zcentre,radius,material,xcentre=0,relief=.008):
    count=128
    vertices=[]
    for depth in [-relief,.012]:
        vertices.append((xcentre,authored.skin(profile,xcentre,zcentre)+depth,zcentre))
        for i in range(count):
            angle=math.tau*i/count
            x,z=xcentre+radius*math.cos(angle),zcentre+radius*math.sin(angle)
            vertices.append((x,authored.skin(profile,x,z)+depth,z))
    n=count+1;faces=[]
    for i in range(count):
        a,b=i+1,(i+1)%count+1
        faces.extend([(0,a,b),(n,n+b,n+a),(a,n+a,n+b,b)])
    return mesh(name,vertices,faces,material)


def ring(name,profile,zcentre,outer,inner,material,xcentre=0):
    count=128;vertices=[]
    for depth in [-.035,.012]:
        for radius in [outer,inner]:
            for i in range(count):
                phi=math.tau*i/count
                x,z=xcentre+radius*math.cos(phi),zcentre+radius*math.sin(phi)
                vertices.append((x,authored.skin(profile,x,z)+depth,z))
    faces=[]
    for i in range(count):
        j=(i+1)%count
        faces.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),
                      (i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)])
    return mesh(name,vertices,faces,material)


def band(name,profile,z0,z1,material):
    count,rows=128,9;vertices=[]
    for back in [False,True]:
        for row in range(rows):
            z=z0+(z1-z0)*row/(rows-1)
            radius=profile_radius(profile,z)+(-.010 if back else .012)
            for i in range(count):
                phi=math.tau*i/count;vertices.append((radius*math.cos(phi),radius*math.sin(phi),z))
    n=count*rows;faces=[]
    for row in range(rows-1):
        for i in range(count):
            j=(i+1)%count;a=row*count+i;b=row*count+j
            faces.extend([(a,b,b+count,a+count),(a+n,a+count+n,b+count+n,b+n)])
    for row in [0,rows-1]:
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;faces.append((a,a+n,b+n,b))
    return mesh(name,vertices,faces,material)


def selected(view):
    objects=[o for o in bpy.context.scene.objects if o.type=='MESH']
    return [o for o in objects if not any(t in o.name for t in ['mast','collar'])] if view=='equipment-detail' else objects


def build(key):
    case=CASES[key];prefix=key.upper();lower,upper=case['lower'],case['upper']
    output,media=folders(key)
    output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    scene=setup_scene(768,32)
    collection=bpy.data.collections.new(case['name']+' complete refined editable source')
    scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined'/key
    materials={}
    for style,colour,metal in [('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),
       ('recess',(.035,.028,.019),.48),('pale-blue',(.48,.61,.72),.62),('blue-collar',(.045,.09,.36),.62),('red-field',(.42,.025,.018),.55)]:
        materials[style]=authored.worn_material(style,colour,metal)
        materials[style].name=prefix+' | worn '+style
    gold,rose,dark,blue,red=[materials[n] for n in ['gold-casting','rose-casing','recess','pale-blue','red-field']]
    vessel(prefix+' lower body',lower,gold if key!='br15' else rose,[(-1.9,.5,.003)])
    vessel(prefix+' upper body',upper,materials[case['body_style']],[(-1.8,(upper[0][0]+upper[-1][0])/2,.003)])
    if 'neck' in case:
        vessel(prefix+' blue collar',case['neck'],materials['blue-collar'],[(-1.8,sum(p[0] for p in case['neck'])/len(case['neck']),.001)])
        vessel(prefix+' single gold mast',case['mast'],gold,[])
    if key=='br14':
        for i in range(12):
            if i==9:continue
            obj=authored.patch(prefix+f' lower gold flute {i:02}',lower,(-.035,.035),(.12,.87),gold,.025)
            obj.rotation_euler.z=math.tau*i/12+math.pi/2
        authored.patch(prefix+' lower dark field',lower,(-.10,.10),(.16,.82),dark,.010)
        for i,z in enumerate([.28,.49,.70]):
            ring(prefix+f' lower port rim {i}',lower,z,.076,.05,gold)
            disc(prefix+f' lower port face {i}',lower,z,.055,red if i<2 else blue,relief=.015)
        authored.patch(prefix+' middle gold field frame',upper,(-.22,.22),(1.29,1.47),gold,.02)
        for i in range(5):
            x=-.16+i*.08
            authored.patch(prefix+f' middle dark field {i}',upper,(x-.023,x+.023),(1.32,1.44),dark,.024)
        ring(prefix+' broad gold upper fitting',upper,1.78,.205,.135,gold)
        disc(prefix+' upper dark fitting centre',upper,1.78,.140,dark)
        ring(prefix+' inner gold upper fitting',upper,1.78,.10,.052,gold)
        disc(prefix+' gold central fitting',upper,1.78,.044,gold,relief=.027)
    elif key=='br04':
        for i in range(8):
            if i==6:continue
            obj=authored.patch(prefix+f' lower cast rib {i}',lower,(-.025,.025),(.13,.87),gold,.025)
            obj.rotation_euler.z=math.tau*i/8+math.pi/2
        for sign in [-1,1]:
            authored.patch(prefix+' lower gold service rail '+str(sign),lower,(sign*.20-.015,sign*.20+.015),(.18,.85),gold,.022)
        for label,profile,z0,z1 in [('lower high',lower,.95,1.015),('lower middle',lower,.70,.77),
                                    ('upper high',upper,1.98,2.035),('upper low',upper,1.48,1.54)]:
            band(prefix+' rose band '+label,profile,z0,z1,rose)
        authored.patch(prefix+' lower gold fitting belt',lower,(-.36,.36),(.47,.65),gold,.016)
        ring(prefix+' lower gold round fitting',lower,.56,.118,.073,gold)
        disc(prefix+' lower dark round fitting',lower,.56,.075,dark)
        disc(prefix+' lower gold centre',lower,.56,.037,gold,relief=.027)
        ring(prefix+' bottom service rim',lower,.18,.065,.043,gold)
        disc(prefix+' bottom pale blue service face',lower,.18,.046,blue,relief=.016)
        authored.patch(prefix+' upper dark equipment field',upper,(-.073,.073),(1.63,1.91),dark,.010)
        for i,z in enumerate([1.70,1.84]):
            authored.patch(prefix+f' upper pale equipment face {i}',upper,(-.045,.045),(z-.027,z+.027),blue,.018)
        for sign in [-1,1]:
            authored.patch(prefix+' upper gold side rail '+str(sign),upper,(sign*.09-.015,sign*.09+.015),(1.62,1.92),gold,.024)
    else:
        band(prefix+' gold waist ring',lower,.86,.94,gold)
        ring(prefix+' upper gold face bezel',upper,1.36,.178,.122,gold)
        disc(prefix+' upper dark grille backing',upper,1.36,.128,dark)
        for i,x in enumerate([-.075,0,.075]):
            authored.patch(prefix+f' upper gold grille bar {i}',upper,(x-.013,x+.013),(1.255,1.465),gold,.029)
        ring(prefix+' lower gold face bezel',lower,.42,.172,.105,gold,xcentre=-.16)
        disc(prefix+' lower dark face backing',lower,.42,.112,dark,xcentre=-.16)
        ring(prefix+' lower inner gold face',lower,.42,.078,.035,gold,xcentre=-.16)
        disc(prefix+' lower gold centre',lower,.42,.030,gold,xcentre=-.16,relief=.028)
        for i,(x,y) in enumerate([(.22,-.51),(.40,-.40)]):
            cylinder(prefix+f' front upright {i}',(x,y,.35),.025,.66,gold,vertices=64)
            cylinder(prefix+f' front upright foot {i}',(x,y,.035),.042,.04,gold,vertices=64)
            cylinder(prefix+f' front upright collar {i}',(x,y,.60),.036,.06,rose,vertices=64)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']=f"openfa:building/legacy/{case['number']:03}"
    root['footprint_width']=root['footprint_height']=case['footprint']
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
    # Unused material families are not evidence for additional source colours.
    for style,material in list(materials.items()):
        if not material.users:bpy.data.materials.remove(material)
    used_images={n.image for mat in bpy.data.materials if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    texture_files={Path(image.filepath_raw) for image in used_images}
    for path in authored.TEXTURES.glob('*.png'):
        if path not in texture_files:path.unlink() # Only newly generated unused maps in this case's new directory.
    collection.asset_mark();collection.asset_data.description=case['name']+' source-supported visible refinement; exact hidden construction authored'
    for view,direction in VIEWS.items():
        fit_camera(direction,selected(view));scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(VIEWS['front-quarter'],objects)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    dependencies=['refine_braccatian_pithoi.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=190,id=root['catalogue_id'],name=case['name'],culture='braccatian',stage='visible-vessel-refinement',
        source_study=source(key).relative_to(ROOT).as_posix(),source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
        generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},
        texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},
        lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),
        reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),
        functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
        observed=case['observed'],inferred=['Exact profiles, absolute dimensions, repeated field/rib counts and fitting depths','Hidden rear construction and alloy identity; no operating mechanism/timing recovered'],
        geometry_policy='New case-specific assembly; earlier generic placeholder preserved unchanged, no retained-geometry claim',
        mesh_objects=len(objects),views=list(VIEWS),blender=bpy.app.version_string,
        acceptance='Visible structural refinement; final artistic acceptance and gameplay calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n')
    print('BRACCATIAN_VESSEL_REFINED',key,len(objects),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True)
    build(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model)


if __name__=='__main__':main()
