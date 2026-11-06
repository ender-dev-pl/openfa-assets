"""Verify that only clean generated site files enter the publication branch."""
from pathlib import Path
import subprocess
import unittest
from test_publication import fixture_directory
from publish_public_pages import prepare, validate


class PagesTests(unittest.TestCase):
    def site(self, root):
        for name in ['index.html', 'ui.html', 'construction-animations.html']:
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
        self.assertEqual(set(names), {'.nojekyll', 'index.html', 'ui.html', 'construction-animations.html'})


if __name__ == '__main__':
    unittest.main()
