"""Bind existing authored textures to three first-pass details; never alter geometry."""
import math

LAYER = 'Authored surface wear'
DETAILS = {
    'RI06 upper mast neck retaining collar',
    'RI23 bronze front strip',
    'RI23 bronze base fitting',
}


def bind_detail_uvs(meshes):
    """Reuse a chart when present, otherwise project each face onto its dominant plane."""
    changed = []
    for obj in meshes:
        if obj.name not in DETAILS:
            continue
        mesh = obj.data
        if mesh.uv_layers.get(LAYER):
            continue
        original = mesh.uv_layers.active
        values = [tuple(loop.uv) for loop in original.data] if original else None
        if values is not None:
            # Keep the shader-required chart at TEXCOORD_0. Preserve the old named
            # chart as an identical copy, without a material-specific texCoord split.
            assert len(mesh.uv_layers) == 1, 'Multiple prior UV sets require explicit review'
            original_name = original.name
            original.name = LAYER
            retained = mesh.uv_layers.new(name=original_name)
            for loop, value in zip(retained.data, values):
                loop.uv = value
            chart = mesh.uv_layers[LAYER]
            method = 'Exact copy of existing ' + original_name
        else:
            chart = mesh.uv_layers.new(name=LAYER)
            low = [min(vertex.co[axis] for vertex in mesh.vertices) for axis in range(3)]
            span = [max(vertex.co[axis] for vertex in mesh.vertices)-low[axis] for axis in range(3)]
            for face in mesh.polygons:
                normal_axis = max(range(3), key=lambda axis: abs(face.normal[axis]))
                axes = [axis for axis in range(3) if axis != normal_axis]
                assert all(span[axis] > 1e-12 for axis in axes), obj.name
                for index in face.loop_indices:
                    point = mesh.vertices[mesh.loops[index].vertex_index].co
                    chart.data[index].uv = tuple((point[axis]-low[axis])/span[axis] for axis in axes)
            method = 'Local dominant-face box projection, normalized to existing bounds'
        assert len(chart.data) == len(mesh.loops)
        assert all(math.isfinite(value) for loop in chart.data for value in loop.uv)
        chart.active_render = True
        mesh.uv_layers.active = chart
        changed.append(dict(object=obj.name, method=method, loops=len(chart.data)))
    return changed


def verify_detail_uvs(meshes):
    """Check shader-selected charts, including after GLB renames UV sets on import."""
    result = {}
    for obj in meshes:
        if obj.name not in DETAILS:
            continue
        mesh = obj.data
        assert mesh.uv_layers.active, 'Missing UV chart: ' + obj.name
        for face in mesh.polygons:
            material = mesh.materials[face.material_index]
            shader = material.node_tree.nodes.get('Principled BSDF')
            for channel in ['Base Color', 'Roughness']:
                texture = shader.inputs[channel].links[0].from_node
                if texture.type in ['SEPARATE_COLOR', 'SEPRGB']:
                    texture = texture.inputs[0].links[0].from_node
                assert texture.type == 'TEX_IMAGE' and texture.image.packed_file
                vector = texture.inputs['Vector']
                name = vector.links[0].from_node.uv_map if vector.is_linked else None
                chart = mesh.uv_layers.get(name) if name else mesh.uv_layers.active
                assert chart is not None, obj.name + ': shader selects an absent UV chart'
                values = [tuple(chart.data[index].uv) for index in face.loop_indices]
                assert all(math.isfinite(value) for uv in values for value in uv)
                # Every nondegenerate face needs a chart with nonzero two-dimensional area.
                area = sum(values[i][0]*values[(i+1)%len(values)][1]-values[(i+1)%len(values)][0]*values[i][1]
                           for i in range(len(values)))
                assert abs(area) > 1e-15, obj.name + ': collapsed UV face'
        result[obj.name] = 'Finite shader-selected UVs with nonzero face areas'
    return result
