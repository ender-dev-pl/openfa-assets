"""Read-only native/GLB decoded input comparisons across all selected sources."""
import hashlib
import json
import sys
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from material_input_channels import INPUTS, material_inputs, compare_input, verified_readback_aliases
from audit_catalogue_texture_uv import parse_glb

REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO/'docs/assets/reconstruction/evidence/material-input-channels'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture():
    bpy.context.scene.frame_set(1)
    graph = bpy.context.evaluated_depsgraph_get()
    bindings, materials = {}, {}
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH' or obj.get('preview_only'):
            continue
        evaluated = obj.evaluated_get(graph)
        mesh = evaluated.to_mesh()
        try:
            names = []
            for index in sorted({face.material_index for face in mesh.polygons}):
                assert index < len(mesh.materials) and mesh.materials[index], obj.name+' missing material'
                material = mesh.materials[index]
                materials[material.name] = material
                names.append(material.name)
            bindings[obj.name] = sorted(set(names))
        finally:
            evaluated.to_mesh_clear()
    records, pixels, cache = {}, {}, {}
    for name, material in sorted(materials.items()):
        records[name], pixels[name] = material_inputs(material, cache)
    return dict(bindings=bindings, materials=records, decoded_image_datablocks=len(cache)), pixels


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    inventory_path = REPO/'docs/reconstruction/models/inventory.json'
    inventory = json.loads(inventory_path.read_text())
    assert len(inventory['records']) == 303
    rows = []
    for index, record in enumerate(inventory['records']):
        study = [s for s in record['available_studies'] if s['present']][-1]
        source = REPO/study['blend']
        export = source.with_suffix('.glb')
        before = dict(blend_sha256=sha(source), glb_sha256=sha(export))
        assert before['blend_sha256'] == study['sha256']
        bpy.ops.wm.open_mainfile(filepath=str(source))
        native, native_pixels = capture()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(export))
        imported, imported_pixels = capture()
        document, _ = parse_glb(export)
        glb_names = [m.get('name', '') for m in document.get('materials', [])]
        aliases = verified_readback_aliases(native_pixels, imported_pixels, glb_names)
        comparisons = {}
        for name in sorted(native['materials'].keys() & imported['materials'].keys()):
            comparisons[name] = {}
            for channel in INPUTS:
                if channel in native_pixels[name] and channel in imported_pixels[name]:
                    comparisons[name][channel] = compare_input(native_pixels[name][channel], imported_pixels[name][channel])
                else:
                    comparisons[name][channel] = dict(status='uninspected', reason='Unsupported native or imported shader path')
        assert before == dict(blend_sha256=sha(source), glb_sha256=sha(export))
        report = dict(issue=1116, id=record['id'], category=record['category'], blend=study['blend'], **before,
            native=native, imported=imported, comparisons=comparisons,
            missing_materials=sorted(native['materials'].keys()-imported['materials'].keys()),
            extra_materials=sorted(imported['materials'].keys()-native['materials'].keys()),
            material_bindings_equal=native['bindings'] == imported['bindings'],
            glb_material_names=glb_names, verified_four_input_aliases=aliases,
            material_bindings_equal_under_verified_four_input_aliases=native['bindings'] == {
                obj: sorted({aliases.get(name, {}).get('native_name', name) for name in names})
                for obj, names in imported['bindings'].items()},
            source_assets_unchanged=True, final_visual_acceptance=False)
        path = OUTPUT/f'{index:03}.json'
        path.write_text(json.dumps(report, indent=2)+'\n')
        rows.append(dict(id=record['id'], category=record['category'], report=path.name, sha256=sha(path)))
        print('MATERIAL_INPUT_CHANNELS_INSPECTED', record['id'], flush=True)
    summary = dict(issue=1116, blender=bpy.app.version_string, records=rows,
        inventory_sha256=sha(inventory_path), auditor_sha256=sha(Path(__file__)),
        helper_sha256=sha(Path(__file__).with_name('material_input_channels.py')), final_visual_acceptance=False,
        glb_parser_sha256=sha(Path(__file__).with_name('audit_catalogue_texture_uv.py')),
        scope='Four supported Principled input paths at rounded 8-bit Blender pixel-readback precision. No rendered shader, UV sampling, normal, emission, final art or game integration acceptance.')
    (OUTPUT/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    print('MATERIAL_INPUT_CHANNELS_AUDIT_OK', len(rows), flush=True)


if __name__ == '__main__':
    main()
