"""Verify actual saved sources/independent exports and stream the imported clip.

Animation frames use one overwritten PNG and an ffmpeg pipe, no frame archive.
"""
from pathlib import Path
import json
import hashlib
import math
import subprocess
import shutil
import sys
import os
import bpy
import bmesh
from mathutils import Vector
from mathutils.kdtree import KDTree

sys.path.insert(0,str(Path(__file__).parent))
import author_extension_missiles as author
sys.path.insert(0,str(author.ROOT/'tools'))
from publication_support import clean_png
from gallery_animation_assets import glb_clips

TASK=Path(os.environ.get('OPENFA_MISSILE_VERIFICATION_ARTIFACTS',str(author.ROOT/'artifacts/extension-missile-models'))).resolve()


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot():
    bpy.context.view_layer.update()
    return {o.name:[o.matrix_world@v.co for v in o.data.vertices] for o in bpy.context.scene.objects if o.type=='MESH'}


def compare(a,b):
    assert a.keys()==b.keys(),(a.keys(),b.keys());error=0
    for name in a:
        for first,second in [(a[name],b[name]),(b[name],a[name])]:
            tree=KDTree(len(first))
            for i,p in enumerate(first):tree.insert(p,i)
            tree.balance();error=max(error,max(tree.find(p)[2] for p in second))
    assert error<1e-4,error
    return error


def remove_models():
    for o in list(bpy.context.scene.objects):
        if o.type in {'MESH','EMPTY'}:bpy.data.objects.remove(o,do_unlink=True)
    for collection in [bpy.data.meshes,bpy.data.materials,bpy.data.images,bpy.data.actions]:
        for item in list(collection):
            if item.users==0:collection.remove(item)


def check_scene(expected,decoy=False):
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==expected
    images=[i for i in bpy.data.images if i.type=='IMAGE'];assert len(images)==2 and all(i.packed_file and tuple(i.size)==(1024,1024) for i in images)
    for mesh in {o.data for o in meshes}:
        assert mesh.uv_layers and len(mesh.materials)==1
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold for e in bm.edges),'open mesh edges'
        assert bm.calc_volume()>0,'nonpositive volume';bm.free()
    if decoy:
        assert len({o.data for o in meshes})==1,'segment instances must share one mesh'
        for i in range(4):assert bpy.data.objects.get('DecoySegment'+str(i))
    return sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)


def separation_samples():
    results={}
    for frame,spread in [(0,.57),(15,.57),(90,1.85),(120,1.85),(180,.57)]:
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        roots=[bpy.data.objects['DecoySegment'+str(i)] for i in range(4)]
        for o in roots:assert abs(abs(o.matrix_world.translation.x)-spread)<1e-4 and abs(abs(o.matrix_world.translation.z)-spread)<1e-4
        results[str(frame)]=[list(o.matrix_world.translation) for o in roots]
    # Across the sampled motion, neighbouring projectile AABBs cannot overlap.
    for frame in range(0,181,3):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        bounds=[]
        for o in meshes:
            pts=[o.matrix_world@Vector(p) for p in o.bound_box]
            bounds.append([(min(p[a] for p in pts),max(p[a] for p in pts)) for a in range(3)])
        for i,a in enumerate(bounds):
            for b in bounds[i+1:]:assert any(a[k][1]<=b[k][0]+1e-4 or b[k][1]<=a[k][0]+1e-4 for k in range(3)),('segment collision',frame)
    bpy.context.scene.frame_set(0);return results


def render_pose(media,name,frame=0,front=False):
    scene=bpy.context.scene;scene.frame_set(frame);author.aim(scene,front,wide=frame>0)
    scene.render.filepath=str(media/(name+'.png'));bpy.ops.render.render(write_still=True)


def animation_video(media):
    scene=bpy.context.scene;scene.render.resolution_x=scene.render.resolution_y=512;scene.cycles.samples=8;scene.render.film_transparent=False
    scene.render.image_settings.color_mode='RGB';author.aim(scene,wide=True)
    video=media/'separation.webm';temporary=TASK/'animation-frame.png';ffmpeg=shutil.which('ffmpeg');assert ffmpeg
    command=[ffmpeg,'-hide_banner','-loglevel','error','-y','-f','image2pipe','-vcodec','png','-r','24','-i','pipe:0','-c:v','libvpx-vp9','-crf','25','-b:v','0','-threads','2','-pix_fmt','yuv420p','-an',str(video)]
    process=subprocess.Popen(command,stdin=subprocess.PIPE);poses=set()
    try:
        for i in range(144):
            frame=180*i/143;scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame))
            poses.add(tuple(round(v,5) for k in range(4) for v in bpy.data.objects['DecoySegment'+str(k)].matrix_world.translation))
            scene.render.filepath=str(temporary);bpy.ops.render.render(write_still=True);process.stdin.write(temporary.read_bytes())
            if i%24==0:print('DECOY_IMPORTED_ANIMATION_FRAME',i,flush=True)
        process.stdin.close();assert process.wait()==0
    finally:
        if process.poll() is None:process.kill();process.wait()
    assert len(poses)>100
    return dict(video=video.relative_to(author.ROOT).as_posix(),sha256=sha(video),fps=24,frames=144,seconds=6,distinct_pose_count=len(poses),source='actual independently imported GLB animation')


def main():
    TASK.mkdir(exist_ok=True);reports=[]
    for name in ['interceptor','decoy']:
        out=author.OUT/name;media=author.MEDIA/name;before={p.name:sha(p) for p in out.glob('*.glb')};before['model.blend']=sha(out/'model.blend')
        bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(0)
        native_count=check_scene(4 if name=='decoy' else 1,name=='decoy');native={}
        frames=[0,15,45,90,120,150,180] if name=='decoy' else [0]
        for f in frames:scene.frame_set(f);native[f]=snapshot()
        native_motion=separation_samples() if name=='decoy' else None
        render_pose(media,'verified-native');remove_models();bpy.ops.import_scene.gltf(filepath=str(out/'model.glb'))
        imported_count=check_scene(4 if name=='decoy' else 1,name=='decoy');assert native_count==imported_count
        errors={}
        for f in frames:scene.frame_set(f);errors[str(f)]=compare(native[f],snapshot())
        imported_motion=separation_samples() if name=='decoy' else None
        scene.frame_set(0);points=[p for row in snapshot().values() for p in row]
        bounds=[[min(p[a] for p in points),max(p[a] for p in points)] for a in range(3)]
        assert bounds[1][1]-bounds[1][0]>9 and bounds[1][1]-bounds[1][0]>3*(bounds[0][1]-bounds[0][0])
        render_pose(media,'verified-imported');render_pose(media,'verified-front',front=True)
        report=dict(id='openfa:missile/'+name,blender=bpy.app.version_string,binaries=before,triangles=imported_count,mesh_instances=4 if name=='decoy' else 1,
            unique_meshes=1,materials=1,packed_maps=2,native_bounds=bounds,native_forward='-Y',native_up='+Z',glb_forward='-Z',glb_up='+Y',
            position_errors=errors,native_motion=native_motion,imported_motion=imported_motion,verifier_sha256=sha(Path(__file__)),generator_sha256=sha(Path(author.__file__)),
            scope='Blender asset runtime; client/Android integration and GPU acceptance separate')
        if name=='decoy':
            assert len(glb_clips(out/'model.glb'))==1 and glb_clips(out/'model.glb')[0]['name']=='DecoyMenuSeparation'
            render_pose(media,'separated',90);report['animation_preview']=animation_video(media)
            remove_models();bpy.ops.import_scene.gltf(filepath=str(out/'segment.glb'));check_scene(1)
            only=next(iter(snapshot().values()));reference=native[0]['DecoySegmentMesh'];offset=Vector((-.57,0,-.57))
            compare({'segment':[p-offset for p in reference]},{'segment':only});report['segment_triangles']=imported_count//4
            scene.render.resolution_x=700;scene.render.resolution_y=900;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
            render_pose(media,'segment')
        for p in media.glob('*.png'):p.write_bytes(clean_png(p.read_bytes()))
        assert before=={p:sha(out/p) for p in before}
        report['renders']={p.name:sha(p) for p in media.glob('*.png')}
        (out/'runtime-verification.json').write_text(json.dumps(report,indent=2)+'\n');reports.append(report)
    print('EXTENSION_MODELS_VERIFIED',json.dumps(reports),flush=True)


if __name__=='__main__':main()
