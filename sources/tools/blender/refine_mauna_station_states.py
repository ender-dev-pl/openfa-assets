"""MN5C: broad service ribs, tower modules and a dense orbital construction cage."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import bpy
import bmesh
from mathutils import Vector, Matrix

sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
import mauna_orbital_construction_area_parts as parts
from build_skymech_construction import tubes
from build_openfa_assets import box,cylinder
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from refine_rigellian_crowns import sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
INITIAL=ROOT/'sources/docs/assets/reconstruction/ships/mauna/orbital-construction-area/model.blend'
EVIDENCE=ROOT/'sources/docs/reconstruction/models/mauna-station-evidence.json'
PROFILE=[(-1.56,.08,.08),(-1.30,.32,.22),(-.70,1.0,.55),(-.58,1.55,.68),(-.50,3.05,1.02),(.50,3.05,1.02),(.65,1.80,.80),(.90,1.0,.45),(1.25,.85,.27),(1.46,.18,.16)]
HEIGHTS=sorted({round(-1.48+i*.098,8) for i in range(30) if min(abs(-1.48+i*.098-z) for z in [-.12,.12])>.04}|{-.12,.12})
EXPOSED=['Orbital central spire','Orbital lower axial stem']+[f'Orbital central orange collar {i}' for i in range(4)]
VIEWS={'front-quarter':(5,-13,8),'front':(0,-16,1),'rear-quarter':(-6,12,6),'side':(16,0,3),'work-detail':(2,-14,5)}


def folders(variant):
    prefix='orbital-station-refined' if variant=='finished' else 'orbital-station-construction'
    rel=Path('docs/assets/reconstruction')/prefix/'mauna/orbital-construction-area'
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def radii(z):
    assert PROFILE[0][0]<=z<=PROFILE[-1][0]
    for a,b in zip(PROFILE,PROFILE[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);return a[1]+t*(b[1]-a[1]),a[2]+t*(b[2]-a[2])
    raise AssertionError(z)


def point(phi,z,offset=0):
    rx,ry=radii(z)
    return Vector(((rx+offset)*math.cos(phi),(ry+offset)*math.sin(phi),z))



def finished(m):
    attachments=[]
    def attach(obj,owner):attachments.append(dict(name=obj.name,owner=owner));return obj
    for j,z in enumerate([-.20,.10]):
        obj=annulus(f'MN5C broad perimeter band {j}',(0,0),[(z-.025,1.015,.98),(z+.025,1.015,.98)],m['edge'],(0,0,0))
        for v in obj.data.vertices:v.co.x*=1.8;v.co.y*=.72
        attach(obj,parts.CORE)
    for i,phi in enumerate([-math.pi/2-.92,-math.pi/2-.56,-math.pi/2+.56,-math.pi/2+.92,math.pi/2-.92,math.pi/2-.56,math.pi/2+.56,math.pi/2+.92]):
        name=f'MN5C broad copper service pier {i}';attach(parts.patch(name,parts.CORE,-.19,.10,phi,.055,m['copper'],.035,-.025),parts.CORE)
        for j,z in enumerate([-.12,-.035,.05]):attach(parts.patch(f'MN5C pier pale fitting {i} {j}',parts.CORE,z-.017,z+.017,phi,.045,m['pale'],.052,.015),name)
    for i,(x,y) in enumerate([(-1.12,-.25),(-.64,-.40),(.64,-.40),(1.12,-.25),(-1.12,.25),(1.12,.25)]):
        name=f'MN5C lower service pod {i}';obj=vessel(name,[(-.56,.025),(-.48,.07),(-.35,.09),(-.22,.09)],m['edge'],[]);obj.location=(x,y,0);attach(obj,parts.CORE)
        for j,z in enumerate([-.46,-.36]):attach(cylinder(f'MN5C lower pod pale band {i} {j}',(x,y,z),.094,.035,m['pale'],32),name)
    for x,owner,z,width in [(0,'Orbital central tower',.92,.20),(-.65,'Orbital secondary tower -1',.70,.13),(.65,'Orbital secondary tower 1',.70,.13)]:
        name=f'MN5C tower equipment case {x}';attach(box(name,(x,-.07,z),(width,.18,.25),m['copper'],.008),owner)
        panel=attach(box(f'MN5C tower dark panel {x}',(x,-.167,z),(width*.8,.03,.20),m['recess'],.004),name)
        for j,dz in enumerate([-.06,0,.06]):attach(box(f'MN5C tower pale panel bar {x} {j}',(x,-.19,z+dz),(width*.65,.025,.022),m['pale'],.002),panel.name)
    for i,phi in enumerate([-math.pi/2-.68,-math.pi/2+.68,math.pi/2-.68,math.pi/2+.68]):
        name=f'MN5C upper grey equipment field {i}';attach(parts.patch(name,parts.CAP,.41,.57,phi,.19,m['edge'],.045,-.025),parts.CAP)
        for j,z in enumerate([.445,.495,.545]):attach(parts.patch(f'MN5C upper field pale bar {i} {j}',parts.CAP,z-.009,z+.009,phi,.15,m['pale'],.060,.025),name)
    return [],attachments


def cover(name,z0,z1,phi0,phi1,mat):
    rows=15;cols=13;vertices=[]
    for depth in [.007,-.018]:
        for j in range(rows):
            f=j/(rows-1);z=z0+(z1-z0)*f
            for i in range(cols):
                g=i/(cols-1);vertices.append(tuple(point(phi0+(phi1-phi0)*g,z,depth-.025*math.sin(math.pi*f)*math.sin(math.pi*g))))
    size=rows*cols;faces=[]
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i;f=(a,a+1,a+cols+1,a+cols);faces += [f,tuple(size+x for x in reversed(f))]
    edge=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[j*cols for j in reversed(range(1,rows-1))]
    faces += [(a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1])]
    return mesh(name,vertices,faces,mat)


def construction(m):
    tubes('MN5C construction horizontal hoops',[([point(i*math.tau/96,z) for i in range(96)],True,(0,0,1)) for z in HEIGHTS],.010,m['framework'])
    zs=sorted(set(round(z,8) for z in [-1.56+j*3.02/120 for j in range(121)]+HEIGHTS+[p[0] for p in PROFILE]));assert min(b-a for a,b in zip(zs,zs[1:]))>1e-6
    tubes('MN5C construction meridian ribs',[([point(i*math.tau/24,z) for z in zs],False,(-math.sin(i*math.tau/24),math.cos(i*math.tau/24),0)) for i in range(24)],.013,m['framework'])
    diagonal=[]
    for j,(a,b) in enumerate(zip(HEIGHTS,HEIGHTS[1:])):
        for i in range(24):
            p,q=(i,i+1) if (i+j)%2 else (i+1,i);start=point(p*math.tau/24,a);end=point(q*math.tau/24,b);inset=(end-start).normalized()*.006
            diagonal.append(([start+inset,end-inset],False,(0,0,1)))
    tubes('MN5C construction diagonal lattice',diagonal,.008,m['framework'])
    stays=[]
    for z in [-.12,.12]:
        for i in range(8):
            p=point(i*math.tau/8,z);a=p.copy();a.x*=.10;a.y*=.10;stays.append(([a,p],False,(0,0,1)))
    tubes('MN5C construction body support stays',stays,.020,m['framework'])
    for i in range(8):
        for side in [-1,1]:
            low,high=(.20,1.39) if side>0 else (-1.48,-.20)
            cover(f'MN5C temporary grey shield {side} {i}',low,high,i*math.tau/8,i*math.tau/8+math.pi/6,m['cover'])
    root=bpy.data.objects['PlacementRoot'];actor=bpy.data.objects.new('ConstructionWorkCarriage',None);bpy.context.collection.objects.link(actor);actor.parent=root
    for name,position,size,style in [('rail clamp',(0,0,0),(.18,.10,.07),'case'),('service case',(0,-.02,.085),(.18,.14,.10),'case'),('pale marker',(0,-.10,.09),(.10,.018,.035),'marker')]:
        obj=box('MN5C construction carriage '+name,position,size,m[style],.004);obj.parent=actor
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=181;scene.render.fps=30
    for frame,angle in [(1,0),(61,.040),(121,-.040),(181,0)]:
        actor.location=point(-math.pi/2+angle,0);actor.rotation_euler.z=angle;actor.keyframe_insert(data_path='location',frame=frame);actor.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    action=actor.animation_data.action;action.name='ConstructionActivity';track=actor.animation_data.nla_tracks.new();track.name='ConstructionActivity';track.strips.new('ConstructionActivity',1,action);actor.animation_data.action=None;scene.frame_set(1)
    return [],[]


def frame_view(variant,view):
    camera=bpy.context.scene.camera;direction=Vector(VIEWS[view]).normalized();points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    if view=='work-detail':centre=Vector((0,-.30,.72)) if variant=='finished' else point(-math.pi/2,0)+Vector((0,0,.05));scale=2.3 if variant=='finished' else 1.20
    else:centre=Vector([(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)]);scale=None
    camera.location=centre+direction*18;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';bpy.context.view_layer.update();local=[camera.matrix_world.inverted()@p for p in points];camera.data.ortho_scale=scale or max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.16


def preview():
    import render_gallery_animations as renderer
    sys.path.insert(0,str(ROOT/'tools'));from gallery_animation_assets import glb_clips
    output,media=folders('construction');meta=json.loads((output/'model.json').read_text());study=dict(stage=meta['stage'],blend=(output/'model.blend').relative_to(ROOT).as_posix(),glb=(output/'model.glb').relative_to(ROOT).as_posix(),image=(media/'front-quarter.png').relative_to(ROOT).as_posix());clips=glb_clips(output/'model.glb');assert len(clips)==1 and clips[0]['name']=='ConstructionActivity'
    result=[renderer.render_clip(dict(id=meta['id']),study,clip,shutil.which('ffmpeg')) for clip in clips]
    (media/'animation-previews.json').write_text(json.dumps(dict(id=meta['id'],stage=meta['stage'],glb=study['glb'],glb_sha256=sha(output/'model.glb'),blend_sha256=sha(output/'model.blend'),renderer_sha256=sha(Path(renderer.__file__)),blender=bpy.app.version_string,clips=result),indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--variant',choices=['finished','construction'],default='finished');parser.add_argument('--preview-only',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.preview_only:preview();return
    variant=args.variant;output,media=folders(variant);output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True);source=INITIAL if variant=='finished' else folders('finished')[0]/'model.blend';old=json.loads(source.with_suffix('.json').read_text());assert old['blend_sha256']==sha(source) and old['glb_sha256']==sha(source.with_suffix('.glb'))
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;root=bpy.data.objects['PlacementRoot'];original={o.name for o in meshes()}
    authored.TEXTURES=ROOT/'sources/materials/reconstruction'/('orbital-station-refined' if variant=='finished' else 'orbital-station-construction')/'mauna/orbital-construction-area'
    specs=[('copper',(.29,.12,.065),.76),('edge',(.19,.24,.27),.72),('recess',(.012,.016,.018),.40),('pale',(.48,.55,.57),.60)] if variant=='finished' else [('framework',(.25,.31,.34),.70),('cover',(.17,.22,.25),.45),('case',(.22,.28,.30),.65),('marker',(.48,.23,.08),.40)]
    m={}
    for style,colour,metal in specs:m[style]=authored.worn_material(style,colour,metal);m[style].name='MN5C Orbital Construction Area '+variant+' | '+style
    removed,attachments=finished(m) if variant=='finished' else construction(m);added=[o for o in meshes() if o.name not in original]
    for obj in added:
        if obj.parent is None:obj.parent=root
        bpy.context.view_layer.objects.active=obj;bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        uv(obj);mod=obj.modifiers.new('Explicit portable tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new('MN5C Orbital Construction Area refined complete '+variant);scene.collection.children.link(collection);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description='MN5C descriptor '+str(int(variant=='construction'))+' refined '+variant+' state'
    root['variant']=variant;root['legacy_sprite_frame']=int(variant=='construction');scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';frame_view(variant,'front-quarter')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=variant=='construction',export_animation_mode='NLA_TRACKS',export_frame_range=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    deps=['build_skymech_construction.py','refine_braccatian_pithoi.py','mauna_orbital_construction_area_parts.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=192,id=old['id'],name='MN5C Orbital Construction Area',culture='mauna',variant=variant,legacy_sprite_frame=int(variant=='construction'),stage='orbital-station-structural-refinement' if variant=='finished' else 'orbital-station-construction-refinement',source_study=source.relative_to(ROOT).as_posix(),source_blend_sha256=sha(source),source_glb_sha256=sha(source.with_suffix('.glb')),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},evidence_sha256=sha(EVIDENCE),preserved_mesh_names=sorted(original-set(removed)),removed_mesh_names=removed,added_mesh_names=[o.name for o in added],attachments=attachments,mesh_objects=len(meshes()),blender=bpy.app.version_string,authored='Exact case profiles, hidden layout and six-second service loop are authored; no concrete spacecraft material or recovered timing claimed',acceptance='Actual native/independent GLB render verification pending; final game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('MN5C_STATE_BUILT',variant,len(meshes()),len(added),flush=True)


if __name__=='__main__':main()
