"""Refine BR11/12/19 casing and face equipment while preserving proven launch geometry/motion."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
from refine_braccatian_vessels import disc,ring
from refine_braccatian_public_facilities import pyramid_fitting
from manufactured_annuli import annulus
from manufactured_vessels import vessel
from build_openfa_assets import beam
from build_launch_facilities import preview_ground
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={'br11':(73,'Launch Site'),'br12':(74,'Eyes-in-the-Sky'),'br19':(81,'Battery')}
VIEWS={'front-quarter':(6,-13,8),'front':(0,-16,6),'side':(16,0,6),'rear-quarter':(-7,12,8),'equipment-detail':(10,-12,7)}
SHELL=[(0,1.00),(.08,1.00),(.18,.94),(.54,.76),(.70,.70)]
BATTERY_SHELL=[(0,.88),(.08,.98),(.18,1.03),(.32,1.00),(.50,.87),(.64,.73),(.70,.70)]
LEAVES=['Pyramidal hatch petal'+suffix for suffix in ['', '.001','.002','.003']]


def source(key):return ROOT/'sources/docs/assets/reconstruction/launch-facilities/braccatian'/key/'model.blend'


def folders(key):
    rel=Path('docs/assets/reconstruction/braccatian-refined')/key
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def real_meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH' and not o.get('preview_only')]


def selected(key,view):
    return [o for o in real_meshes() if not (key=='br11' and o.name in ['Recessed launch well floor','Vertical hangar shaft walls'])]


def frame_view(key,view):
    scene=bpy.context.scene;points=[]
    for obj in selected(key,view):
        points += [p for v in obj.data.vertices if (p:=obj.matrix_world@v.co).z>=(-.001 if key=='br11' else -1000)]
    low=Vector([min(p[i] for p in points) for i in range(3)]);high=Vector([max(p[i] for p in points) for i in range(3)])
    centre=(low+high)/2;direction=Vector(VIEWS.get(view,VIEWS['front-quarter'])).normalized();camera=scene.camera
    camera.location=centre+direction*15;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO'
    bpy.context.view_layer.update();projected=[camera.matrix_world.inverted()@p for p in points]
    camera.data.ortho_scale=max(max(p.x for p in projected)-min(p.x for p in projected),max(p.y for p in projected)-min(p.y for p in projected))*1.18


def foundation(name,half,inner,top,mat,corner_cut=0):
    count=128;vertices=[]
    for z,rim in [(0,False),(top,False),(0,True),(top,True)]:
        for i in range(count):
            a=math.tau*i/count;c,s=math.cos(a),math.sin(a)
            r=inner if rim else min(half/max(abs(c),abs(s)),(2-corner_cut)*half/(abs(c)+abs(s)))
            vertices.append((r*c,r*s,z))
    faces=[]
    for i in range(count):
        j=(i+1)%count
        faces += [(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),
          (i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)]
    return mesh(name,vertices,faces,mat,smooth=False)


def decorate_pyramid(m):
    leaf=bpy.data.objects[LEAVES[3]];before={o.name for o in real_meshes()}
    intercept=.88*.85/.70
    pyramid_fitting('BR11 moving gold face rim',.42,.17,.85,intercept,0,m['gold-casting'],.105)
    pyramid_fitting('BR11 moving dark face backing',.42,.112,.85,intercept,0,m['recess'],relief=.008)
    pyramid_fitting('BR11 moving gold face centre',.42,.047,.85,intercept,0,m['gold-casting'],relief=.035)
    for obj in real_meshes():
        if obj.name not in before:
            obj.rotation_euler.z=math.pi/2
            bpy.context.view_layer.update();world=obj.matrix_world.copy()
            obj.parent=leaf;obj.matrix_world=world
    foundation('BR11 square shaft surround',1.00,.65,.15,m['rose-casing'])


def open_silo(key,m):
    accent=m['pale-blue'] if key=='br12' else m['red-field']
    profile=SHELL if key=='br12' else BATTERY_SHELL
    liner=annulus(key.upper()+' inner structural liner',(0,0),[(.046,.635,.61),(.70,.635,.61)],m['recess'],(-1.8,.30,0))
    liner.data.materials.append(accent)
    for face in liner.data.polygons:
        x,y,z=face.center
        if .20<z<.50 and y>.60 and abs(x)<.065 and math.hypot(x,y)<.62:face.material_index=1
    annulus(key.upper()+' tapered rose shell',(0,0),[(z,r,.63) for z,r in profile],m['rose-casing'],(-1.8,.30,.002))
    foundation(key.upper()+' square hollow foundation',1.05 if key=='br12' else 1.40,.63,.10,m['rose-casing'],.18 if key=='br12' else 0)
    ring(key.upper()+' broad gold face rim',profile,.36,.21,.133,m['gold-casting'])
    disc(key.upper()+' dark face backing',profile,.36,.140,m['recess'],relief=.008)
    disc(key.upper()+' gold face centre',profile,.36,.054,m['gold-casting'],relief=.028)
    if key=='br19':
        beam('BR19 front gold connection',(0,-.75,.115),(0,-1.30,.115),.025,m['gold-casting'])
        obj=vessel('BR19 low foundation fitting',[(.095,.075),(.11,.10),(.13,.10)],m['gold-casting'],[]);obj.location.y=-1.30


def preview_only(key):
    assert key=='br11','Only BR11 has an authored operating clip'
    import render_gallery_animations as renderer
    sys.path.insert(0,str(ROOT/'tools'))
    from gallery_animation_assets import glb_clips
    output,media=folders(key);meta=json.loads((output/'model.json').read_text());relative=output.relative_to(ROOT)
    study=dict(blend=(relative/'model.blend').as_posix(),glb=(relative/'model.glb').as_posix(),image=(media.relative_to(ROOT)/'front-quarter.png').as_posix(),stage=meta['stage'])
    ffmpeg=shutil.which('ffmpeg');assert ffmpeg
    clips=glb_clips(output/'model.glb');assert len(clips)==1 and clips[0]['name']=='LaunchFacilityCycle'
    previews=[renderer.render_clip(dict(id=meta['id']),study,clip,ffmpeg) for clip in clips]
    manifest=dict(id=meta['id'],stage=meta['stage'],glb=study['glb'],glb_sha256=sha(output/'model.glb'),blend_sha256=sha(output/'model.blend'),renderer_sha256=sha(Path(renderer.__file__)),blender=bpy.app.version_string,clips=previews)
    (media/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True);parser.add_argument('--preview-only',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);key=args.model
    if args.preview_only:preview_only(key);return
    number,name=CASES[key];output,media=folders(key);old=json.loads(source(key).with_suffix('.json').read_text())
    assert old['id']==f'openfa:building/legacy/{number:03}'
    output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source(key)));scene=bpy.context.scene;scene.frame_set(1);scene.render.fps=30
    retained=LEAVES+['Recessed launch well floor','Vertical hangar shaft walls'] if key=='br11' else ['Recessed launch well floor']
    removed=[]
    for obj in list(real_meshes()):
        if obj.name not in retained:removed.append(obj.name);bpy.data.objects.remove(obj,do_unlink=True)
    for obj in list(scene.objects):
        if obj.get('preview_only'):bpy.data.objects.remove(obj,do_unlink=True)
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined'/key;materials={}
    for style,colour,metal in [('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),('recess',(.035,.028,.019),.48),('pale-blue',(.48,.61,.72),.62),('red-field',(.42,.025,.018),.55)]:
        materials[style]=authored.worn_material(style,colour,metal);materials[style].name=key.upper()+' | worn '+style
    for obj in real_meshes():
        if obj.name in LEAVES:
            for i in range(len(obj.data.materials)):obj.data.materials[i]=materials['rose-casing'] if i==0 else materials['recess']
        else:
            obj.data.materials.clear();obj.data.materials.append(materials['recess'])
            for face in obj.data.polygons:face.material_index=0
    if key=='br11':decorate_pyramid(materials)
    else:open_silo(key,materials)
    root=bpy.data.objects['PlacementRoot'];root['catalogue_id']=old['id']
    for collection in bpy.data.collections:
        if collection.asset_data:collection.asset_clear()
    collection=bpy.data.collections.new(name+' refined complete launch assembly');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    objects=real_meshes()
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        if obj!=root and obj.parent is None:obj.parent=root
        if obj.name not in collection.objects:collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
        if obj.type!='MESH':continue
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();uv(obj)
        modifier=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');modifier.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=modifier.name)
    for mat in list(materials.values()):
        if not mat.users:bpy.data.materials.remove(mat)
    used={Path(n.image.filepath_raw) for obj in objects for mat in obj.data.materials if mat.use_nodes for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for path in authored.TEXTURES.glob('*.png'):
        if path not in used:path.unlink() # Only newly generated unused case maps.
    collection.asset_mark();collection.asset_data.description=name+' retained launch geometry/motion with source-visible casing and equipment'
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    # Preview-only terrain hides the underground shaft but never enters the GLB.
    if key=='br11':preview_ground(old['aperture_radius'])
    for view,direction in VIEWS.items():
        frame_view(key,view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    if key=='br11':
        scene.frame_set(31);frame_view(key,'open');scene.render.filepath=str(media/'open.png');bpy.ops.render.render(write_still=True)
    scene.frame_set(1);frame_view(key,'front-quarter');bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY'] and not obj.get('preview_only'):obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=key=='br11',export_animation_mode='NLA_TRACKS',export_frame_range=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    dependencies=['refine_braccatian_pithoi.py','refine_braccatian_vessels.py','refine_braccatian_public_facilities.py','build_launch_facilities.py','launch_facility_recipes.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=190,id=old['id'],key=key.upper(),name=name,culture='braccatian',stage='launch-casing-refinement',source_study=source(key).relative_to(ROOT).as_posix(),source_blend_sha256=sha(source(key)),
      blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},
      texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      retained_mesh_names=retained,removed_placeholder_or_old_scuff_names=removed,footprint=old['footprint'],aperture_radius=old['aperture_radius'],floor_height=old['floor_height'],terrain_cutout_fraction=old['terrain_cutout_fraction'],fixed_open=old['fixed_open'],launch_animation=old['launch_animation'],
      observed=['All 41 paletted catalogue phases and all surface descriptors inspected; BR11 descriptors 2-15 show pink opening structure, descriptor 1 is a different green state','BR11 pink pyramid with large gold face fitting; BR12 tapered casing/front fitting; BR19 rounded tapered casing/square base/front foundation connection','Original functional payloads read/hash checked; no invented extra security or symbolic machinery'],
      inferred=['Exact casing profiles, face fitting details, hidden supports and alloy identities; existing authored hinge engineering/timing remains inferred'],
      geometry_policy='Retain named floor/shaft/leaves and prior studies; replace generic outer casing/old flat scuff overlays and author new source-visible fittings',mesh_objects=len(objects),views=list(VIEWS)+(['open'] if key=='br11' else []),blender=bpy.app.version_string,acceptance='Actual source-led refinement; final artistic/game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('BRACCATIAN_LAUNCH_REFINED',key,len(objects),flush=True)


if __name__=='__main__':main()
