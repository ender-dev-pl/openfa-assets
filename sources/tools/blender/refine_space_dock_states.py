"""Source-led PS7C finished structure and independent scaffolded construction state."""
import argparse
import json
import math
from pathlib import Path
import shutil
import sys

import bmesh
import bpy
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
import refine_braccatian_pithoi as authored
from build_skymech_construction import tubes
from build_openfa_assets import box
from refine_rigellian_crowns import sha
from refine_rigellian_extractor import mesh
from refine_rigellian_missiles import uv
from space_dock_parts import PROFILES, front_y
from manufactured_vessels import profile_radius

ROOT = Path(__file__).resolve().parents[3]
INITIAL = ROOT/'sources/docs/assets/reconstruction/ships/terran/space-dock/model.blend'
EVIDENCE = ROOT/'sources/docs/reconstruction/models/space-dock-refining-evidence.json'
PROFILE = [(-2.90,.06),(-2.50,.23),(-1.80,.62),(-1.10,1.08),(-.40,2.05),(.12,2.15),(.55,1.38),(1.0,.76),(1.50,.27),(2.05,.055)]
HEIGHTS = sorted(set([round(-2.72+i*.18,6) for i in range(27)]+[-.23,.12]))
VIEWS = {'front-quarter':(6,-12,7),'front':(0,-15,3),'rear-quarter':(-6,12,6),'side':(15,0,3),'equipment-detail':(3,-12,4)}


def folders(variant):
    prefix = 'orbital-station-refined' if variant == 'finished' else 'orbital-station-construction'
    rel = Path('docs/assets/reconstruction')/prefix/'terran/space-dock'
    return ROOT/'sources'/rel, ROOT/'gallery/media'/rel


def meshes():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


def radius(z):
    return profile_radius(PROFILE,z)


def square(phi,z):
    # Octagonal faceted scaffold follows the angular Terran hull, unlike BR4C's rounded cage.
    sector = math.tau/8
    r = radius(z)*math.cos(math.pi/8)/math.cos((phi+math.pi/8)%sector-math.pi/8)
    return Vector((r*math.cos(phi),r*math.sin(phi),z))


def panel(name,rows,phi,mat,front=.018,back=-.018):
    """Closed fitted face field: rows are (height,left/right fractional hull radius)."""
    vertices=[]
    for depth in [front,back]:
        for z,left,right in rows:
            r=profile_radius(PROFILES['Space Dock lower tapered hull'],z)
            for x in [left*r,right*r]:
                p=Vector((x,front_y(PROFILES['Space Dock lower tapered hull'],z)-depth,z))
                p.rotate(__import__('mathutils').Matrix.Rotation(phi,3,'Z'));vertices.append(tuple(p))
    n=len(rows);side=2*n;faces=[]
    for j in range(n-1):
        a=j*2;f=(a,a+1,a+3,a+2);faces.extend([f,tuple(side+x for x in reversed(f))])
    edge=[0,1]+[2*j+1 for j in range(1,n)]+list(reversed([2*j for j in range(1,n)]))
    faces.extend((a,a+side,b+side,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    return mesh(name,vertices,faces,mat)


def roof_field(name,points,mat,front=.018):
    verts=[]
    for offset in [front,-.012]:
        verts += [(x,front_y(PROFILES['Space Dock pyramidal upper hull'],z)-offset,z) for x,z in points]
    n=len(points);return mesh(name,verts,[tuple(range(n)),tuple(reversed(range(n,2*n)))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat)


def build_finished(m):
    removed=[f'Space Dock roof red band {i}' for i in [-1,1]]
    for name in removed:bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    additions=[]
    for i in range(4):
        phi=i*math.pi/2
        obj=panel(f'Space Dock broad dark lower face {i}',[(-1.95,-.20,.20),(-1.30,-.36,.36),(-.50,-.36,.36),(.04,-.36,.36)],phi,m['recess']);additions.append((obj.name,'Space Dock lower tapered hull'))
        for side in [-1,1]:
            a,b=(.23,.38) if side>0 else (-.38,-.23)
            obj=panel(f'Space Dock pale longitudinal hull stiffener {i} {side}',[(-2.12,a,b),(-1.30,a,b),(-.50,a,b),(.06,a,b)],phi,m['frame'],front=.035,back=-.018);additions.append((obj.name,'Space Dock lower tapered hull'))
        # Four large service housings are authored symmetry; the front one is directly visible.
        n=Vector((math.sin(phi),-math.cos(phi),0));z=-.48;y=abs(front_y(PROFILES['Space Dock lower tapered hull'],z))
        for suffix,offset,size,style in [('case',.06,(.40,.24,.23),'frame'),('dark opening',.19,(.27,.035,.11),'recess'),('lower service collar',.08,(.20,.17,.24),'hull')]:
            centre=n*(y+offset);centre.z=z if suffix!='lower service collar' else z-.20
            obj=box(f'Space Dock projecting service {suffix} {i}',centre,size,m[style],.008);obj.rotation_euler.z=phi;additions.append((obj.name,'Space Dock lower tapered hull' if suffix=='case' else f'Space Dock projecting service case {i}'))
        for side in [-1,1]:
            profile=PROFILES['Space Dock pyramidal upper hull']
            points=[(side*x*profile_radius(profile,z),z) for x,z in [(.10,.235),(.31,.235),(.31,.76),(.10,.76)]]
            obj=roof_field(f'Space Dock broad roof armour field {i} {side}',points,m['hull'],front=.010);obj.rotation_euler.z=phi;additions.append((obj.name,'Space Dock pyramidal upper hull'))
    # A broad stepped roof marking replaces the thin pair in the first study.
    obj=roof_field('Space Dock broad stepped red roof field',[(-.34,.29),(.34,.29),(.28,.42),(.12,.42),(.10,.57),(-.10,.57),(-.12,.42),(-.28,.42)],m['red']);additions.append((obj.name,'Space Dock pyramidal upper hull'))
    for side in [-1,1]:
        obj=roof_field(f'Space Dock roof pale service field {side}',[(side*.33,.23),(side*.44,.23),(side*.32,.48),(side*.23,.48)],m['frame']);additions.append((obj.name,'Space Dock pyramidal upper hull'))
    return removed,additions


def scaffold_cover(name,z0,z1,phi0,phi1,mat):
    cols=9;rows=9;verts=[]
    for depth in [.006,-.016]:
        for j in range(rows):
            f=j/(rows-1);z=z0+(z1-z0)*f
            for i in range(cols):
                g=i/(cols-1);p=square(phi0+(phi1-phi0)*g,z);p+=Vector((p.x,p.y,0)).normalized()*(depth-.018*math.sin(math.pi*f)*math.sin(math.pi*g));verts.append(tuple(p))
    size=cols*rows;faces=[]
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i;f=(a,a+1,a+cols+1,a+cols);faces += [f,tuple(size+x for x in reversed(f))]
    edge=list(range(cols))+[j*cols+cols-1 for j in range(1,rows)]+list(reversed(range((rows-1)*cols,(rows-1)*cols+cols-1)))+[j*cols for j in reversed(range(1,rows-1))]
    faces += [(a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1])]
    return mesh(name,verts,faces,mat)


def build_construction(m):
    count=24
    paths=[([square(i*math.tau/96,z) for i in range(96)],True,(0,0,1)) for z in HEIGHTS]
    tubes('Space Dock construction horizontal frames',paths,.012,m['frame'])
    heights=sorted(set(round(z,8) for z in [PROFILE[0][0]+j*(PROFILE[-1][0]-PROFILE[0][0])/100 for j in range(101)]+[z for z,_ in PROFILE]))
    assert min(b-a for a,b in zip(heights,heights[1:]))>1e-6,'Near-coincident scaffold rings'
    tubes('Space Dock construction longitudinal girders',[([square(i*math.tau/count,z) for z in heights],False,(0,0,1)) for i in range(count)],.014,m['frame'])
    diagonals=[]
    for j,(a,b) in enumerate(zip(HEIGHTS,HEIGHTS[1:])):
        for i in range(count):
            p,q=(i,i+1) if (i+j)%2 else (i+1,i)
            diagonals.append(([square(p*math.tau/count,a),square(q*math.tau/count,b)],False,(0,0,1)))
    tubes('Space Dock construction diagonal lattice',diagonals,.009,m['frame'])
    stays=[]
    for z in [-1.10,.55]:
        for i in range(8):
            phi=i*math.tau/8;p=square(phi,z)*.50;p.z=z
            stays.append(([p,square(phi,z)],False,(0,0,1)))
    tubes('Space Dock construction body support stays',stays,.024,m['frame'])
    for i in range(12):
        low,high=(-1.82,-1.10) if i%2 else (.16,.70)
        scaffold_cover(f'Space Dock temporary shield {i}',low,high,i*math.tau/12,(i+1)*math.tau/12,m['cover'])
    root=bpy.data.objects['PlacementRoot'];actor=bpy.data.objects.new('ConstructionWorkCarriage',None);bpy.context.collection.objects.link(actor);actor.parent=root
    actor.location=square(-math.pi/2,-.38)
    for suffix,position,size,style in [('rail clamp',(0,0,0),(.18,.10,.07),'hull'),('service case',(0,-.03,.08),(.18,.13,.10),'frame'),('amber marker',(0,-.10,.08),(.08,.018,.035),'marker')]:
        obj=box('Space Dock construction carriage '+suffix,position,size,m[style],.004);obj.parent=actor
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=181;scene.render.fps=30
    for frame,x in [(1,0),(61,.14),(121,-.14),(181,0)]:actor.location.x=x;actor.keyframe_insert(data_path='location',index=0,frame=frame)
    action=actor.animation_data.action;action.name='ConstructionActivity';track=actor.animation_data.nla_tracks.new();track.name='ConstructionActivity';track.strips.new('ConstructionActivity',1,action);actor.animation_data.action=None
    scene.frame_set(1);return [],[]


def frame_view(variant,view):
    camera=bpy.context.scene.camera;direction=Vector(VIEWS[view]).normalized()
    points=[o.matrix_world@v.co for o in meshes() for v in o.data.vertices]
    if view=='equipment-detail':centre=Vector((0,-1.05,-.52));scale=1.65
    else:centre=Vector([(min(p[i] for p in points)+max(p[i] for p in points))/2 for i in range(3)]);scale=None
    camera.location=centre+direction*15;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';bpy.context.view_layer.update()
    local=[camera.matrix_world.inverted()@p for p in points]
    camera.data.ortho_scale=scale or max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.16


def preview():
    import render_gallery_animations as renderer
    sys.path.insert(0,str(ROOT/'tools'));from gallery_animation_assets import glb_clips
    output,media=folders('construction');meta=json.loads((output/'model.json').read_text());study=dict(stage=meta['stage'],blend=(output/'model.blend').relative_to(ROOT).as_posix(),glb=(output/'model.glb').relative_to(ROOT).as_posix(),image=(media/'front-quarter.png').relative_to(ROOT).as_posix())
    clips=glb_clips(output/'model.glb');assert len(clips)==1 and clips[0]['name']=='ConstructionActivity'
    result=[renderer.render_clip(dict(id=meta['id']),study,clip,shutil.which('ffmpeg')) for clip in clips]
    (media/'animation-previews.json').write_text(json.dumps(dict(id=meta['id'],stage=meta['stage'],glb=study['glb'],glb_sha256=sha(output/'model.glb'),blend_sha256=sha(output/'model.blend'),renderer_sha256=sha(Path(renderer.__file__)),blender=bpy.app.version_string,clips=result),indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--variant',choices=['finished','construction'],default='finished');parser.add_argument('--preview-only',action='store_true');args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    if args.preview_only:preview();return
    variant=args.variant;output,media=folders(variant);output.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    source=INITIAL if variant=='finished' else folders('finished')[0]/'model.blend';source_meta=json.loads(source.with_suffix('.json').read_text());assert sha(source)==source_meta['blend_sha256'];assert sha(source.with_suffix('.glb'))==source_meta['glb_sha256']
    bpy.ops.wm.open_mainfile(filepath=str(source));scene=bpy.context.scene;root=bpy.data.objects['PlacementRoot'];original={o.name for o in meshes()}
    authored.TEXTURES=ROOT/'sources/materials/reconstruction'/('orbital-station-refined' if variant=='finished' else 'orbital-station-construction')/'terran/space-dock'
    specs=[('hull',(.16,.17,.20),.65),('frame',(.40,.43,.45),.72),('recess',(.022,.025,.030),.35),('red',(.43,.035,.025),.45),('cover',(.22,.25,.27),.25),('marker',(.65,.20,.02),.25)]
    m={}
    for style,colour,metal in specs:
        m[style]=authored.worn_material(style,colour,metal);m[style].name='Space Dock '+variant+' | '+style
    removed,attachments=(build_finished(m) if variant=='finished' else build_construction(m));added=[o for o in meshes() if o.name not in original]
    for obj in added:
        if obj.parent is None:obj.parent=root
        bpy.context.view_layer.objects.active=obj;bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        for mod in list(obj.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        uv(obj);mod=obj.modifiers.new('Explicit portable tessellation','TRIANGULATE');mod.keep_custom_normals=True;bpy.ops.object.modifier_apply(modifier=mod.name)
    for c in bpy.data.collections:
        if c.asset_data:c.asset_clear()
    collection=bpy.data.collections.new('Space Dock refined '+variant);scene.collection.children.link(collection);bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    for obj in [o for o in scene.objects if o.type in ['MESH','EMPTY']]:
        collection.objects.link(obj)
        for previous in list(obj.users_collection):
            if previous!=collection:previous.objects.unlink(obj)
    collection.asset_mark();collection.asset_data.description='PS7C descriptor '+str(int(variant=='construction'))+' refined '+variant+' state'
    root['variant']=variant;root['legacy_sprite_frame']=int(variant=='construction')
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.frame_set(1)
    for view in VIEWS:frame_view(variant,view);scene.render.filepath=str(media/(view+'.png'));bpy.ops.render.render(write_still=True)
    if variant=='construction':scene.frame_set(61);frame_view(variant,'equipment-detail');scene.render.filepath=str(media/'equipment-detail-moved.png');bpy.ops.render.render(write_still=True)
    scene.frame_set(1);frame_view(variant,'front-quarter');bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root;bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_extras=True,export_animations=variant=='construction',export_animation_mode='NLA_TRACKS',export_frame_range=True)
    bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    deps=['build_skymech_construction.py','refine_braccatian_pithoi.py','build_openfa_assets.py','refine_rigellian_crowns.py','refine_rigellian_extractor.py','refine_rigellian_missiles.py','space_dock_parts.py','manufactured_vessels.py']
    meta=dict(issue=192,id='openfa:space-dock',name='Space Dock',culture='terran',variant=variant,legacy_sprite_frame=int(variant=='construction'),stage='orbital-station-structural-refinement' if variant=='finished' else 'orbital-station-construction-refinement',source_study=source.relative_to(ROOT).as_posix(),source_blend_sha256=sha(source),source_glb_sha256=sha(source.with_suffix('.glb')),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),generator_sha256=sha(Path(__file__)),dependency_sha256={n:sha(Path(__file__).with_name(n)) for n in deps},texture_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(authored.TEXTURES.glob('*.png'))},evidence_sha256=sha(EVIDENCE),preserved_mesh_names=sorted(original-set(removed)),removed_mesh_names=removed,added_mesh_names=[o.name for o in added],attachments=[dict(name=n,owner=o) for n,o in attachments],mesh_objects=len(meshes()),blender=bpy.app.version_string,authored='Hidden symmetry, member layout and six-second service motion; no original timing claimed',acceptance='Independent runtime verification pending; game calibration remains open')
    (output/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('SPACE_DOCK_STATE_BUILT',variant,len(meshes()),len(added),flush=True)


if __name__=='__main__':main()
