"""AR5C source-visible shell equipment and independent ribbed construction state."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys
import bpy
import bmesh
from mathutils import Vector,Quaternion
sys.path.insert(0,str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
import artemian_geostationary_construction_parts as parts
from build_skymech_construction import tubes
from build_openfa_assets import box,cylinder
from manufactured_vessels import vessel,profile_radius
from refine_rigellian_crowns import sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv
ROOT=Path(__file__).resolve().parents[3]
INITIAL=ROOT/'sources/docs/assets/reconstruction/ships/artemian/geostationary-construction/model.blend'
EVIDENCE=ROOT/'sources/docs/reconstruction/models/geostationary-station-evidence.json'
AXIAL_FIT=1.65
PROFILE=[(-3.72,.08),(-3.0,.42),(-2.1,.98),(-1.2,1.16),(-.4,1.46),(.55,1.65),(1.1,1.32),(1.8,.60),(2.65,.08)]
HEIGHTS=sorted({z for z in [round(-3.50+i*5.95/30,6) for i in range(31)] if min(abs(z-t) for t in [-.55,0,.55])>.07}|{-.55,0,.55})
VIEWS={'front-quarter':(6,-16,6),'front':(0,-16,6),'rear-quarter':(-7,12,-5),'side':(16,0,3),'work-detail':(3,-14,6),'neck-detail':(3,-14,3)}


def folders(variant):
    prefix='orbital-station-refined' if variant=='finished' else 'orbital-station-construction'
    rel=Path('docs/assets/reconstruction')/prefix/'artemian/geostationary-construction'
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel

def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']

def point(phi,z,offset=0):
    r=profile_radius(PROFILE,z)+offset
    return Vector((r*math.cos(phi),r*math.sin(phi),z))


def finished(m):
    removed=[f'Geostationary blue face insert {i}' for i in range(12)];attachments=[]
    for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    def attach(obj,owner):attachments.append(dict(name=obj.name,owner=owner));return obj
    for i in range(12):
        phi=i*math.tau/12;obj=box(f'AR5C broad blue face field {i}',(1.10*math.cos(phi),1.10*math.sin(phi),.366),(.065,.12,.022),m['blue'],.002);obj.rotation_euler.z=phi;attach(obj,'Geostationary dark backing face')
    for i in range(6):
        phi=i*math.tau/6;centre=Vector((1.33*math.cos(phi),1.33*math.sin(phi),0));name=f'AR5C green rim equipment casing {i}'
        obj=vessel(name,[(.365,.05),(.39,.10),(.48,.11),(.56,.06)],m['shell'],[(phi,.46,.001)]);parts.place(obj,centre);attach(obj,'Geostationary copper face rim')
        obj=cylinder(f'AR5C pale rim equipment face {i}',centre+Vector((0,0,.558)),.045,.016,m['pale'],vertices=32);attach(obj,name)
        owner=f'Geostationary front module {i}';field=f'AR5C module equipment field {i}'
        obj=parts.patch(field,owner,.46,.54,phi,.50,m['recess'],top=.014,back=-.020);attach(obj,owner)
        for j,z in enumerate([.479,.516]):attach(parts.patch(f'AR5C pale module bar {i} {j}',owner,z-.008,z+.008,phi,.40,m['pale'],top=.027,back=.009),field)
    for i in range(4):
        phi=i*math.pi/2;centre=Vector((.50*math.cos(phi),.50*math.sin(phi),0));name=f'AR5C broad neck equipment shell {i}'
        profile=[(-.70,.12),(-.62,.22),(-.37,.30),(-.10,.29),(.16,.18),(.25,.07)]
        parts.PROFILES[name]=profile;parts.LOCATIONS[name]=centre;parts.DENTS[name]=(phi,-.37,.002)
        obj=vessel(name,profile,m['shell'],[(phi,-.37,.002)]);parts.place(obj,centre);attach(obj,parts.CORE)
        field=f'AR5C neck equipment field {i}';attach(parts.patch(field,name,-.48,-.20,phi,.50,m['recess'],top=.014,back=-.02),name)
        for j,z in enumerate([-.43,-.34,-.25]):attach(parts.patch(f'AR5C neck pale equipment bar {i} {j}',name,z-.014,z+.014,phi,.40,m['pale'],top=.027,back=.009),field)
    for i in range(8):
        phi=i*math.tau/8;attach(parts.patch(f'AR5C broad axial armour field {i}',parts.CORE,-.83,.16,phi,.18,m['shell'],top=.014,back=-.025),parts.CORE)
    owner=parts.BOSS;field='AR5C central boss equipment field';attach(parts.patch(field,owner,.45,.65,-math.pi/2,.40,m['recess'],top=.014,back=-.02),owner)
    for j,z in enumerate([.48,.55,.62]):attach(parts.patch(f'AR5C central pale equipment bar {j}',owner,z-.009,z+.009,-math.pi/2,.30,m['pale'],top=.027,back=.009),field)
    for i in range(4):attach(parts.patch(f'AR5C broad aft green field {i}',parts.CAP,-1.26,-.99,i*math.pi/2,.26,m['shell'],top=.016,back=-.026),parts.CAP)
    verts=[];faces=[];count=96
    for i in range(count):
        phi=i*math.tau/count;z=-1.16+.09*math.cos(phi)
        for dz,depth in [(-.018,.014),(.018,.014),(.018,-.024),(-.018,-.024)]:verts.append(tuple(parts.surface(parts.CAP,phi,z+dz,depth)))
    for i in range(count):
        for j in range(4):faces.append((i*4+j,i*4+(j+1)%4,((i+1)%count)*4+(j+1)%4,((i+1)%count)*4+j))
    attach(mesh('AR5C oblique aft shell trim',verts,faces,m['trim']),parts.CAP)
    root=bpy.data.objects['PlacementRoot'];fit=bpy.data.objects.new('Authored station axial fit',None);bpy.context.collection.objects.link(fit);fit.parent=root;fit.scale=(1,1,AXIAL_FIT)
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
    tubes('AR5C construction circumferential hoops',[([point(i*math.tau/96,z) for i in range(96)],True,(0,0,1)) for z in HEIGHTS],.012,m['framework'])
    zs=sorted(set(round(z,8) for z in [-3.715+i*6.36/140 for i in range(141)]+HEIGHTS+[z for z,_ in PROFILE if -3.715<z<2.645]));assert min(b-a for a,b in zip(zs,zs[1:]))>1e-6
    tubes('AR5C construction axial ribs',[([point(i*math.tau/24,z) for z in zs],False,(0,0,1)) for i in range(24)],.014,m['framework'])
    diagonal=[]
    for j,(a,b) in enumerate(zip(HEIGHTS,HEIGHTS[1:])):
        for i in range(24):
            p,q=(i,i+1) if (i+j)%2 else (i+1,i);start=point(p*math.tau/24,a);end=point(q*math.tau/24,b);inset=(end-start).normalized()*.003
            diagonal.append(([start+inset,end-inset],False,(0,0,1)))
    tubes('AR5C construction diagonal lattice',diagonal,.009,m['framework'])
    stays=[]
    for z in [-.55,.55]:
        for i in range(8):
            phi=i*math.tau/8;stays.append(([(.20*math.cos(phi),.20*math.sin(phi),z),point(phi,z)],False,(0,0,1)))
    tubes('AR5C construction body support stays',stays,.022,m['framework'])
    for i in range(12):
        low,high=(.05,1.90) if i%2==0 else (-2.95,-.65);cover(f'AR5C temporary green shield {i}',low,high,i*math.tau/12,(i+1)*math.tau/12,m['cover'])
    root=bpy.data.objects['PlacementRoot'];actor=bpy.data.objects.new('ConstructionWorkCarriage',None);bpy.context.collection.objects.link(actor);actor.parent=root
    for name,position,size,style in [('rail clamp',(0,0,0),(.18,.10,.07),'case'),('service case',(0,-.02,.09),(.19,.14,.11),'case'),('amber marker',(0,-.10,.09),(.09,.018,.035),'marker')]:
        obj=box('AR5C construction carriage '+name,position,size,m[style],.004);obj.parent=actor
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=181;scene.render.fps=30
    for frame,angle in [(1,0),(61,.08),(121,-.08),(181,0)]:
        actor.location=point(-math.pi/2+angle,.55);actor.rotation_euler.z=angle;actor.keyframe_insert(data_path='location',frame=frame);actor.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    action=actor.animation_data.action;action.name='ConstructionActivity';track=actor.animation_data.nla_tracks.new();track.name='ConstructionActivity';track.strips.new('ConstructionActivity',1,action);actor.animation_data.action=None;scene.frame_set(1)
    return [],[]


def frame_view(variant,view):
    camera=bpy.context.scene.camera;direction=Vector(VIEWS[view]).normalized();points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    if view=='neck-detail':centre=Vector((0,-.65,-.65));scale=1.90
    elif view=='work-detail':centre=Vector((0,-1.24,.65)) if variant=='finished' else point(-math.pi/2,.55)+Vector((0,0,.06));scale=1.75 if variant=='finished' else 1.20
    else:centre=Vector([(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)]);scale=None
    camera.location=centre+direction*18;camera.rotation_mode='XYZ';camera.rotation_euler=((-direction).to_track_quat('-Z','Y')@Quaternion((0,0,1),math.pi/2)).to_euler()
    # A source-only camera target preserves the side presentation when the
    # unchanged gallery renderer places its generic camera. Cameras are not
    # exported, counted as model helpers, or included in animation pose samples.
    target=bpy.data.objects.get('AR5C preview frame centre')
    if target is None:
        target=bpy.data.objects.new('AR5C preview frame centre',bpy.data.cameras.new('AR5C preview target data'));bpy.context.scene.collection.objects.link(target);target.hide_render=True;target['preview_only']=True
    target.location=centre
    constraint=camera.constraints.get('Source side presentation') or camera.constraints.new('TRACK_TO');constraint.name='Source side presentation';constraint.target=target;constraint.track_axis='TRACK_NEGATIVE_Z';constraint.up_axis='UP_X'
    camera.data.type='ORTHO';bpy.context.view_layer.update();local=[camera.matrix_world.inverted()@p for p in points];camera.data.ortho_scale=scale or max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.16


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
    if bpy.data.objects.get('AR5C preview neck fill') is None:
        light=bpy.data.lights.new('AR5C preview neck fill','AREA');light.energy=350;light.shape='DISK';light.size=4.5
        lamp=bpy.data.objects.new(light.name,light);scene.collection.objects.link(lamp);lamp['preview_only']=True;lamp.location=(0,-5,-1);lamp.rotation_euler=(Vector((0,0,-.5))-lamp.location).to_track_quat('-Z','Y').to_euler()
    authored.TEXTURES=ROOT/'sources/materials/reconstruction'/('orbital-station-refined' if variant=='finished' else 'orbital-station-construction')/'artemian/geostationary-construction'
    specs=[('shell',(.10,.27,.17),.68),('pale',(.35,.48,.39),.58),('recess',(.014,.021,.017),.35),('blue',(.025,.06,.42),.40),('trim',(.32,.24,.10),.70)] if variant=='finished' else [('framework',(.10,.22,.14),.65),('cover',(.06,.15,.085),.35),('case',(.12,.20,.15),.60),('marker',(.48,.24,.05),.30)]
    m={}
    for style,colour,metal in specs:m[style]=authored.worn_material(style,colour,metal);m[style].name='Geostationary Construction '+variant+' | '+style
    removed,attachments=finished(m) if variant=='finished' else construction(m);added=[o for o in meshes() if o.name not in original]
    for obj in added:
        if obj.parent is None:obj.parent=root
        bpy.context.view_layer.objects.active=obj;bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        uv(obj);mod=obj.modifiers.new('Explicit portable tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new('Geostationary Construction refined complete '+variant);scene.collection.children.link(collection);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description='AR5C descriptor '+str(int(variant=='construction'))+' refined '+variant+' state'
    root['variant']=variant;root['legacy_sprite_frame']=int(variant=='construction');scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';frame_view(variant,'front-quarter')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=variant=='construction',export_animation_mode='NLA_TRACKS',export_frame_range=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    deps=['build_skymech_construction.py','refine_braccatian_pithoi.py','artemian_geostationary_construction_parts.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=192,id=old['id'],name='Geostationary Construction',culture='artemian',variant=variant,legacy_sprite_frame=int(variant=='construction'),stage='orbital-station-structural-refinement' if variant=='finished' else 'orbital-station-construction-refinement',source_study=source.relative_to(ROOT).as_posix(),source_blend_sha256=sha(source),source_glb_sha256=sha(source.with_suffix('.glb')),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},evidence_sha256=sha(EVIDENCE),preserved_mesh_names=sorted(original-set(removed)),removed_mesh_names=removed,added_mesh_names=[o.name for o in added],attachments=attachments,authored_axial_scale=AXIAL_FIT,mesh_objects=len(meshes()),blender=bpy.app.version_string,authored='Exact equipment profiles, rear repetition, 1.65 longitudinal fit and six-second service loop authored; source-side camera roll is presentation only, no named alloy or recovered timing claimed',acceptance='Actual native/independent GLB render verification pending; final game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('AR5C_STATE_BUILT',variant,len(meshes()),len(added),flush=True)

if __name__=='__main__':main()
