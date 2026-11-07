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


def hull_solids(objects):
    """Reconnect complementary skin batches before testing individual solids.

    Material batching and partial/final splitting are rendering concerns; they
    cannot be treated as closed physical solids for ray parity tests.
    """
    points=[];index={};faces=[];parents=[]
    def find(i):
        while parents[i]!=i:
            parents[i]=parents[parents[i]];i=parents[i]
        return i
    for obj in objects:
        local={}
        for vertex in obj.data.vertices:
            p=obj.matrix_world@vertex.co;key=tuple(round(c,6) for c in p)
            if key not in index:
                index[key]=len(points);points.append(p);parents.append(len(parents))
            local[vertex.index]=index[key]
        for polygon in obj.data.polygons:
            face=tuple(local[i] for i in polygon.vertices);faces.append(face)
            for i in face[1:]:parents[find(i)]=find(face[0])
    groups={}
    for face in faces:groups.setdefault(find(face[0]),[]).append(face)
    return [BVHTree.FromPolygons(points,group) for group in groups.values()]


def hull_partition(obj,indices,name):
    source=obj.data;vertices=[];mapping={};faces=[];loops=[];smooth=[]
    for index in indices:
        polygon=source.polygons[index];face=[]
        for vi in polygon.vertices:
            if vi not in mapping:mapping[vi]=len(vertices);vertices.append(source.vertices[vi].co.copy())
            face.append(mapping[vi])
        faces.append(face);loops.extend(polygon.loop_indices);smooth.append(polygon.use_smooth)
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update()
    for material in source.materials:mesh.materials.append(material)
    for original in source.uv_layers:
        uv=mesh.uv_layers.new(name=original.name)
        for i,li in enumerate(loops):uv.data[i].uv=original.data[li].uv
    for p,value in zip(mesh.polygons,smooth):p.use_smooth=value
    mesh.normals_split_custom_set([source.corner_normals[li].vector for li in loops])
    result=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(result);result.matrix_world=obj.matrix_world.copy()
    return result


def build(ship, render):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    # Rebuild from the canonical exterior; an upgraded ship is its own hull input.
    # No frozen pre-construction GLB is distributed alongside the current model.
    source = ROOT/'sources/objects/terran'/ship/'model.glb'
    source_digest = sha(source)
    out = ROOT/'sources/objects/terran'/ship
    media = ROOT/'gallery/media/objects/terran'/ship/'construction'
    out.mkdir(parents=True, exist_ok=True); media.mkdir(parents=True, exist_ok=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    layered = bpy.data.objects.get('ShipAssembly') is not None
    shell = [o for o in bpy.context.scene.objects if o.type == 'MESH'
             and (not layered or o.name.startswith(('HullPartialBatch_', 'HullFinalBatch_')))]
    for obj in list(bpy.context.scene.objects):
        if obj.type == 'MESH' and obj not in shell:
            bpy.data.objects.remove(obj, do_unlink=True)
    tree, vertices = hull_bvh(shell)
    # Test each manufactured solid independently. Global parity across overlapping
    # armour and pressure hulls would incorrectly classify their shared core as air.
    solid_trees=hull_solids(shell) if layered else [hull_bvh([obj])[0] for obj in shell]
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
    partial=bpy.data.objects.new('HullPartial',None);bpy.context.collection.objects.link(partial);partial.parent=hull
    final=bpy.data.objects.new('HullFinal',None);bpy.context.collection.objects.link(final);final.parent=hull
    batches = {}
    for obj in shell:
        assert len(obj.data.materials) == 1, obj.name
        selected=[];remaining=[]
        for p in obj.data.polygons:
            point=obj.matrix_world@p.center;u=(point.x-low.x)/(high.x-low.x);v=(point.y-low.y)/(high.y-low.y)
            target=selected if (u<.36 and v>.22) or (u>.64 and v<.35) or (.40<u<.60 and v<.30) else remaining
            target.append(p.index)
        for parent,indices in [(partial,selected),(final,remaining)]:
            if indices:
                part=hull_partition(obj,indices,obj.name+' '+parent.name)
                batches.setdefault((parent.name,obj.data.materials[0].name),[]).append(part)
        bpy.data.objects.remove(obj,do_unlink=True)
    for index, ((parent_name,material_name),objects) in enumerate(batches.items()):
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects: obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        bpy.ops.object.join(); obj = bpy.context.object
        obj.name = f'{parent_name}Batch_{index:02}'
        matrix = obj.matrix_world.copy(); obj.parent = bpy.data.objects[parent_name]; obj.matrix_world = matrix
    hull_meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    sections = {}

    def section(x, y):
        key = (round(x, 7), round(y, 7))
        if key in sections: return sections[key]
        intervals=[]
        for solid in solid_trees:
            point=Vector((x,y,low.z-length*.1));hits=[]
            for _ in range(40):
                hit,normal,face,distance=solid.ray_cast(point,Vector((0,0,1)),length*2)
                if hit is None or hit.z>high.z+length*.001:break
                if not hits or hit.z-hits[-1]>length*1e-5:hits.append(hit.z)
                point=hit+Vector((0,0,length*1e-5))
            intervals.extend((a,b) for a,b in zip(hits[::2],hits[1::2]) if b-a>length*.004)
        merged=[]
        for a,b in sorted(intervals):
            if merged and a<=merged[-1][1]+length*.00001:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
            else:merged.append((a,b))
        value=max(merged,key=lambda pair:pair[1]-pair[0]) if merged else None
        sections[key] = value; return value

    def inside(point, margin=0):
        row = section(point.x, point.y)
        return row is not None and row[0]+margin <= point.z <= row[1]-margin

    original_facegroup=geo.facegroup
    def contained_component(group,vertices,faces,tile=1):
        if all(inside(Vector(p),length*.0001) for p in vertices):
            if group=='Build02_ExpandedFrame':
                mid=sum((Vector(p) for p in vertices),Vector())/len(vertices)
                if abs(mid.x-centre.x)<length*.11:group='Build01_BaseFrame'
            original_facegroup(group,vertices,faces,tile)
    geo.facegroup=contained_component
    geo.GROUPS.clear(); geo.COUNTS.clear(); geo.PARENTS.clear()
    names = ['Build02_ExpandedFrame', 'Build03_Systems', 'Build03_Systems']
    internal=['Build01_BaseFrame','Build02_ExpandedFrame','Build03_Systems']
    for name in internal: geo.empty(name, root)
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
        for stage in range(5):
            for obj in hull_meshes: obj.hide_render=stage<(3 if obj.parent==partial else 4)
            for index,name in enumerate(internal):
                for obj in bpy.data.objects[name].children:obj.hide_render=index>stage
            path=media/f'stage-{stage+1:02}.png';scene.render.filepath=str(path);bpy.ops.render.render(write_still=True);stages.append(path.name)
        for obj in meshes: obj.hide_render=False
        scene.render.filepath=str(media/'front-quarter.png');bpy.ops.render.render(write_still=True)
        sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png
        for path in media.glob('*.png'):path.write_bytes(clean_png(path.read_bytes()))
    layer_vertices=[v.co for name in internal for obj in bpy.data.objects[name].children for v in obj.data.vertices]
    outside=sum(not inside(p,length*-.001) for p in layer_vertices)
    assert outside==0,(ship,outside)
    report=dict(issue=227,id='openfa:'+ship,source_glb=source.relative_to(ROOT).as_posix(),source_glb_sha256=source_digest,blend_sha256=sha(out/'model.blend'),glb_sha256=sha(out/'model.glb'),generator_sha256=sha(Path(__file__)),geometry_helper_sha256=sha(Path(geo.__file__)),shell_bounds=[list(low),list(high)],game_world_size=SHIPS[ship],layers=[dict(node=name,progress_start=value) for name,value in zip(internal+['HullPartial','HullFinal'],[0,.16,.38,.65,.88])],flight_hidden_nodes=internal,flight_visible_nodes=['HullPartial','HullFinal'],lift_socket=eye,lifting_contacts=contacts,mesh_nodes=len(meshes),triangles=sum(len(p.vertices)-2 for o in meshes for p in o.data.polygons),interior_vertices=len(layer_vertices),vertices_outside_ray_sections=outside,engineering='Authored interior constrained by actual shell sections; original exterior faces, normals, UVs and materials preserved and partitioned into disjoint partial/final hull batches.',client_binding='Use real build fraction for cumulative five-layer visibility. In flight draw both children of Hull, skip all Build* batches. Socket coordinates are ship-local; apply the same placement transform as the ship.',stage_images=stages)
    (out/'model.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('SHIP_CONSTRUCTION_LAYERS',ship,len(nodes),equipment,outside,report['triangles'],flush=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--no-render',action='store_true');parser.add_argument('--ship',choices=SHIPS)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    for ship in [args.ship] if args.ship else SHIPS:build(ship,not args.no_render)


if __name__=='__main__':main()
