"""MK4C: flattened copper interfaces, chamber braces and green construction envelope."""
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
import mikotaj_na_xanth_parts as parts
from build_skymech_construction import tubes
from build_openfa_assets import box
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
from refine_rigellian_crowns import sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv

ROOT=Path(__file__).resolve().parents[3]
INITIAL=ROOT/'sources/docs/assets/reconstruction/ships/mikotaj/na-xanth/model.blend'
EVIDENCE=ROOT/'sources/docs/reconstruction/models/na-xanth-station-evidence.json'
PLANFORM=1.18
CASE=[(-.82,.035),(-.69,.16),(-.43,.24),(.28,.23),(.62,.15),(.76,.045)]
AXES=(3.0*PLANFORM,1.55*PLANFORM,1.65)
HEIGHTS=sorted({z for z in [round(-1.53+i*.102,6) for i in range(31)] if abs(abs(z)-.25)>.06}|{-.25,.25})
VIEWS={'front-quarter':(5,-13,8),'front':(0,-16,2),'rear-quarter':(-6,12,6),'side':(16,0,3),'work-detail':(2,-14,4)}


def folders(variant):
    prefix='orbital-station-refined' if variant=='finished' else 'orbital-station-construction'
    rel=Path('docs/assets/reconstruction')/prefix/'mikotaj/na-xanth'
    return ROOT/'sources'/rel,ROOT/'gallery/media'/rel


def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']


def point(phi,z,offset=0):
    f=math.sqrt(max(0,1-(z/AXES[2])**2))
    return Vector(((AXES[0]*f+offset)*math.cos(phi),(AXES[1]*f+offset)*math.sin(phi),z))


def place_interface(obj,i):
    rotation=Matrix.Rotation(math.pi/2,3,'Y')
    for vertex in obj.data.vertices:
        p=vertex.co.copy();p.x*=1.25;vertex.co=parts.point(i,Vector((0,-1.04,.22))+rotation@p)
    obj.data.update();return obj


def finished(m):
    removed=[];attachments=[]
    for i in range(3):
        removed += [f'Na-Xanth body bezel {i}',f'Na-Xanth forward coupler {i}',f'Na-Xanth dark coupler face {i}']+[f'Na-Xanth face amber tile {i} {j}' for j in range(3)]
    for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    for i in range(3):
        name=f'Na-Xanth flattened copper interface {i}'
        place_interface(vessel(name,CASE,m['copper'],[(-math.pi/2,-.25,.002)]),i);attachments.append(dict(name=name,owner=f'Na-Xanth green chamber {i}'))
        for j,x in enumerate([-.50,-.25,0,.28]):
            heights=sorted(set([x-.022,x+.022]+[z for z,_ in CASE if x-.022<z<x+.022]));rows=[(z,profile_radius(CASE,z)+.017,profile_radius(CASE,z)-.025) for z in heights]
            obj=annulus(f'Na-Xanth copper interface transverse band {i} {j}',(0,0),rows,m['copper'],(0,0,0));place_interface(obj,i);attachments.append(dict(name=obj.name,owner=name))
        scale=parts.SCALES[i]
        obj=box(f'Na-Xanth flattened interface dark field {i}',parts.point(i,(.08,-1.28,.22)),(.34*scale,.045*scale,.075*scale),m['recess'],.003*scale);attachments.append(dict(name=obj.name,owner=name))
        for j,x in enumerate([-.04,.07,.18]):
            obj=box(f'Na-Xanth flattened interface amber field {i} {j}',parts.point(i,(x,-1.306,.22)),(.04*scale,.016*scale,.028*scale),m['amber'],.001*scale);attachments.append(dict(name=obj.name,owner=f'Na-Xanth flattened interface dark field {i}'))
        for j,phi in enumerate([-math.pi/2-.64,-math.pi/2+.64,math.pi/2-.64,math.pi/2+.64]):
            for kind,z0,z1 in [('green',.03,.87),('slate',-.85,-.06)]:
                owner=f'Na-Xanth {kind} chamber {i}';name=f'Na-Xanth broad {kind} chamber brace {i} {j}'
                parts.patch(name,owner,z0,z1,phi,.10,m['brace'],top=.018,back=-.025);attachments.append(dict(name=name,owner=owner))
    root=bpy.data.objects['PlacementRoot'];planform=bpy.data.objects.new('Authored station planform fit',None);bpy.context.collection.objects.link(planform);planform.parent=root;planform.scale=(PLANFORM,PLANFORM,1)
    for obj in meshes():obj.parent=planform
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
    tubes('MK4C construction horizontal hoops',[([point(i*math.tau/96,z) for i in range(96)],True,(0,0,1)) for z in HEIGHTS],.010,m['framework'])
    zs=sorted(set(round(z,8) for z in [-1.645+j*3.29/120 for j in range(121)]+HEIGHTS));assert min(b-a for a,b in zip(zs,zs[1:]))>1e-6
    tubes('MK4C construction meridian ribs',[([point(i*math.tau/24,z) for z in zs],False,(0,0,1)) for i in range(24)],.013,m['framework'])
    diagonal=[]
    for j,(a,b) in enumerate(zip(HEIGHTS,HEIGHTS[1:])):
        for i in range(24):
            p,q=(i,i+1) if (i+j)%2 else (i+1,i);start=point(p*math.tau/24,a);end=point(q*math.tau/24,b);inset=(end-start).normalized()*.003
            diagonal.append(([start+inset,end-inset],False,(0,0,1)))
    tubes('MK4C construction diagonal lattice',diagonal,.008,m['framework'])
    stays=[]
    for z in [-.25,.25]:
        for i in range(8):
            p=point(i*math.tau/8,z);a=p.copy();a.x*=.27;a.y*=.27;stays.append(([a,p],False,(0,0,1)))
    tubes('MK4C construction body support stays',stays,.020,m['framework'])
    for i in range(8):
        for side in [-1,1]:
            low,high=(.18,1.44) if side>0 else (-1.44,-.18)
            cover(f'MK4C temporary green shield {side} {i}',low,high,i*math.tau/8,i*math.tau/8+math.pi/6,m['cover'])
    root=bpy.data.objects['PlacementRoot'];actor=bpy.data.objects.new('ConstructionWorkCarriage',None);bpy.context.collection.objects.link(actor);actor.parent=root
    for name,position,size,style in [('rail clamp',(0,0,0),(.18,.10,.07),'case'),('service case',(0,-.02,.085),(.18,.14,.10),'case'),('pale marker',(0,-.10,.09),(.10,.018,.035),'marker')]:
        obj=box('MK4C construction carriage '+name,position,size,m[style],.004);obj.parent=actor
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=181;scene.render.fps=30
    for frame,angle in [(1,0),(61,.047),(121,-.047),(181,0)]:
        actor.location=point(-math.pi/2+angle,0);actor.rotation_euler.z=angle;actor.keyframe_insert(data_path='location',frame=frame);actor.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    action=actor.animation_data.action;action.name='ConstructionActivity';track=actor.animation_data.nla_tracks.new();track.name='ConstructionActivity';track.strips.new('ConstructionActivity',1,action);actor.animation_data.action=None;scene.frame_set(1)
    return [],[]


def frame_view(variant,view):
    camera=bpy.context.scene.camera;direction=Vector(VIEWS[view]).normalized();points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    if view=='work-detail':centre=Vector((0,-1.40,.22)) if variant=='finished' else point(-math.pi/2,0)+Vector((0,0,.05));scale=1.85 if variant=='finished' else 1.20
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
    authored.TEXTURES=ROOT/'sources/materials/reconstruction'/('orbital-station-refined' if variant=='finished' else 'orbital-station-construction')/'mikotaj/na-xanth'
    specs=[('copper',(.31,.14,.08),.72),('brace',(.26,.31,.34),.65),('recess',(.015,.020,.018),.30),('amber',(.45,.24,.06),.40)] if variant=='finished' else [('framework',(.10,.22,.14),.65),('cover',(.06,.15,.085),.35),('case',(.12,.20,.15),.60),('marker',(.12,.42,.34),.30)]
    m={}
    for style,colour,metal in specs:m[style]=authored.worn_material(style,colour,metal);m[style].name='Na-Xanth '+variant+' | '+style
    removed,attachments=finished(m) if variant=='finished' else construction(m);added=[o for o in meshes() if o.name not in original]
    for obj in added:
        if obj.parent is None:obj.parent=root
        bpy.context.view_layer.objects.active=obj;bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        uv(obj);mod=obj.modifiers.new('Explicit portable tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new('Na-Xanth refined complete '+variant);scene.collection.children.link(collection);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description='MK4C descriptor '+str(int(variant=='construction'))+' refined '+variant+' state'
    root['variant']=variant;root['legacy_sprite_frame']=int(variant=='construction');scene.frame_set(1);scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';frame_view(variant,'front-quarter')
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=variant=='construction',export_animation_mode='NLA_TRACKS',export_frame_range=True);bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    deps=['build_skymech_construction.py','refine_braccatian_pithoi.py','mikotaj_na_xanth_parts.py','build_openfa_assets.py','manufactured_vessels.py','manufactured_annuli.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py']
    meta=dict(issue=192,id=old['id'],name='Na-Xanth',culture='mikotaj',variant=variant,legacy_sprite_frame=int(variant=='construction'),stage='orbital-station-structural-refinement' if variant=='finished' else 'orbital-station-construction-refinement',source_study=source.relative_to(ROOT).as_posix(),source_blend_sha256=sha(source),source_glb_sha256=sha(source.with_suffix('.glb')),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},evidence_sha256=sha(EVIDENCE),preserved_mesh_names=sorted(original-set(removed)),removed_mesh_names=removed,added_mesh_names=[o.name for o in added],attachments=attachments,authored_planform_scale=PLANFORM,mesh_objects=len(meshes()),blender=bpy.app.version_string,authored='Exact copper profiles, brace count, hidden layout, 1.18 radial planform fit and six-second service loop; no named alloy or recovered timing claimed',acceptance='Actual native/independent GLB render verification pending; final game calibration open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('MK4C_STATE_BUILT',variant,len(meshes()),len(added),flush=True)


if __name__=='__main__':main()
