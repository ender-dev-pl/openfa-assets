"""Retained RI19 anatomy/maps and all sixteen independently driven yaw poses."""
import math
import bpy
import bmesh
from mathutils import Matrix,Quaternion,Vector
from verify_rigellian_thermal_lance import structure as original_structure,texture_evidence
from rigellian_thermal_lance_parts import PIVOT,LANCE_TIP,LANCE_AXIS,MOVING


def yaw_pose(angle):
    yaw = bpy.data.objects['YawPivot']
    yaw.rotation_mode = 'QUATERNION'
    yaw.rotation_quaternion = Quaternion((0,0,1),angle)
    bpy.context.view_layer.update()


def structure():
    meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
    for obj in meshes:
        assert not obj.modifiers and obj.data.shape_keys is None
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
            assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0,obj.name
        finally:
            bm.free()
    yaw_pose(0)
    bounds,contacts = original_structure(meshes)
    textures = texture_evidence(meshes)
    fixed = {o.name:o.matrix_world.copy() for o in meshes if o.name not in MOVING}
    poses = []
    maximum_error = 0
    for index in range(16):
        angle = index*math.tau/16
        yaw_pose(angle)
        rotation = Matrix.Rotation(angle,3,'Z')
        socket = bpy.data.objects['LanceTipSocket']
        expected = PIVOT+rotation@(LANCE_TIP-PIVOT)
        forward = (socket.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        error = max((socket.matrix_world.translation-expected).length,
            (forward-rotation@LANCE_AXIS).length,
            (bpy.data.objects['RI19 tapered thermal lance'].matrix_world@Vector((0,0,.90))-expected).length)
        assert error<1e-5,(index,error)
        maximum_error = max(maximum_error,error)
        for name,matrix in fixed.items():
            assert max(abs(matrix[i][j]-bpy.data.objects[name].matrix_world[i][j]) for i in range(4) for j in range(4))<1e-6
        poses.append(dict(index=index,authored_yaw_degrees=index*22.5,
            socket_position=list(socket.matrix_world.translation),socket_forward=list(forward),
            moving_world_matrices={name:[float(v) for row in bpy.data.objects[name].matrix_world for v in row] for name in MOVING},
            fixed_base_unchanged=True))
    yaw_pose(0)
    return dict(positive_closed_meshes=len(meshes),body_bounds=bounds,retained_anatomy_contacts=contacts,
        texture_pixels_and_uvs=textures,yaw_validation=dict(poses=poses,maximum_socket_error=maximum_error,
            fixed_base_unchanged=True,model_yaw_phase_sign_calibrated=False,continuous_collision_sweep_proven=False))
