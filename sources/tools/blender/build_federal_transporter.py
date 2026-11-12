"""IS0C Federal Transporter: independent detailed geometry, portable authored wear.

Run in Blender: --background --python this_file -- --root ASSET_REPOSITORY
No original image, geometry or texture is read by the generator.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Vector

TAU = math.tau
ID = 'openfa:federal-transporter'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def surface(name, colour, metallic, roughness, seed, textures, glow=0):
    """Real portable colour maps: grime, rubbed seams, stains and fine scratches."""
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*colour, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (*colour, 1)
    shader.inputs['Metallic'].default_value = metallic
    shader.inputs['Roughness'].default_value = roughness
    if glow:
        shader.inputs['Emission Color'].default_value = (*colour, 1)
        shader.inputs['Emission Strength'].default_value = glow
        return mat
    rng = np.random.default_rng(seed)
    size = 512
    yy, xx = np.mgrid[:size, :size] / size
    value = .90 + rng.normal(0, .025, (size, size))
    edge = np.minimum.reduce([xx, yy, 1-xx, 1-yy])
    value -= .18*np.exp(-edge*70)
    for _ in range(24):
        cx, cy = rng.random(2)
        sx, sy = rng.uniform(.012, .08, 2)
        value -= rng.uniform(.025, .13)*np.exp(-((xx-cx)/sx)**2-((yy-cy)/sy)**2)
    for _ in range(180):
        x, y = rng.integers(8, size-8, 2)
        length = int(rng.integers(2, 19))
        value[y, x:min(size, x+length)] += rng.uniform(.04, .20)
        if y+1 < size:
            value[y+1, x:min(size, x+length)] -= .045
    pixels = np.ones((size, size, 4), dtype=np.float32)
    pixels[:, :, :3] = np.clip(value[:, :, None]*np.array(colour), 0, 1)
    image = bpy.data.images.new(name+' authored service wear', size, size, alpha=True)
    image.pixels.foreach_set(pixels.ravel())
    image.filepath_raw = str(textures / (name+'.png'))
    image.file_format = 'PNG'
    image.save()
    image.pack()
    node = mat.node_tree.nodes.new('ShaderNodeTexImage')
    node.image = image
    mat.node_tree.links.new(node.outputs['Color'], shader.inputs['Base Color'])
    return mat


def finish(obj, name, mat, bevel=0):
    obj.name = name
    obj.data.materials.append(mat)
    if bevel:
        mod = obj.modifiers.new('Machined edge radii', 'BEVEL')
        mod.width = bevel
        mod.segments = 3
        obj.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
    if not obj.data.uv_layers:
        uv = obj.data.uv_layers.new(name='Manufactured panel wear UV')
        for face in obj.data.polygons:
            axis = max(range(3), key=lambda i: abs(face.normal[i]))
            axes = [i for i in range(3) if i != axis]
            coords = [v.co for v in obj.data.vertices]
            low = [min(p[i] for p in coords) for i in axes]
            high = [max(p[i] for p in coords) for i in axes]
            for loop in face.loop_indices:
                p = obj.data.vertices[obj.data.loops[loop].vertex_index].co
                uv.data[loop].uv = tuple((p[i]-low[j])/max(1e-7, high[j]-low[j]) for j, i in enumerate(axes))
    return obj


def box(name, p, size, mat, bevel=.018):
    bpy.ops.mesh.primitive_cube_add(size=1, location=p)
    obj = bpy.context.object
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, bevel)


def rod(name, a, b, radius, mat, vertices=16):
    delta = Vector(b)-Vector(a)
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=delta.length,
                                       location=(Vector(a)+Vector(b))/2)
    obj = bpy.context.object
    obj.rotation_euler = delta.to_track_quat('Z', 'Y').to_euler()
    return finish(obj, name, mat, min(.009, radius*.15))


def ring(name, p, major, minor, mat, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_segments=64, minor_segments=10,
                                    location=p, major_radius=major, minor_radius=minor, rotation=rotation)
    obj = finish(bpy.context.object, name, mat)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    return obj


def mesh(name, vertices, faces, mat):
    data = bpy.data.meshes.new(name)
    data.from_pydata(vertices, [], faces)
    data.update()
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    return finish(obj, name, mat)


def shell_panel(name, x, t0, t1, p0, p1, mat):
    """Closed curved plate following the spherical pressure shell, with real seam gaps."""
    verts = []
    nu, nv = 5, 5
    for radius in [1.052, 1.040]:
        for i in range(nv+1):
            t = t0+(t1-t0)*i/nv
            for j in range(nu+1):
                p = p0+(p1-p0)*j/nu
                dent = .007*math.exp(-((t-(t0+t1)/2)/.07)**2-((p-(p0+p1)/2)/.06)**2)
                r = radius-dent
                verts.append((x+r*math.sin(t)*math.cos(p),
                              r*.88*math.sin(t)*math.sin(p), r*math.cos(t)))
    count = (nu+1)*(nv+1)
    faces = []
    for i in range(nv):
        for j in range(nu):
            k = i*(nu+1)+j
            q = (k, k+nu+1, k+nu+2, k+1)
            faces.extend([q, tuple(v+count for v in reversed(q))])
    outline = list(range(nu+1))+[i*(nu+1)+nu for i in range(1, nv+1)]
    outline += [nv*(nu+1)+j for j in range(nu-1, -1, -1)]
    outline += [i*(nu+1) for i in range(nv-1, 0, -1)]
    faces += [(a, a+count, b+count, b) for a, b in zip(outline, outline[1:]+outline[:1])]
    obj = mesh(name, verts, faces, mat)
    for poly in obj.data.polygons[:nu*nv*2]:
        poly.use_smooth = True
    return obj


def pod(index, x, m):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64, ring_count=32, location=(x, 0, 0))
    hull = bpy.context.object
    hull.scale = (1.032, .908, 1.032)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    finish(hull, f'Cargo {index} pressure hull', m['dark'])
    for p in hull.data.polygons:
        p.use_smooth = True
    levels = [.04, .48, .94, 1.40, 1.74, 2.22, 2.70, math.pi-.04]
    for row, (a, b) in enumerate(zip(levels, levels[1:])):
        for sector in range(12):
            mat = m['copper'] if row >= 4 else m['silver' if (row+sector+index)%4 else 'steel']
            shell_panel(f'Cargo {index} formed plate {row:02}-{sector:02}', x,
                        a+.006, b-.006, sector*TAU/12+.006, (sector+1)*TAU/12-.006, mat)
    # The broad blue-grey middle stripe and upper/lower seams are visible in IS0C.
    for z, radius, mat in [(0, 1.058, m['blue']), (.16, 1.046, m['steel']), (-.16, 1.046, m['steel'])]:
        obj = ring(f'Cargo {index} equatorial reinforcement {z}', (x, 0, z), radius, .035 if z else .065, mat)
        obj.scale.y = .88
    for sign in [-1, 1]:
        box(f'Cargo {index} side hatch {sign}', (x+.08, sign*.925, .29), (.43, .035, .37), m['steel'], .04)
        for k in range(4):
            box(f'Cargo {index} hatch vent {sign} {k}', (x-.06+k*.085, sign*.951, .28), (.036, .012, .18), m['dark'], .006)
        box(f'Cargo {index} copper service plate {sign}', (x-.47, sign*.86, -.42), (.27, .045, .18), m['copper'])
        for a in [-1, 1]:
            for b in [-1, 1]:
                rod(f'Cargo {index} hatch fastener {sign} {a} {b}',
                    (x+.08+a*.17, sign*.948, .29+b*.14),
                    (x+.08+a*.17, sign*.96, .29+b*.14), .018, m['edge'], 8)
        # Small equipment stays clear of the broad spherical silhouette.
        for k in range(3):
            px = x-.25+k*.24
            box(f'Cargo {index} lower mounting shoe {sign} {k}', (px, sign*.69, -.77),
                (.14, .075, .10), m['steel'], .012)
            rod(f'Cargo {index} shoe pin {sign} {k}', (px, sign*.73, -.77),
                (px, sign*.75, -.77), .022, m['edge'], 8)
        for offset in [-.50, .50]:
            obj = box(f'Cargo {index} shoulder reinforcement {sign} {offset}',
                      (x+offset, sign*.49, .73), (.18, .10, .035), m['steel'], .012)
            obj.rotation_euler.x = -sign*.55
    rod(f'Cargo {index} lower drain collar', (x, 0, -1.02), (x, 0, -1.14), .15, m['steel'])
    rod(f'Cargo {index} upper inspection plug', (x, 0, 1.02), (x, 0, 1.075), .12, m['steel'])


def bow(m):
    sections = [(3.65, .19, .16), (4.12, .40, .28), (4.65, .47, .31), (5.25, .34, .24), (6.12, .025, .025)]
    vertices = []
    for x, w, h in sections:
        vertices.extend((x, w*y, h*z) for y, z in [(-1, 0), (-.7, 1), (.7, 1), (1, 0), (.65, -.65), (-.65, -.65)])
    faces = [tuple(reversed(range(6))), tuple(range(24, 30))]
    faces += [(i*6+j, i*6+(j+1)%6, (i+1)*6+(j+1)%6, (i+1)*6+j) for i in range(4) for j in range(6)]
    obj = mesh('Faceted blue-grey command prow', vertices, faces, m['blue'])
    mod = obj.modifiers.new('Command prow narrow chamfers', 'BEVEL')
    mod.width, mod.segments = .018, 2
    def profile(x):
        for (xa, wa, ha), (xb, wb, hb) in zip(sections, sections[1:]):
            if xa <= x <= xb:
                fraction = (x-xa)/(xb-xa)
                return wa+(wb-wa)*fraction, ha+(hb-ha)*fraction
        raise ValueError(x)
    # Closed trapezoid plates on the actual prow roof, with physical seam spacing.
    for index, ((xa, _, _), (xb, _, _)) in enumerate(zip(sections, sections[1:])):
        if index == 0:
            continue
        a, b = xa+.015, xb-.015
        wa, ha = profile(a)
        wb, hb = profile(b)
        for sign in [-1, 1]:
            top = [(a, sign*wa*.025, ha+.009), (b, sign*wb*.025, hb+.009),
                   (b, sign*wb*.67, hb+.009), (a, sign*wa*.67, ha+.009)]
            verts = top+[(x, y, z-.014) for x, y, z in top]
            faces = [(0, 1, 2, 3), (7, 6, 5, 4)]+[(i, (i+1)%4, (i+1)%4+4, i+4) for i in range(4)]
            mesh(f'Prow roof formed plate {index} {sign}', verts, faces, m['blue'])
    for side in [-1, 1]:
        for k in range(3):
            x = 4.23+k*.21
            _, h = profile(x)
            window = box(f'Recessed bridge glazing {side} {k}', (x, side*.115, h+.021),
                         (.17, .18, .013), m['glass'], .009)
            window.rotation_euler.y = -.0565
            _, h0 = profile(x-.10)
            rod(f'Bridge glazing divider {side} {k}', (x-.10, 0, h0+.028),
                (x-.10, side*.22, h0+.028), .010, m['steel'], 8)
        _, h0 = profile(4.13)
        _, h1 = profile(4.75)
        rod(f'Bridge outer glazing frame {side}', (4.13, side*.22, h0+.028),
            (4.75, side*.22, h1+.028), .012, m['steel'])
        for k in range(3):
            x = 4.20+k*.25
            w, h = profile(x)
            angle = math.atan(.3*w/h)
            obj = box(f'Prow side equipment panel {side} {k}', (x, side*(w*(1-.3*.08/h)+.014), .08),
                      (.18, .018, .16), m['steel'], .012)
            obj.rotation_euler.x = side*angle
            for z in [.025, .08, .135]:
                slot = box(f'Prow radiator slot {side} {k} {z}', (x, side*(w*(1-.3*z/h)+.027), z),
                           (.12, .010, .018), m['dark'], .004)
                slot.rotation_euler.x = side*angle
        box(f'Prow running light {side}', (5.18, side*.285, .05), (.07, .025, .04), m['red'] if side == -1 else m['light'], .006)
    box('Lower prow copper keel', (4.60, 0, -.20), (1.30, .30, .12), m['copper'], .06)
    for side in [-1, 1]:
        for index, (a, b) in enumerate(zip([4.85, 5.25], [5.25, 5.94])):
            wa, ha = profile(a)
            wb, hb = profile(b)
            rod(f'Forward sloping prow rail {side} {index}', (a, side*wa*.70, ha+.012),
                (b, side*wb*.70, hb+.012), .010, m['steel'])


def drive(m):
    # The tall stern and red-orange exhaust accents are observed; rear cavities are inferred.
    before = set(bpy.context.scene.objects)
    pod(0, -5.05, m)
    for obj in set(bpy.context.scene.objects)-before:
        # Distinct flattened stern bulb; not a fourth full-size cargo module.
        obj.location.x = -5.05+(obj.location.x+5.05)*.49
        obj.location.y *= .74
        obj.scale.x *= .49
        obj.scale.y *= .74
    box('Stern reinforced thrust plate', (-5.59, 0, .05), (.10, .83, 1.48), m['steel'], .06)
    for side in [-1, 1]:
        box(f'Stern copper heat shield {side}', (-5.30, side*.42, -.65), (.65, .32, .16), m['copper'], .04)
    for z in [-.50, .07, .64]:
        rod(f'Drive nacelle {z}', (-5.72, 0, z), (-5.20, 0, z), .24, m['steel'], 48)
        ring(f'Engine machined lip {z}', (-5.77, 0, z), .20, .037, m['edge'], (0, math.pi/2, 0))
        rod(f'Engine recessed throat {z}', (-5.74, 0, z), (-5.67, 0, z), .165, m['dark'], 48)
        rod(f'Engine red pilot {z}', (-5.755, 0, z), (-5.748, 0, z), .12, m['red'], 32)
        for a in range(8):
            theta = a*TAU/8
            rod(f'Engine cooling rib {z} {a}', (-5.67, .23*math.cos(theta), z+.23*math.sin(theta)),
                (-5.15, .23*math.cos(theta), z+.23*math.sin(theta)), .018, m['dark'], 8)
    # Aft machinery between thrust block and first sphere.
    for x in [-4.58, -3.96]:
        rod(f'Aft machinery drum {x}', (x-.16, 0, 0), (x+.16, 0, 0), .49, m['steel'], 32)
        ring(f'Aft machinery flange {x}', (x-.17, 0, 0), .49, .035, m['edge'], (0, math.pi/2, 0))
        for angle in range(8):
            a = angle*TAU/8
            rod(f'Aft machinery clamp {x} {angle}', (x-.17, .49*math.cos(a), .49*math.sin(a)),
                (x+.18, .49*math.cos(a), .49*math.sin(a)), .025, m['copper'], 8)


def build(m):
    rod('Continuous axial cargo spine', (-5.22, 0, 0), (4.13, 0, 0), .20, m['steel'], 32)
    for i, x in enumerate([-2.40, 0, 2.40], 1):
        pod(i, x, m)
    for x in [-3.6, -1.2, 1.2, 3.6]:
        rod(f'Intermodule copper coupling {x}', (x-.15, 0, 0), (x+.15, 0, 0), .28, m['copper'], 32)
        for d in [-.12, .12]:
            ring(f'Coupling seal {x} {d}', (x+d, 0, 0), .28, .018, m['dark'], (0, math.pi/2, 0))
        for side in [-1, 1]:
            rod(f'Cargo longitudinal rail {x} {side}', (x-.37, side*.35, -.05), (x+.37, side*.35, -.05), .035, m['edge'])
            rod(f'Cargo diagonal brace {x} {side}', (x-.35, side*.35, -.05), (x+.32, side*.20, .30), .023, m['steel'])
    for side in [-1, 1]:
        rod(f'Continuous recessed utility conduit {side}', (-4.85, side*.21, -.21), (4.10, side*.21, -.21), .035, m['copper'])
        rod(f'Blue-grey lateral spine rail {side}', (-4.85, side*.58, -.02), (3.50, side*.58, -.02), .035, m['steel'])
        # Raised spatial trusses retain a readable continuous horizontal spine.
        for z in [-.20, .10]:
            rod(f'External longitudinal truss chord {side} {z}', (-4.85, side*.97, z),
                (3.73, side*.97, z), .023, m['edge'])
        for k in range(28):
            x = -4.85+k*(8.58/28)
            dx = 8.58/28
            for za, zb in [(-.20, .10), (.10, -.20)]:
                rod(f'External truss diagonal {side} {k} {za}', (x, side*.97, za),
                    (x+dx, side*.97, zb), .013, m['steel'], 8)
            rod(f'Truss vertical web {side} {k}', (x, side*.97, -.20), (x, side*.97, .10), .018, m['copper'], 8)
            if k % 4 == 0:
                box(f'Amber spine inspection lamp {side} {k}', (x, side*.998, -.075), (.055, .018, .025), m['light'], .004)
        for x in [-3.62, -1.20, 1.20, 3.60]:
            box(f'Intermodule service manifold {side} {x}', (x, side*.53, .29), (.24, .20, .28), m['steel'], .025)
            for dz in [-.07, .07]:
                rod(f'Manifold copper pipe {side} {x} {dz}', (x-.26, side*.53, .29+dz),
                    (x+.26, side*.53, .29+dz), .022, m['copper'])
            for k in range(3):
                box(f'Manifold rib {side} {x} {k}', (x-.075+k*.075, side*.65, .29), (.018, .035, .20), m['dark'], .004)
    drive(m)
    bow(m)
    box('Ventral central servicing locker', (0, 0, -1.16), (.42, .43, .34), m['steel'], .035)
    for sign in [-1, 1]:
        for k in range(4):
            box(f'Ventral locker cooling fin {sign} {k}', (-.14+k*.09, sign*.23, -1.16),
                (.028, .05, .22), m['copper'], .006)
        rod(f'Ventral locker retaining strap {sign}', (-.23, sign*.20, -.91),
            (.23, sign*.20, -1.30), .022, m['edge'])


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 1536, 640
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'AgX'
    scene.world = bpy.data.worlds.new('Neutral orbital studio')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs['Color'].default_value = (.25, .30, .40, 1)
    scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value = .45
    for name, p, energy, colour, size in [('Key', (-1, -5, 8), 2200, (1, .93, .84), 7),
                                        ('Fill', (3, 4, 5), 1700, (.72, .83, 1), 6),
                                        ('Rim', (-5, 2, 2), 1000, (1, .76, .56), 4)]:
        bpy.ops.object.light_add(type='AREA', location=p)
        lamp = bpy.context.object
        lamp.name = name
        lamp.data.energy, lamp.data.color, lamp.data.size = energy, colour, size
        lamp.rotation_euler = (-lamp.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.ops.object.camera_add()
    scene.camera = bpy.context.object
    scene.camera.data.type = 'ORTHO'
    return scene


def frame(scene, objects, direction):
    points = [o.matrix_world @ Vector(p) for o in objects for p in o.bound_box]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    centre = (low+high)/2
    offset = Vector(direction).normalized()*25
    scene.camera.location = centre+offset
    scene.camera.rotation_euler = (-offset).to_track_quat('-Z', 'Y').to_euler()
    inv = scene.camera.rotation_euler.to_matrix().transposed()
    projected = [inv@(p-centre) for p in points]
    width = max(p.x for p in projected)-min(p.x for p in projected)
    height = max(p.y for p in projected)-min(p.y for p in projected)
    scene.camera.data.ortho_scale = max(width, height*scene.render.resolution_x/scene.render.resolution_y)*1.13
    return [list(low), list(high)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    root = args.root.resolve()
    out = root/'sources/objects/shared/federal-transporter/refined'
    media = root/'gallery/media/objects/shared/federal-transporter/refined'
    textures = root/'sources/materials/shared/federal-transporter'
    for folder in [out, media, textures]:
        folder.mkdir(parents=True, exist_ok=True)
    scene = setup()
    m = {key: surface(key, col, metal, rough, seed, textures, glow) for seed, (key, col, metal, rough, glow) in enumerate([
        ('silver', (.37, .41, .43), .78, .36, 0), ('steel', (.21, .26, .28), .78, .42, 0),
        ('edge', (.58, .61, .60), .82, .34, 0), ('copper', (.40, .22, .105), .72, .49, 0),
        ('blue', (.15, .23, .34), .65, .46, 0), ('dark', (.026, .033, .038), .60, .56, 0),
        ('glass', (.018, .035, .05), .08, .24, 0), ('red', (.70, .045, .012), .22, .34, 2.2),
        ('light', (.65, .32, .08), .2, .30, 1.5)], 215)}
    build(m)
    objects = [o for o in scene.objects if o.type == 'MESH']
    root_obj = bpy.data.objects.new('FederalTransporterRoot', None)
    scene.collection.objects.link(root_obj)
    root_obj['catalogue_id'], root_obj['forward_axis'], root_obj['up_axis'] = ID, '+X', '+Z'
    root_obj['legacy_source'] = '_S/IS0C.256, frame 0; distinct from player PS05'
    for obj in objects:
        obj.parent = root_obj
        # Apply edge geometry so native/import checks compare the same surfaces.
        bpy.context.view_layer.objects.active = obj
        for modifier in list(obj.modifiers):
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.to_mesh(obj.data)
        bm.free()
    bpy.context.view_layer.update()
    root_obj.asset_mark()
    root_obj.asset_data.description = 'Refined IS0C Federal Transporter; three spherical cargo modules, command prow, separate thrust block'
    views = [('legacy-side', (0, -14, 5)), ('front-quarter', (7, -13, 7)),
             ('rear-quarter', (-8, -12, 6)), ('top', (0, 0, 20)), ('underside', (0, -5, -15)), ('rear', (-20, 0, 3))]
    bounds = None
    for name, direction in views:
        bounds = frame(scene, objects, direction)
        scene.render.filepath = str(media/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    frame(scene, objects, views[1][1])
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root_obj]:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root_obj
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'), export_format='GLB', use_selection=True,
                              export_apply=True, export_animations=False, export_extras=True)
    for image in bpy.data.images:
        if image.source == 'FILE' and image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(out))
    scene.render.filepath = bpy.path.relpath(str(media/'front-quarter.png'), start=str(out))
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'), compress=True)
    meta = dict(id=ID, issue=215, revision=1, name='Federal Transporter (IS0C)', culture='shared',
                forward_axis='+X', up_axis='+Z', root_scale=[1, 1, 1], bounds=bounds,
                meshes=len(objects), triangles=sum(len(p.vertices)-2 for o in objects for p in o.data.polygons),
                views=[v[0] for v in views], materials=list(m), packed_colour_maps=7,
                source='_S/IS0C.256, frame 0; embedded VGA palette',
                observed=['Long horizontal spine with three spherical silver-grey cargo modules',
                          'Blue-grey equatorial stripe, copper lower hemispheres',
                          'Separate tall stern, exposed aft machinery, red exhaust accents',
                          'Slim faceted blue-grey command prow'],
                inferred=['Hidden rear/underside forms, exact depth and cross sections',
                          'Panel seams, bolts, hatches, glazing, three rear throats and service hardware',
                          'Function of spherical modules is interpreted as cargo; no recovered internal layout'],
                authored_wear='Seeded packed colour maps: seam dirt, stains, rubbed edges and scratches; closed geometry seam gaps',
                animations=[], imported_legacy_pixels_or_geometry=False,
                blend_sha256=sha(out/'model.blend'), glb_sha256=sha(out/'model.glb'),
                generator_sha256=sha(Path(__file__)), blender=bpy.app.version_string,
                limitations=['One reference view only; no original turntable or operation cycle established',
                             'Client scale/orientation/sky and Command Centre integration require game runtime review'])
    (out/'model.json').write_text(json.dumps(meta, indent=2)+'\n')
    print('FEDERAL_TRANSPORTER_GENERATED', json.dumps(meta), flush=True)


if __name__ == '__main__':
    main()
