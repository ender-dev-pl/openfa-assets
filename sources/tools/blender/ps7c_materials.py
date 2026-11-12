"""Portable authored PS7C plating, worn paint, roughness and tangent normals."""
import bpy
import numpy as np

from build_federal_transporter import surface


def mapped_image(name, values, folder, colour_space):
    height, width = values.shape[:2]
    image = bpy.data.images.new(name, width, height, alpha=True)
    image.colorspace_settings.name = colour_space
    image.pixels.foreach_set(values.astype(np.float32).ravel())
    image.filepath_raw = str(folder/(name+'.png'))
    image.file_format = 'PNG'
    image.save()
    image.pack()
    return image


def worn_material(name, colour, metal, rough, seed, folder, glow=0):
    mat = surface('PS7C '+name, colour, metal, rough, seed, folder, glow)
    if glow:
        return mat
    shader = mat.node_tree.nodes.get('Principled BSDF')
    texture = next(n for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE')
    image = texture.image
    size = image.size[0]
    pixels = np.array(image.pixels[:], dtype=np.float32).reshape(size, size, 4)
    rng = np.random.default_rng(seed+6216)
    height = np.zeros((size, size), dtype=np.float32)
    yy, xx = np.mgrid[:size, :size]
    modulation = np.ones((size, size), dtype=np.float32)
    if name in ['hull', 'steel', 'dark', 'red']:
        # Smaller stamped tiles and irregular repairs within the larger geometric plates.
        for row in range(4):
            top, bottom = row*size//4, (row+1)*size//4
            shift = (row%2)*size//6
            for column in range(-1, 4):
                left, right = max(0, column*size//3+shift), min(size, (column+1)*size//3+shift)
                if right <= left:
                    continue
                modulation[top:bottom, left:right] *= rng.uniform(.77, 1.08)
                modulation[top:top+2, left:right] *= .58
                modulation[top:bottom, left:left+2] *= .60
                height[top:top+2, left:right] = -.006
                height[top:bottom, left:left+2] = -.006
                for x, y in [(left+5, top+5), (right-6, bottom-6)]:
                    if 0 <= x < size and 0 <= y < size:
                        bolt = (xx-x)**2+(yy-y)**2 < 3
                        modulation[bolt] *= 1.18
                        height[bolt] = .003
        for _ in range(110):
            x, y = rng.integers(6, size-6, 2)
            length = int(rng.integers(3, 26))
            modulation[y, x:min(size, x+length)] *= rng.uniform(1.1, 1.4)
            height[y, x:min(size, x+length)] = -.002
    pixels[:, :, :3] = np.clip(pixels[:, :, :3]*modulation[:, :, None], 0, 1)
    image.pixels.foreach_set(pixels.ravel())
    image.save()
    image.pack()
    rough_pixels = np.ones_like(pixels)
    value = np.clip(rough+(1-modulation)*.35+rng.normal(0, .025, (size, size)), .18, .90)
    # glTF-native ORM layout avoids a temporary channel repack during export.
    rough_pixels[:, :, 0] = 1
    rough_pixels[:, :, 1] = value
    rough_pixels[:, :, 2] = metal
    rough_image = mapped_image('PS7C '+name+' roughness', rough_pixels, folder, 'Non-Color')
    rough_node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    rough_node.image = rough_image
    channels = mat.node_tree.nodes.new('ShaderNodeSeparateColor')
    mat.node_tree.links.new(rough_node.outputs['Color'], channels.inputs['Color'])
    mat.node_tree.links.new(channels.outputs['Green'], shader.inputs['Roughness'])
    mat.node_tree.links.new(channels.outputs['Blue'], shader.inputs['Metallic'])
    dy, dx = np.gradient(height)
    normal = np.stack((-dx*18, -dy*18, np.ones_like(height)), axis=2)
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)
    normal_pixels = np.ones_like(pixels)
    normal_pixels[:, :, :3] = normal*.5+.5
    normal_image = mapped_image('PS7C '+name+' normal', normal_pixels, folder, 'Non-Color')
    normal_texture = mat.node_tree.nodes.new('ShaderNodeTexImage')
    normal_texture.image = normal_image
    normal_node = mat.node_tree.nodes.new('ShaderNodeNormalMap')
    mat.node_tree.links.new(normal_texture.outputs['Color'], normal_node.inputs['Color'])
    mat.node_tree.links.new(normal_node.outputs['Normal'], shader.inputs['Normal'])
    return mat
