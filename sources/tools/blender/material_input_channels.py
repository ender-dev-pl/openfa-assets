"""Decode a deliberately limited subset of Principled inputs at 8-bit readback precision."""
import hashlib

import numpy as np

INPUTS = {'Base Color': 3, 'Roughness': 1, 'Metallic': 1, 'Alpha': 1}


class UnsupportedInput(Exception):
    pass


def quantize(values):
    values = np.asarray(values, dtype=np.float32)
    if not np.isfinite(values).all():
        raise UnsupportedInput('Nonfinite decoded input')
    if values.min() < 0 or values.max() > 1:
        raise UnsupportedInput('HDR/out-of-range input; no silent clipping')
    return np.rint(values*255).astype(np.uint8)


def image_values(image, cache):
    key = image.as_pointer()
    if key not in cache:
        width, height = image.size
        if not width or not height:
            raise UnsupportedInput('Image has no decoded pixels: '+image.name)
        values = np.empty(len(image.pixels), dtype=np.float32)
        image.pixels.foreach_get(values)
        cache[key] = values.reshape(height, width, -1)
    return cache[key]


def output_values(output, cache, trail=None):
    trail = set() if trail is None else trail
    node = output.node
    if node in trail:
        raise UnsupportedInput('Cyclic shader path')
    trail.add(node)
    if node.type == 'TEX_IMAGE':
        if node.image is None:
            raise UnsupportedInput('Connected image node has no image')
        pixels = image_values(node.image, cache)
        if output.name == 'Alpha':
            values = pixels[:, :, 3:4] if pixels.shape[2] >= 4 else np.ones((*pixels.shape[:2], 1), dtype=np.float32)
        elif output.name == 'Color':
            if pixels.shape[2] < 3:
                raise UnsupportedInput('Unexpected decoded colour channel layout')
            values = pixels[:, :, :3]
        else:
            raise UnsupportedInput('Unknown image output '+output.name)
        return values, dict(image=node.image.name, size=list(node.image.size),
            colour_space=node.image.colorspace_settings.name, output=output.name,
            interpolation=node.interpolation, extension=node.extension)
    if node.type in ['SEPARATE_COLOR', 'SEPRGB']:
        if node.type == 'SEPARATE_COLOR' and node.mode != 'RGB':
            raise UnsupportedInput('Non-RGB colour separation')
        socket = node.inputs[0]
        if not socket.is_linked:
            raise UnsupportedInput('Unlinked colour separation')
        values, evidence = output_values(socket.links[0].from_socket, cache, trail)
        index = {'Red': 0, 'Green': 1, 'Blue': 2, 'R': 0, 'G': 1, 'B': 2}.get(output.name)
        if index is None or values.shape[-1] < 3:
            raise UnsupportedInput('Unknown separate-colour output')
        return values[:, :, index:index+1], dict(evidence, selected_channel=index)
    if node.type == 'REROUTE' and node.inputs[0].is_linked:
        return output_values(node.inputs[0].links[0].from_socket, cache, trail)
    if node.type == 'MATH' and node.operation == 'MULTIPLY':
        operands, sources = [], []
        for socket in list(node.inputs)[:2]:
            if socket.is_linked:
                values, source = output_values(socket.links[0].from_socket, cache, set(trail))
                if values.shape[-1] == 3:
                    if not np.all(values[:, :, 0] == values[:, :, 1]) or not np.all(values[:, :, 1] == values[:, :, 2]):
                        raise UnsupportedInput('Non-grey implicit math colour-to-scalar conversion')
                    values = values[:, :, :1]
            else:
                values = np.array([[[socket.default_value]]], dtype=np.float32)
                source = dict(constant=socket.default_value)
            operands.append(values)
            sources.append(source)
        if operands[0].shape != operands[1].shape and not any(v.shape[:2] == (1, 1) for v in operands):
            raise UnsupportedInput('Different math image dimensions; no resampling assumption')
        values = operands[0]*operands[1]
        if node.use_clamp:
            values = np.clip(values, 0, 1)
        return values, dict(operation='MULTIPLY', inputs=sources, clamp=node.use_clamp)
    raise UnsupportedInput('Uninspected node '+node.type+' / '+output.name)


def describe(values, source):
    pixels = quantize(values)
    flat = pixels.reshape(-1, pixels.shape[-1])
    low, high = flat.min(axis=0), flat.max(axis=0)
    uniform = low.tolist() if np.array_equal(low, high) else None
    return dict(source=source, shape=list(pixels.shape), decoded_sha256=hashlib.sha256(pixels.tobytes()).hexdigest(),
                minimum=low.tolist(), maximum=high.tolist(), uniform=uniform), pixels


def material_inputs(material, cache):
    records, pixels = {}, {}
    if not material.use_nodes:
        return {'uninspected': 'Material does not use shader nodes'}, pixels
    outputs = [node for node in material.node_tree.nodes if node.type == 'OUTPUT_MATERIAL' and node.is_active_output]
    if len(outputs) != 1 or not outputs[0].inputs['Surface'].is_linked:
        return {'uninspected': 'No unique connected active material surface'}, pixels
    shader = outputs[0].inputs['Surface'].links[0].from_node
    if shader.type != 'BSDF_PRINCIPLED':
        return {'uninspected': 'Active surface is '+shader.type}, pixels
    for name, components in INPUTS.items():
        socket = shader.inputs[name]
        try:
            if socket.is_linked:
                values, source = output_values(socket.links[0].from_socket, cache)
                if values.shape[-1] == 3 and components == 1:
                    if not np.all(values[:, :, 0] == values[:, :, 1]) or not np.all(values[:, :, 1] == values[:, :, 2]):
                        raise UnsupportedInput('Non-grey implicit colour-to-scalar conversion')
                    values = values[:, :, :1]
                elif values.shape[-1] == 1 and components == 3:
                    values = np.repeat(values, 3, axis=2)
                if values.shape[-1] != components:
                    raise UnsupportedInput('Uninterpreted channel conversion')
            else:
                value = socket.default_value
                value = list(value)[:components] if components > 1 else [value]
                values, source = np.asarray(value, dtype=np.float32).reshape(1, 1, components), {'constant': value}
            records[name], pixels[name] = describe(values, source)
        except UnsupportedInput as error:
            records[name] = {'uninspected': str(error)}
    return records, pixels


def compare_input(a, b):
    """Compare full decoded arrays; broadcast a genuinely uniform input, never resample."""
    if a.shape[-1] != b.shape[-1]:
        return dict(status='uninspected', reason='Component counts differ')
    a_flat, b_flat = a.reshape(-1, a.shape[-1]), b.reshape(-1, b.shape[-1])
    a_uniform = np.all(a_flat == a_flat[0])
    b_uniform = np.all(b_flat == b_flat[0])
    if a.shape == b.shape:
        left, right = a, b
    elif a_uniform:
        left, right = a_flat[0], b
    elif b_uniform:
        left, right = a, b_flat[0]
    else:
        return dict(status='uninspected', reason='Different nonuniform dimensions; no resampling assumption')
    difference = np.abs(left.astype(np.int16)-right.astype(np.int16))
    maximum = int(difference.max())
    return dict(status='equal-at-8-bit-readback' if maximum == 0 else 'different-at-8-bit-readback',
                maximum_channel_difference=maximum, differing_components=int(np.count_nonzero(difference)))


def verified_readback_aliases(native_pixels, imported_pixels, glb_names):
    """Resolve only importer suffixes backed by duplicate GLB names and four equal inputs."""
    aliases = {}
    for name in imported_pixels.keys()-native_pixels.keys():
        base, separator, suffix = name.rpartition('.')
        if not separator or not suffix.isdigit() or name in glb_names or glb_names.count(base) < 2 or base not in native_pixels:
            continue
        if set(native_pixels[base]) != set(INPUTS) or set(imported_pixels[name]) != set(INPUTS):
            continue
        checks = {channel: compare_input(native_pixels[base][channel], imported_pixels[name][channel]) for channel in INPUTS}
        if all(check['status'] == 'equal-at-8-bit-readback' for check in checks.values()):
            aliases[name] = dict(native_name=base, checks=checks,
                scope='Duplicate GLB name and four decoded inputs only; not complete shader/UV equivalence')
    return aliases
