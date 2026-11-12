"""RI20: restore readable shoulder, lower ribbed mechanism and recessed service faces."""
import json
import math
from pathlib import Path
import sys
import random

import bmesh
import bpy
from mathutils import Vector
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from refine_rigellian_crowns import fit_camera, sha

ROOT = Path(__file__).resolve().parents[3]
REL = Path('docs/assets/reconstruction/rigellian-refined/ri20')
OUTPUT = ROOT/'sources'/REL
MEDIA = ROOT/'gallery/media'/REL
SOURCE = ROOT/'sources/docs/assets/reconstruction/buildings/rigellian/extractor/model.blend'
COAT = ROOT/'sources/materials/reconstruction/rigellian-refined/ri20/bronze-green-finish.png'
PROFILE = [(.42, .385), (.46, .52), (.51, .585), (.62, .60), (1.03, .59),
           (1.12, .55), (1.20, .465), (1.53, .45), (1.66, .425),
           (1.77, .355), (1.85, .26), (1.91, .15), (1.94, .035)]
VIEWS = {'front-quarter': (6, -13, 8), 'rear-quarter': (-7, 12, 7),
         'front': (0, -16, 5), 'side': (16, 0, 4), 'top': (0, -.01, 20),
         'mechanism-detail': (4, -13, 5)}


def radius(z):
    return next(a+(b-a)*(z-za)/(zb-za)
                for (za, a), (zb, b) in zip(PROFILE, PROFILE[1:]) if za <= z <= zb)


def surface_finish(original):
    # Coherent visible colour regions, not extra solid pipes invented from
    # ambiguous green pixels. All masks are independently authored functions.
    material = original.copy()
    material.name = 'RI20 refined | bronze and green surface finish'
    shader = material.node_tree.nodes.get('Principled BSDF')
    node = shader.inputs['Base Color'].links[0].from_node
    old = node.image
    pixels = np.empty(len(old.pixels), dtype=np.float32)
    old.pixels.foreach_get(pixels)
    pixels = pixels.reshape((old.size[1], old.size[0], 4))
    size = 512
    yy, xx = np.mgrid[:size, :size]/(size-1)
    angles, heights = xx*math.tau-math.pi, yy*3
    mask = np.zeros((size, size))
    rng = random.Random(18520)
    for _ in range(64):
        phi, z = -1.75+rng.uniform(-.52, .52), rng.uniform(.57, 1.89)
        delta = np.arctan2(np.sin(angles-phi), np.cos(angles-phi))
        blob = np.exp(-2*(delta/rng.uniform(.07, .15))**4-2*((heights-z)/rng.uniform(.025, .07))**4)
        mask = np.maximum(mask, blob)
    mask = np.clip((mask-.15)/.40, 0, .55)
    base = pixels[np.linspace(0, old.size[1]-1, size).astype(int)[:, None],
                  np.linspace(0, old.size[0]-1, size).astype(int)[None, :]].copy()
    green = np.stack([.245+.018*np.sin(xx*71+yy*39), .35+.02*np.sin(xx*63-yy*51), .27+.015*np.sin(xx*47+yy*67)], axis=-1)
    base[:, :, :3] = base[:, :, :3]*(1-mask[:, :, None])+green*mask[:, :, None]
    image = bpy.data.images.new('RI20 independently authored bronze-green finish', width=size, height=size)
    image.pixels.foreach_set(base.ravel())
    COAT.parent.mkdir(parents=True, exist_ok=True)
    image.filepath_raw = str(COAT)
    image.file_format = 'PNG'
    image.save()
    image = bpy.data.images.load(str(COAT), check_existing=False)
    image.colorspace_settings.name = 'sRGB'
    image.pack()
    node.image = image
    return material


def uv_for(obj):
    mesh = obj.data
    if not mesh.uv_layers:
        mesh.uv_layers.new()
    uv = mesh.uv_layers.active
    uv.name = 'Authored surface wear'
    for face in mesh.polygons:
        values = []
        for loop in face.loop_indices:
            point = mesh.vertices[mesh.loops[loop].vertex_index].co
            values.append((math.atan2(point.y, point.x)+math.pi)/math.tau)
        wraps = max(values)-min(values) > .5
        for index, u in zip(face.loop_indices, values):
            p = mesh.vertices[mesh.loops[index].vertex_index].co
            uv.data[index].uv = (u+1 if wraps and u < .5 else u, p.z/3)


def mesh(name, vertices, faces, material, smooth=True):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    bm = bmesh.new()
    bm.from_mesh(data)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(data)
    bm.free()
    obj = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(material)
    for face in data.polygons:
        face.use_smooth = smooth and abs(face.normal.z) < .98
    uv_for(obj)
    return obj


def lathe(name, profile, material, centre=(0, 0), dent=False):
    count = 96
    points = []
    for z, r in profile:
        for i in range(count):
            phi = math.tau*i/count
            depth = .002*math.exp(-((phi-4.6)/.18)**2-((z-.86)/.23)**2) if dent else 0
            points.append((centre[0]+(r-depth)*math.cos(phi), centre[1]+(r-depth)*math.sin(phi), z))
    faces = [tuple(reversed(range(count)))]
    for row in range(len(profile)-1):
        for i in range(count):
            j = (i+1)%count
            faces.append((row*count+i, row*count+j, (row+1)*count+j, (row+1)*count+i))
    faces.append(tuple((len(profile)-1)*count+i for i in range(count)))
    return mesh(name, points, faces, material)


def box(name, centre, dimensions, material, bevel=.012):
    bpy.ops.mesh.primitive_cube_add(size=1, location=centre)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    obj.data.materials.append(material)
    obj.data.uv_layers.active.name = 'Authored surface wear'
    if bevel:
        mod = obj.modifiers.new('Soft cast housing edges', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        bpy.ops.object.modifier_apply(modifier=mod.name)
    return obj


def cylinder(name, centre, r, depth, material, normal=(0, 0, 1)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=r, depth=depth, location=centre)
    obj = bpy.context.object
    obj.name = name
    obj.rotation_euler = Vector(normal).to_track_quat('Z', 'Y').to_euler()
    obj.data.materials.append(material)
    obj.data.uv_layers.active.name = 'Authored surface wear'
    for face in obj.data.polygons:
        face.use_smooth = len(face.vertices) == 4
    return obj


def patch(name, phi, width, low, high, material, lift=.008, depth=.020):
    # A closed, body-following panel/rim; its root intersects the casing rather
    # than leaving floating planar trim on the rounded shoulder.
    angles = [phi-width/2+width*i/8 for i in range(9)]
    heights = [low+(high-low)*i/6 for i in range(7)]
    points = []
    for offset in [lift-depth, lift]:
        for z in heights:
            for a in angles:
                r = radius(z)+offset
                points.append((r*math.cos(a), r*math.sin(a), z))
    layer = len(angles)*len(heights)
    faces = []
    for row in range(6):
        for col in range(8):
            a = row*9+col
            faces.extend([(a, a+1, a+10, a+9), (a+layer, a+9+layer, a+10+layer, a+1+layer)])
    perimeter = list(range(9))+[i*9+8 for i in range(1, 7)]+list(range(61, 53, -1))+[i*9 for i in range(5, 0, -1)]
    for i, a in enumerate(perimeter):
        b = perimeter[(i+1)%len(perimeter)]
        faces.append((a, a+layer, b+layer, b))
    return mesh(name, points, faces, material)


def cut_slot(body, index, phi, material, bronze):
    normal = Vector((math.cos(phi), math.sin(phi), 0))
    centre = normal*.59+Vector((0, 0, .82))
    cutter = box('Temporary real slot cutter', centre, (.080, .21, .43), material, .024)
    cutter.rotation_euler.z = phi-math.pi/2
    bpy.context.view_layer.objects.active = body
    mod = body.modifiers.new('Actual recessed front service slot', 'BOOLEAN')
    mod.operation = 'DIFFERENCE'
    mod.solver = 'EXACT'
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    backing = box(f'RI20 slot {index} recessed backing', normal*.488+Vector((0, 0, .82)), (.077, .045, .40), material, .012)
    backing.rotation_euler.z = phi-math.pi/2
    for side in [-1, 1]:
        patch(f'RI20 slot {index} cast side rim {side}', phi+side*.090, .035, .60, 1.04, bronze)
    for z in [.595, 1.025]:
        patch(f'RI20 slot {index} cast end rim {z}', phi, .19, z, z+.022, bronze)


def build(materials):
    m = materials
    body = lathe('RI20 stepped main casing', PROFILE, m['body'], dent=True)
    lathe('RI20 exposed lower mechanism core', [(.02, .25), (.06, .29), (.42, .29), (.47, .35)], m['dark'])
    for i, z in enumerate([.095, .225, .355]):
        lathe(f'RI20 lower mechanism broad rib {i}', [(z-.035, .27), (z-.022, .345),
              (z+.018, .345), (z+.035, .29)], m['body'])
    for i, phi in enumerate([-2.5, -1.9, -1.3, -.7]):
        cylinder(f'RI20 exposed upper drum contact {i}', (.29*math.cos(phi), .29*math.sin(phi), .405), .033, .15, m['edge'])
    for i, z in enumerate([.10, .22, .34]):
        box(f'RI20 lower green inset {i}', (.285, -.245, z), (.10, .09, .108), m['green'], .016)
    for i, x in enumerate([.22, .35]):
        box(f'RI20 lower fitting retainer {i}', (x, -.23, .22), (.025, .08, .40), m['edge'], .006)
    side_profile = [(.51, .08), (.56, .165), (.64, .19), (1.04, .19), (1.11, .15), (1.15, .07)]
    lathe('RI20 pronounced side equipment pod', side_profile, m['body'], centre=(-.53, -.10), dent=True)
    for i, z in enumerate([.70, .96]):
        p = Vector((-.53, -.288, z))
        cylinder(f'RI20 side pod dark seat {i}', p, .054, .040, m['dark'], (0, -1, 0))
        cylinder(f'RI20 side pod gold fitting {i}', p+Vector((0, -.018, 0)), .039, .025, m['edge'], (0, -1, 0))
    for i, phi in enumerate([-1.23, -.94]):
        cut_slot(body, i, phi, m['dark'], m['edge'])
    for i, z in enumerate([.66, .84, 1.02]):
        phi = -2.02
        normal = Vector((math.cos(phi), math.sin(phi), 0))
        p = normal*(radius(z)+.01)+Vector((0, 0, z))
        cylinder(f'RI20 forward gold boss {i}', p, .044, .040, m['edge'], normal)
        cylinder(f'RI20 forward boss dark seat {i}', p-normal*.014, .054, .018, m['dark'], normal)
    phi, z = -1.96, 1.54
    n = Vector((math.cos(phi), math.sin(phi), .04)).normalized()
    p = Vector((radius(z)*math.cos(phi), radius(z)*math.sin(phi), z))
    cylinder('RI20 upper inspection bezel', p+n*.012, .112, .050, m['retainer'], n)
    cylinder('RI20 upper gold inspection face', p+n*.038, .085, .024, m['edge'], n)
    for i, phi in enumerate([-1.35, -1.04]):
        patch(f'RI20 upper dark inset {i}', phi, .14, 1.48, 1.60, m['dark'], lift=.002, depth=.025)
    # Green marks in legacy are ambiguous: retain patinated surface colour from
    # the authored source maps instead of inventing an external pipe network.
    return body


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    MEDIA.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene = bpy.context.scene
    names = {'body': 'weathered bronze casing', 'green': 'aged green lower alloy',
             'edge': 'worn brass fittings', 'dark': 'recessed dark insets',
             'retainer': 'dark bronze retaining alloy'}
    materials = {key: bpy.data.materials['RI20 | '+suffix] for key, suffix in names.items()}
    materials['body'] = surface_finish(materials['body'])
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA', 'LIGHT']:
            bpy.data.objects.remove(obj, do_unlink=True)
    build(materials)
    root = bpy.data.objects.new('PlacementRoot', None)
    scene.collection.objects.link(root)
    root['catalogue_id'] = 'openfa:building/legacy/059'
    root['footprint_width'] = root['footprint_height'] = 2
    meshes = [obj for obj in scene.objects if obj.type == 'MESH']
    for obj in meshes:
        obj.parent = root
        bpy.context.view_layer.objects.active = obj
        triangulate = obj.modifiers.new('Explicit portable surface tessellation', 'TRIANGULATE')
        triangulate.keep_custom_normals = True
        bpy.ops.object.modifier_apply(modifier=triangulate.name)
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.file_format = 'PNG'
    if scene.render.engine == 'CYCLES':
        scene.cycles.samples = 40
    fit_camera(VIEWS['front-quarter'], meshes)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT/'model.glb'), export_format='GLB', use_selection=True,
                             export_apply=True, export_extras=True, export_animations=False)
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUTPUT/'model.blend'))
    for name, direction in VIEWS.items():
        selected = [obj for obj in meshes if any(w in obj.name for w in ['lower', 'drum', 'slot'])] if name == 'mechanism-detail' else meshes
        fit_camera(direction, selected)
        scene.render.filepath = str(MEDIA/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    meta = dict(issue=185, id='openfa:building/legacy/059', culture='rigellian', name='Extractor', footprint=[2, 2],
                stage='structural-detail-refinement', source_study=SOURCE.relative_to(ROOT).as_posix(),
                source_blend_sha256=sha(SOURCE), blend_sha256=sha(OUTPUT/'model.blend'), glb_sha256=sha(OUTPUT/'model.glb'),
                generator_sha256=sha(Path(__file__)), camera_helper_sha256=sha(Path(__file__).with_name('refine_rigellian_crowns.py')),
                reference_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-building-references.json'),
                lore_sha256=sha(ROOT/'sources/docs/reconstruction/models/rigellian-lore-evidence.json'),
                observed=['Pronounced lower shoulder and attached side pod', 'Three readable lower horizontal ribs',
                          'Green segmented lower fitting', 'Vertical front slots, gold front fittings and upper inspection feature'],
                inferred=['Exact mechanical sections, depth, backside and dimensions',
                          'Bronze-coloured alloy identity; green patches do not establish plumbing',
                          'Service interpretation of ambiguous fittings; no external drill or operating cycle established'],
                material_policy='Reuse prior independently authored packed roughness/wear, with a new authored visible bronze-green colour treatment; no original-game pixels',
                authored_finish_sha256=sha(COAT),
                culture_policy='Elegant ergonomic integrated mining machinery, consistent with CDB Architecture record 18; alloy identity is not named in Rigellian lore',
                mesh_objects=len(meshes), views=list(VIEWS), blender=bpy.app.version_string,
                acceptance='Structural refinement study; final artistic acceptance and game calibration open')
    (OUTPUT/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('RIGELLIAN_EXTRACTOR_STRUCTURAL_REFINEMENT', len(meshes), flush=True)


if __name__ == '__main__':
    main()
