"""Independently check ship reference coverage, mappings and decoded frame hashes."""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LEGACY = REPO.parent / 'legacy'


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    index = read(REPO / 'docs/reconstruction/models/ship-reference-index.json')
    records = read(REPO / 'docs/reconstruction/models/inventory.json')['records']
    expected = {row['id']: row for row in records if row['category'] == 'ships'}
    ships = index['ships']
    assert len(ships) == len(expected) == index['definition_count'] == 41
    assert {ship['id'] for ship in ships} == set(expected)
    gameplay = read(REPO / 'content/standard/catalogues/legacy-gameplay.json')
    rules = gameplay['presentation']['shipAnimation']
    assert index['ship_animation_rules'] == rules
    sample_count = video_count = 0
    for ship in ships:
        original = expected[ship['id']]
        assert ship['culture'] == original['culture']
        assert ship['global_type'] == original['legacy_identity']['globalTypeIndex']
        variant = original['runtime_variants']['surface']
        assert ship['source_entry'] == variant['selected_first_available']
        candidate = next(row for row in variant['ordered_candidates'] if row['entry'] == ship['source_entry'])
        assert ship['source_sha256'] == candidate['sha256']
        root = LEGACY / '_S/png'
        metadata_path = root / (Path(ship['source_entry']).stem + '.json')
        assert sha(metadata_path) == ship['decoded_metadata_sha256']
        metadata = read(metadata_path)
        assert metadata['palette']['embedded']
        count = len(metadata['frames'])
        assert count == ship['frame_count']
        assert [frame['index'] for frame in ship['frames']] == ([0, 8, 16, 24] if count == 32 else list(range(count)))
        assert ship['runtime_even_heading_only'] == (ship['id'] in rules['evenSurfaceFrameShipIds'])
        assert ship['runtime_fixed_scale'] == (ship['id'] in rules['fixedScaleShipIds'])
        assert ship['selection_mode'].startswith('directional' if count == 32 else 'fixed-state')
        for frame in ship['frames']:
            source = metadata['frames'][frame['index']]
            assert frame['png'] == source['png']
            assert sha(root / frame['png']) == frame['png_sha256']
            assert (frame['pixel_width'], frame['pixel_height']) == (source['width'], source['height'])
            sample_count += 1
        references = [row for row in original['references'] if row.get('kind') == 'rotation-video']
        assert len(references) == len(ship['videos'])
        for video, reference in zip(ship['videos'], references):
            assert video['decoded']
            assert video['source_entry'] == reference['entry']
            assert video['source_directory'] == reference['directory']
            assert video['source_sha256'] == reference['sha256'] == sha(LEGACY / reference['directory'] / reference['entry'])
            first = REPO / video['frames'][0]['png']
            decoded = read(first.parent.parent / 'metadata.json')
            count = decoded['head']['frame_count']
            assert count == video['frame_count']
            assert [row['index'] for row in video['frames']] == sorted({0, count // 4, count // 2, count * 3 // 4, count - 1})
            for frame in video['frames']:
                assert sha(REPO / frame['png']) == frame['png_sha256']
            video_count += 1
    assert (sample_count, video_count) == (147, 9)
    print('SHIP_REFERENCES_VERIFIED 41 ships 147 surface samples 9 decoded rotations')


if __name__ == '__main__':
    main()
