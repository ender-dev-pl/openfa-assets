"""Sampled UV surface correspondence when tessellation changes, including seams."""
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from rigellian_extractor_remaster_checks import image_node


def selected_layer(data,node):
    vector = node.inputs['Vector']
    if vector.is_linked:
        coord = vector.links[0].from_node
        assert coord.type=='UVMAP'
        layer = data.uv_layers.get(coord.uv_map)
    else:
        layer = data.uv_layers.active
    assert layer is not None
    return layer


def snapshot_uv_surfaces():
    result = {}
    graph = bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':
            continue
        evaluated = obj.evaluated_get(graph)
        data = evaluated.to_mesh(preserve_all_data_layers=True,depsgraph=graph)
        data.calc_loop_triangles()
        groups = {}
        for triangle in data.loop_triangles:
            material = data.materials[triangle.material_index]
            shader = material.node_tree.nodes.get('Principled BSDF')
            if not shader.inputs['Base Color'].is_linked:
                continue
            node,_ = image_node(material,'Base Color')
            rough,_ = image_node(material,'Roughness')
            layer = selected_layer(data,node)
            assert selected_layer(data,rough)==layer
            group = groups.setdefault(material.name,dict(points=[],faces=[],uvs=[],samples={},repeat=node.extension=='REPEAT'))
            start = len(group['points'])
            uvs = []
            for index in triangle.loops:
                point = obj.matrix_world@data.vertices[data.loops[index].vertex_index].co
                uv = layer.data[index].uv.copy()
                assert all(math.isfinite(v) for v in uv)
                group['points'].append(point)
                uvs.append(uv)
                group['samples'][tuple(point)+tuple(uv)] = (point,uv)
            group['faces'].append((start,start+1,start+2))
            group['uvs'].append(uvs)
        for group in groups.values():
            group['tree'] = BVHTree.FromPolygons(group['points'],group['faces'],all_triangles=True)
        result[obj.name] = groups
        evaluated.to_mesh_clear()
    return result


def interpolate_uv(point,points,uvs):
    a,b,c = [tuple(float(value) for value in row) for row in points]
    v0 = tuple(b[i]-a[i] for i in range(3))
    v1 = tuple(c[i]-a[i] for i in range(3))
    v2 = tuple(float(point[i])-a[i] for i in range(3))
    def cross(left,right):
        return (left[1]*right[2]-left[2]*right[1],
                left[2]*right[0]-left[0]*right[2],
                left[0]*right[1]-left[1]*right[0])
    def dot(left,right):
        return math.fsum(x*y for x,y in zip(left,right))
    normal = cross(v0,v1)
    den = dot(normal,normal)
    if den==0:
        # Blender can triangulate a polygon with collinear boundary vertices.
        # Its zero-area triangles contribute edges, not a barycentric interior.
        candidates = []
        for first,second in [(0,1),(1,2),(2,0)]:
            start,end = [a,b,c][first],[a,b,c][second]
            edge = tuple(end[i]-start[i] for i in range(3))
            length = dot(edge,edge)
            offset = tuple(float(point[i])-start[i] for i in range(3))
            t = max(0,min(1,dot(offset,edge)/length)) if length else 0
            projection = tuple(start[i]+t*edge[i] for i in range(3))
            distance = math.sqrt(math.fsum((float(point[i])-projection[i])**2 for i in range(3)))
            if distance<1e-7:
                candidates.append(uvs[first]*(1-t)+uvs[second]*t)
        assert candidates, ('No corresponding degenerate edge',a,b,c,point)
        return candidates
    v = dot(cross(v2,v1),normal)/den
    w = dot(cross(v0,v2),normal)/den
    return [uvs[0]*(1-v-w)+uvs[1]*v+uvs[2]*w]



def compare_surface_uv(left,right,position_tolerance=1e-4,uv_tolerance=.001):
    assert left.keys()==right.keys()
    maximum_uv,maximum_position,count = 0.0,0.0,0
    for name in left:
        assert left[name].keys()==right[name].keys(),name
        for material in left[name]:
            for first,second in [(left[name][material],right[name][material]),(right[name][material],left[name][material])]:
                assert first['repeat']==second['repeat']
                for point,uv in first['samples'].values():
                    hits = second['tree'].find_nearest_range(point,position_tolerance)
                    assert hits,(name,material,'No corresponding surface',list(point))
                    candidates = []
                    for closest,normal,index,distance in hits:
                        points = [second['points'][i] for i in second['faces'][index]]
                        for expected in interpolate_uv(closest,points,second['uvs'][index]):
                            errors = [abs(uv[i]-expected[i]) for i in range(2)]
                            if second['repeat']:
                                errors = [abs((uv[i]-expected[i]+.5)%1-.5) for i in range(2)]
                            candidates.append((max(errors),distance))
                    error,distance = min(candidates)
                    assert error<uv_tolerance,(name,material,'UV interpolation changed',error)
                    maximum_uv = max(maximum_uv,error)
                    maximum_position = max(maximum_position,distance)
                    count += 1
    return dict(maximum_uv_corner_error=maximum_uv,maximum_sampled_surface_distance=maximum_position,
        matched_directed_corners=count,position_tolerance=position_tolerance,uv_tolerance=uv_tolerance,
        scope='All unique material/UV corner samples projected bidirectionally onto corresponding triangles, with barycentric UV interpolation and repeat-wrap equivalence; not a continuous UV-field proof.')
