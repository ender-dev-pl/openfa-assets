"""Recover BR18/20/23 source-visible bodies, feet and distinct directional emitters."""
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
from manufactured_vessels import vessel
from refine_rigellian_crowns import sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
CASES={'br18':(80,'Anti-Battery'),'br20':(82,'Turret'),'br23':(85,'Fire Power')}
VIEWS={'front-quarter':(6,-13,8),'front':(0,-16,5),'side':(16,0,5),'rear-quarter':(-7,12,8),'equipment-detail':(5,-12,7)}
BODY=[(0,.52),(.04,.67),(.14,.77),(.31,.78),(.47,.65),(.62,.40),(.73,.16),(.97,.09),(1.04,.08)]


def source(key):return ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/braccatian'/key/'model.blend'


def folders(key):
    rel=Path('docs/assets/reconstruction/braccatian-refined')/key
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def objects():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def parent_world(obj,parent):
    bpy.context.view_layer.update();world=obj.matrix_world.copy();obj.parent=parent;obj.matrix_world=world


def sweep(name,sections,mat):
    """Closed shaped casing along a rising, forward-curving centreline."""
    count=64;verts=[]
    for i,(point,rx,ry) in enumerate(sections):
        centre=Vector(point)
        tangent=Vector(sections[min(i+1,len(sections)-1)][0])-Vector(sections[max(0,i-1)][0])
        tangent.normalize();side=Vector((1,0,0));up=tangent.cross(side).normalized()
        for j in range(count):
            a=math.tau*j/count
            # Shallow casting wear; keep the strongly tapering casing readable.
            dent=.0015*math.exp(-((a-1.1)/.20)**2) if i in [1,2] else 0
            verts.append(tuple(centre+side*((rx-dent)*math.cos(a))+up*((ry-dent)*math.sin(a))))
    faces=[tuple(reversed(range(count)))]
    for i in range(len(sections)-1):
        for j in range(count):faces.append((i*count+j,i*count+(j+1)%count,(i+1)*count+(j+1)%count,(i+1)*count+j))
    faces.append(tuple((len(sections)-1)*count+j for j in range(count)))
    return mesh(name,verts,faces,mat)


def fixed_body(key,m):
    p=key.upper()+' '
    vessel(p+'rose domed pedestal and narrow neck',BODY,m['rose-casing'],[(-1.4,.30,.003),(.4,.45,.002)])
    count=6 if key=='br20' else 4
    for i in range(count):
        a=-math.pi/2+math.tau*i/count;x,y=.71*math.cos(a),.71*math.sin(a)
        foot=vessel(p+f'gold radial foot {i}',[(0,.073),(.035,.095),(.12,.086),(.38,.072),(.425,.055)],m['gold-casting'],[])
        foot.location.x,foot.location.y=x,y
        style='blue-cap' if key=='br20' else 'red-cap' if key=='br23' else 'gold-casting'
        cap=vessel(p+f'foot upper cap {i}',[(.39,.066),(.43,.083),(.48,.075),(.50,.036)],m[style],[])
        cap.location.x,cap.location.y=x,y


def head(key,m):
    p=key.upper()+' '
    if key=='br18':
        sweep(p+'single tapered rose emitter',[
          ((0,0,.94),.16,.14),((0,-.08,1.07),.25,.19),((0,-.24,1.24),.18,.125),
          ((0,-.50,1.43),.075,.065),((0,-.81,1.65),.043,.040),((0,-.98,1.77),.030,.028)],m['rose-casing'])
    elif key=='br20':
        sweep(p+'rose rising head casing',[
          ((0,0,.94),.12,.10),((0,-.04,1.10),.15,.12),((0,-.23,1.35),.24,.15),((0,-.40,1.52),.18,.12)],m['rose-casing'])
        for i,x in enumerate([-.17,0,.17]):
            length=1 if i==1 else .79
            sweep(p+f'separate emitter prong {i}',[
              ((x,-.29,1.40),.075,.071),((x,-.48,1.58),.066,.064),
              ((x,-.29-.62*length,1.40+.60*length),.029,.028),
              ((x,-.29-.73*length,1.40+.72*length),.015,.014)],m['rose-casing'])
    else:
        sweep(p+'single gold plasma emitter',[
          ((0,0,.95),.075,.07),((0,-.08,1.12),.16,.13),((0,-.23,1.38),.145,.11),
          ((0,-.38,1.55),.085,.07),((0,-.72,1.88),.036,.034),((0,-1.02,2.18),.017,.016)],m['gold-casting'])


def frame_view(view):
    """Fit the union of all sixteen headings to avoid a moving camera."""
    scene=bpy.context.scene;restore=scene.frame_current;points=[]
    for frame in range(1,17):
        scene.frame_set(frame);bpy.context.view_layer.update()
        points += [o.matrix_world@v.co for o in objects() for v in o.data.vertices]
    scene.frame_set(restore)
    low=Vector([min(p[i] for p in points) for i in range(3)]);high=Vector([max(p[i] for p in points) for i in range(3)])
    centre=(low+high)/2;direction=Vector(VIEWS[view]).normalized();camera=scene.camera
    camera.location=centre+direction*15;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO'
    bpy.context.view_layer.update();projected=[camera.matrix_world.inverted()@p for p in points]
    camera.data.ortho_scale=max(max(p.x for p in projected)-min(p.x for p in projected),max(p.y for p in projected)-min(p.y for p in projected))*1.18


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--model',choices=CASES,required=True);parser.add_argument('--preview-only',action='store_true')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);key=args.model;number,name=CASES[key];output,media=folders(key)
    if args.preview_only:
        sys.path.insert(0,str(ROOT/'tools'))
        from gallery_animation_assets import glb_clips
        import render_gallery_animations as renderer
        meta=json.loads((output/'model.json').read_text());blend=(output/'model.blend').relative_to(ROOT).as_posix();glb=(output/'model.glb').relative_to(ROOT).as_posix()
        study=dict(stage=meta['stage'],blend=blend,glb=glb,image=(media.relative_to(ROOT)/'front-quarter.png').as_posix())
        ffmpeg=shutil.which('ffmpeg');assert ffmpeg
        clips=glb_clips(output/'model.glb');assert clips==glb_clips(source(key).with_suffix('.glb')) and len(clips)==1
        previews=[renderer.render_clip(dict(id=meta['id']),study,clip,ffmpeg) for clip in clips]
        manifest=dict(id=meta['id'],stage=meta['stage'],glb=glb,glb_sha256=sha(output/'model.glb'),blend_sha256=sha(output/'model.blend'),renderer_sha256=sha(Path(renderer.__file__)),blender=bpy.app.version_string,clips=previews)
        (media/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+'\n')
        return
    old=json.loads(source(key).with_suffix('.json').read_text());assert old['global_type']==number
    output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source(key)));scene=bpy.context.scene;scene.frame_set(1)
    original_meshes=[o.name for o in objects()]
    for obj in list(objects()):bpy.data.objects.remove(obj,do_unlink=True)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new(name+' refined complete directional assembly');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root)
    root['catalogue_id']=f'openfa:building/legacy/{number:03}';root['footprint_width'],root['footprint_height']=old['footprint']
    controllers=[bpy.data.objects[n] for n in ['StaticBase','DirectionalHead']]
    for c in controllers:
        parent_world(c,root)
        if c.name not in collection.objects:collection.objects.link(c)
        for previous in list(c.users_collection):
            if previous!=collection:previous.objects.unlink(c)
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/braccatian-refined'/key;m={}
    for style,colour,metal in [('rose-casing',(.48,.235,.17),.65),('gold-casting',(.48,.33,.115),.76),('blue-cap',(.045,.09,.36),.62),('red-cap',(.42,.025,.018),.55)]:
        m[style]=authored.worn_material(style,colour,metal);m[style].name=key.upper()+' | worn '+style
    fixed_body(key,m);fixed=list(objects());head(key,m);moving=[o for o in objects() if o not in fixed]
    for obj in objects():
        if obj.name not in collection.objects:collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
        parent_world(obj,bpy.data.objects['StaticBase' if obj in fixed else 'DirectionalHead']);bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();uv(obj)
        mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for mat in list(m.values()):
        if not mat.users:bpy.data.materials.remove(mat)
    used={Path(n.image.filepath_raw) for obj in objects() for mat in obj.data.materials for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.image}
    for path in authored.TEXTURES.glob('*.png'):
        if path not in used:path.unlink() # Only unused maps generated for this new study.
    collection.asset_mark();collection.asset_data.description=name+' source-visible shape with retained heading control; no firing loop inferred'
    scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    for view in VIEWS:
        frame_view(view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    directions=media/'directions';directions.mkdir(exist_ok=True);frame_view('front-quarter')
    for index in range(16):
        scene.frame_set(index+1);scene.render.filepath=str(directions/f'{index:02}.png');bpy.ops.render.render(write_still=True)
    scene.frame_set(1);bpy.ops.object.select_all(action='DESELECT')
    for obj in objects()+controllers+[root]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=True,export_animation_mode='ACTIVE_ACTIONS',export_frame_range=True)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    dependencies=['refine_braccatian_pithoi.py','manufactured_vessels.py','build_openfa_assets.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=190,id=f'openfa:building/legacy/{number:03}',key=key.upper(),name=name,culture='braccatian',stage='directional-weapon-refinement',
      source_study=source(key).relative_to(ROOT).as_posix(),source_blend_sha256=sha(source(key)),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),
      dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in dependencies},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},
      lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json'),functional_sha256=sha(ROOT/'sources/docs/reconstruction/models/functional-text-index.json'),
      mesh_objects=len(objects()),removed_placeholder_names=original_meshes,footprint=old['footprint'],views=list(VIEWS),blender=bpy.app.version_string,
      rotation_rig=dict(head='DirectionalHead',base='StaticBase',moving_meshes=[o.name for o in moving],static_meshes=[o.name for o in fixed],direction_count=16,axis='+Z',zero_forward='-Y',animation='HeadingPreview_360'),
      observed=['All surface descriptors, sixteen base/head composites using original offsets, and all 41 full catalogue phases inspected','Rose domed base with gold radial feet; blue caps BR20, red caps BR23; BR18 single rose emitter, BR20 three separate prongs, BR23 single gold emitter','Full culture/functional evidence reviewed; Sci-Tek audit has no direct BR-specific animation'],
      inferred=['Exact shaped casing profiles, emitter cross-sections, hidden back surfaces and four/six repeated foot counts','Heading preview remains an authored directional demonstration, not a recovered idle or firing cycle; runtime heading registration remains separate'],
      geometry_policy='Replace entire generic placeholder geometry in a separate study; retain exact directional controller and action',acceptance='Source-led refinement; final artistic/game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('BRACCATIAN_WEAPON_REFINED',key,len(objects()),flush=True)


if __name__=='__main__':main()
