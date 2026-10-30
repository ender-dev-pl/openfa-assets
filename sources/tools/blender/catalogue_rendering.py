"""Blender solid assembly and camera framing for catalogue model sources."""
import math

import bpy
from mathutils import Vector

from build_openfa_assets import beam, box, finish, material
from build_legacy_buildings import lathe, dome, arc, cpu, solar, air, hydroponics, hydration, materials as detailed_materials


# Independently authored palette approximations; no original pixels are sampled.
COLOURS = {
 'terran': [(0.17,0.24,0.20),(0.30,0.35,0.37),(0.46,0.29,0.10),(0.40,0.12,0.08),(0.20,0.16,0.31),(0.19,0.30,0.22),(0.82,0.70,0.31)],
 'rigellian': [(0.13,0.30,0.23),(0.30,0.42,0.37),(0.48,0.30,0.07),(0.12,0.23,0.17),(0.13,0.25,0.24),(0.11,0.47,0.31),(0.82,0.68,0.28)],
 'braccatian': [(0.38,0.18,0.11),(0.48,0.31,0.12),(0.51,0.33,0.11),(0.025,0.08,0.45),(0.24,0.10,0.07),(0.03,0.10,0.40),(0.85,0.70,0.34)],
 'mikotaj': [(0.055,0.16,0.115),(0.11,0.24,0.19),(0.40,0.27,0.07),(0.05,0.18,0.13),(0.08,0.19,0.16),(0.07,0.25,0.22),(0.55,0.78,1.0)],
 'artemian': [(0.10,0.27,0.19),(0.15,0.21,0.25),(0.38,0.24,0.10),(0.25,0.11,0.07),(0.12,0.24,0.19),(0.30,0.40,0.40),(0.80,0.60,0.22)],
 'mauna': [(0.19,0.27,0.38),(0.31,0.40,0.47),(0.52,0.31,0.09),(0.52,0.02,0.015),(0.17,0.25,0.36),(0.18,0.25,0.32),(0.84,0.68,0.32)],
 'achaean': [(0.40,0.18,0.12),(0.22,0.31,0.36),(0.47,0.28,0.08),(0.56,0.12,0.08),(0.30,0.14,0.12),(0.05,0.10,0.29),(0.65,0.78,0.90)],
}


def materials(culture):
    colours = dict(zip(['body','trim','cap','accent','purple','glass','light'], COLOURS[culture]))
    colours.update(red=(0.58,0.025,0.015), bronze=(0.28,0.16,0.07), dark=(0.014,0.019,0.023))
    return {name: material(culture + ' | ' + name, colour, 0.45 if name != 'light' else 0.1,
                           0.43, 0.25 if name == 'light' else 0) for name, colour in colours.items()}


def wedge(name, position, size, surface):
    w, d, h = size
    vertices = [(x*w/2,y*d/2,z*h) for x,y,z in [
        (-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0),
        (-1,-1,0.20),(1,-1,0.20),(0.75,1,1),(-0.75,1,1)]]
    faces = [(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = position
    return finish(obj, name, surface, 0.012)


def assemble(record):
    detailed = record['detailed_builder']
    if detailed:
        {'cpu':cpu,'solar':solar,'air':air,'hydroponics':hydroponics,'hydration':hydration}[detailed](detailed_materials())
        return
    palette = materials(record['culture'])
    for part in record['parts']:
        kind, name = part['kind'], part['name']
        surface = palette[part['material']]
        position = part.get('position', [0,0,0])
        if kind == 'box':
            box(name, position, part['size'], surface, 0.014).rotation_euler = part['rotation']
        elif kind == 'lathe':
            profile = [(z+position[2],radius) for z,radius in part['profile']]
            obj = lathe(name, profile, surface, position[:2], part['segments'])
            sharp = obj.modifiers.new('Preserve industrial profile breaks','EDGE_SPLIT')
            sharp.split_angle = math.radians(32)
            sharp.use_edge_angle = True
        elif kind == 'dome':
            dome(name, part['radius'], part['height'], position[2], surface, position[:2])
        elif kind == 'sphere':
            if part['faceted']:
                bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1, location=position)
            else:
                bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=1, location=position)
            obj = bpy.context.object
            obj.scale = part['size']
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            finish(obj, name, surface, 0)
            for polygon in obj.data.polygons:
                polygon.use_smooth = not part['faceted']
        elif kind == 'rod':
            beam(name, part['start'], part['end'], part['radius'], surface)
        elif kind == 'ring':
            arc(name, part['radius'], position[2], surface, position[:2], part['tube'])
        elif kind == 'wedge':
            wedge(name, position, part['size'], surface)
        else:
            raise ValueError('Unknown authored primitive ' + kind)


def evaluated_points(meshes):
    graph = bpy.context.evaluated_depsgraph_get()
    bpy.context.view_layer.update()
    return [evaluated.matrix_world @ Vector(corner) for obj in meshes
            for evaluated in [obj.evaluated_get(graph)] for corner in evaluated.bound_box]


def fit_camera(scene, points, direction):
    low = Vector(tuple(min(point[axis] for point in points) for axis in range(3)))
    high = Vector(tuple(max(point[axis] for point in points) for axis in range(3)))
    centre = (low + high) / 2
    offset = Vector(direction).normalized() * 20
    scene.camera.location = centre + offset
    scene.camera.rotation_euler = (-offset).to_track_quat('-Z','Y').to_euler()
    inverse = scene.camera.rotation_euler.to_matrix().transposed()
    projected = [inverse @ (point-centre) for point in points]
    span = [max(point[axis] for point in projected)-min(point[axis] for point in projected) for axis in [0,1]]
    # A world-space bounding-box centre need not centre an oblique projection.
    screen_centre = Vector(tuple((max(point[axis] for point in projected)+min(point[axis] for point in projected))/2 for axis in [0,1])+(0,))
    scene.camera.location += scene.camera.rotation_euler.to_matrix() @ screen_centre
    scene.camera.data.type = 'ORTHO'
    scene.camera.data.ortho_scale = max(span) * 1.23
    scene.camera.data.clip_end = 100
    return low, high
