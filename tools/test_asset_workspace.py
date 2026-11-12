"""Regression scenarios for editable sources, independent preparation and provenance."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asset_workspace as work


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.root_patch = patch.object(work, 'ROOT', self.root)
        self.root_patch.start()
        self.addCleanup(self.temp.cleanup)
        self.addCleanup(self.root_patch.stop)
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)
        self.files = [dict(original='tools/hello.py', destination='sources/tools/hello.py', role='source', ownership='moved'),
                      dict(original='images/source.png', destination='sources/materials/test/source.png', role='material-texture', ownership='moved'),
                      dict(original='tools/one_time.py', destination='sources/tools/historical-repairs/one_time.py', role='historical-script', ownership='moved')]
        for row in self.files:
            path = self.root / row['destination']
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'print("original")\n' if path.suffix == '.py' else b'png fixture')
        self.write_layout()
        baseline = []
        for row in self.files:
            path = self.root / row['destination']
            baseline.append(dict(row, bytes=path.stat().st_size, sha256=work.sha(path)))
        baseline.append(dict(original='content/unused.json', destination='sources/content/unused.json',
                             role='fixture', ownership='fixture', bytes=2, sha256=hashlib.sha256(b'{}').hexdigest()))
        (self.root / 'project/import-baseline.json').write_text(json.dumps(dict(files=baseline,
            external_inputs=[dict(original='src/unavailable.cs', sha256='missing')])) )

    def write_layout(self):
        folder = self.root / 'project'
        folder.mkdir(exist_ok=True)
        (folder / 'layout.json').write_text(json.dumps(dict(files=self.files,
            retired_imports=[dict(original='content/unused.json', reason='No consumer')])) )

    def test_original_game_media_is_rejected(self):
        name = 'gallery/media/legacy.png'
        (self.root / 'project/excluded-media.json').write_text(json.dumps(dict(paths=[name])))
        work.verify()
        path = self.root / name
        path.parent.mkdir(parents=True)
        path.write_bytes(b'original pixels')
        with self.assertRaisesRegex(ValueError, 'Original-game media'):
            work.verify()

    def test_prepare_does_not_require_external_game_or_legacy(self):
        with patch.object(work, 'junction', side_effect=AssertionError('Unexpected external link')):
            workspace = work.prepare()
        self.assertEqual((workspace / 'tools/hello.py').read_bytes(), b'print("original")\n')
        self.assertFalse((workspace / 'src').exists())
        self.assertFalse((self.root / 'legacy').exists())
        self.assertFalse((workspace / 'tools/one_time.py').exists())

    def test_source_edits_sync_without_rewriting_import_manifest(self):
        workspace = work.prepare()
        baseline = (self.root / 'project/import-baseline.json').read_bytes()
        source = self.root / 'sources/tools/hello.py'
        source.write_text('print("updated source")\n')
        work.verify()
        work.prepare()
        self.assertEqual((workspace / 'tools/hello.py').read_bytes(), source.read_bytes())
        self.assertEqual((self.root / 'project/import-baseline.json').read_bytes(), baseline)
        with self.assertRaisesRegex(ValueError, 'differs from original import'):
            work.audit_import()

    def test_workspace_edits_block_all_updates_without_data_loss(self):
        workspace = work.prepare()
        edited = workspace / 'tools/hello.py'
        edited.write_text('print("local unsaved authoring work")\n')
        texture = self.root / 'sources/materials/test/source.png'
        texture.write_bytes(b'updated material')
        old_texture = (workspace / 'images/source.png').read_bytes()
        state = (workspace / '.asset-workspace-state.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'Preserving edited'):
            work.prepare()
        self.assertIn('local unsaved', edited.read_text())
        self.assertEqual((workspace / 'images/source.png').read_bytes(), old_texture)
        self.assertEqual((workspace / '.asset-workspace-state.json').read_bytes(), state)

    def test_equal_source_and_workspace_edits_are_adopted(self):
        workspace = work.prepare()
        for path in [self.root / 'sources/tools/hello.py', workspace / 'tools/hello.py']:
            path.write_text('print("reviewed identical edits")\n')
        work.prepare()
        state = json.loads((workspace / '.asset-workspace-state.json').read_text())
        self.assertEqual(state['tools/hello.py'], work.sha(workspace / 'tools/hello.py'))

    def test_existing_unmanaged_workspace_edit_is_preserved(self):
        dest = self.root / '.workspace/tools/hello.py'
        dest.parent.mkdir(parents=True)
        dest.write_text('unmanaged work')
        with self.assertRaisesRegex(ValueError, 'Preserving edited'):
            work.prepare()
        self.assertEqual(dest.read_text(), 'unmanaged work')

    def test_history_is_explicit_and_retired_data_is_not_restored(self):
        work.audit_import()
        workspace = work.prepare(include_history=True)
        self.assertTrue((workspace / 'tools/one_time.py').is_file())
        self.assertFalse((workspace / 'content/unused.json').exists())

    def test_archived_import_support_can_be_materialized_without_executing_it(self):
        self.files[-1]['verification_support'] = True
        self.write_layout()
        with patch.object(work.subprocess, 'run', side_effect=AssertionError('Preparation must not execute support code')):
            workspace = work.prepare()
        self.assertTrue((workspace / 'tools/one_time.py').is_file())

    def test_unregistered_render_is_rejected_but_material_inputs_allowed(self):
        work.verify()
        preview = self.root / 'sources/materials/preview.png'
        preview.write_bytes(b'finished render')
        with self.assertRaisesRegex(ValueError, 'Unregistered'):
            work.verify()

    def test_layout_cannot_write_outside_workspace(self):
        self.files[0]['original'] = '../escape.py'
        self.write_layout()
        with self.assertRaisesRegex(ValueError, 'relative path'):
            work.prepare()

    def test_custom_workspace_cannot_overwrite_canonical_source_tree(self):
        with self.assertRaisesRegex(ValueError, 'outside sources'):
            work.prepare(self.root / 'sources/edited')

    def test_optional_evidence_fails_before_workspace_changes(self):
        legacy = self.root / 'local-original'
        legacy.mkdir()
        with self.assertRaisesRegex(ValueError, 'game evidence changed/missing'):
            work.prepare_evidence(legacy, self.root / 'no-game')
        self.assertFalse((self.root / '.workspace').exists())

    def test_archived_script_cannot_be_run_accidentally(self):
        work.prepare(include_history=True)
        with patch.object(sys, 'argv', ['asset_workspace.py', 'python', '--', './tools/one_time.py']), \
             patch.object(work.subprocess, 'run', side_effect=AssertionError('Historical execution is forbidden')), \
             contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as failure:
                work.main()
        self.assertEqual(failure.exception.code, 2)

    def test_historical_git_context_uses_game_history(self):
        game = self.root / 'game'
        with patch.object(work.subprocess, 'check_output', return_value='/original/gitdir\n') as command:
            env = work.history_environment(game)
        self.assertEqual(env['GIT_DIR'], '/original/gitdir')
        self.assertEqual(env['GIT_WORK_TREE'], str(game.resolve()))
        self.assertIn(str(game), command.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
