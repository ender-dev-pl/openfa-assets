"""AC3C: equipped curved axial modules and a tapered construction sleeve."""
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
import achaean_orbital_shipyard_parts as parts
from build_skymech_construction import tubes
from build_openfa_assets import box,cylinder
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from refine_rigellian_crowns import sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
INITIAL=ROOT/'sources/docs/assets/reconstruction/ships/achaean/orbital-shipyard/model.blend'
EVIDENCE=ROOT/'sources/docs/reconstruction/models/achaean-station-evidence.json'
VERTICAL=1.18
PROFILE=[(-4.55,.04,.05),(-4.0,.14,.20),(-3.0,.30,.38),(-2.0,.55,.95),(-1.60,.62,1.26),(1.60,.62,1.26),(2.0,.55,.95),(3.0,.30,.38),(4.0,.14,.20),(4.55,.04,.05)]
HEIGHTS=sorted({round(-4.3+i*8.6/30,8) for i in range(31) if min(abs(-4.3+i*8.6/30-x) for x in [-.95,.95])>.08}|{-.95,.95})
VIEWS={'front-quarter':(3,-14,7),'front':(0,-16,0),'rear-quarter':(-3,14,7),'work-detail':(2,-14,5)}


def folders(variant):
    prefix='orbital-station-refined' if variant=='finished' else 'orbital-station-construction'
    rel=Path('docs/assets/reconstruction')/prefix/'achaean/orbital-shipyard'
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def radii(z):
    assert PROFILE[0][0]<=z<=PROFILE[-1][0]
    for a,b in zip(PROFILE,PROFILE[1:]):
        if a[0]<=z<=b[0]:
            t=(z-a[0])/(b[0]-a[0]);return a[1]+t*(b[1]-a[1]),a[2]+t*(b[2]-a[2])
    raise AssertionError(z)


def point(phi,x,offset=0):
    ry,rz=radii(x)
    return Vector((x,(ry+offset)*math.cos(phi),(rz+offset)*math.sin(phi)))


def finished(m):
    attachments=[];removed=[f'Shipyard {kind} {i}' for kind in ['field mount','blue field'] for i in range(7)]
    for n in removed:bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
    def attach(obj,owner):attachments.append(dict(name=obj.name,owner=owner));return obj
    def axial(obj,x):
        for v in obj.data.vertices:v.co=Vector((x,0,0))+parts.ROTATIONS[parts.CORE]@v.co
        obj.data.update();return obj
    sections=[(-2.55,[(-.50,.055),(-.3125,.15),(.125,.16),(.50,.09)],'copper'),(2.35,[(-.625,.11),(-.375,.22),(.25,.20),(.625,.07)],'rose')]
    for i,(x,profile,style) in enumerate(sections):
        name=f'AC3C broad axial service module {i}';attach(axial(vessel(name,profile,m[style],[]),x),parts.CORE)
        for j,z in enumerate([-.22,.04,.20]):
            rr=profile_radius(profile,z);obj=annulus(f'AC3C axial module pale band {i} {j}',(0,0),[(z-.017,rr+.014,rr-.025),(z+.017,rr+.014,rr-.025)],m['pale'],(0,0,0));attach(axial(obj,x),name)
    name='AC3C central rounded equipment module';obj=vessel(name,[(-.3125,.045),(-.20,.15),(.08,.23),(.28,.19),(.375,.11)],m['rose'],[]);obj.location=(.25,0,0);attach(obj,parts.CORE)
    attach(cylinder('AC3C central module upper rim',(.25,0,.275),.20,.045,m['pale'],64),name)
    for j,z in enumerate([-.12,0,.12]):attach(box(f'AC3C central module equipment bar {j}',(.25,-.205,z),(.19,.065,.035),m['pale'],.003),name)
    for i,x in enumerate(parts.WINDOW_X):
        radius=profile_radius(parts.PROFILES[parts.CORE],x);owner=parts.CORE
        for j,(centre,profile,style) in enumerate(sections):
            if profile[0][0]<=x-centre<=profile[-1][0]:radius=max(radius,profile_radius(profile,x-centre));owner=f'AC3C broad axial service module {j}'
        if x==.30:radius=.30;owner=name
        mount=f'AC3C fitted field housing {i}';attach(box(mount,(x,0,radius+.025),(.19,.18,.09),m['copper'],.008),owner)
        attach(box(f'AC3C fitted blue field {i}',(x,-.095,radius+.025),(.14,.035,.055),m['blue'],.003),mount)
    for i in range(6):
        owner=f'Shipyard vertical segment {i}'
        for j,(z0,z1) in enumerate([(-.58,-.33),(.33,.58)]):
            label=f'AC3C segment pale equipment field {i} {j}';attach(parts.patch(label,owner,z0,z1,-math.pi/2,.48,m['pale'],.018,-.025),owner)
            for k,z in enumerate([z0+.075,z1-.075]):attach(parts.patch(f'AC3C segment dark equipment slot {i} {j} {k}',owner,z-.013,z+.013,-math.pi/2,.34,m['recess'],.029,.004),label)
    root=bpy.data.objects['PlacementRoot'];fit=bpy.data.objects.new('Authored station vertical fit',None);bpy.context.collection.objects.link(fit);fit.parent=root;fit.scale=(1,1,VERTICAL)
    for obj in meshes():obj.parent=fit
    return removed,attachments


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
    tubes('AC3C construction transverse hoops',[([point(i*math.tau/96,x) for i in range(96)],True,(1,0,0)) for x in HEIGHTS],.010,m['framework'])
    xs=sorted(set(round(x,8) for x in [-4.55+j*9.10/120 for j in range(121)]+HEIGHTS+[p[0] for p in PROFILE]))
    tubes('AC3C construction longitudinal ribs',[([point(i*math.tau/24,x) for x in xs],False,(0,-math.sin(i*math.tau/24),math.cos(i*math.tau/24))) for i in range(24)],.014,m['framework'])
    diagonal=[]
    for j,(a,b) in enumerate(zip(HEIGHTS,HEIGHTS[1:])):
        for i in range(24):
            p,q=(i,i+1) if (i+j)%2 else (i+1,i);start=point(p*math.tau/24,a);end=point(q*math.tau/24,b);inset=(end-start).normalized()*.006;diagonal.append(([start+inset,end-inset],False,(1,0,0)))
    tubes('AC3C construction diagonal lattice',diagonal,.008,m['framework'])
    stays=[]
    for x in [-.95,.95]:
        for i in range(8):
            b=point(i*math.tau/8,x);a=b.copy();a.y*=.08;a.z*=.08;stays.append(([a,b],False,(1,0,0)))
    tubes('AC3C construction body support stays',stays,.020,m['framework'])
    for i in range(8):
        for side in [-1,1]:
            low,high=(.35,4.0) if side>0 else (-4.0,-.35);cover(f'AC3C temporary copper shield {side} {i}',low,high,i*math.tau/8,i*math.tau/8+math.pi/6,m['cover'])
    root=bpy.data.objects['PlacementRoot'];actor=bpy.data.objects.new('ConstructionWorkCarriage',None);bpy.context.collection.objects.link(actor);actor.parent=root
    for name,position,size,style in [('rail clamp',(0,0,0),(.11,.08,.07),'case'),('service case',(0,-.02,.085),(.18,.14,.10),'case'),('pale marker',(0,-.10,.09),(.10,.018,.035),'marker')]:
        obj=box('AC3C construction carriage '+name,position,size,m[style],.004);obj.parent=actor
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=181;scene.render.fps=30
    for frame,x in [(1,0),(61,.16),(121,-.16),(181,0)]:
        actor.location=point(math.pi,x);actor.keyframe_insert(data_path='location',frame=frame)
    action=actor.animation_data.action;action.name='ConstructionActivity';track=actor.animation_data.nla_tracks.new();track.name='ConstructionActivity';track.strips.new('ConstructionActivity',1,action);actor.animation_data.action=None;scene.frame_set(1)
    return [],[]


def frame_view(variant,view):
    camera=bpy.context.scene.camera;direction=Vector(VIEWS[view]).normalized();points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    if view=='work-detail':centre=Vector((.20,-.12,.10)) if variant=='finished' else point(math.pi,0)+Vector((0,0,.05));scale=2.3 if variant=='finished' else 1.20
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
    authored.TEXTURES=ROOT/'sources/materials/reconstruction'/('orbital-station-refined' if variant=='finished' else 'orbital-station-construction')/'achaean/orbital-shipyard'
    specs=[('copper',(.29,.12,.065),.76),('rose',(.37,.15,.12),.68),('blue',(.18,.30,.36),.50),('recess',(.012,.016,.018),.40),('pale',(.48,.55,.57),.60)] if variant=='finished' else [('framework',(.30,.16,.095),.70),('cover',(.29,.15,.11),.45),('case',(.22,.28,.30),.65),('marker',(.48,.23,.08),.40)]
    m={}
    for style,colour,metal in specs:m[style]=authored.worn_material(style,colour,metal);m[style].name='AC3C Orbital Shipyard '+variant+' | '+style
    removed,attachments=finished(m) if variant=='finished' else construction(m);added=[o for o in meshes() if o.name not in original]
    for obj in added:
        if obj.parent is None:obj.parent=root
        bpy.context.view_layer.objects.active=obj;bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        uv(obj);mod=obj.modifiers.new('Explicit portable tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new('AC3C Orbital Shipyard refined complete '+variant);scene.collection.children.link(collection);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description='AC3C descriptor '+str(int(variant=='construction'))+' refined '+variant+' state'
    root['variant']=variant;root['legacy_sprite_frame']=int(variant=='construction');scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';frame_view(variant,'front-quarter')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=variant=='construction',export_animation_mode='NLA_TRACKS',export_frame_range=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    deps=['build_skymech_construction.py','refine_braccatian_pithoi.py','achaean_orbital_shipyard_parts.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=192,id=old['id'],name='AC3C Orbital Shipyard',culture='achaean',variant=variant,legacy_sprite_frame=int(variant=='construction'),stage='orbital-station-structural-refinement' if variant=='finished' else 'orbital-station-construction-refinement',source_study=source.relative_to(ROOT).as_posix(),source_blend_sha256=sha(source),source_glb_sha256=sha(source.with_suffix('.glb')),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},evidence_sha256=sha(EVIDENCE),preserved_mesh_names=sorted(original-set(removed)),removed_mesh_names=removed,added_mesh_names=[o.name for o in added],attachments=attachments,mesh_objects=len(meshes()),blender=bpy.app.version_string,authored_vertical_scale=VERTICAL,authored='Exact case profiles, hidden layout and six-second service loop are authored; no concrete spacecraft material or recovered timing claimed',acceptance='Actual native/independent GLB render verification pending; final game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('AC3C_STATE_BUILT',variant,len(meshes()),len(added),flush=True)


if __name__=='__main__':main()
