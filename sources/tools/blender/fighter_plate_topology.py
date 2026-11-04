"""Repair only the existing four-corner extruded fighter armour cap connectivity."""
from mathutils import Vector
from mathutils.geometry import convex_hull_2d, tessellate_polygon


def area(points, order):
    return sum(points[a].x*points[b].y-points[b].x*points[a].y
               for a, b in zip(order, order[1:]+order[:1]))/2


def turn(a, b, c):
    return (b.x-a.x)*(c.y-a.y)-(b.y-a.y)*(c.x-a.x)


def crosses(a, b, c, d):
    return turn(a, b, c)*turn(a, b, d) < -1e-14 and turn(c, d, a)*turn(c, d, b) < -1e-14


def repair_plate(obj):
    mesh = obj.data
    assert obj.name.startswith('Swept tessellated wing armour')
    assert len(mesh.vertices) == 8 and len(mesh.polygons) == 6
    assert len(mesh.materials) == 1 and {face.material_index for face in mesh.polygons} == {0}
    assert not mesh.uv_layers and mesh.shape_keys is None and not obj.vertex_groups
    points = [vertex.co.copy() for vertex in mesh.vertices]
    thickness = points[0].z-points[4].z
    assert thickness > 0
    for index in range(4):
        assert (points[index]-points[index+4]-Vector((0, 0, thickness))).length < 1e-7
    projected = [Vector((point.x, point.y, 0)) for point in points[:4]]
    crossed = crosses(*projected) or crosses(projected[1], projected[2], projected[3], projected[0])
    order = list(convex_hull_2d([point.to_2d() for point in projected])) if crossed else list(range(4))
    assert len(order) == 4, 'Crossed panel needs a reviewed four-corner hull'
    if area(projected, order) < 0:
        order.reverse()
    assert area(projected, order) > 1e-10
    triangles = tessellate_polygon([[projected[index] for index in order]])
    top = []
    for triangle in triangles:
        indices = []
        for corner in triangle:
            if isinstance(corner, int):
                index = order[corner]
            else:
                index = min(range(4), key=lambda i: (projected[i]-corner).length)
                assert (projected[index]-corner).length < 1e-6
            indices.append(index)
        top.append(tuple(indices))
    assert len(top) == 2 and all(area(projected, list(triangle)) > 1e-10 for triangle in top)
    bottom = [tuple(index+4 for index in reversed(triangle)) for triangle in top]
    sides = [(a, a+4, b+4, b) for a, b in zip(order, order[1:]+order[:1])]
    mesh.clear_geometry()
    mesh.from_pydata([tuple(point) for point in points], [], top+bottom+sides)
    mesh.update()
    assert [tuple(vertex.co) for vertex in mesh.vertices] == [tuple(point) for point in points]
    return dict(object=obj.name, crossed_projected_boundary_reordered=crossed,
                top_boundary=order, matched_cap_triangles=[list(triangle) for triangle in top],
                thickness=thickness, projected_area=area(projected, order), original_vertices_preserved=True)
