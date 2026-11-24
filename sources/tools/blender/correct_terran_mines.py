"""Focused PB08 utility-envelope and PB08/PB13 drilling-assembly correction.

Run in Blender against the outgoing committed canonical models. This technical
repair preserves the deck/trestles; it is not a full artistic remaster.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
from mathutils import Vector

PREFIX = 'Mine correction | '


def clean_render(path):
    """Retain pixels while dropping Blender text, timestamp and EXIF chunks."""
    data = Path(path).read_bytes()
    output = bytearray(data[:8])
    offset = 8
    while offset < len(data):
        size = struct.unpack_from('>I', data, offset)[0]
        kind = data[offset+4:offset+8]
        end = offset+12+size
        if kind not in {b'tEXt',b'zTXt',b'iTXt',b'eXIf',b'tIME'}:
            output.extend(data[offset:end])
        offset = end
    Path(path).write_bytes(output)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def meshes():
    return [o for o in bpy.context.scene.objects if o.type == 'MESH']


def bounds(objects):
    points = [o.matrix_world @ Vector(v) for o in objects for v in o.bound_box]
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]


def signature(obj):
    payload = dict(vertices=[[round(c, 7) for c in v.co] for v in obj.data.vertices],
                   faces=[list(p.vertices) for p in obj.data.polygons],
                   transform=[[round(c, 7) for c in row] for row in obj.matrix_world])
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def evaluated_triangles(objects):
    deps = bpy.context.evaluated_depsgraph_get()
    count = 0
    for obj in objects:
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        count += len(mesh.loop_triangles)
        evaluated.to_mesh_clear()
    return count


def material(name, colour, metallic, roughness):
    mat = bpy.data.materials.new(PREFIX + name)
    mat.diffuse_color = (*colour, 1)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (*colour, 1)
    p.inputs['Metallic'].default_value = metallic
    p.inputs['Roughness'].default_value = roughness
    return mat


def finish(obj, name, mat, role):
    obj.name = PREFIX + name
    obj.data.materials.append(mat)
    obj['mine_correction_role'] = role
    return obj


def box(name, position, size, mat, role='utility'):
    bpy.ops.mesh.primitive_cube_add(size=1, location=position)
    obj = bpy.context.object
    obj.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(obj, name, mat, role)


def cylinder(name, position, radius, depth, mat, role='drill', vertices=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=position)
    obj = finish(bpy.context.object, name, mat, role)
    for p in obj.data.polygons:
        p.use_smooth = len(p.vertices) == 4
    return obj


def rod(name, start, end, radius, mat, role='utility'):
    a, b = Vector(start), Vector(end)
    obj = cylinder(name, (a+b)/2, radius, (b-a).length, mat, role, vertices=8)
    obj.rotation_euler = (b-a).to_track_quat('Z', 'Y').to_euler()
    return obj


def drill(deep, mats):
    radius = .32 if deep else .235
    head = .435 if deep else .325
    cylinder('continuous bore pipe', (0, 0, .89), radius, 1.22, mats['steel'])
    for z in [.38, .83, 1.34]:
        cylinder('pipe service coupling', (0, 0, z), radius+.035, .085, mats['dark'])
        cylinder('coupling polished shoulder', (0, 0, z+.048), radius+.026, .012, mats['edge'])
        for a in [0, math.pi/2, math.pi, math.pi*1.5]:
            obj = box('coupling fastener', ((radius+.035)*math.cos(a), (radius+.035)*math.sin(a), z),
                      (.042, .042, .048), mats['edge'], 'drill')
            obj.rotation_euler.z = a
    cylinder('deck rotary chuck', (0, 0, 1.355), radius+.075, .13, mats['bronze'])
    cylinder('rotary chuck grime seal', (0, 0, 1.285), radius+.07, .018, mats['grime'])
    # A closed downward-pointing cutting crown, connected to the pipe.
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=head*.35, radius2=head,
                                   depth=.25, location=(0, 0, .145))
    finish(bpy.context.object, 'downward cutting crown', mats['steel'], 'drill')
    cylinder('cutting crown shoulder', (0, 0, .275), head, .06, mats['dark'])
    for i in range(8):
        a = i*math.tau/8
        x, y = head*.78*math.cos(a), head*.78*math.sin(a)
        cutter = box('worn carbide cutting tooth', (x, y, .18), (.075, .10, .17), mats['edge'], 'drill')
        cutter.rotation_euler = (.16*math.sin(a), -.16*math.cos(a), a)
        box('tooth root grime', (x, y, .267), (.08, .08, .017), mats['grime'], 'drill')
    # Sparse authored scuff strips survive GLB export without procedural textures.
    for i in range(6):
        a = i*math.tau/6+.2
        rod('pipe abrasion', (radius*1.004*math.cos(a), radius*1.004*math.sin(a), .49+i*.055),
            (radius*1.004*math.cos(a), radius*1.004*math.sin(a), .59+i*.055), .004, mats['edge'], 'drill')


def utilities(old_bounds, mats):
    lo, hi = old_bounds
    centre = [(lo[i]+hi[i])/2 for i in range(3)]
    half = [(hi[i]-lo[i])*2/3 for i in range(2)]
    # Exact symmetric outer envelope, including the physical post widths.
    x0, x1 = centre[0]-half[0]+.025, centre[0]+half[0]-.025
    y0, y1 = centre[1]-half[1]+.025, centre[1]+half[1]-.025
    for x, y in [(x0,y0),(x1,y0),(x0,y1),(x1,y1),(x0,centre[1]),(x1,centre[1]),(-.43,y0),(.43,y0)]:
        box('grounded fence post', (x,y,.19), (.05,.05,.38), mats['steel'])
        box('post ground dirt', (x,y,.017), (.05,.05,.034), mats['grime'])
        box('post scraped top', (x,y,.381), (.038,.038,.002), mats['edge'])
    for start, end in [((x0,y0),(x0,y1)),((x1,y0),(x1,y1)),((x0,y1),(x1,y1)),((x0,y0),(-.43,y0)),((.43,y0),(x1,y0))]:
        for z in [.14,.31]:
            rod('low safety fence rail', (*start,z), (*end,z), .014, mats['steel'])
    for side in [-1,1]:
        x = side*1.17
        box('coolant and power skid', (x,.19,.055), (.31,.65,.11), mats['dark'])
        box('weathered coolant cabinet', (x,.19,.245), (.28,.48,.32), mats['bronze'])
        box('cabinet recessed service face', (x,-.055,.24), (.22,.015,.24), mats['dark'])
        for z in [.17,.22,.27,.32]:
            box('cabinet cooling slot', (x,-.064,z), (.18,.007,.014), mats['steel'])
        box('cabinet basal grime', (x,-.066,.094), (.27,.007,.028), mats['grime'])
        for offset in [-.075,.018,.086]:
            box('cabinet chipped paint', (x+offset,-.066,.365), (.023,.006,.011), mats['edge'])
        for z in [.09,.16]:
            rod('coolant feed to trestle', (x,.39,z), (side*.75,.39,z), .018, mats['dark'])
        rod('grounded power conduit', (x,-.05,.05), (side*.75,-.42,.05), .016, mats['steel'])
    return dict(minimum=[centre[0]-half[0],centre[1]-half[1],0],
                maximum=[centre[0]+half[0],centre[1]+half[1],hi[2]])


def render(scene, path, azimuth, target, ortho):
    camera = scene.camera
    a = math.radians(azimuth)
    camera.location = Vector(target)+Vector((math.cos(a)*9,math.sin(a)*9,7))
    camera.rotation_euler = (Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = ortho
    scene.render.resolution_x = scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.film_transparent = True
    scene.cycles.samples = 24
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    clean_render(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    bpy.context.preferences.filepaths.save_version = 0
    for code in ['pb08','pb13']:
        source = args.source_root/'sources/docs/assets/bootstrap-3d/terran-refined'/code/'model.blend'
        bpy.ops.wm.open_mainfile(filepath=str(source))
        scene = bpy.context.scene
        assert not any(o.name.startswith(PREFIX) for o in meshes()), 'Run only against the outgoing canonical input'
        original_bounds = bounds(meshes())
        original = {o.name:signature(o) for o in meshes()}
        removed = []
        for obj in list(meshes()):
            if 'shaft' in obj.name.lower() and 'hydraulic' not in obj.name.lower():
                removed.append(obj.name)
                bpy.data.objects.remove(obj,do_unlink=True)
        if code == 'pb13':
            assert removed, 'Expected the existing deep-bore drill proxy'
        mats = dict(steel=material('used steel',(.25,.30,.31),.72,.48),
                    edge=material('exposed metal',(.46,.49,.46),.76,.36),
                    dark=material('dark housing',(.055,.070,.075),.54,.64),
                    bronze=material('worn ochre utilities',(.30,.235,.13),.48,.62),
                    grime=material('joint dirt',(.036,.026,.017),.1,.91))
        drill(code=='pb13', mats)
        expected = utilities(original_bounds,mats) if code=='pb08' else None
        bpy.context.view_layer.update()
        for obj in meshes():
            if obj.name in original:
                assert signature(obj)==original[obj.name],obj.name
        corrected_bounds = bounds(meshes())
        if expected:
            for axis in range(2):
                assert abs((corrected_bounds[1][axis]-corrected_bounds[0][axis]) /
                           (original_bounds[1][axis]-original_bounds[0][axis])-4/3)<.0001
        else:
            assert all(abs(a-b)<.00001 for row0,row1 in zip(original_bounds,corrected_bounds) for a,b in zip(row0,row1))
        output=args.output/code
        output.mkdir(parents=True,exist_ok=True)
        media=output/'media';media.mkdir(exist_ok=True)
        scene.camera.location=(9,-13,12)
        scene['mine_correction_issue']='ender-dev-pl/openfa-assets#271'
        bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'),compress=True)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in meshes():obj.select_set(True)
        bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',use_selection=True,
                                 export_apply=True,export_extras=True,export_animations=False,export_yup=True)
        target=((corrected_bounds[0][0]+corrected_bounds[1][0])/2,
                (corrected_bounds[0][1]+corrected_bounds[1][1])/2,.85)
        for name,azimuth in [('front-quarter',-60),('rear-quarter',120)]:
            render(scene,media/(name+'.png'),azimuth,target,4.25 if code=='pb08' else 3.5)
        camera=scene.camera;camera.location=(0,0,10);camera.rotation_euler=(0,0,0)
        camera.data.ortho_scale=3.75 if code=='pb08' else 3.2
        scene.render.filepath=str(media/'top.png');bpy.ops.render.render(write_still=True)
        clean_render(media/'top.png')
        proof=dict(format='terran-mine-utility-drill-correction-v1',issue=271,identity='terran:mine' if code=='pb08' else 'terran:deep-bore-mine',
                   source_sha256=sha(source),generator_sha256=sha(__file__),blend_sha256=sha(output/'model.blend'),glb_sha256=sha(output/'model.glb'),
                   original_bounds=original_bounds,bounds=corrected_bounds,footprint=[2,2],
                   unchanged_original_meshes={name:value for name,value in original.items() if name not in removed},removed_drill_proxies=removed,
                   added_meshes=[o.name for o in meshes() if o.name.startswith(PREFIX)],
                   mesh_objects=len(meshes()),triangles=evaluated_triangles(meshes()),
                   control_mesh_triangles=sum(len(p.vertices)-2 for o in meshes() for p in o.data.polygons),
                   native_renders={name:sha(media/(name+'.png')) for name in ['front-quarter','rear-quarter','top']},
                   note='User-directed visible utility envelope and explicit bore pipe/cutting crown. Paired footprint rendering is verified separately; gameplay acceptance remains external.')
        (output/'correction.json').write_text(json.dumps(proof,indent=2)+'\n')
        print('MINE_CORRECTED',code,proof['mesh_objects'],proof['triangles'],flush=True)


if __name__ == '__main__':
    main()
