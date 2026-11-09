"""Read current GLBs in memory; prepare flight-only remaster review contracts.

No render, model generation, historical extraction or acceptance promotion.
"""
import hashlib
import json
from pathlib import Path
import struct

ROOT = Path(__file__).resolve().parents[1]
SHIPS = ('assault-fighter', 'combat-eagle', 'scoutship')
REPORT = ROOT / 'sources/docs/reconstruction/models/light-ship-protocol-inputs.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_glb(path):
    raw = path.read_bytes()
    magic, version, length = struct.unpack_from('<4sII', raw)
    assert magic == b'glTF' and version == 2 and length == len(raw)
    chunks = {}
    offset = 12
    while offset < len(raw):
        size, kind = struct.unpack_from('<I4s', raw, offset)
        assert kind not in chunks and offset + size + 8 <= len(raw)
        chunks[kind] = raw[offset + 8:offset + 8 + size]
        offset += size + 8
    return json.loads(chunks[b'JSON']), chunks[b'BIN\0']


def positions(document, binary, index):
    accessor = document['accessors'][index]
    assert accessor['componentType'] == 5126 and accessor['type'] == 'VEC3'
    assert not accessor.get('normalized') and 'sparse' not in accessor
    view = document['bufferViews'][accessor['bufferView']]
    assert view['buffer'] == 0
    start = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
    stride = view.get('byteStride', 12)
    assert stride >= 12
    assert start + (accessor['count'] - 1) * stride + 12 <= view.get('byteOffset', 0) + view['byteLength']
    return [struct.unpack_from('<3f', binary, start + i * stride)
            for i in range(accessor['count'])]


def local_matrix(node):
    if 'matrix' in node:
        values = node['matrix']
        return [[values[column * 4 + row] for column in range(4)] for row in range(4)]
    x, y, z, w = node.get('rotation', [0, 0, 0, 1])
    scale = node.get('scale', [1, 1, 1])
    translation = node.get('translation', [0, 0, 0])
    rotation = [[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]]
    return [[rotation[row][column] * scale[column] for column in range(3)]
            + [translation[row]] for row in range(3)] + [[0, 0, 0, 1]]


def multiply(left, right):
    return [[sum(left[row][k] * right[k][column] for k in range(4))
             for column in range(4)] for row in range(4)]


def inspect(slug):
    folder = ROOT / 'sources/objects/terran' / slug
    meta_path = folder / 'model.json'
    metadata_before = sha(meta_path)
    meta = json.loads(meta_path.read_bytes())
    for ext in ('blend', 'glb'):
        assert sha(folder / ('model.' + ext)) == meta[ext + '_sha256']
    document, binary = read_glb(folder / 'model.glb')
    nodes = document['nodes']
    by_name = {node['name']: i for i, node in enumerate(nodes)}
    assert len(by_name) == len(nodes)
    seen = set()

    def descendants(index):
        assert index not in seen, 'Cycle or shared node in expected tree'
        seen.add(index)
        node = nodes[index]
        result = {index}
        for child in node.get('children', []):
            result.update(descendants(child))
        return result

    roots = document['scenes'][document.get('scene', 0)]['nodes']
    assert roots == [by_name['ShipAssembly']]
    assert nodes[roots[0]]['extras']['catalogue_id'] == meta['id']
    assert descendants(roots[0]) == set(range(len(nodes)))
    world = {}

    def place(index, parent):
        world[index] = multiply(parent, local_matrix(nodes[index]))
        for child in nodes[index].get('children', []):
            place(child, world[index])

    identity = [[int(row == column) for column in range(4)] for row in range(4)]
    place(roots[0], identity)
    stages = []
    consumed = set()
    all_points = []
    for layer in meta['layers']:
        seen.clear()
        group = descendants(by_name[layer['node']])
        assert not consumed.intersection(group)
        consumed.update(group)
        meshes = []
        points = []
        triangles = 0
        for index in group:
            node = nodes[index]
            if 'mesh' not in node:
                continue
            meshes.append(node['name'])
            for primitive in document['meshes'][node['mesh']]['primitives']:
                assert primitive.get('mode', 4) == 4
                accessor = document['accessors'][primitive['indices']]
                assert accessor['type'] == 'SCALAR' and accessor['count'] % 3 == 0
                triangles += accessor['count'] // 3
                matrix = world[index]
                for point in positions(document, binary, primitive['attributes']['POSITION']):
                    points.append(tuple(sum(matrix[a][b] * point[b] for b in range(3)) + matrix[a][3]
                                        for a in range(3)))
        assert meshes and points
        if layer['node'] in meta['flight_visible_nodes']:
            assert all(name.startswith(('HullPartialBatch_', 'HullFinalBatch_')) for name in meshes)
            all_points.extend(points)
        stages.append(dict(node=layer['node'], progress_start=layer['progress_start'],
                           meshes=sorted(meshes), mesh_count=len(meshes), triangles=triangles))
    assert [row['progress_start'] for row in stages] == [0, .16, .38, .65, .88]
    assert meta['flight_visible_nodes'] == ['HullPartial', 'HullFinal']
    assert meta['flight_hidden_nodes'] == [row['node'] for row in stages[:3]]
    assert sum(row['triangles'] for row in stages) == meta['triangles']
    assert sum(row['mesh_count'] for row in stages) == meta['mesh_nodes']
    assert all(index in consumed for index, node in enumerate(nodes) if 'mesh' in node)
    assert not document.get('animations'), 'Build visibility is client-driven, not a baked clip'
    # glTF +Y up corresponds to Blender +Z; glTF +Z is Blender -Y.
    blender_points = [(x, -z, y) for x, y, z in all_points]
    bounds = [[min(p[a] for p in blender_points) for a in range(3)],
              [max(p[a] for p in blender_points) for a in range(3)]]
    error = max(abs(a - b) for actual, expected in zip(bounds, meta['shell_bounds'])
                for a, b in zip(actual, expected))
    assert error < 1e-5
    helper_tags = [dict(node=node['name'], catalogue_id=node['extras']['catalogue_id'])
                   for node in nodes if 'mesh' in node and node.get('extras', {}).get('catalogue_id')
                   and node['extras']['catalogue_id'] != meta['id']]
    assert metadata_before == sha(meta_path)
    for ext in ('blend', 'glb'):
        assert sha(folder / ('model.' + ext)) == meta[ext + '_sha256']
    return dict(id=meta['id'], blend=(folder / 'model.blend').relative_to(ROOT).as_posix(),
                glb=(folder / 'model.glb').relative_to(ROOT).as_posix(),
                binaries={ext: meta[ext + '_sha256'] for ext in ('blend', 'glb')},
                metadata_sha256=metadata_before, stages=stages,
                cumulative_triangles=[sum(r['triangles'] for r in stages[:i + 1]) for i in range(5)],
                flight_triangles=sum(r['triangles'] for r in stages[3:]),
                flight_meshes=sum(r['mesh_count'] for r in stages[3:]),
                flight_hide=meta['flight_hidden_nodes'], flight_show=meta['flight_visible_nodes'],
                blender_flight_bounds=bounds, metadata_bounds_error=error,
                non_root_helper_catalogue_tags=helper_tags,
                build_progress_is_client_driven=True, source_bytes_unchanged=True)


def main():
    rows = [inspect(slug) for slug in SHIPS]
    result = dict(issue=248, auditor_sha256=sha(Path(__file__)), models=rows,
                  scope='Current GLB hierarchy, indexed triangle counts, decoded POSITION bounds and metadata identities only. No new Blender run, render, historical exterior equality, concept, legacy fidelity or client acceptance inferred.',
                  pending='Generate legacy-referenced concepts and actual flight-only native/import renders when disk headroom is restored. Preserve both complementary hull groups; hide all three internal build groups in flight.')
    REPORT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('LIGHT_SHIP_PROTOCOL_INPUTS_AUDITED', len(rows))
    for row in rows:
        print(row['id'], 'flight', row['flight_triangles'], 'all', row['cumulative_triangles'][-1])


if __name__ == '__main__':
    main()
