"""Render the actual imported six-second construction clip with the gallery renderer."""
import argparse
import json
from pathlib import Path
import shutil
import sys

import bpy


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root = args.root.resolve()
    sys.path.insert(0, str(root/'sources/tools/blender'))
    import render_gallery_animations as renderer
    sys.path.insert(0, str(root/'tools'))
    from gallery_animation_assets import glb_clips, sha
    source = root/'sources/objects/terran/space-dock/construction'
    media = root/'gallery/media/objects/terran/space-dock/construction'
    study = dict(blend=(source/'model.blend').relative_to(root).as_posix(),
                 glb=(source/'model.glb').relative_to(root).as_posix(),
                 image=(media/'front-quarter.png').relative_to(root).as_posix())
    clips = glb_clips(source/'model.glb')
    assert len(clips) == 1 and clips[0]['name'] == 'ConstructionActivity'
    previews = [renderer.render_clip(dict(id='openfa:space-dock'), study, clip, shutil.which('ffmpeg')) for clip in clips]
    manifest = dict(id='openfa:space-dock', stage='ps7c-detailed-construction', glb=study['glb'],
                    glb_sha256=sha(source/'model.glb'), blend_sha256=sha(source/'model.blend'),
                    renderer_sha256=sha(Path(renderer.__file__)), blender=bpy.app.version_string, clips=previews)
    (media/'animation-previews.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('PS7C_ACTIVITY_PREVIEW_OK', flush=True)


if __name__ == '__main__':
    main()
