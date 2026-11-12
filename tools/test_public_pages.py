"""Verify that only clean generated site files enter the publication branch."""
from pathlib import Path
import subprocess
import unittest
from test_publication import fixture_directory
from publish_public_pages import prepare, validate
from build_public_pages import PAGES
import build_public_pages
from unittest.mock import patch
import tempfile
from PIL import Image


class PagesTests(unittest.TestCase):
    def site(self, root):
        for name in PAGES:
            (root / name).write_text('<!doctype html><title>OpenFA</title>')
        (root / '.nojekyll').write_text('')
        return root

    def test_private_text_and_raw_logs_are_rejected(self):
        with fixture_directory() as root:
            self.site(root)
            (root / 'private.log').write_text('raw log')
            with self.assertRaises(AssertionError):
                validate(root)

    def test_private_paths_are_rejected_even_in_html(self):
        with fixture_directory() as root:
            self.site(root)
            (root / 'index.html').write_text('C' + ':' + '/Us' + 'ers/private/model.blend')
            with self.assertRaises(ValueError):
                validate(root)

    def test_proposal_page_keeps_navigation_and_routes_downloads_to_repository(self):
        parent=Path(__file__).resolve().parents[1]/'artifacts';parent.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=parent,prefix='engineering-pages-test-') as temp:
            root=Path(temp).resolve();self.assertTrue(root.is_relative_to(parent.resolve()))
            (root/'gallery/media').mkdir(parents=True);(root/'sources/proposals').mkdir(parents=True)
            Image.new('RGB',(2,2),'blue').save(root/'gallery/media/concept.png')
            (root/'sources/proposals/model.glb').write_bytes(b'fixture-download-only')
            for name in PAGES:(root/'gallery'/name).write_text('<a href="engineering-proposals.html">Proposals</a>')
            (root/'gallery/engineering-proposals.html').write_text('<a href="index.html">Catalogue</a><img src="media/concept.png"><a href="../sources/proposals/model.glb">GLB</a>')
            with patch.object(build_public_pages,'ROOT',root):build_public_pages.build(root/'site',ref='proposal-test')
            self.assertIn('href="engineering-proposals.html"',(root/'site/index.html').read_text())
            proposal=(root/'site/engineering-proposals.html').read_text()
            self.assertIn('href="index.html"',proposal)
            self.assertIn('https://github.com/ender-dev-pl/openfa-assets/raw/proposal-test/sources/proposals/model.glb',proposal)
            self.assertEqual(len(list((root/'site/media').glob('*.webp'))),1)
            self.assertFalse(list((root/'site').rglob('*.glb')))

    def test_content_commit_is_a_root_without_source_history(self):
        # Git data is kept under the ignored evidence directory, never the source index.
        import uuid
        root = Path(__file__).resolve().parents[1] / 'artifacts' / ('pages-root-test-' + uuid.uuid4().hex)
        root.mkdir(parents=True)
        self.site(root)
        commit = prepare(root)
        parents = subprocess.check_output(['git', '-C', str(root), 'rev-list', '--parents', '-n', '1', commit], text=True).split()
        self.assertEqual(parents, [commit])
        names = subprocess.check_output(['git', '-C', str(root), 'ls-tree', '-r', '--name-only', 'HEAD'], text=True).splitlines()
        self.assertEqual(set(names), {'.nojekyll', *PAGES})


if __name__ == '__main__':
    unittest.main()
