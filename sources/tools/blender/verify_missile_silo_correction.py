"""Source/import mechanics, full-bore/Decoy fit, lamp presets and streamed preview."""
from pathlib import Path
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import bpy
from mathutils import Vector,Quaternion
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree

sys.path.insert(0,str(Path(__file__).parent))
import correct_missile_silo as author
sys.path.insert(0,str(author.ROOT/'tools'))
from publication_support import clean_png
from gallery_animation_assets import glb_clips

TASK=Path(os.environ.get('OPENFA_SILO_VERIFICATION_ARTIFACTS',str(author.ROOT/'artifacts/missile-silo-aperture-lights'))).resolve()
IMPORTED=False


def phase(frame):
    value=frame-(1 if IMPORTED else 0)
    bpy.context.scene.frame_set(math.floor(value),subframe=value-math.floor(value))


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def geometry():
    bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();rows={}
    for o in bpy.context.scene.objects:
        if o.type!='MESH' or o.get('preview_only'):continue
        eo=o.evaluated_get(deps);mesh=eo.to_mesh();rows[o.name]=dict(points=[o.matrix_world@v.co for v in mesh.vertices],faces=[tuple(p.vertices) for p in mesh.polygons]);eo.to_mesh_clear()
    return rows


def compare(a,b):
    assert a.keys()==b.keys(),(a.keys()-b.keys(),b.keys()-a.keys());error=0;details={}
    for name in a:
        for first,second in [(a[name]['points'],b[name]['points']),(b[name]['points'],a[name]['points'])]:
            tree=KDTree(len(first))
            for i,p in enumerate(first):tree.insert(p,i)
            tree.balance();distance=max(tree.find(p)[2] for p in second);error=max(error,distance);details[name]=max(details.get(name,0),distance)
    assert error<1e-4,(error,{n:e for n,e in details.items() if e>1e-4});return error


def fixed_clearance():
    # Deliberate iris leaf laps are excluded; this tests moving vs fixed structures.
    checks=0
    for f in range(1,34):
        phase(f);rows=geometry();trees={n:BVHTree.FromPolygons(r['points'],r['faces']) for n,r in rows.items()}
        leaves=[n for n in trees if n.startswith('Iris curved leaf')];assert len(leaves)==16
        for leaf in leaves:
            for name in trees:
                if name in leaves:continue
                overlap=trees[leaf].overlap(trees[name]);assert not overlap,(f,leaf,name,len(overlap));checks+=1
    return dict(frames=33,moving_vs_fixed_tests=checks,overlaps=0,leaf_laps='Thin overlapping iris sheets intentionally excluded from fixed-structure test')


def open_bore():
    scene=bpy.context.scene;phase(17);deps=bpy.context.evaluated_depsgraph_get();count=0
    for radii,stop in [([0,.2,.4,.6,.8,.82],-3.05),([.85,.87],0)]:
        for r in radii:
            for i in range(96):
                p=Vector((r*math.cos(math.tau*i/96),r*math.sin(math.tau*i/96),1.1))
                hit,*_=scene.ray_cast(deps,p,Vector((0,0,-1)),distance=1.1-stop)
                assert not hit,('launch bore blocked',r,i,stop);count+=1
    phase(1);deps=bpy.context.evaluated_depsgraph_get()
    for r in [.05,.3,.6,.84]:
        for i in range(16):
            p=Vector((r*math.cos(math.tau*i/16),r*math.sin(math.tau*i/16),1.1));hit,*_=scene.ray_cast(deps,p,Vector((0,0,-1)),distance=.7);assert hit,('closed iris gap',r,i)
    return dict(open_mouth_radius_tested=.87,continuous_shaft_radius_tested=.82,shaft_z_tested=[-3.05,1.1],empty_ray_samples=count,closed_cover_samples=64)


def view(direction=(3,-5,4)):
    scene=bpy.context.scene;cam=scene.camera;target=Vector((0,0,.30));cam.location=target+Vector(direction);cam.rotation_mode='QUATERNION';cam.rotation_quaternion=(-Vector(direction)).to_track_quat('-Z','Y')
    cam.data.type='ORTHO';cam.data.ortho_scale=3.6;scene.render.resolution_x=scene.render.resolution_y=512;scene.render.resolution_percentage=100;scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'


def ground_holdout():
    # Preview-only ground occlusion. Actual buried mechanism remains in the GLB.
    n=96;vs=[(r*math.cos(math.tau*i/n),r*math.sin(math.tau*i/n),0) for r in [.885,20] for i in range(n)]
    mesh=bpy.data.meshes.new('Preview ground cut');mesh.from_pydata(vs,[],[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]);mesh.update()
    mat=bpy.data.materials.new('Preview ground holdout');mat.use_nodes=True;t=mat.node_tree;t.nodes.clear();hold=t.nodes.new('ShaderNodeHoldout');out=t.nodes.new('ShaderNodeOutputMaterial');t.links.new(hold.outputs[0],out.inputs[0]);mesh.materials.append(mat)
    o=bpy.data.objects.new('Preview ground cut',mesh);bpy.context.collection.objects.link(o);o['preview_only']=True


def render(name,frame=17,direction=(3,-5,4)):
    phase(frame);view(direction);bpy.context.scene.render.filepath=str(author.MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)


def remove_models():
    for o in list(bpy.context.scene.objects):
        if o.type in {'MESH','EMPTY'} and not o.get('preview_only'):bpy.data.objects.remove(o,do_unlink=True)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images,bpy.data.actions]:
        for item in list(collection):
            if item.users==0:collection.remove(item)


def decoy_fixture():
    scene=bpy.context.scene;phase_sources=[]
    for f in range(1,34):phase(f);phase_sources.append(geometry())
    phase(17);source=geometry();trees=[BVHTree.FromPolygons(r['points'],r['faces']) for n,r in source.items()]
    points=[p for row in source.values() for p in row['points']];xy=[max(p[a] for p in points)-min(p[a] for p in points) for a in [0,1]]
    before=set(scene.objects);path=author.ROOT/'sources/objects/extensions/munitions/decoy/model.glb';bpy.ops.import_scene.gltf(filepath=str(path));new=set(scene.objects)-before
    for o in new:
        if o.animation_data:o.animation_data_clear()
    root=bpy.data.objects['PlacementRoot'];root.rotation_mode='XYZ';root.rotation_euler=(0,0,0)
    for i,(x,z) in enumerate([(-.57,-.57),(-.57,.57),(.57,-.57),(.57,.57)]):bpy.data.objects['DecoySegment'+str(i)].location=(x,0,z)
    bpy.context.view_layer.update();missile=[o for o in new if o.type=='MESH'];p=[o.matrix_world@v.co for o in missile for v in o.data.vertices]
    length=max(v.y for v in p)-min(v.y for v in p);silo_scale=min(64/d for d in xy);factor=(48/length)/silo_scale;required=max(math.hypot(v.x,v.z) for v in p)*factor
    assert required<.82;root.scale=(factor,)*3;root.rotation_euler.x=-math.pi/2
    tests=0
    for tip in [-1.15,-.75,-.25,.25,.55,.75,1.0,1.4,1.8,2.2,2.8]:
        root.location.z=tip-(-min(v.y for v in p))*factor;bpy.context.view_layer.update()
        for o in missile:
            mesh=o.data;tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in mesh.vertices],[list(f.vertices) for f in mesh.polygons])
            for obstacle in trees:assert not tree.overlap(obstacle),('Decoy launch collision',tip,o.name);tests+=1
    # Loaded projectile waits below the closed iris until the iris is clear.
    root.location.z=-1.15-(-min(v.y for v in p))*factor;bpy.context.view_layer.update();loaded_tests=0
    for posed in phase_sources:
        obstacles=[BVHTree.FromPolygons(r['points'],r['faces']) for r in posed.values()]
        for o in missile:
            tree=BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(f.vertices) for f in o.data.polygons])
            for obstacle in obstacles:assert not tree.overlap(obstacle),'Loaded Decoy intersects iris blades';loaded_tests+=1
    root.location.z=1.8-(-min(v.y for v in p))*factor;bpy.context.view_layer.update()
    render('decoy-clearance',17)
    for o in new:bpy.data.objects.remove(o,do_unlink=True)
    return dict(decoy_glb_sha256=sha(path),world_size_proposal=48,building_footprint=[2,2],surface_cell_world_units=32,silo_world_fit_scale=silo_scale,relative_scale=factor,required_projectile_radius=required,usable_shaft_radius=.82,radial_margin=.82-required,launch_collision_tests=tests,loaded_payload_collision_tests=loaded_tests,loaded_payload_nose_z=-1.15,overlaps=0,orientation='Native-Y missile to native+Z launch axis by X-90deg; explicit proposed adapter',scope='Asset fixture using current source fitting formulas; loaded payload held below the closed iris before lift. Not a game-client runtime test')


def preview(clip):
    scene=bpy.context.scene;view();scene.render.film_transparent=False;scene.render.image_settings.color_mode='RGB';scene.cycles.samples=8
    # Omit the holdout for opaque video: a neutral visible ground annulus hides
    # the buried exterior while the bore remains visible, just as the surface.
    ground=next(o for o in scene.objects if o.get('preview_only'));mat=ground.data.materials[0];t=mat.node_tree;t.nodes.clear();b=t.nodes.new('ShaderNodeBsdfPrincipled');b.inputs['Base Color'].default_value=(.025,.03,.04,1);out=t.nodes.new('ShaderNodeOutputMaterial');t.links.new(b.outputs[0],out.inputs[0])
    command=[shutil.which('ffmpeg'),'-hide_banner','-loglevel','error','-y','-f','image2pipe','-vcodec','png','-r','24','-i','pipe:0','-c:v','libvpx-vp9','-crf','27','-b:v','0','-threads','2','-pix_fmt','yuv420p','-an',str(author.MEDIA/'animation-00.webm')]
    process=subprocess.Popen(command,stdin=subprocess.PIPE);poses=set();temp=TASK/'preview-frame.png'
    for i in range(48):
        f=1+32*i/47;phase(f);poses.add(tuple(round(v,5) for o in scene.objects if o.name.startswith('Iris curved leaf') for row in o.matrix_world for v in row))
        scene.render.filepath=str(temp);bpy.ops.render.render(write_still=True);process.stdin.write(temp.read_bytes())
    process.stdin.close();assert process.wait()==0 and len(poses)>20
    return dict(**clip,video=(author.MEDIA/'animation-00.webm').relative_to(author.ROOT).as_posix(),sha256=sha(author.MEDIA/'animation-00.webm'),frames=48,fps=24,distinct_pose_count=len(poses))


def main():
    global IMPORTED
    TASK.mkdir(parents=True,exist_ok=True);before={k:sha(author.OUT/('model.'+k)) for k in ['blend','glb']};scene=bpy.context.scene
    bpy.ops.wm.open_mainfile(filepath=str(author.OUT/'model.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
    frames=[1,5,9,13,17,25,33];native={}
    for f in frames:phase(f);native[f]=geometry()
    native_fixed=fixed_clearance();native_bore=open_bore();ground_holdout();render('verified-native')
    remove_models();bpy.ops.import_scene.gltf(filepath=str(author.OUT/'model.glb'));scene.render.fps=16;IMPORTED=True
    errors={}
    for f in frames:phase(f);errors[str(f)]=compare(native[f],geometry())
    imported_fixed=fixed_clearance();imported_bore=open_bore()
    assert bpy.data.objects['SiloPlacementRoot']['preserve_ground_origin']
    render('verified-imported');render('front-quarter');render('rear-quarter',17,(-3,5,4));render('top',17,(0,.001,6));render('closed',1)
    lamp_views=[]
    for mode in author.COLOURS:
        author.set_lamps(mode);render('lamps-'+mode);lamp_views.append('lamps-'+mode+'.png')
    for label,l,r in [('off',False,False),('left',True,False),('right',False,True)]:
        author.set_lamps('Hybrid',l,r);render('lamps-'+label);lamp_views.append('lamps-'+label+'.png')
    author.set_lamps();fixture=decoy_fixture()
    clips=glb_clips(author.OUT/'model.glb');assert len(clips)==1 and clips[0]['name']=='Animation' and abs(clips[0]['duration']-2)<1e-5 and clips[0]['start']==0
    # Refresh the existing first-half still sequence/GIF from the actual GLB.
    (author.MEDIA/'iris').mkdir(exist_ok=True)
    for i in range(17):render('iris/'+f'{i:02}',i+1)
    animation=preview(clips[0])
    for p in author.MEDIA.rglob('*.png'):p.write_bytes(clean_png(p.read_bytes()))
    manifest=dict(id='terran:missile-silo',stage='refined-study',glb=(author.OUT/'model.glb').relative_to(author.ROOT).as_posix(),glb_sha256=before['glb'],blend_sha256=before['blend'],renderer_path=Path(__file__).relative_to(author.ROOT).as_posix(),renderer_sha256=sha(Path(__file__)),blender=bpy.app.version_string,clips=[animation]);(author.MEDIA/'animation-previews.json').write_text(json.dumps(manifest,indent=2)+'\n')
    report=dict(id='terran:missile-silo',blender=bpy.app.version_string,binaries=before,patcher_sha256=sha(Path(author.__file__)),verifier_sha256=sha(Path(__file__)),position_errors=errors,native_fixed_clearance=native_fixed,imported_fixed_clearance=imported_fixed,native_bore=native_bore,imported_bore=imported_bore,decoy_fixture=fixture,clip=animation,lamp_views=lamp_views,lamp_control='Two channels, three fixed colour presets each, zero/unit node scales; no invented blink timeline',renders={p.relative_to(author.MEDIA).as_posix():sha(p) for p in author.MEDIA.rglob('*.png')},scope='Saved-source and imported asset runtime. Planar diaphragm mechanics are authored; actual game/Android and final visual acceptance separate')
    assert before=={k:sha(author.OUT/('model.'+k)) for k in before};(author.OUT/'correction-runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');print('SILO_CORRECTION_VERIFIED',json.dumps(report),flush=True)


if __name__=='__main__':main()
