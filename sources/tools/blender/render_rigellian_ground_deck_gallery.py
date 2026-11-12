"""Render every authored GLB clip into a local playable WebM; never edit models."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import bpy
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from gallery_animation_assets import glb_clips,sha


def frame_at(seconds):
    frame=seconds*30
    bpy.context.scene.frame_set(math.floor(frame),subframe=frame-math.floor(frame))


def imported_objects():
    return [obj for obj in bpy.context.scene.objects if obj.type in ['MESH','EMPTY'] and not obj.get('preview_only')]


def render_clip(row,study,clip,ffmpeg):
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/study['blend']))
    scene=bpy.context.scene;scene.render.fps=30
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT'] and not obj.get('preview_only'):
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/study['glb']))
    # Blender's importer selects the first clip. When more clips are authored,
    # select their generated NLA tracks explicitly by the glTF clip name.
    if clip['index']:
        selected=0
        for obj in imported_objects():
            if not obj.animation_data:continue
            obj.animation_data.action=None
            for track in obj.animation_data.nla_tracks:
                track.mute=track.name!=clip['name']
                selected+=not track.mute
        assert selected,(study['glb'],clip['name'],'Could not select imported clip')
    count=max(2,round(clip['duration']*24))
    times=[clip['start']+clip['duration']*i/(count-1) for i in range(count)]
    points=[];poses=set();objects=imported_objects()
    underground=any(obj.get('preserve_ground_origin') for obj in objects)
    for seconds in times:
        frame_at(seconds);deps=bpy.context.evaluated_depsgraph_get()
        poses.add(tuple(round(v,5) for obj in objects for row in obj.matrix_world for v in row))
        for obj in objects:
            if obj.type!='MESH':continue
            evaluated=obj.evaluated_get(deps)
            points.extend(p for corner in evaluated.bound_box if (p:=evaluated.matrix_world@Vector(corner)).z>=(-.001 if underground else -1000))
    assert len(poses)>1,(study['glb'],'Imported clip remains static')
    camera=scene.camera;assert camera is not None,study['blend']
    low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)])
    centre=(low+high)/2;direction=Vector((6,-10,7)).normalized()
    camera.location=centre+direction*15;camera.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
    bpy.context.view_layer.update();local=[camera.matrix_world.inverted()@p for p in points]
    camera.data.type='ORTHO';camera.data.ortho_scale=max(max(p.x for p in local)-min(p.x for p in local),max(p.y for p in local)-min(p.y for p in local))*1.16
    scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True
    scene.render.resolution_x=scene.render.resolution_y=384;scene.render.resolution_percentage=100
    scene.render.film_transparent=False;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB'
    token=hashlib.sha256(study['glb'].encode()).hexdigest()[:12]
    frames=ROOT/f'artifacts/rigellian-final-audit-temp/ri10-frames-{token}-{clip["index"]:02}';frames.mkdir(parents=True,exist_ok=True)
    for index,seconds in enumerate(times):
        frame_at(seconds);scene.render.filepath=str(frames/f'{index:04}.png');bpy.ops.render.render(write_still=True)
    media=ROOT/study['image'];output=media.parent/f'animation-{clip["index"]:02}.webm'
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-y','-framerate',str(count/clip['duration']),'-i',str(frames/'%04d.png'),
        '-frames:v',str(count),'-c:v','libvpx-vp9','-crf','30','-b:v','0','-deadline','good','-cpu-used','4','-threads','2','-pix_fmt','yuv420p','-an',str(output)],check=True)
    print('GALLERY_ANIMATION_RENDERED',study['glb'],clip['name'],count,flush=True)
    return dict(**clip,video=output.relative_to(ROOT).as_posix(),sha256=sha(output),frames=count,fps=count/clip['duration'],distinct_pose_count=len(poses))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--worker-index',type=int,default=0);parser.add_argument('--workers',type=int,default=1)
    parser.add_argument('--limit',type=int);parser.add_argument('--ffmpeg',default=shutil.which('ffmpeg'));args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    assert args.ffmpeg,'ffmpeg is required'
    jobs=[]
    for row in json.loads((ROOT/'gallery/catalogue.json').read_text()):
        if row['id']!='openfa:building/legacy/049':continue
        for study in row['studies']:
            clips=glb_clips(ROOT/study['glb'])
            if clips:jobs.append((row,study,clips))
    for index,(row,study,clips) in enumerate(jobs):
        if index%args.workers!=args.worker_index:continue
        if args.limit is not None and index>=args.limit:continue
        path=(ROOT/study['image']).parent/'animation-previews.json'
        if path.exists():
            old=json.loads(path.read_text())
            if old['glb_sha256']==sha(ROOT/study['glb']) and old['blend_sha256']==sha(ROOT/study['blend']) and old['renderer_sha256']==sha(Path(__file__)) and all((ROOT/c['video']).is_file() and sha(ROOT/c['video'])==c['sha256'] for c in old['clips']):
                print('GALLERY_ANIMATION_CURRENT',study['glb'],flush=True);continue
        previews=[render_clip(row,study,clip,args.ffmpeg) for clip in clips]
        manifest=dict(renderer=Path(__file__).relative_to(ROOT).as_posix(),id=row['id'],stage=study['stage'],glb=study['glb'],glb_sha256=sha(ROOT/study['glb']),blend_sha256=sha(ROOT/study['blend']),renderer_sha256=sha(Path(__file__)),blender=bpy.app.version_string,clips=previews)
        path.write_text(json.dumps(manifest,indent=2)+'\n')


if __name__=='__main__':main()
