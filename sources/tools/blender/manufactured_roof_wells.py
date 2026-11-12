"""Editable actual roof bores with embedded sleeves, floors and supported fins."""
import math
import bmesh
import bpy
from build_openfa_assets import box,cylinder
from build_shield_equipment import shell
from mathutils import Vector


def analytic_lathe_normals(obj,profile):
    """Preserve radial outer-surface shading after long Boolean roof triangles."""
    mesh=obj.data;mesh.update();slopes=[(rb-ra)/(zb-za) for (za,ra),(zb,rb) in zip(profile,profile[1:])]
    gradients=[]
    for index in range(len(profile)):
        before=Vector((1,-slopes[max(0,index-1)])).normalized()
        after=Vector((1,-slopes[min(index,len(slopes)-1)])).normalized();gradients.append((before+after).normalized())
    def segment(z):
        return next(i for i,((za,_),(zb,_)) in enumerate(zip(profile,profile[1:])) if za-1e-6<=z<=zb+1e-6)
    normals=[None]*len(mesh.loops)
    for face in mesh.polygons:
        coords=[mesh.vertices[mesh.loops[index].vertex_index].co for index in face.loop_indices]
        flat=max(p.z for p in coords)-min(p.z for p in coords)<1e-6
        outer=not flat and all(abs(math.hypot(p.x,p.y)-(profile[(i:=segment(p.z))][1]+
            (profile[i+1][1]-profile[i][1])*(p.z-profile[i][0])/(profile[i+1][0]-profile[i][0])))<.004 for p in coords)
        for loop,point in zip(face.loop_indices,coords):
            normal=face.normal.copy()
            if outer:
                i=segment(point.z);t=(point.z-profile[i][0])/(profile[i+1][0]-profile[i][0]);gradient=gradients[i].lerp(gradients[i+1],t).normalized()
                radial=Vector((point.x,point.y,0)).normalized();normal=Vector((radial.x*gradient.x,radial.y*gradient.x,gradient.y))
            normals[loop]=normal
    mesh.normals_split_custom_set(normals)
    obj['normal_policy']='Analytic radial/profile outer normals; actual bore/floor retain hard transitions'


def roof_well(obj,label,xy,start,m):
    cylinder('Temporary actual roof well cutter',(*xy,start+.47),.17,.60,m['dark'],vertices=64)
    cutter=bpy.context.object
    for modifier in list(cutter.modifiers): cutter.modifiers.remove(modifier)
    bpy.context.view_layer.objects.active=obj;modifier=obj.modifiers.new('Actual recessed roof well','BOOLEAN')
    modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter
    bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
    bmesh.ops.dissolve_degenerate(bm,dist=.000001,edges=list(bm.edges));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    for face in bm.faces:
        zs=[v.co.z for v in face.verts];face.smooth=max(zs)-min(zs)>1e-6
    for edge in bm.edges:
        if edge.is_manifold and edge.calc_face_angle()>.65: edge.smooth=False
    bm.to_mesh(obj.data);bm.free()
    liner=shell(label+' embedded well sleeve',[(start+.15,.177),(start+.41,.177)],0,math.tau,
        dict(shell=m['edge'],dark=m['dark']),64,.022)
    liner.rotation_euler.x=math.pi/2;liner.location=(*xy,0)
    cylinder(label+' recessed well floor',(*xy,start+.17),.160,.040,m['dark'],vertices=64)
    for y in [xy[1]-.045,xy[1]+.045]: box(label+' well cooling fin',(xy[0],y,start+.20),(.18,.018,.030),m['gold'],.003)
