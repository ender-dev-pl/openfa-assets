"""Expand reviewed modelling decisions into explicit per-building part recipes and provenance."""
import argparse
import json
from pathlib import Path

from catalogue_families import make_recipe
from catalogue_recipe_table import CULTURES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--references', type=Path, default=Path('artifacts/issue-943-catalogue/references/index.json'))
    args = parser.parse_args()
    references = json.loads(args.references.read_text(encoding='utf-8'))
    root = Path(__file__).resolve().parents[2] / 'docs/assets/bootstrap-3d/full-catalogue'
    root.mkdir(parents=True, exist_ok=True)
    records = []
    counts = {culture: 0 for culture in CULTURES}
    for reference in references:
        culture = reference['culture']
        local = counts[culture]
        family, parameters, notes = CULTURES[culture][local]
        counts[culture] += 1
        detailed = family.removeprefix('basic-') if family.startswith('basic-') else None
        parts = [] if detailed else make_recipe(family, parameters)
        assert detailed or len(parts) >= 4, (reference['preview'], len(parts))
        record = {**reference, 'assembly_family': family, 'parameters': parameters,
                  'observed_features': notes, 'authoring_status': 'reviewed silhouette study',
                  'hidden_geometry': 'authored approximation; original source geometry is unavailable',
                  'detailed_builder': detailed, 'parts': parts}
        records.append(record)
    assert len(records) == 177 and len({item['building_id'] for item in records}) == 177
    assert {item['global_type'] for item in records} == set(range(177))
    assert all(counts[culture] == len(CULTURES[culture]) for culture in counts), counts
    (root / 'recipes.json').write_text(json.dumps({'schema_version': 1, 'imported_geometry_or_textures': [],
        'cultures': counts, 'buildings': records}, indent=2) + '\n', encoding='utf-8')
    print('AUTHORED_CATALOGUE_RECIPES_OK', len(records), counts)


if __name__ == '__main__':
    main()
