# SPDX-License-Identifier: MIT
"""Regression checks for recipe/tool boundaries and mixed-rights exceptions."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tooling'))
from openfa_tools.licensing import audit, classify, load_policy, validate_policy


class LicensingTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_policy(ROOT)

    def license_for(self, path):
        return classify(path,self.policy)['license_expression']

    def test_executable_recipes_are_not_licensed_as_general_tools(self):
        paths = ['sources/tools/blender/build_federal_transporter.py',
                 'sources/tools/trading-goods/recipes.py',
                 'sources/ui/scitek/screen-generator/geometry.py',
                 'sources/docs/assets/bootstrap-3d/recipe.py',
                 'tools/render_sphere_gallery.py','sources/tools/historical-repairs/model.py']
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.license_for(path),'LicenseRef-OpenFA-Assets-1.0')

    def test_tool_permission_does_not_determine_asset_output_permission(self):
        self.assertEqual(self.license_for('tooling/openfa_tools/publication.py'),'MIT')
        self.assertEqual(self.license_for('tools/build_gallery.py'),'MIT')
        self.assertEqual(self.license_for('sources/objects/terran/space-dock/refined/model.glb'),
                         'LicenseRef-OpenFA-Assets-1.0')
        self.assertEqual(self.license_for('gallery/media/objects/model.png'),
                         'LicenseRef-OpenFA-Assets-1.0')

    def test_future_tools_default_to_asset_specific_until_reviewed(self):
        self.assertEqual(self.license_for('tools/new-model-builder.py'),'LicenseRef-OpenFA-Assets-1.0')

    def test_confirmed_ownership_and_font_terms_override_asset_default(self):
        self.assertEqual(self.license_for('sources/ui/legacy-menu-labels/font/NotoSerif-Bold.ttf'),'OFL-1.1')
        self.assertEqual(self.license_for('sources/tools/fragile256.py'),'MIT')
        self.assertEqual(self.license_for('sources/ui/quick-menu/quick-asteroid-icon.png'),'LicenseRef-OpenFA-Assets-1.0')

    def test_reviewed_source_exception_cannot_be_a_directory_or_asset(self):
        for change in [dict(prefixes=['sources/tools/']), dict(paths=['sources/tools/model.glb'])]:
            broken=deepcopy(self.policy)
            rule=next(rule for rule in broken['rules'] if rule.get('reviewed_general_source'))
            rule.update(change)
            with self.subTest(change=change),self.assertRaisesRegex(ValueError,'exact Python'):
                validate_policy(broken)

    def test_compatibility_data_retains_payload_provenance_notice(self):
        row=classify('sources/content/standard/catalogues/legacy-gameplay.json',self.policy)
        self.assertEqual(row['license_expression'],'LicenseRef-OpenFA-Assets-1.0')
        self.assertIn('recovered legacy payloads',row['notice'])

    def test_gallery_code_and_content_are_distinguished(self):
        row=classify('gallery/index.html',self.policy)
        self.assertEqual(row['kind'],'composite')
        self.assertIn('Presentation code is MIT',row['notice'])

    def test_unknown_roots_and_creative_tooling_payloads_fail_closed(self):
        for path in ['unreviewed/new-file.py','tooling/model.glb','tooling/render.png']:
            with self.subTest(path=path),self.assertRaises(ValueError):
                classify(path,self.policy)

    def test_unsafe_paths_and_duplicate_exact_scopes_are_rejected(self):
        for path in ['../outside.py','/outside.py','tools/../outside.py','tools\\outside.py']:
            with self.subTest(path=path),self.assertRaises(ValueError):
                classify(path,self.policy)
        broken=deepcopy(self.policy)
        broken['rules'][1]['paths'].append('sources/ui/legacy-menu-labels/font/NotoSerif-Bold.ttf')
        with self.assertRaisesRegex(ValueError,'Conflicting exact'):
            validate_policy(broken)

    def test_bilingual_terms_cover_recipe_sources_and_regeneration(self):
        texts={name:(ROOT/name).read_text(encoding='utf-8') for name in ['LICENSE.md','LICENSE.pl.md']}
        self.assertIn('Asset-Specific Source',texts['LICENSE.md'])
        self.assertIn('Regenerating an Asset',texts['LICENSE.md'])
        self.assertIn('Źródła Konkretnego Assetu',texts['LICENSE.pl.md'])
        self.assertIn('Ponowne wygenerowanie Assetu',texts['LICENSE.pl.md'])
        for name,text in texts.items():
            with self.subTest(name=name):
                self.assertNotIn('â€',text)
                self.assertNotIn('Ĺ‚',text)
                self.assertIn('320987843',text)
                self.assertIn('PL8581767172',text)

    def test_audit_rejects_broad_mit_grant_over_an_actual_asset(self):
        path='sources/objects/terran/space-dock/refined/model.glb'
        unsafe=dict(rules=[dict(id='wrong-mit',paths=[path],license_expression='MIT',kind='general-tool',notice='LICENSES/MIT.txt')])
        with patch('openfa_tools.licensing.load_policy',return_value=unsafe):
            with self.assertRaisesRegex(ValueError,'must not receive'):
                audit(ROOT,[path])

    def test_legacy_publication_import_is_the_same_reusable_implementation(self):
        import publication_support
        from openfa_tools import publication
        for name in ['clean_blend','clean_png','clean_jpeg','clean_text','zstd','png_chunks']:
            self.assertIs(getattr(publication_support,name),getattr(publication,name))


if __name__ == '__main__':
    unittest.main()
