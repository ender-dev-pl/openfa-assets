"""Render the two canonical RI18 clips with measured Blender NLA time offsets."""
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import bpy

sys.path.insert(0, str(Path(__file__).parent))
from remaster_rigellian_launcher import ROOT, FOLDER, MEDIA, TARGETS, sha, select_clip
from rigellian_shaft_preview import asset_meshes, surface_points
from catalogue_rendering import fit_camera
sys.path.insert(0, str(ROOT / 'tools'))
from gallery_animation_assets import glb_clips


def main():
    ffmpeg = shutil.which('ffmpeg')
    assert ffmpeg
    clips = glb_clips(FOLDER / 'model.glb')
    previews = []
    frames_root = ROOT / 'artifacts/ri18-canonical-animation-frames'
    frames_root.mkdir(parents=True, exist_ok=True)
    for clip in clips:
        bpy.ops.wm.open_mainfile(filepath=str(FOLDER / 'model.blend'), load_ui=False, use_scripts=False)
        scene = bpy.context.scene
        for obj in list(scene.objects):
            if obj.type not in ['CAMERA', 'LIGHT']:
                bpy.data.objects.remove(obj, do_unlink=True)
        for material in list(bpy.data.materials):
            bpy.data.materials.remove(material, do_unlink=True)
        bpy.ops.import_scene.gltf(filepath=str(FOLDER / 'model.glb'))
        meshes = asset_meshes(scene)
        offsets = []
        for name in TARGETS:
            strip = bpy.data.objects[name].animation_data.nla_tracks[clip['name']].strips[0]
            offsets.append(strip.action_frame_start-strip.frame_start)
        assert max(offsets)-min(offsets) < 1e-5
        offset = offsets[0]
        count = 61 if clip['index'] == 0 else 16
        fps = json.loads((FOLDER / 'model.json').read_bytes())['animation']['fps']
        scene.render.resolution_x = scene.render.resolution_y = 384
        scene.render.resolution_percentage = 100
        scene.cycles.samples = 12
        scene.render.image_settings.color_mode = 'RGB'
        scene.render.film_transparent = False
        points = []
        times = [clip['start']+clip['duration']*i/(count-1) for i in range(count)]
        for seconds in [times[0], times[-1], (times[0]+times[-1])/2]:
            select_clip(clip['name'], max(1, round(seconds*fps-offset)))
            points.extend(surface_points(meshes))
        fit_camera(scene, points, (0, -16, 7))
        frames = frames_root / f'clip-{clip["index"]}'
        frames.mkdir(exist_ok=True)
        assert frames.resolve().is_relative_to(frames_root.resolve())
        poses = set()
        created = []
        for index, seconds in enumerate(times):
            value = seconds*fps-offset
            # Binary float times may be infinitesimally below an integer STEP.
            if abs(value-round(value)) < 1e-4:
                value = round(value)
            select_clip(clip['name'], math.floor(value))
            scene.frame_set(math.floor(value), subframe=value-math.floor(value))
            bpy.context.view_layer.update()
            poses.add(tuple(round(v,5) for obj in meshes for row in obj.matrix_world for v in row))
            target = frames / f'{index:04}.png'
            scene.render.filepath = str(target)
            bpy.ops.render.render(write_still=True)
            created.append(target)
        assert len(poses) > 1
        output = MEDIA / f'animation-{clip["index"]:02}.webm'
        subprocess.run([ffmpeg, '-hide_banner', '-loglevel', 'error', '-y', '-framerate', str(count/clip['duration']),
                        '-i', str(frames/'%04d.png'), '-frames:v', str(count), '-c:v', 'libvpx-vp9', '-crf', '30',
                        '-b:v', '0', '-threads', '2', '-pix_fmt', 'yuv420p', '-an', str(output)], check=True)
        previews.append(dict(**clip, video=output.relative_to(ROOT).as_posix(), sha256=sha(output),
                             frames=count, fps=count/clip['duration'], distinct_pose_count=len(poses)))
        for target in created:
            assert target.resolve().parent == frames.resolve()
            target.unlink()
        frames.rmdir()
    frames_root.rmdir()
    manifest = dict(id='openfa:building/legacy/057', stage='canonical-game-remaster',
                    glb=(FOLDER/'model.glb').relative_to(ROOT).as_posix(), glb_sha256=sha(FOLDER/'model.glb'),
                    blend_sha256=sha(FOLDER/'model.blend'), renderer=Path(__file__).relative_to(ROOT).as_posix(),
                    renderer_sha256=sha(Path(__file__)), blender=bpy.app.version_string, clips=previews)
    (MEDIA/'animation-previews.json').write_bytes((json.dumps(manifest, indent=2)+'\n').encode())
    print('RI18_CANONICAL_GALLERY_ANIMATIONS_VERIFIED', len(previews), flush=True)


if __name__ == '__main__':
    main()
