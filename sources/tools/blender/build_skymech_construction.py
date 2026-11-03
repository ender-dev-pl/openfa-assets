"""BR4C frame-one construction variant: dense physical scaffolds/covers and gentle authored servicing."""
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
from manufactured_annuli import annulus
from build_openfa_assets import box
from refine_rigellian_crowns import fit_camera,sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
REL=Path('docs/assets/reconstruction/orbital-station-construction/braccatian/skymech')
SOURCE=ROOT/'sources/docs/assets/reconstruction/braccatian-refined/ships/skymech/model.blend'
OUTPUT=ROOT/'sources'/REL;MEDIA=ROOT/'gallery/media'/REL
PROFILE=[(-3.30,.07),(-2.80,.30),(-2.15,.85),(-1.70,1.20),(-1.15,1.55),(-.55,1.90),(0,2.02),(.55,1.90),(1.15,1.55),(1.70,1.20),(2.15,.85),(2.80,.30),(3.30,.07)]
VIEWS={'front-quarter':(7,-12,9),'front':(0,-15,4),'side':(15,0,4),'rear-quarter':(-7,12,8),'work-detail':(4,-12,5)}
HEIGHTS=sorted(set([round(-3.15+i*.21,6) for i in range(31)]+[-1.2,0,1.2]))


def radius(z):
    return next(ra+(rb-ra)*(z-a)/(b-a) for (a,ra),(b,rb) in zip(PROFILE,PROFILE[1:]) if a<=z<=b)


def point(phi,z):return Vector((radius(z)*math.cos(phi),radius(z)*math.sin(phi),z))


def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def tubes(name,paths,width,mat):
    """Multiple capped physical tubes or closed hoops, grouped without shader wireframes."""
    sides=8;verts=[];faces=[]
    for coords,closed,hint in paths:
        coords=[Vector(p) for p in coords];offset=len(verts);count=len(coords)
        for i,p in enumerate(coords):
            tangent=(coords[(i+1)%count]-coords[(i-1)%count]) if closed else coords[min(i+1,count-1)]-coords[max(0,i-1)]
            tangent.normalize();normal=Vector(hint)
            if abs(normal.dot(tangent))>.95:normal=Vector((1,0,0))
            normal=(normal-tangent*normal.dot(tangent)).normalized();other=tangent.cross(normal).normalized()
            for j in range(sides):
                angle=j*math.tau/sides;verts.append(tuple(p+width*(normal*math.cos(angle)+other*math.sin(angle))))
        for i in range(count if closed else count-1):
            for j in range(sides):faces.append((offset+i*sides+j,offset+i*sides+(j+1)%sides,offset+((i+1)%count)*sides+(j+1)%sides,offset+((i+1)%count)*sides+j))
        if not closed:
            faces.append(tuple(offset+j for j in reversed(range(sides))));faces.append(tuple(offset+(count-1)*sides+j for j in range(sides)))
    return mesh(name,verts,faces,mat)


def cover(name,low,high,phi0,phi1,mat):
    columns=13;rows=13;verts=[]
    for depth in [.007,-.015]:
        for j in range(rows):
            f=j/(rows-1);z=low+(high-low)*f
            for i in range(columns):
                g=i/(columns-1);phi=phi0+(phi1-phi0)*g
                r=radius(z)+depth-.035*math.sin(math.pi*f)*math.sin(math.pi*g)
                verts.append((r*math.cos(phi),r*math.sin(phi),z))
    size=rows*columns;faces=[]
    for j in range(rows-1):
        for i in range(columns-1):
            a=j*columns+i;f=(a,a+1,a+columns+1,a+columns);faces += [f,tuple(size+x for x in reversed(f))]
    edge=list(range(columns))+[j*columns+columns-1 for j in range(1,rows)]+list(reversed(range((rows-1)*columns,(rows-1)*columns+columns-1)))+[j*columns for j in reversed(range(1,rows-1))]
    faces += [(a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1])]
    return mesh(name,verts,faces,mat)


def frame_view(view):
    scene=bpy.context.scene;camera=scene.camera;direction=Vector(VIEWS[view]).normalized()
    if view=='work-detail':
        centre=Vector((0,-radius(.42),.48));scale=1.15
    else:
        points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
        low=Vector([min(p[i] for p in points) for i in range(3)]);high=Vector([max(p[i] for p in points) for i in range(3)]);centre=(low+high)/2;scale=None
    camera.location=centre+direction*15;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO'
    bpy.context.view_layer.update()
    if scale is None:
        local=[camera.matrix_world.inverted()@p for p in points]
        scale=max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.16
    camera.data.ortho_scale=scale


def preview():
    import render_gallery_animations as renderer
    sys.path.insert(0,str(ROOT/'tools'));from gallery_animation_assets import glb_clips
    meta=json.loads((OUTPUT/'model.json').read_text());study=dict(stage=meta['stage'],blend=(OUTPUT/'model.blend').relative_to(ROOT).as_posix(),glb=(OUTPUT/'model.glb').relative_to(ROOT).as_posix(),image=(MEDIA/'front-quarter.png').relative_to(ROOT).as_posix())
    ffmpeg=shutil.which('ffmpeg');assert ffmpeg;clips=glb_clips(OUTPUT/'model.glb');assert len(clips)==1 and clips[0]['name']=='ConstructionActivity'
    result=[renderer.render_clip(dict(id=meta['id']),study,clip,ffmpeg) for clip in clips]
    (MEDIA/'animation-previews.json').write_text(json.dumps(dict(id=meta['id'],stage=meta['stage'],glb=study['glb'],glb_sha256=sha(OUTPUT/'model.glb'),blend_sha256=sha(OUTPUT/'model.blend'),renderer_sha256=sha(Path(renderer.__file__)),blender=bpy.app.version_string,clips=result),indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preview-only',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.preview_only:preview();return
    OUTPUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    old=json.loads(SOURCE.with_suffix('.json').read_text());assert old['id']=='openfa:ship/braccatian/skymech' and sha(SOURCE)==old['blend_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;root=bpy.data.objects['PlacementRoot'];original={o.name for o in meshes()}
    authored.TEXTURES=ROOT/'sources/materials/reconstruction/orbital-station-construction/braccatian/skymech';m={}
    for style,colour,metal in [('temporary-framework',(.24,.18,.06),.70),('temporary-covers',(.29,.22,.09),.28),('service-case',(.16,.19,.17),.62),('work-marker',(.65,.20,.025),.35)]:
        m[style]=authored.worn_material(style,colour,metal);m[style].name='SkyMech construction | '+style
    hoops=[]
    for z in HEIGHTS:hoops.append(([tuple(point(i*math.tau/96,z)) for i in range(96)],True,(0,0,1)))
    tubes('Construction outer horizontal scaffold hoops',hoops,.012,m['temporary-framework'])
    ribs=[]
    for i in range(24):
        phi=i*math.tau/24;ribs.append(([tuple(point(phi,-3.30+j*6.60/66)) for j in range(67)],False,(-math.sin(phi),math.cos(phi),0)))
    tubes('Construction outer longitudinal scaffold ribs',ribs,.014,m['temporary-framework'])
    braces=[]
    for j,(za,zb) in enumerate(zip(HEIGHTS,HEIGHTS[1:])):
        for i in range(24):
            target=i+(1 if (i+j)%2 else -1)
            braces.append(([tuple(point(i*math.tau/24,za)),tuple(point(target*math.tau/24,zb))],False,(0,0,1)))
    tubes('Construction alternating diagonal lattice',braces,.009,m['temporary-framework'])
    anchors=[]
    for z in [-1.2,1.2]:
        for i in range(8):
            phi=i*math.tau/8;inside=(.74*math.cos(phi),.74*math.sin(phi),-.96 if z<0 else 1.0)
            anchors.append(([inside,tuple(point(phi,z))],False,(0,0,1)))
    tubes('Construction body anchored support stays',anchors,.022,m['temporary-framework'])
    for i,z in enumerate([-1.2,0,1.2]):
        r=radius(z);annulus(f'Construction temporary annular work deck {i}',(0,0),[(z-.025,r+.035,r-.15),(z+.025,r+.035,r-.15)],m['temporary-framework'],(0,0,0))
    covers=[]
    for i in range(12):
        low,high=(.42,1.26) if i%2==0 else (-1.26,-.42);name=f'Construction temporary shield panel {i}'
        cover(name,low,high,i*math.tau/12,(i+1)*math.tau/12,m['temporary-covers']);covers.append(name)
    for i in range(4):
        name=f'Construction temporary waist cover {i}';cover(name,-.21,.21,i*math.pi/2+math.pi/12,i*math.pi/2+math.pi/4,m['temporary-covers']);covers.append(name)
    actor=bpy.data.objects.new('ConstructionWorkCarriage',None);bpy.context.collection.objects.link(actor);actor.parent=root
    actor.location=(0,-radius(.42),.42);actor['role']='Subtle authored servicing movement along a scaffold rail'
    for name,position,size,style in [
      ('Construction carriage rail clamp',(0,0,0),(.18,.10,.08),'service-case'),
      ('Construction carriage service case',(0,0,.09),(.20,.14,.12),'service-case'),
      ('Construction carriage amber marker',(0,-.073,.10),(.11,.018,.045),'work-marker')]:
        obj=box(name,position,size,m[style],.004);obj.parent=actor
    scene.frame_start=1;scene.frame_end=181;scene.render.fps=30
    for frame,x in [(1,0),(61,.18),(121,-.12),(181,0)]:actor.location.x=x;actor.keyframe_insert(data_path='location',index=0,frame=frame)
    action=actor.animation_data.action;action.name='ConstructionActivity'
    track=actor.animation_data.nla_tracks.new();track.name='ConstructionActivity';strip=track.strips.new('ConstructionActivity',1,action);actor.animation_data.action=None
    scene.frame_set(1);added=[o for o in meshes() if o.name not in original]
    for obj in added:
        if obj.parent is None:obj.parent=root
        bpy.context.view_layer.objects.active=obj
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for modifier in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        uv(obj);mod=obj.modifiers.new('Portable explicit tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new('SkyMech complete construction variant');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        if obj.name not in collection.objects:collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description='BR4C source frame 1: scaffolded station under construction; authored gentle work activity'
    root['variant']='construction';root['legacy_sprite_frame']=1
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    for view in VIEWS:frame_view(view);scene.render.filepath=str(MEDIA/(view+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(61);frame_view('work-detail');scene.render.filepath=str(MEDIA/'work-detail-moved.png');bpy.ops.render.render(write_still=True)
    scene.frame_set(1);frame_view('front-quarter');bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    baseline=ROOT/'sources/docs/reconstruction/models/braccatian-refining-baseline.json';ref=next(r for r in json.loads(baseline.read_text())['records'] if r['key']=='BR4C')
    deps=['refine_braccatian_pithoi.py','manufactured_annuli.py','build_openfa_assets.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=192,id=old['id'],name='SkyMech',culture='braccatian',variant='construction',legacy_sprite_frame=1,stage='orbital-station-construction-refinement',
      source_study=SOURCE.relative_to(ROOT).as_posix(),source_blend_sha256=sha(SOURCE),source_glb_sha256=sha(SOURCE.with_suffix('.glb')),blend_sha256=sha(OUTPUT/'model.blend'),glb_sha256=sha(OUTPUT/'model.glb'),generator_sha256=sha(Path(__file__)),
      dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},
      reference_sha256=sha(baseline),lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/braccatian-lore-evidence.json'),source_frame_one=ref['surface']['layers'][1],
      preserved_mesh_names=sorted(original),added_mesh_names=[o.name for o in added],temporary_cover_names=covers,mesh_objects=len(meshes()),views=list(VIEWS)+['work-detail-moved'],blender=bpy.app.version_string,
      observed=['User identifies frame 1 as dense scaffolding and temporary covers around the station under construction','Correctly paletted BR4C frame 1 has a larger dense construction envelope than frame 0; finished expanded body retained'],
      inferred=['Exact scaffold members, shield coverage, service carriage and six-second gentle movement are authored; no original construction timing recovered'],
      activity=dict(clip='ConstructionActivity',duration_seconds=6,moving_root='ConstructionWorkCarriage',station_root_static=True),acceptance='Actual runtime/independent import/animation/gallery checks pending')
    (OUTPUT/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('SKYMECH_CONSTRUCTION_BUILT',len(meshes()),len(added),flush=True)


if __name__=='__main__':main()
