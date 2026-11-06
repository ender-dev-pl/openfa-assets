"""RI4C construction sleeve, elliptical scaffold bands and outboard work stations."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import bpy
import bmesh
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
from build_skymech_construction import tubes
from build_openfa_assets import box
from manufactured_vessels import profile_radius
from refine_rigellian_crowns import sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'sources/docs/assets/reconstruction/rigellian-refined/observatory/model.blend'
REL=Path('docs/assets/reconstruction/orbital-station-construction/rigellian/observatory')
OUTPUT=ROOT/'sources'/REL;MEDIA=ROOT/'gallery/media'/REL
EVIDENCE=ROOT/'sources/docs/reconstruction/models/observatory-construction-evidence.json'
FINISHED_REVIEW=MEDIA/'finished-review'
PROFILE=[(-3.10,.08),(-2.60,.40),(-2.0,.95),(-1.3,1.35),(-.65,1.80),(0,2.28),(.65,1.83),(1.30,1.35),(2.0,.92),(2.60,.40),(3.10,.08)]
HEIGHTS=sorted({z for z in [round(-2.94+i*.196,6) for i in range(31)] if abs(abs(z)-.6)>.04}|{-.60,.60})
SCALE_Y=.78
VIEWS={'front-quarter':(6,-13,5),'front':(0,-16,1),'rear-quarter':(-7,12,5),'side':(16,0,1),'work-detail':(2,-14,3)}


def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def point(phi,z,offset=0):
    r=profile_radius(PROFILE,z)+offset
    return Vector((r*math.cos(phi),r*SCALE_Y*math.sin(phi),z))


def cover(name,z0,z1,phi0,phi1,mat):
    rows=15;cols=13;verts=[]
    for depth in [.007,-.016]:
        for j in range(rows):
            f=j/(rows-1);z=z0+(z1-z0)*f
            for i in range(cols):
                g=i/(cols-1);p=point(phi0+(phi1-phi0)*g,z,depth-.025*math.sin(math.pi*f)*math.sin(math.pi*g));verts.append(tuple(p))
    size=rows*cols;faces=[]
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i;f=(a,a+1,a+cols+1,a+cols);faces += [f,tuple(size+x for x in reversed(f))]
    edge=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[j*cols for j in reversed(range(1,rows-1))]
    faces += [(a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1])]
    return mesh(name,verts,faces,mat)


def frame_view(view):
    camera=bpy.context.scene.camera;direction=Vector(VIEWS[view]).normalized()
    points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    if view=='work-detail':centre=point(-math.pi/2,0)+Vector((0,0,.07));scale=1.25
    else:centre=Vector([(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)]);scale=None
    camera.location=centre+direction*16;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';bpy.context.view_layer.update()
    local=[camera.matrix_world.inverted()@p for p in points];camera.data.ortho_scale=scale or max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.16


def preview():
    import render_gallery_animations as renderer
    sys.path.insert(0,str(ROOT/'tools'));from gallery_animation_assets import glb_clips
    meta=json.loads((OUTPUT/'model.json').read_text());study=dict(stage=meta['stage'],blend=(OUTPUT/'model.blend').relative_to(ROOT).as_posix(),glb=(OUTPUT/'model.glb').relative_to(ROOT).as_posix(),image=(MEDIA/'front-quarter.png').relative_to(ROOT).as_posix())
    clips=glb_clips(OUTPUT/'model.glb');assert len(clips)==1 and clips[0]['name']=='ConstructionActivity'
    result=[renderer.render_clip(dict(id=meta['id']),study,clip,shutil.which('ffmpeg')) for clip in clips]
    (MEDIA/'animation-previews.json').write_text(json.dumps(dict(id=meta['id'],stage=meta['stage'],glb=study['glb'],glb_sha256=sha(OUTPUT/'model.glb'),blend_sha256=sha(OUTPUT/'model.blend'),renderer_sha256=sha(Path(renderer.__file__)),blender=bpy.app.version_string,clips=result),indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preview-only',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.preview_only:preview();return
    OUTPUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    old=json.loads(SOURCE.with_suffix('.json').read_text());assert old['blend_sha256']==sha(SOURCE) and old['glb_sha256']==sha(SOURCE.with_suffix('.glb'))
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;root=bpy.data.objects['PlacementRoot'];original={o.name for o in meshes()}
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/orbital-station-construction/rigellian/observatory'
    m={}
    for style,colour,metal in [('frame',(.27,.35,.48),.65),('cover',(.20,.25,.39),.30),('case',(.15,.21,.29),.60),('marker',(.10,.40,.56),.30)]:
        m[style]=authored.worn_material(style,colour,metal);m[style].name='Observatory construction | '+style
    tubes('RI4C construction elliptical hoops',[([point(i*math.tau/96,z) for i in range(96)],True,(0,0,1)) for z in HEIGHTS],.012,m['frame'])
    zs=sorted(set(round(z,8) for z in [-3.1+i*6.2/124 for i in range(125)]+[z for z,_ in PROFILE]));assert min(b-a for a,b in zip(zs,zs[1:]))>1e-6
    tubes('RI4C construction meridian ribs',[([point(i*math.tau/24,z) for z in zs],False,(0,0,1)) for i in range(24)],.014,m['frame'])
    paths=[]
    for j,(low,high) in enumerate(zip(HEIGHTS,HEIGHTS[1:])):
        for i in range(24):
            a,b=(i,i+1) if (i+j)%2 else (i+1,i)
            paths.append(([point(a*math.tau/24,low),point(b*math.tau/24,high)],False,(0,0,1)))
    tubes('RI4C construction diagonal lattice',paths,.009,m['frame'])
    stays=[]
    for z in [-.6,.6]:
        for i in range(8):
            phi=i*math.tau/8;stays.append(([(.20*math.cos(phi),.20*SCALE_Y*math.sin(phi),z),point(phi,z)],False,(0,0,1)))
    tubes('RI4C construction axial body stays',stays,.022,m['frame'])
    covers=[]
    for i in range(12):
        low,high=(.65,2.55) if i%2==0 else (-2.55,-.65);name=f'RI4C temporary conical shield {i}';cover(name,low,high,i*math.tau/12,(i+1)*math.tau/12,m['cover']);covers.append(name)
    booms=[]
    for i in range(4):
        phi=i*math.pi/2;start=Vector((1.90*math.cos(phi),1.90*.70*math.sin(phi),0));end=Vector((3.20*math.cos(phi),3.20*SCALE_Y*math.sin(phi),0));booms.append(([start,end],False,(0,0,1)))
        obj=box(f'RI4C outboard temporary service casing {i}',end,(.24,.24,.22),m['case'],.012)
        box(f'RI4C outboard pale work field {i}',end+Vector((0,-.122,0)),(.13,.020,.09),m['marker'],.003)
    tubes('RI4C temporary outboard support booms',booms,.020,m['frame'])
    actor=bpy.data.objects.new('ConstructionWorkCarriage',None);bpy.context.collection.objects.link(actor);actor.parent=root
    for name,position,size,style in [('rail clamp',(0,0,0),(.18,.10,.075),'case'),('service case',(0,-.02,.095),(.20,.15,.12),'case'),('pale marker',(0,-.10,.10),(.10,.018,.04),'marker')]:
        obj=box('RI4C construction carriage '+name,position,size,m[style],.004);obj.parent=actor
    scene.frame_start=1;scene.frame_end=181;scene.render.fps=30
    for frame,angle in [(1,0),(61,.08),(121,-.08),(181,0)]:
        actor.location=point(-math.pi/2+angle,0);actor.rotation_euler.z=angle
        actor.keyframe_insert(data_path='location',frame=frame);actor.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    action=actor.animation_data.action;action.name='ConstructionActivity';track=actor.animation_data.nla_tracks.new();track.name='ConstructionActivity';track.strips.new('ConstructionActivity',1,action);actor.animation_data.action=None;scene.frame_set(1)
    added=[o for o in meshes() if o.name not in original]
    for obj in added:
        if obj.parent is None:obj.parent=root
        bpy.context.view_layer.objects.active=obj;bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        uv(obj);mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new('Observatory refined complete construction state');scene.collection.children.link(collection);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description='RI4C second descriptor: conical construction sleeves, wide working bands and temporary outboard stations'
    root['variant']='construction';root['legacy_sprite_frame']=1
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    for view in VIEWS:frame_view(view);scene.render.filepath=str(MEDIA/(view+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(61);frame_view('work-detail');scene.render.filepath=str(MEDIA/'work-detail-moved.png');bpy.ops.render.render(write_still=True);scene.frame_set(1);frame_view('front-quarter')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    deps=['build_skymech_construction.py','refine_braccatian_pithoi.py','build_openfa_assets.py','manufactured_vessels.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=192,id=old['id'],name='Observatory',culture='rigellian',variant='construction',legacy_sprite_frame=1,stage='orbital-station-construction-refinement',source_study=SOURCE.relative_to(ROOT).as_posix(),source_blend_sha256=sha(SOURCE),source_glb_sha256=sha(SOURCE.with_suffix('.glb')),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},evidence_sha256=sha(EVIDENCE),preserved_mesh_names=sorted(original),added_mesh_names=[o.name for o in added],temporary_cover_names=covers,mesh_objects=len(meshes()),blender=bpy.app.version_string,activity=dict(clip='ConstructionActivity',duration_seconds=6,moving_root='ConstructionWorkCarriage',static_station=True),observed='Second descriptor has dense conical blue/pale construction envelope, wide elliptical working bands and small outboard work objects',authored='Exact member layout, supporting booms, covers, symmetry and six-second carriage loop are interpretations; no recovered timing or autonomous craft mechanics claimed',acceptance='Independent runtime/GLB verification pending; final game calibration open')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('RI4C_CONSTRUCTION_BUILT',len(meshes()),len(added),flush=True)


if __name__=='__main__':main()
