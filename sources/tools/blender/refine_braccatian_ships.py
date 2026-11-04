"""Refine visible BR1C/BR2C forward fields and BR4C axial/dome fittings; preserve existing bodies."""
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
import braccatian_widowmaker_parts as craft
import braccatian_skymech_parts as station
from manufactured_vessels import vessel
from manufactured_annuli import annulus
from manufactured_surface_mounts import cast_bezel
from build_openfa_assets import cylinder,box
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={'rattlesnake':('BR0A','Rattlesnake'),'widowmaker':('BR1C','WidowMaker'),'heartsblood':('BR2C','HeartsBlood'),
       'morning-glory':('BR3A','Morning Glory'),'skymech':('BR4C','SkyMech')}
MODIFIED={'widowmaker','heartsblood','skymech'}
VIEWS={'front-quarter':(7,-12,9),'rear-quarter':(-7,12,8),'front':(0,-15,5),'side':(15,0,5),'top':(0,0,20),'underside':(7,-8,-14),'equipment-detail':(4,-12,7)}
STATION_CORE=[(-1.50,.42),(-1.30,.62),(-1.12,.78),(-.92,.84),(-.55,.86),(-.30,.81),(-.16,.69),(.03,.70),(.18,.78),(.38,.88),(.80,.88),(1.02,.77),(1.20,.58),(1.3125,.50)]


def source(key):return ROOT/'sources/docs/assets/reconstruction/ships/braccatian'/key/'model.blend'


def folders(key):
    rel=Path('docs/assets/reconstruction/braccatian-refined/ships')/key
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def review_media(key):
    return folders(key)[1] if key in MODIFIED else ROOT/'gallery/media/docs/assets/reconstruction/braccatian-refined/ship-retention'/key


def objects():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def frame_view(key,view):
    selected=objects()
    if view=='equipment-detail':
        if key=='skymech':selected=[o for o in selected if 'upper' in o.name or 'new axial housing upper' in o.name]
        elif key in ['widowmaker','heartsblood']:selected=[o for o in selected if 'forward rose field' in o.name or 'rose nose' in o.name]
    fit_camera(VIEWS[view],selected)


def forward_fields(key,materials):
    prefix=CASES[key][1]
    removed=[o.name for o in objects() if o.name.startswith(prefix+' rose neck accent ')]
    assert len(removed)==8
    for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    added=[]
    for i in range(4):
        phi=i*math.pi/2
        for side in [-1,1]:
            name=prefix+f' forward rose field {i} {side}'
            # HeartsBlood inherits this exact pressure-hull profile under its own name.
            craft.patch(name,'WidowMaker gold pressure hull',-1.25,-.60,phi+side*.12,.115,
              materials['rose-field'],top=.014,back=-.020,drift=side*.14)
            added.append(dict(name=name,owner=prefix+' gold pressure hull',phi=phi+side*.12,drift=side*.14))
    return removed,added


def station_fittings(materials):
    removed=['SkyMech upper dark panel']+[f'SkyMech upper amber tile {i}' for i in range(5)]
    removed+=['SkyMech dark axial core','SkyMech rose equatorial collar']
    removed+=[f'SkyMech {side} column rib {i}' for side in ['upper','lower'] for i in range(8)]
    removed+=[f'SkyMech core gold band {i}' for i in range(3)]
    for i in range(4):
        removed += [f'SkyMech arm service housing {i}',f'SkyMech arm dark inset {i}']
        removed += [f'SkyMech arm amber tile {i} {j}' for j in range(3)]
    for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    attachments=[]
    core='SkyMech expanded axial pressure core';station.PROFILES[core]=STATION_CORE
    vessel(core,STATION_CORE,materials['recess'],[(-1.4,.52,.004),(.5,-.75,.003)])
    attachments.append(dict(name=core,owner='SkyMech upper gold dome'))
    for side,low,high in [('upper',.16,1.29),('lower',-1.46,-.17)]:
        for i in range(8):
            name=f'SkyMech broad {side} casing rail {i}'
            station.patch(name,core,low,high,i*math.tau/8,.07,materials['rose-fitting'],top=.022,back=-.022)
            attachments.append(dict(name=name,owner=core))
    from manufactured_vessels import profile_radius
    for i,(low,high) in enumerate([(.24,.31),(.94,1.01),(-1.10,-1.02)]):
        rows=[(z,profile_radius(STATION_CORE,z)+.025,profile_radius(STATION_CORE,z)-.03) for z in [low,high]]
        name=f'SkyMech expanded core gold band {i}';annulus(name,(0,0),rows,materials['gold-fitting'],(0,0,0));attachments.append(dict(name=name,owner=core))
    name='SkyMech expanded equatorial collar'
    annulus(name,(0,0),[(-.10,.85,.65),(0,.94,.65),(.10,.85,.65)],materials['rose-fitting'],(0,0,0));attachments.append(dict(name=name,owner=core))
    for i in range(4):
        phi=i*math.pi/2;n=station.pod_axis(i);name=f'SkyMech broad radial service casing {i}'
        obj=box(name,n*1.02+Vector((0,0,.05)),(.68,.40,.30),materials['gold-fitting'],.014);obj.rotation_euler.z=phi
        attachments.append(dict(name=name,owner='SkyMech radial arm '+str(i)))
        inset=box(name+' dark face',n*1.02+Vector((0,0,.201)),(.50,.26,.025),materials['recess'],.003);inset.rotation_euler.z=phi;attachments.append(dict(name=inset.name,owner=name))
        for j,distance in enumerate([-.15,0,.15]):
            obj=box(name+f' amber field {j}',n*(1.02+distance)+Vector((0,0,.218)),(.105,.20,.025),materials['amber-field'],.002);obj.rotation_euler.z=phi;attachments.append(dict(name=obj.name,owner=inset.name))
    for side,low,high in [('upper',.32,1.06),('lower',-1.13,-.20)]:
        for i in range(4):
            phi=i*math.pi/2;n=Vector((math.cos(phi),math.sin(phi),0));centre=n*.98
            name=f'SkyMech new axial housing {side} {i}'
            profile=[(low,.075),(low+.035,.13),(low+.09,.14),(high-.09,.14),(high-.035,.13),(high,.075)]
            shell=vessel(name,profile,materials['gold-fitting'],[(phi,(low+high)/2,.0015)])
            shell.location.x,shell.location.y=centre.x,centre.y
            attachments.append(dict(name=name,owner=core))
            for j,(a,b) in enumerate([(low+.01,low+.075),(high-.075,high-.01)]):
                obj=annulus(name+f' rose collar {j}',(centre.x,centre.y),[(a,.137,.10),(b,.15,.10)],materials['rose-fitting'],(0,0,0))
                attachments.append(dict(name=obj.name,owner=name))
            # Add an explicit local profile to the unchanged patch helper's configuration.
            station.PROFILES[name]=profile
            obj=station.patch(name+' red service face',name,low+.15,high-.15,phi,.65,materials['rose-field'],top=.008,back=-.015)
            obj.location.x,obj.location.y=centre.x,centre.y;attachments.append(dict(name=obj.name,owner=name))
    owner='SkyMech upper gold dome'
    station.patch('SkyMech new broad upper window',owner,1.315,1.415,-math.pi/2,.48,materials['recess'],top=.012,back=-.020)
    attachments.append(dict(name='SkyMech new broad upper window',owner=owner))
    for i in range(3):
        name=f'SkyMech new upper window field {i}'
        station.patch(name,owner,1.345,1.385,-math.pi/2+(i-1)*.27,.115,materials['amber-field'],top=.022,back=.003)
        attachments.append(dict(name=name,owner='SkyMech new broad upper window'))
    dome=bpy.data.objects[owner]
    for i,phi in enumerate([-math.pi/2-.85,-math.pi/2+.85]):
        point=station.surface(owner,phi,1.69);normal=Vector((math.cos(phi),math.sin(phi),1.12)).normalized()
        name=f'SkyMech new upper round casting {i}';cast_bezel(name,dome,point,normal,.105,materials['gold-fitting']);attachments.append(dict(name=name,owner=owner))
        cap=cylinder(name+' rose centre',point+normal*.027,.051,.026,materials['rose-fitting'],vertices=48,rotation=normal.to_track_quat('Z','Y').to_euler())
        attachments.append(dict(name=cap.name,owner=name))
    for i in range(4):
        name=f'SkyMech new module concentric rim {i}'
        obj=annulus(name,(0,0),[(.185,.25,.18),(.255,.25,.18)],materials['gold-fitting'],(0,0,0));station.fit_radial(obj,i)
        attachments.append(dict(name=name,owner=f'SkyMech gold module face {i}'))
    return removed,attachments


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=sorted(MODIFIED),required=True)
    key=parser.parse_args(sys.argv[sys.argv.index('--')+1:]).model;code,name=CASES[key];output,media=folders(key)
    old=json.loads(source(key).with_suffix('.json').read_text());output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source(key)));scene=bpy.context.scene
    original={o.name for o in objects()};root=bpy.data.objects['PlacementRoot'];assert root['catalogue_id']==old['id']
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined/ships'/key;m={}
    styles=[('rose-field',(.49,.16,.13),.65)] if key!='skymech' else [
      ('rose-field',(.49,.16,.13),.65),('rose-fitting',(.30,.13,.115),.68),('gold-fitting',(.33,.23,.09),.72),('recess',(.015,.018,.014),.40),('amber-field',(.60,.15,.025),.35)]
    for style,colour,metal in styles:
        m[style]=authored.worn_material(style,colour,metal);m[style].name=name+' refined | '+style
    removed,attachments=station_fittings(m) if key=='skymech' else forward_fields(key,m)
    added=[o for o in objects() if o.name not in original]
    for obj in added:
        obj.parent=root;bpy.context.view_layer.objects.active=obj
        # Cast roots contain mixed initial winding; orient the closed shell
        # before bevel evaluates convex/concave edges, then check it again below.
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();uv(obj)
        mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new(name+' complete refined ship');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        if obj.name not in collection.objects:collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description=old['id']+' preserved body with source-visible refined equipment'
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    for view in VIEWS:
        frame_view(key,view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    frame_view(key,'front-quarter');bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    deps=['refine_braccatian_pithoi.py','braccatian_widowmaker_parts.py','braccatian_skymech_parts.py','manufactured_vessels.py','manufactured_annuli.py','manufactured_surface_mounts.py','build_openfa_assets.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=190,id=old['id'],key=code,name=name,culture='braccatian',stage='ship-visible-equipment-refinement',
      source_study=source(key).relative_to(ROOT).as_posix(),source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),
      dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},
      lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      mesh_objects=len(objects()),removed_objects=removed,added_objects=[o.name for o in added],attachments=attachments,views=list(VIEWS),equipment_slots=old['equipment_slots'],blender=bpy.app.version_string,
      observed=['All available paletted states/headings reviewed: 32 WidowMaker, 16 populated HeartsBlood and empty odds, 2 fixed SkyMech states','Craft forward rose fields are broader than the earlier hairline accents; user identifies SkyMech as an orbital station with a much broader detail-filled core reaching nearly to peripheral hemispheres','SkyMech replaces the thin core/ribs/service casings with a broad two-chamber body, substantial axial equipment and radial casings, plus dome fittings/window and concentric module faces','Functional text binds ship names only; exact equipment mechanisms and alloys remain unconfirmed'],
      inferred=['Field widths, hidden repetitions, service module identities and exact casting depths; inherited fine construction remains authored','SkyMech wireframe-like state is not evidence of deployment motion; no operating clip added'],
      geometry_policy='Retain all original meshes/materials except explicitly named replaced fields or station core/ribs/casings/window; preserve alignment helpers and prior files',acceptance='Source-led refinement; final artistic/game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('BRACCATIAN_SHIP_REFINED',key,len(objects()),len(added),flush=True)


if __name__=='__main__':main()
