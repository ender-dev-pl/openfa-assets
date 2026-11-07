# SPDX-License-Identifier: MIT
"""A showcase must fail closed when any source or video provenance is stale."""
import json
import unittest
from unittest.mock import patch
import gallery_showcase_assets as showcases


class ShowcaseTests(unittest.TestCase):
    def setUp(self):
        self.study={'showcase':'sources/objects/terran/ship-yard/hangar/showcase.json'}

    def test_unset_showcase_is_optional(self):
        self.assertEqual(showcases.showcase_previews({}),[])

    def test_current_actual_multimodel_showcase(self):
        clips=showcases.showcase_previews(self.study)
        self.assertEqual(len(clips),1)
        self.assertGreater(clips[0]['frames'],100)

    def test_stale_source_is_rejected(self):
        with patch.object(showcases,'sha',return_value='stale'):
            with self.assertRaises(AssertionError):showcases.showcase_previews(self.study)

    def test_paths_outside_sources_are_rejected(self):
        with self.assertRaises(AssertionError):showcases.showcase_previews({'showcase':'project/layout.json'})

    def test_stale_video_is_rejected(self):
        original=showcases.sha
        def digest(path):return 'stale' if path.suffix=='.webm' else original(path)
        with patch.object(showcases,'sha',side_effect=digest):
            with self.assertRaises(AssertionError):showcases.showcase_previews(self.study)

    def test_stale_mp4_download_is_rejected(self):
        original=showcases.sha
        def digest(path):return 'stale' if path.suffix=='.mp4' else original(path)
        study={'showcase':'sources/objects/terran/assault-fighter/construction/showcase.json'}
        with patch.object(showcases,'sha',side_effect=digest):
            with self.assertRaises(AssertionError):showcases.showcase_previews(study)


if __name__=='__main__':unittest.main()
