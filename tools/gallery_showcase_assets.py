# SPDX-License-Identifier: MIT
"""Verify multi-asset offline showcase provenance before adding gallery players."""
import json
from pathlib import Path
from gallery_animation_assets import sha

ROOT=Path(__file__).resolve().parents[1]


def showcase_previews(study):
    path=study.get('showcase')
    if not path:return []
    manifest_path=(ROOT/path).resolve()
    assert manifest_path.is_relative_to(ROOT/'sources') and manifest_path.is_file(),path
    data=json.loads(manifest_path.read_text(encoding='utf-8'))
    assert data['inputs'],'Showcase must identify its actual model inputs'
    for relative,digest in data['inputs'].items():
        source=(ROOT/relative).resolve()
        assert source.is_relative_to(ROOT/'sources') and sha(source)==digest,relative
    for clip in data['clips']:
        video=(ROOT/clip['video']).resolve()
        assert video.is_relative_to(ROOT/'gallery/media') and sha(video)==clip['sha256'],clip['video']
        assert clip['frames']>1 and clip['distinct_pose_count']>1
    for download in data.get('downloads',{}).values():
        path=(ROOT/download['path']).resolve()
        assert path.is_relative_to(ROOT/'gallery/media') and sha(path)==download['sha256'],download['path']
    return data['clips']
