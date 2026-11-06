"""Detailed PS7C shared core and synchronized construction source (#216).

Original pixels are evidence only. The previous #192 pair remains unchanged.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import tempfile

import bmesh
import bpy
from mathutils import Matrix, Vector

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_federal_transporter import box, finish, frame, mesh, ring, rod, surface
from space_dock_parts import PROFILES
from manufactured_vessels import profile_radius
from ps7c_materials import worn_material

TAU = math.tau
VIEWS = [('front-quarter', (5, -13, 6)), ('legacy-front', (0, -15, 5)),
         ('rear-quarter', (-6, 12, 5)), ('side', (15, 0, 4)), ('top', (0, 0, 20)),
         ('underside', (3, -8, -12))]
XY_REFINEMENT = .78
ROOF_REFINEMENT = .64
MAST_SHIFT = (1.05-.08)*(1-ROOF_REFINEMENT)


def refine_point(name, p):
    """Explicit source geometry edit; no stretched root or renderer correction."""
    p = Vector(p)
    p.x *= XY_REFINEMENT
    p.y *= XY_REFINEMENT
    if 'antenna' in name.lower():
        p.z -= MAST_SHIFT
    elif 'roof' in name.lower() or 'pyramidal upper hull' in name.lower():
        p.z = .08+(p.z-.08)*ROOF_REFINEMENT
    return p


def scaffold_point(p):
    p = Vector(p)
    p.x *= XY_REFINEMENT
    p.y *= XY_REFINEMENT
    if p.z > .12:
        p.z = .12+(p.z-.12)*.82
    return p


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def point(profile, z, fraction, phi, depth):
    r = profile_radius(profile, z)
    n, t = Vector((math.cos(phi), math.sin(phi), 0)), Vector((-math.sin(phi), math.cos(phi), 0))
    p = n*(r*math.cos(math.pi/8)+depth)+t*(fraction*r)
    p.z = z
    return p


def fitted(name, profile, z0, z1, left, right, phi, material, depth=.008):
    # Actual closed plate with an inner face penetrating the source hull.
    vertices = [tuple(point(profile, z, f, phi, d)) for d in [depth, -.012]
                for z, f in [(z0, left), (z0, right), (z1, right), (z1, left)]]
    return mesh(name, vertices, [(0, 1, 2, 3), (7, 6, 5, 4)]+
                [(i, (i+1)%4, (i+1)%4+4, i+4) for i in range(4)], material)


def hull_details(m):
    lower, roof = PROFILES['Space Dock lower tapered hull'], PROFILES['Space Dock pyramidal upper hull']
    for face in range(8):
        phi = -math.pi/2+face*TAU/8
        for region, profile, heights in [('lower', lower, [-2.35, -2.10, -1.75, -1.30, -.90, -.50, -.20, .055]),
                                        ('roof', roof, [.215, .37, .54, .70, .87, 1.015])]:
            fractions = [-.37, -.125, .125, .37]
            for row, (z0, z1) in enumerate(zip(heights, heights[1:])):
                for col, (left, right) in enumerate(zip(fractions, fractions[1:])):
                    style = 'hull' if region == 'roof' else 'steel'
                    if (face+row+col)%5 == 0:
                        style = 'edge' if region == 'roof' else 'hull'
                    if region == 'lower' and col == 1:
                        style = 'dark'
                    fitted(f'PS7C {region} segmented plate {face} {row} {col}', profile,
                           z0+.007, z1-.007, left+.006, right-.006, phi, m[style])
            # Recess-like lamps are physically fitted to the same hull plane.
            for row, z in enumerate(([.30, .61] if region == 'roof' else [-1.70, -1.07, -.57])):
                for k in range(3):
                    f = -.09+k*.09
                    fitted(f'PS7C {region} inspection window {face} {row} {k}', profile,
                           z-.012, z+.012, f-.015, f+.015, phi, m['light'], .017)
            # Real raised seam spines; ends follow the actual profile.
            for f in [-.37, .37]:
                for index, (a, b) in enumerate(zip(heights, heights[1:])):
                    rod(f'PS7C {region} perimeter rib {face} {f} {index}',
                        point(profile, a, f, phi, .013), point(profile, b, f, phi, .013),
                        .009 if region == 'roof' else .014, m['edge'], 8)
        # Lateral equipment slots embedded in the broad dark lower field.
        for index, z in enumerate([-.76, -1.18, -1.55]):
            fitted(f'PS7C lower maintenance recess {face} {index}', lower,
                   z-.045, z+.045, -.20, .20, phi, m['dark'], .021)
            for k in range(5):
                f = -.16+k*.08
                fitted(f'PS7C lower heat grille {face} {index} {k}', lower,
                       z-.03, z+.03, f-.012, f+.012, phi, m['steel'], .028)
        if face%2 == 0:
            # Source red fields are broad and stepped. Hidden repetition is inferred.
            fitted(f'PS7C upper broad red roof field {face}', roof, .70, .86, -.34, .34, phi, m['red'], .025)
            fitted(f'PS7C red roof descending stem {face}', roof, .39, .70, -.115, .115, phi, m['red'], .025)
            for side in [-1, 1]:
                fitted(f'PS7C roof pale identification field {face} {side}', roof,
                       .30, .53, side*.235-.042, side*.235+.042, phi, m['edge'], .022)
    # Equatorial belt has real brackets, inspection openings and amber markers.
    for index in range(32):
        phi = index*TAU/32
        n = Vector((math.cos(phi), math.sin(phi), 0))
        p = n*1.285
        p.z = .105
        part = box(f'PS7C equatorial belt clamp {index}', p, (.055, .065, .065), m['steel'], .008)
        part.rotation_euler.z = phi
        if index%2 == 0:
            light = box(f'PS7C equatorial running light {index}', n*1.315+Vector((0, 0, .11)),
                        (.025, .045, .018), m['light'], .003)
            light.rotation_euler.z = phi


def service_details(m):
    lower = PROFILES['Space Dock lower tapered hull']
    for side in range(4):
        phi = side*math.pi/2
        rot = Matrix.Rotation(phi, 3, 'Z')
        def p(x, y, z):
            return rot@Vector((x, y, z))
        y = -profile_radius(lower, -.48)*math.cos(math.pi/8)
        # Mechanical fork below the pale service housing, visible in original PS7C.
        for sign in [-1, 1]:
            start, end = p(sign*.14, y-.15, -.52), p(sign*.11, y-.15, -.91)
            rod(f'PS7C service fork rail {side} {sign}', start, end, .027, m['edge'])
            rod(f'PS7C service hydraulic shaft {side} {sign}', p(sign*.075, y-.16, -.58),
                p(sign*.06, y-.16, -.85), .012, m['brass'])
            rod(f'PS7C service hinge axle {side} {sign}', p(sign*.11-.025, y-.15, -.88),
                p(sign*.11+.025, y-.15, -.88), .042, m['steel'], 24)
        case = box(f'PS7C service fork lower bridge {side}', p(0, y-.15, -.90), (.23, .10, .075), m['edge'])
        case.rotation_euler.z = phi
        for k in range(4):
            obj = box(f'PS7C service front illuminated segment {side} {k}',
                      p(-.12+k*.08, y-.217, -.47), (.055, .014, .045), m['white'], .004)
            obj.rotation_euler.z = phi
        for k in range(5):
            obj = box(f'PS7C service top cooling slat {side} {k}', p(-.15+k*.075, y-.10, -.35),
                      (.025, .17, .016), m['dark'], .004)
            obj.rotation_euler.z = phi
        # Detailed side berth: a dark end, rim, axial collar and work lights.
        if side not in [0, 2]:
            continue  # The old speculative front berth hid the source-visible service assembly.
        n = Vector((math.cos(phi), math.sin(phi), 0))
        tangent = Vector((-math.sin(phi), math.cos(phi), 0))
        end = n*1.846+Vector((0, 0, -.23))
        rod(f'PS7C berth dark docking mouth {side}', end, end+n*.012, .078, m['dark'], 32)
        obj = ring(f'PS7C berth machined rim {side}', end+n*.018, .087, .012, m['edge'])
        obj.rotation_euler = n.to_track_quat('Z', 'Y').to_euler()
        for sign in [-1, 1]:
            p0 = end+n*.02+tangent*sign*.09+Vector((0, 0, .04))
            rod(f'PS7C berth running lamp {side} {sign}', p0, p0+n*.016, .012, m['white'], 16)
        for k in range(4):
            p0 = n*(1.42+k*.08)+Vector((0, 0, -.105))
            obj = box(f'PS7C berth shoulder armour segment {side} {k}', p0, (.057, .22, .025), m['steel'], .007)
            obj.rotation_euler.z = phi
    # Existing antennas and their tip positions stay intact; add collars and lamps.
    for index, (x, top) in enumerate([(0, 1.90), (-.14, 1.54), (.14, 1.67)]):
        for k in range(4):
            z = 1.09+(top-1.12)*k/4
            ring(f'PS7C antenna insulator {index} {k}', (x, 0, z), .034 if index == 0 else .019,
                 .008, m['brass'] if k == 0 else m['steel'])
        rod(f'PS7C antenna beacon {index}', (x, 0, top-.022), (x, 0, top),
            .012 if index == 0 else .008, m['light'], 16)


def native_meshes():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


def ensure_uv(obj):
    if obj.data.uv_layers:
        return
    uv = obj.data.uv_layers.new(name='PS7C portable service-wear projection')
    coords = [v.co for v in obj.data.vertices]
    low = [min(p[i] for p in coords) for i in range(3)]
    high = [max(p[i] for p in coords) for i in range(3)]
    for face in obj.data.polygons:
        dominant = max(range(3), key=lambda i: abs(face.normal[i]))
        axes = [i for i in range(3) if i != dominant]
        for loop in face.loop_indices:
            p = obj.data.vertices[obj.data.loops[loop].vertex_index].co
            uv.data[loop].uv = tuple((p[i]-low[i])/max(1e-7, high[i]-low[i]) for i in axes)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--variant', choices=['refined', 'construction'], default='refined')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root, variant = args.root.resolve(), args.variant
    texture_temp = root/'artifacts/issue-216/texture-export-temp'
    texture_temp.mkdir(parents=True, exist_ok=True)
    tempfile.tempdir = str(texture_temp)
    out = root/'sources/objects/terran/space-dock'/variant
    media = root/'gallery/media/objects/terran/space-dock'/variant
    textures = root/'sources/materials/terran/space-dock/refined'
    for folder in [out, media, textures]:
        folder.mkdir(parents=True, exist_ok=True)
    source = (root/'sources/docs/assets/reconstruction/orbital-station-refined/terran/space-dock/model.blend'
              if variant == 'refined' else root/'sources/objects/terran/space-dock/refined/model.blend')
    bpy.ops.wm.open_mainfile(filepath=str(source), load_ui=False, use_scripts=False)
    scene = bpy.context.scene
    placement = bpy.data.objects['PlacementRoot']
    assert max(abs(placement.matrix_world[i][j]-(1 if i == j else 0)) for i in range(4) for j in range(4)) < 1e-6
    baseline = set(o.name for o in native_meshes())
    removed = []
    if variant == 'refined':
        for obj in list(native_meshes()):
            obsolete_arm = any(obj.name == f'Space Dock {part} {index}' for index in [1, 3]
                               for part in ['radial arm', 'diagonal brace', 'berth pod', 'berth dark inset', 'berth marker'])
            if obsolete_arm or any(k in obj.name for k in ['broad roof armour field', 'broad dark lower face',
                                                          'broad stepped red roof field', 'roof pale service field']):
                removed.append(obj.name)
                bpy.data.objects.remove(obj, do_unlink=True)
        specs = [('hull', (.27, .30, .32), .72, .44, 0), ('steel', (.13, .16, .18), .76, .51, 0),
                 ('edge', (.43, .46, .48), .78, .40, 0), ('dark', (.025, .032, .040), .45, .60, 0),
                 ('red', (.43, .045, .022), .52, .52, 0), ('brass', (.32, .20, .075), .72, .53, 0),
                 ('light', (.64, .34, .075), .1, .3, 1.7), ('white', (.65, .72, .70), .1, .3, 1.0)]
        materials = {name: worn_material(name, colour, metal, rough, 216+i, textures, glow)
                     for i, (name, colour, metal, rough, glow) in enumerate(specs)}
        for obj in native_meshes():
            name = obj.name.lower()
            style = 'hull'
            if any(s in name for s in ['antenna', 'radial arm', 'diagonal brace', 'rim']):
                style = 'steel'
            if any(s in name for s in ['dark', 'slot', 'lower tapered hull']):
                style = 'dark'
            if any(s in name for s in ['pale', 'service case']):
                style = 'edge'
            if any(s in name for s in ['fastener', 'marker', 'sensor']):
                style = 'brass'
            obj.data.materials.clear()
            obj.data.materials.append(materials[style])
        hull_details(materials)
        service_details(materials)
        for obj in native_meshes():
            if obj.name not in baseline:
                obj.parent = placement
                bpy.context.view_layer.objects.active = obj
                for modifier in list(obj.modifiers):
                    bpy.ops.object.modifier_apply(modifier=modifier.name)
                bm = bmesh.new()
                bm.from_mesh(obj.data)
                bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
                bm.to_mesh(obj.data)
                bm.free()
        # The old station projected ~30% too wide. Re-author its actual cross-section
        # and roof pitch against PS7C, keeping the placement root rigid and unit-scale.
        for obj in native_meshes():
            world = obj.matrix_world.copy()
            for vertex in obj.data.vertices:
                vertex.co = refine_point(obj.name, world@vertex.co)
            obj.matrix_world = Matrix.Identity(4)
            obj.data.update()
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
            bm.to_mesh(obj.data)
            bm.free()
        for obj in scene.objects:
            if obj.name.startswith('Equipment '):
                position = obj.matrix_world.translation.copy()
                position.x *= XY_REFINEMENT
                position.y *= XY_REFINEMENT
                if obj.name == 'Equipment crown':
                    position.z -= MAST_SHIFT
                obj.matrix_world.translation = position
    else:
        old = root/'sources/docs/assets/reconstruction/orbital-station-construction/terran/space-dock/model.blend'
        with bpy.data.libraries.load(str(old), link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects if name.startswith('Space Dock construction')
                               or name.startswith('Space Dock temporary shield') or name == 'ConstructionWorkCarriage']
        for obj in data_to.objects:
            scene.collection.objects.link(obj)
            if obj.name == 'ConstructionWorkCarriage' or obj.parent is None or obj.parent.name.startswith('PlacementRoot'):
                obj.parent = placement
            if obj.type == 'MESH':
                for index, old_material in enumerate(obj.data.materials):
                    style = old_material.name.rsplit(' | ', 1)[-1]
                    replacement = {'frame': 'edge', 'cover': 'steel', 'hull': 'hull',
                                   'marker': 'light', 'recess': 'dark', 'red': 'red'}.get(style)
                    assert replacement, (obj.name, old_material.name)
                    obj.data.materials[index] = bpy.data.materials['PS7C '+replacement]
        bpy.context.view_layer.update()
        for obj in data_to.objects:
            if obj.type == 'MESH' and not obj.name.startswith('Space Dock construction carriage '):
                world = obj.matrix_world.copy()
                for vertex in obj.data.vertices:
                    vertex.co = scaffold_point(world@vertex.co)
                obj.matrix_world = Matrix.Identity(4)
                obj.data.update()
            elif obj.type == 'MESH':
                obj.data.transform(Matrix.Diagonal((XY_REFINEMENT, XY_REFINEMENT, 1, 1)))
                obj.location.x *= XY_REFINEMENT
                obj.location.y *= XY_REFINEMENT
        actor = scene.objects.get('ConstructionWorkCarriage')
        actor.location.y *= XY_REFINEMENT
        for track in actor.animation_data.nla_tracks:
            for strip in track.strips:
                for curve in strip.action.fcurves:
                    if curve.data_path == 'location' and curve.array_index == 0:
                        for key in curve.keyframe_points:
                            key.co.y *= XY_REFINEMENT
                            key.handle_left.y *= XY_REFINEMENT
                            key.handle_right.y *= XY_REFINEMENT
        scene.frame_start, scene.frame_end, scene.render.fps = 1, 181, 30
        assert scene.objects.get('ConstructionWorkCarriage').animation_data.nla_tracks
    for collection in bpy.data.collections:
        if collection.asset_data:
            collection.asset_clear()
    collection = bpy.data.collections.new('PS7C detailed '+variant)
    scene.collection.children.link(collection)
    for obj in list(scene.objects):
        if obj.type in ['MESH', 'EMPTY']:
            collection.objects.link(obj)
            for old_collection in list(obj.users_collection):
                if old_collection != collection:
                    old_collection.objects.unlink(obj)
    collection.asset_mark()
    collection.asset_data.description = 'PS7C detailed shared core; '+variant+' state'
    for material in list(bpy.data.materials):
        if material.users == 0:
            bpy.data.materials.remove(material)
    for image in list(bpy.data.images):
        if image.users == 0:
            bpy.data.images.remove(image)
    for obj in native_meshes():
        ensure_uv(obj)
    placement['variant'], placement['legacy_sprite_frame'] = variant, int(variant == 'construction')
    scene.frame_set(1)
    scene.render.engine = 'CYCLES'
    scene.cycles.samples, scene.cycles.use_denoising = 32, True
    scene.render.resolution_x = scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format, scene.render.image_settings.color_mode = 'PNG', 'RGBA'
    objects = native_meshes()
    bpy.context.view_layer.update()
    for name, direction in VIEWS:
        frame(scene, objects, direction)
        scene.render.filepath = str(media/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    frame(scene, objects, VIEWS[0][1])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in scene.objects:
        if obj.type in ['MESH', 'EMPTY']:
            obj.select_set(True)
    bpy.context.view_layer.objects.active = placement
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'), export_format='GLB', use_selection=True,
                              export_apply=True, export_extras=True, export_animations=variant == 'construction',
                              export_animation_mode='NLA_TRACKS', export_frame_range=True)
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(bpy.path.abspath(image.filepath), start=str(out))
    scene.render.filepath = bpy.path.relpath(str(media/'front-quarter.png'), start=str(out))
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'), compress=True)
    meta = dict(issue=216, id='openfa:space-dock', culture='terran', variant=variant,
                stage='ps7c-detailed-refinement' if variant == 'refined' else 'ps7c-detailed-construction',
                source=source.relative_to(root).as_posix(), source_sha256=sha(source),
                blend_sha256=sha(out/'model.blend'), glb_sha256=sha(out/'model.glb'),
                generator_sha256=sha(Path(__file__)), helper_sha256=sha(Path(__file__).with_name('build_federal_transporter.py')),
                material_generator_sha256=sha(Path(__file__).with_name('ps7c_materials.py')),
                meshes=len(objects), core_meshes=len(baseline)-len(removed) if variant == 'construction' else len(objects),
                removed_obsolete_surface_fields=removed, retained_source_parts=sorted(baseline-set(removed)),
                views=[name for name, _ in VIEWS], sockets='Four Equipment empties follow refined cross-section; crown follows lower roof; authored/uncalibrated',
                source_geometry_refinement=dict(xy_cross_section=XY_REFINEMENT, roof_height_factor=ROOF_REFINEMENT,
                                                mast_and_crown_shift=-MAST_SHIFT, root_scale=[1, 1, 1]),
                construction_refinement=dict(shared_core='Exact refined finished geometry; never a separately refined duplicate',
                                             scaffold_xy=XY_REFINEMENT, scaffold_upper_z_factor=.82,
                                             carriage_span=.28*XY_REFINEMENT, clip_seconds=6),
                legacy='PS7C.256 frames 0/1; original one-view states, no recovered operating cycle',
                detail_reference='User-provided station artwork; additional surface/equipment detail, not a recovered second legacy viewpoint',
                animations=['ConstructionActivity'] if variant == 'construction' else [],
                wear='Portable packed seeded colour maps; source grime, fine scratches, stains, rubbed seams and retained original small dents',
                limitations=['Hidden sides, exact berth symmetry and small service details are authored',
                             'Game-client placement, GPU shading, size and equipment calibration require integration review'],
                blender=bpy.app.version_string)
    (out/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('PS7C_DETAIL_BUILT', variant, len(objects), flush=True)


if __name__ == '__main__':
    main()
