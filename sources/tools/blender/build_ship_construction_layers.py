"""Author internal construction layers inside the existing Terran small-ship hulls.

The visible hull is preserved. Internal engineering is an authored extension,
constrained by actual hull ray sections, not recovered legacy machinery.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).parent))
import refine_terran_shipyard as geo
SHIPS = {'assault-fighter': 30, 'combat-eagle': 32, 'scoutship': 28}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_clean(path):
    sys.path.insert(0, str(ROOT/'tools'))
    from publication_support import clean_blend
    bpy.ops.wm.save_as_mainfile(filepath=str(path), compress=True)
    path.write_bytes(clean_blend(path.read_bytes())[0])


def hull_bvh(objects):
    vertices, faces = [], []
    for obj in objects:
        offset = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(vertices, faces), vertices


def build(ship, render):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    source = ROOT/'sources/docs/assets/reconstruction/ships/terran'/ship/'model.glb'
    out = ROOT/'sources/objects/terran'/ship/'construction'
    media = ROOT/'gallery/media/objects/terran'/ship/'construction'
    out.mkdir(parents=True, exist_ok=True); media.mkdir(parents=True, exist_ok=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    shell = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    tree, vertices = hull_bvh(shell)
    low = Vector([min(p[i] for p in vertices) for i in range(3)])
    high = Vector([max(p[i] for p in vertices) for i in range(3)])
    length = max(high-low); centre = (high+low)/2
    # Preserve exact world vertices/materials, while batching by existing material.
    for obj in shell:
        matrix = obj.matrix_world.copy(); obj.parent = None; obj.matrix_world = matrix
    for obj in list(bpy.context.scene.objects):
        if obj.type != 'MESH': bpy.data.objects.remove(obj, do_unlink=True)
    root = bpy.data.objects.new('ShipAssembly', None); bpy.context.collection.objects.link(root)
    root['catalogue_id'] = 'openfa:'+ship
    hull = bpy.data.objects.new('Hull', None); bpy.context.collection.objects.link(hull); hull.parent = root
    batches = {}
    for obj in shell:
        assert len(obj.data.materials) == 1, obj.name
        batches.setdefault(obj.data.materials[0].name, []).append(obj)
    for index, objects in enumerate(batches.values()):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects: obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join(); obj = bpy.context.object
        obj.name = f'HullBatch_{index:02}'
        matrix = obj.matrix_world.copy(); obj.parent = hull; obj.matrix_world = matrix
    hull_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    sections = {}

    def section(x, y):
        key = (round(x, 7), round(y, 7))
        if key in sections: return sections[key]
        point = Vector((x, y, low.z-length*.1)); hits = []
        for _ in range(80):
            hit, normal, face, distance = tree.ray_cast(point, Vector((0, 0, 1)), length*2)
            if hit is None or hit.z > high.z+length*.001: break
            if not hits or hit.z-hits[-1] > length*1e-5: hits.append(hit.z)
            point = hit+Vector((0, 0, length*1e-5))
        # Longest solid interval avoids placing machinery inside thin exterior fittings.
        pairs = [(a, b) for a, b in zip(hits[::2], hits[1::2]) if b-a > length*.004]
        value = max(pairs, key=lambda pair: pair[1]-pair[0]) if pairs else None
        sections[key] = value; return value

    def inside(point, margin=0):
        row = section(point.x, point.y)
        return row is not None and row[0]+margin <= point.z <= row[1]-margin

    original_facegroup=geo.facegroup
    def contained_component(group,vertices,faces,tile=1):
        if all(inside(Vector(p),length*.0001) for p in vertices):
            original_facegroup(group,vertices,faces,tile)
    geo.facegroup=contained_component
    geo.GROUPS.clear(); geo.COUNTS.clear(); geo.PARENTS.clear()
    names = ['Build01_Frame', 'Build02_Systems', 'Build03_InnerPanels']
    for name in names: geo.empty(name, root)
    step = length/13; nodes = {}; equipment = 0
    for i in range(14):
        for j in range(14):
            x = centre.x+(i-6.5)*step; y = centre.y+(j-6.5)*step
            row = section(x, y)
            if row:
                nodes[i, j] = (Vector((x, y, sum(row)/2)), row[1]-row[0])
    for (i, j), (point, thickness) in nodes.items():
        # Bulkhead depth and paired longerons give a real three-dimensional frame.
        dz=thickness*.22
        geo.rod(names[0],point-Vector((0,0,dz)),point+Vector((0,0,dz)),min(length*.003,thickness*.10),8,6)
        for other in [(i+1, j), (i, j+1)]:
            if other not in nodes: continue
            end, depth = nodes[other]; radius = min(length*.0035, thickness*.12, depth*.12)
            # Reject bars crossing the Eagle notch or missing skin between columns.
            if all(inside(point.lerp(end, k/12), radius*1.5) for k in range(13)):
                geo.rod(names[0], point, end, radius, 8, 6)
                for sign in [-1,1]:
                    a=point+Vector((0,0,sign*thickness*.22));b=end+Vector((0,0,sign*depth*.22))
                    if all(inside(a.lerp(b,k/12),radius*1.5) for k in range(13)):
                        geo.rod(names[0],a,b,radius*.65,8,6)
                        if (i+j)%2==0:geo.rod(names[0],a,end,radius*.55,1,6)
                # Bundled power/coolant line remains within the same hull section.
                offset = Vector((0, 0, radius*1.8))
                if all(inside(point.lerp(end, k/12)+offset, radius*.6) for k in range(13)):
                    geo.rod(names[1], point+offset, end+offset, radius*.45, 10, 6)
        if thickness > length*.025:
            size = Vector((step*.30, step*.32, min(thickness*.38, step*.55)))
            corners = [point+Vector((x*size.x/2, y*size.y/2, z*size.z/2)) for x in [-1,1] for y in [-1,1] for z in [-1,1]]
            if all(inside(v, length*.002) for v in corners):
                geo.box(names[1], point, size, 2 if i%2 else 1, chamfer=length*.003)
                for k in range(3):
                    geo.box(names[1], point+Vector(((k-1)*size.x*.24, 0, size.z*.52)), (size.x*.10,size.y*.82,length*.002), 8)
                equipment += 1
        if all(key in nodes for key in [(i+1,j),(i,j+1),(i+1,j+1)]):
            quad = [nodes[key][0]+Vector((0,0,nodes[key][1]*.26)) for key in [(i,j),(i+1,j),(i+1,j+1),(i,j+1)]]
            if all(inside(a.lerp(b,k/6),length*.002) for a,b in zip(quad,quad[1:]+quad[:1]) for k in range(7)):
                c = sum(quad,Vector())/4
                if inside(c,length*.002):
                    quad = [c+(p-c)*.89 for p in quad]
                    lower = [p-Vector((0,0,length*.002)) for p in quad]
                    geo.facegroup(names[2], lower+quad, [(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)], 1 if (i+j)%3 else 8)
    geo.facegroup=original_facegroup
    assert equipment >= 3, (ship, equipment)
    material, images = geo.materials(); geo.finalize_geometry(material)
    # Three independently sampled upper-skin contacts and a common suspension eye.
    contacts = []
    for dx, dy in [(-.07,.07),(.07,.07),(0,-.09)]:
        p = centre+Vector((dx*length,dy*length,0)); row = section(p.x,p.y)
        assert row, (ship, 'missing lifting contact')
        contacts.append([p.x,p.y,row[1]])
    eye = [centre.x,centre.y,high.z+length*.06]
    socket = bpy.data.objects.new('ShipLiftSocket',None); bpy.context.collection.objects.link(socket); socket.parent=root; socket.location=eye
    for i,p in enumerate(contacts):
        obj=bpy.data.objects.new(f'LiftingContact_{i}',None);bpy.context.collection.objects.link(obj);obj.parent=root;obj.location=p
    bpy.context.scene.world=bpy.data.worlds.new('Construction preview world')
    scene=geo.setup_scene(True);scene.frame_end=1
    scene.camera.location=centre+Vector((length*.9,-length*1.25,length*.95))
    scene.camera.rotation_euler=(centre-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=length*1.35
    scene.render.resolution_x=scene.render.resolution_y=768;scene.cycles.samples=32
    for light in [o for o in scene.objects if o.type=='LIGHT']:
        light.location=centre+light.location*length/2.7;light.data.energy*= (length/2.7)**2;light.data.size*=length/2.7
    bpy.ops.object.select_all(action='DESELECT')
    meshes=[o for o in scene.objects if o.type=='MESH']
    for obj in scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    scene.render.filepath='//front-quarter.png';save_clean(out/'model.blend')
    stages=[]
    if render:
        for stage in range(4):
            for obj in hull_meshes: obj.hide_render=stage<3
            for index,name in enumerate(names):
                for obj in bpy.data.objects[name].children:obj.hide_render=index>stage
            path=media/f'stage-{stage+1:02}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);stages.append(path.name)
        for obj in meshes: obj.hide_render=False
        scene.render.filepath=str(media/'front-quarter.png');bpy.ops.render.render(write_still=True)
        sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png
        for path in media.glob('*.png'):path.write_bytes(clean_png(path.read_bytes()))
    layer_vertices=[v.co for name in names for obj in bpy.data.objects[name].children for v in obj.data.vertices]
    outside=sum(not inside(p,length*-.001) for p in layer_vertices)
    assert outside==0,(ship,outside)
    report=dict(issue=227,id='openfa:'+ship,source_glb=source.relative_to(ROOT).as_posix(),source_glb_sha256=sha(source),blend_sha256=sha(out/'model.blend'),glb_sha256=sha(out/'model.glb'),generator_sha256=sha(Path(__file__)),geometry_helper_sha256=sha(Path(geo.__file__)),shell_bounds=[list(low),list(high)],game_world_size=SHIPS[ship],layers=[dict(node=name,progress_start=value) for name,value in zip(names+["Hull"],[0,.25,.55,.82])],flight_hidden_nodes=names,lift_socket=eye,lifting_contacts=contacts,mesh_nodes=len(meshes),triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),interior_vertices=len(layer_vertices),vertices_outside_ray_sections=outside,engineering='Authored interior constrained by actual shell sections; original exterior geometry and materials preserved, batched by material.',client_binding='Use real build fraction for cumulative layer visibility. In flight draw Hull only, skip all Build* batches. Socket coordinates are ship-local; apply the same placement transform as the ship.',stage_images=stages)
    (out/'model.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('SHIP_CONSTRUCTION_LAYERS',ship,len(nodes),equipment,outside,report['triangles'],flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-render',action='store_true');parser.add_argument('--ship',choices=SHIPS)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for ship in [args.ship] if args.ship else SHIPS:build(ship,not args.no_render)


if __name__=='__main__':main()
