"""Validate exact current bindings and summarize the narrowly decoded material findings."""
import hashlib
import json
import math
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/material-input-channels'
CHANNELS = {'Base Color', 'Roughness', 'Metallic', 'Alpha'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def colour_spaces(source):
    if isinstance(source, dict):
        return ([source['colour_space']] if 'colour_space' in source else []) + [space
            for key, value in source.items() if key != 'colour_space' for space in colour_spaces(value)]
    if isinstance(source, list):
        return [space for value in source for space in colour_spaces(value)]
    return []


def main():
    summary = json.loads((OUTPUT/'summary.json').read_text())
    for field, name in [('auditor_sha256', 'audit_material_input_channels.py'),
                        ('helper_sha256', 'material_input_channels.py'),
                        ('glb_parser_sha256', 'audit_catalogue_texture_uv.py')]:
        assert summary[field] == sha(Path(__file__).with_name(name))
    inventory_path = REPO/'docs/reconstruction/models/inventory.json'
    assert sha(inventory_path) == summary['inventory_sha256']
    selected = {r['id']: [s for s in r['available_studies'] if s['present']][-1]
                for r in json.loads(inventory_path.read_text())['records']}
    assert len(summary['records']) == len(selected) == 303
    assert {row['id'] for row in summary['records']} == selected.keys()
    counts, findings, aliases = Counter(), [], []
    for row in summary['records']:
        path = OUTPUT/row['report']
        assert sha(path) == row['sha256']
        report = json.loads(path.read_text())
        study = selected[row['id']]
        assert report['id'] == row['id'] and report['blend'] == study['blend']
        source = REPO/study['blend']
        assert report['blend_sha256'] == study['sha256'] == sha(source)
        assert report['glb_sha256'] == sha(source.with_suffix('.glb'))
        assert report['source_assets_unchanged'] and report['final_visual_acceptance'] is False
        counts['definitions'] += 1
        for side in ['native', 'imported']:
            state = report[side]
            counts[side+'_materials'] += len(state['materials'])
            counts[side+'_decoded_image_datablocks'] += state['decoded_image_datablocks']
            counts[side+'_models_with_decoded_images'] += state['decoded_image_datablocks'] > 0
            for material, inputs in state['materials'].items():
                if 'uninspected' in inputs:
                    findings.append(dict(id=report['id'], side=side, material=material, detail=inputs))
                for channel, value in inputs.items():
                    if channel not in CHANNELS:
                        continue
                    if 'uninspected' in value:
                        counts[side+'_uninspected_inputs'] += 1
                    else:
                        assert len(value['decoded_sha256']) == 64
                        counts[side+'_decoded_input_components'] += math.prod(value['shape'])
                        counts[side+'_image_driven_inputs'] += bool(colour_spaces(value['source']))
        for material, inputs in report['comparisons'].items():
            assert inputs.keys() == CHANNELS
            for channel, comparison in inputs.items():
                counts[comparison['status']] += 1
                if comparison['status'] != 'equal-at-8-bit-readback':
                    findings.append(dict(id=report['id'], material=material, channel=channel, comparison=comparison))
                a = set(colour_spaces(report['native']['materials'][material].get(channel, {}).get('source', {})))
                b = set(colour_spaces(report['imported']['materials'][material].get(channel, {}).get('source', {})))
                if a and b:
                    counts['compared_image_colour_space_roles'] += 1
                    if a != b:
                        findings.append(dict(id=report['id'], material=material, channel=channel,
                            native_colour_spaces=sorted(a), imported_colour_spaces=sorted(b)))
        for name, alias in report['verified_four_input_aliases'].items():
            counts['verified_four_input_aliases'] += 1
            base = alias['native_name']
            assert name not in report['glb_material_names'] and report['glb_material_names'].count(base) >= 2
            assert alias['checks'].keys() == CHANNELS
            assert all(check['status'] == 'equal-at-8-bit-readback' for check in alias['checks'].values())
            aliases.append(dict(id=report['id'], imported=name, native=base, scope=alias['scope']))
            counts['equal-at-8-bit-readback'] += len(alias['checks'])
        unresolved_extra = set(report['extra_materials'])-report['verified_four_input_aliases'].keys()
        if report['missing_materials'] or unresolved_extra or not report['material_bindings_equal_under_verified_four_input_aliases']:
            findings.append(dict(id=report['id'], missing=report['missing_materials'], unresolved_extra=sorted(unresolved_extra),
                four_input_material_bindings_equal=report['material_bindings_equal_under_verified_four_input_aliases']))
        counts['models_with_equal_four_input_material_bindings'] += report['material_bindings_equal_under_verified_four_input_aliases']
    result = dict(issue=1116, summary_sha256=sha(OUTPUT/'summary.json'), checker_sha256=sha(Path(__file__)),
        counts=dict(counts), findings=findings, verified_four_input_aliases=aliases, final_visual_acceptance=False,
        scope='Decoded supported inputs rounded to 8-bit Blender readback. No unquantized equality, complete shader/normal/emission/UV-sampling/render equivalence, final art or game integration acceptance.')
    (OUTPUT/'findings.json').write_text(json.dumps(result, indent=2)+'\n')
    print('MATERIAL_INPUT_CHANNELS_EVIDENCE_OK', json.dumps(dict(counts)), 'findings', len(findings))


if __name__ == '__main__':
    main()
