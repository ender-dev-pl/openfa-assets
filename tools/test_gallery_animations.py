"""Source/clip integrity contracts for offline playable gallery previews."""
import json
from pathlib import Path
import struct
import shutil
import uuid
import unittest
from unittest.mock import patch

import gallery_animation_assets as assets


class GalleryAnimationsTests(unittest.TestCase):
    def setUp(self):
        parent = Path(__file__).resolve().parents[1] / 'artifacts'
        self.root = parent / ('gallery-animation-test-' + uuid.uuid4().hex)
        assert self.root.resolve().is_relative_to(parent.resolve())
        self.root.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.root)
        self.patch=patch.object(assets,'ROOT',self.root);self.patch.start();self.addCleanup(self.patch.stop)
        self.blend=self.root/'sources/model.blend';self.blend.parent.mkdir();self.blend.write_bytes(b'editable native source')
        self.glb=self.root/'sources/model.glb';self.write_glb()
        self.renderer=self.root/'sources/tools/blender/render_gallery_animations.py';self.renderer.parent.mkdir(parents=True);self.renderer.write_text('renderer')
        self.media=self.root/'gallery/media/model';self.media.mkdir(parents=True)
        self.video=self.media/'animation-00.webm';self.video.write_bytes(b'encoded preview fixture')
        self.manifest=dict(glb_sha256=assets.sha(self.glb),blend_sha256=assets.sha(self.blend),renderer_sha256=assets.sha(self.renderer),
            clips=[dict(**assets.glb_clips(self.glb)[0],video='gallery/media/model/animation-00.webm',sha256=assets.sha(self.video),distinct_pose_count=20)])
        self.save()

    def write_glb(self,animated=True):
        data=dict(accessors=[dict(min=[.25],max=[2.25])])
        if animated:data['animations']=[dict(name='Launch',samplers=[dict(input=0)])]
        payload=json.dumps(data).encode();payload+=b' '*((-len(payload))%4)
        self.glb.write_bytes(struct.pack('<4sIIII',b'glTF',2,20+len(payload),len(payload),0x4e4f534a)+payload)

    def save(self):
        (self.media/'animation-previews.json').write_text(json.dumps(self.manifest))

    def previews(self):
        return assets.animation_previews('sources/model.blend','sources/model.glb',self.media)

    def test_authored_clip_timing_and_preview_are_preserved(self):
        clip=self.previews()[0]
        self.assertEqual(('Launch',.25,2.25,2),tuple(clip[k] for k in ['name','start','end','duration']))

    def test_changed_model_native_source_renderer_or_video_are_rejected(self):
        for path in [self.glb,self.blend,self.renderer,self.video]:
            with self.subTest(path=path):
                original=path.read_bytes();path.write_bytes(original+b' changed')
                with self.assertRaises(AssertionError):self.previews()
                path.write_bytes(original)

    def test_missing_or_mismatched_clips_are_rejected(self):
        self.manifest['clips']=[];self.save()
        with self.assertRaises(AssertionError):self.previews()
        self.manifest['clips']=[dict(index=0,name='Invented',start=0,end=2,duration=2)];self.save()
        with self.assertRaises(AssertionError):self.previews()

    def test_missing_video_and_static_imported_pose_are_rejected(self):
        self.manifest['clips'][0]['distinct_pose_count']=1;self.save()
        with self.assertRaises(AssertionError):self.previews()
        self.manifest['clips'][0]['distinct_pose_count']=20;self.save();self.video.unlink()
        with self.assertRaises(AssertionError):self.previews()

    def test_video_cannot_escape_gallery_media(self):
        self.manifest['clips'][0]['video']='sources/model.blend';self.save()
        with self.assertRaises(AssertionError):self.previews()

    def test_static_glb_does_not_gain_invented_animation(self):
        self.write_glb(animated=False)
        self.assertEqual([],self.previews())

    def test_bound_case_renderer_preserves_old_renderer_contract(self):
        custom = self.renderer.with_name('render_rigellian_ground_deck_animations.py')
        custom.write_text('case-specific NLA time mapping')
        self.manifest['renderer'] = custom.relative_to(self.root).as_posix()
        self.manifest['renderer_sha256'] = assets.sha(custom)
        self.save()
        self.assertEqual(len(self.previews()), 1)
        custom.write_text('changed mapping')
        with self.assertRaises(AssertionError):
            self.previews()
        self.manifest['renderer'] = 'sources/model.blend'
        self.save()
        with self.assertRaises(AssertionError):
            self.previews()


if __name__=='__main__':unittest.main()
