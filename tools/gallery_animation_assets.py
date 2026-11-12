"""Read authored GLB clips and verify source-bound offline gallery previews."""
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def glb_clips(path):
    with path.open('rb') as stream:
        magic,version,total=struct.unpack('<4sII',stream.read(12))
        assert magic==b'glTF' and version==2, str(path)
        size,kind=struct.unpack('<II',stream.read(8));assert kind==0x4e4f534a
        data=json.loads(stream.read(size))
    clips=[]
    for index,animation in enumerate(data.get('animations',[])):
        accessors=[data['accessors'][sampler['input']] for sampler in animation['samplers']]
        first=min(a['min'][0] for a in accessors);last=max(a['max'][0] for a in accessors)
        assert last>first,(path,index,'Empty authored clip')
        clips.append(dict(index=index,name=animation.get('name',f'Clip {index+1}'),start=first,end=last,duration=last-first))
    return clips


def animation_previews(blend,glb,media):
    clips=glb_clips(ROOT/glb)
    if not clips:return []
    path=media/'animation-previews.json'
    assert path.is_file(),f'Render missing animation previews for {glb}'
    manifest=json.loads(path.read_text())
    assert manifest['glb_sha256']==sha(ROOT/glb),f'Stale GLB animation preview: {glb}'
    assert manifest['blend_sha256']==sha(ROOT/blend),f'Stale animation lighting/framing source: {blend}'
    renderer = (ROOT / manifest.get('renderer', 'sources/tools/blender/render_gallery_animations.py')).resolve()
    assert renderer.is_relative_to((ROOT/'sources/tools/blender').resolve()) and renderer.suffix == '.py'
    assert manifest['renderer_sha256']==sha(renderer),f'Stale animation renderer: {glb}'
    assert len(manifest['clips'])==len(clips),(glb,'Missing preview clips')
    result=[]
    for actual,preview in zip(clips,manifest['clips']):
        assert all(actual[key]==preview[key] for key in actual),(glb,'Clip metadata differs')
        video=ROOT/preview['video']
        assert video.resolve().is_relative_to((ROOT/'gallery/media').resolve())
        assert video.is_file() and sha(video)==preview['sha256'],(glb,'Missing or changed preview video')
        assert preview['distinct_pose_count']>1,(glb,'Imported clip was not moving')
        result.append(preview)
    return result
