"""Preserve existing studies and replace thin gold forks with tapered crown arms."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
TEXTURES = ROOT/'sources/materials/reconstruction/rigellian-refined/crowns'
CASES = {
    'ri01': ('040', 'central-unit', (0, 0, 2.81), 1.25, .30),
    'ri04': ('043', 'community', (0, 0, 2.76), .85, .24),
    'ri05': ('044', 'health-unit', (0, 0, 2.72), .92, .21),
    'ri06': ('045', 'strategic-bunker', (0, 0, 3.98), .99, .18),
    'ri17': ('056', 'arms-unit', (-.55, -.50, 1.40), .92, .17),
}
VIEWS = {'front-quarter': (6, -13, 8), 'front': (0, -16, 4),
         'side': (16, 0, 4), 'crown-detail': (2, -12, 3)}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def folders(key):
    rel = Path('docs/assets/reconstruction/rigellian-refined')/key
    return ROOT/'sources'/rel, ROOT/'gallery/media'/rel


def source(key):
    return ROOT/'sources/docs/assets/reconstruction/buildings/rigellian'/CASES[key][1]/'model.blend'


def wear_material():
    TEXTURES.mkdir(parents=True, exist_ok=True)
    mat = bpy.data.materials.new('Rigellian refined crown | aged conductor brass')
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Metallic'].default_value = .76
    coord = mat.node_tree.nodes.new('ShaderNodeTexCoord')
    for kind, socket in [('colour', 'Base Color'), ('roughness', 'Roughness')]:
        path = TEXTURES/(kind+'.png')
        if not path.is_file():
            size = 256
            image = bpy.data.images.new('Authored crown '+kind, width=size, height=size)
            rng = random.Random(185)
            pixels = []
            for y in range(size):
                for x in range(size):
                    u, v = x/(size-1), y/(size-1)
                    stain = .12*math.exp(-((v-.10)/.12)**2)*(1+.3*math.sin(u*27))
                    grain = .022*math.sin(u*79+v*21)+rng.uniform(-.025, .025)
                    scratch = .16 if x in [28, 29, 114, 188] and 75 < y < 145 else 0
                    value = .91+grain-stain+scratch
                    rgb = [c*value for c in (.46, .29, .085)] if kind == 'colour' else [min(.85, .52+stain-grain-scratch)]*3
                    pixels.extend([*rgb, 1])
            image.pixels.foreach_set(pixels)
            image.filepath_raw = str(path)
            image.file_format = 'PNG'
            image.save()
        image = bpy.data.images.load(str(path), check_existing=True)
        image.colorspace_settings.name = 'sRGB' if kind == 'colour' else 'Non-Color'
        image.pack()
        tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = image
        mat.node_tree.links.new(coord.outputs['UV'], tex.inputs['Vector'])
        mat.node_tree.links.new(tex.outputs['Color'], shader.inputs[socket])
    return mat


def arm(name, sign, centre, height, spread, material, parent):
    # Broad lower cheeks, narrow tips and an actual open interval beside the
    # central stem. This replaces the former constant-section bent wire.
    sections = [(0, .10, .38), (.10, .18, .70), (.24, .38, 1.00),
                (.41, .56, 1.06), (.57, .61, 1.00), (.72, .65, .90),
                (.80, .70, .82)]
    vertices = []
    for z, inner, outer in sections:
        thickness = spread*(.30-.12*z)
        dent = height*.0018*math.exp(-((z-.41)/.16)**2)
        for x, y in [(inner, -1), (outer, -1), (outer, 1), (inner, 1)]:
            vertices.append((centre[0]+sign*x*spread,
                             centre[1]+y*thickness/2+(dent if y < 0 else 0),
                             centre[2]+z*height))
    faces = [(3, 2, 1, 0)]
    for i in range(len(sections)-1):
        for n in range(4):
            faces.append((i*4+n, i*4+(n+1)%4, (i+1)*4+(n+1)%4, (i+1)*4+n))
    faces.append(tuple((len(sections)-1)*4+n for n in range(4)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    obj.parent = parent
    uv = mesh.uv_layers.new(name='Independent conductor wear')
    for poly in mesh.polygons:
        for index in poly.loop_indices:
            p = mesh.vertices[mesh.loops[index].vertex_index].co
            uv.data[index].uv = ((abs(p.x-centre[0])/spread), (p.z-centre[2])/height)
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new('Worn small casting edge radius', 'BEVEL')
    modifier.width = height*.004
    modifier.segments = 3
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj['refinement'] = 'Tapered gold crown arm; broad lower cheek, narrow tip, localized geometric dent'
    return obj


def ri17_stem(centre, height, material, parent):
    # The original model had only one bulb and spike: replace it with the
    # continuous middle stem of the source-backed three-prong crown.
    bpy.ops.mesh.primitive_cone_add(vertices=48, radius1=.085, radius2=.020,
                                   depth=height, location=(centre[0], centre[1], centre[2]+height/2))
    obj = bpy.context.object
    obj.name = 'RI17 refined crown central stem'
    obj.data.materials.append(material)
    obj.parent = parent
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    # Fix the native tessellation before export: a tapered UV quad otherwise
    # receives a different diagonal in Cycles and glTF's required triangles.
    bpy.context.view_layer.objects.active = obj
    modifier = obj.modifiers.new('Consistent tapered stem tessellation', 'TRIANGULATE')
    modifier.keep_custom_normals = True
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def fit_camera(direction, selected):
    scene = bpy.context.scene
    points = [obj.matrix_world@Vector(p) for obj in selected for p in obj.bound_box]
    centre = (Vector([min(p[i] for p in points) for i in range(3)])+
              Vector([max(p[i] for p in points) for i in range(3)]))/2
    direction = Vector(direction).normalized()
    camera = scene.camera
    camera.location = centre+direction*15
    camera.rotation_euler = (-direction).to_track_quat('-Z', 'Y').to_euler()
    camera.data.type = 'ORTHO'
    bpy.context.view_layer.update()
    projected = [camera.matrix_world.inverted()@p for p in points]
    camera.data.ortho_scale = max(max(p.x for p in projected)-min(p.x for p in projected),
                                  max(p.y for p in projected)-min(p.y for p in projected))*1.18


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', choices=CASES, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    key = args.model
    id_number, _, centre, height, spread = CASES[key]
    output, media = folders(key)
    output.mkdir(parents=True, exist_ok=True)
    media.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source(key)))
    scene = bpy.context.scene
    root = bpy.data.objects['PlacementRoot']
    removed = []
    for obj in list(scene.objects):
        if (any(term in obj.name for term in ['crown outer conductor', 'crown side terminal']) or
                (key == 'ri17' and obj.name == 'RI17 bronze mast head')):
            removed.append(obj.name)
            bpy.data.objects.remove(obj, do_unlink=True)
    assert removed, key
    mat = wear_material()
    new_parts = [arm(key.upper()+' refined crown arm '+side, sign, centre, height, spread, mat, root)
                 for sign, side in [(-1, 'left'), (1, 'right')]]
    if key == 'ri17':
        ri17_stem(centre, height, mat, root)
        new_parts.append(bpy.context.object)
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.film_transparent = True
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 32
    meshes = [obj for obj in scene.objects if obj.type == 'MESH']
    fit_camera(VIEWS['front-quarter'], meshes)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH', 'EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'), export_format='GLB',
                             use_selection=True, export_extras=True, export_apply=True, export_animations=False)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'))
    for name, direction in VIEWS.items():
        crown = [obj for obj in meshes if 'crown' in obj.name.lower()]
        fit_camera(direction, crown if name == 'crown-detail' else meshes)
        scene.render.filepath = str(media/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    meta = dict(issue=185, id='openfa:building/legacy/'+id_number, culture='rigellian',
                stage='crown-refinement-study', source_study=source(key).relative_to(ROOT).as_posix(),
                source_blend_sha256=sha(source(key)), blend_sha256=sha(output/'model.blend'),
                glb_sha256=sha(output/'model.glb'), generator_sha256=sha(Path(__file__)),
                removed_objects=removed, added_objects=[obj.name for obj in new_parts],
                authored_dimensions=dict(centre=centre, height=height, spread=spread),
                observed=['Broad gold lateral crown arms taper toward their tips',
                          'Central stem projects higher than lateral arms'],
                inferred=['Exact arm sections, hidden thickness, absolute dimensions and wear'],
                preserved='Existing body, materials, openings, fittings, hierarchy and earlier files',
                views=list(VIEWS), blender=bpy.app.version_string,
                acceptance='Verified study pending rendered review; final artistic acceptance remains open')
    (output/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('RIGELLIAN_CROWN_REFINED', key, len(meshes), flush=True)


if __name__ == '__main__':
    main()
