"""Issue246 follow-up: eight small radial spikes, without another ship variant.

Run after the base Mikotaj generator and before publication/runtime verification.
The count/spacing follows user interpretation of tiny MK0A silhouettes; dimensions
are authored, not recovered hidden engineering.
"""
from pathlib import Path
import json,math,sys
import bpy,bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
import remaster_mikotaj_mobile_ships as author
PREFIX='HieroPeripheralSpike'


def main():
    out,media=author.folders('hiero');meta=json.loads((out/'model.json').read_text());before={k:author.sha(out/('model.'+k)) for k in ['blend','glb']}
    bpy.ops.wm.open_mainfile(filepath=str(out/'model.blend'),load_ui=False,use_scripts=False);bpy.context.preferences.filepaths.save_version=0
    body=next(o for o in author.meshes() if 'Hiero faceted hull' in o.vertex_groups);old=[g for g in body.vertex_groups if g.name.startswith(PREFIX)]
    if old:
        indices={g.index for g in old};remove=[v.index for v in body.data.vertices if any(w.group in indices for w in v.groups)]
        bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.verts[i] for i in remove],context='VERTS');bm.to_mesh(body.data);bm.free()
        for group in old:body.vertex_groups.remove(group)
    bpy.context.view_layer.update();tree=author.core.tree(body);material=body.data.materials[0];spikes=[];parts=[]
    for i in range(8):
        angle=i*math.tau/8;radial=Vector((math.cos(angle),math.sin(angle),0));p,n,face,distance=tree.ray_cast(radial*2+Vector((0,0,.105)),-radial,3)
        assert p is not None,('no hull at spike base',i,author.bounds([body]))
        start=p-radial*.025;tip=p+radial*.22+Vector((0,0,.02));axis=tip-start
        bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=.038,radius2=.003,depth=axis.length,location=(start+tip)/2)
        cone=bpy.context.object;cone.name=PREFIX+f'{i:02}';cone.rotation_euler=axis.to_track_quat('Z','Y').to_euler();cone.data.materials.append(material)
        author.core.assign_uv(cone,material,0)
        group=cone.vertex_groups.new(name=cone.name);group.add(list(range(len(cone.data.vertices))),1,'REPLACE')
        # Explicit corner normals preserve small manufactured facets in both formats.
        normals=[tuple(v.vector) for v in cone.data.corner_normals]
        for face in cone.data.polygons:face.use_smooth=True
        cone.data.normals_split_custom_set(normals)
        parts.append(cone);spikes.append(dict(name=cone.name,azimuth_degrees=i*45,surface_point=list(p),start=list(start),tip=list(tip),base_radius=.038,tip_radius=.003))
    bpy.ops.object.select_all(action='DESELECT');body.select_set(True)
    for cone in parts:cone.select_set(True)
    bpy.context.view_layer.objects.active=body;bpy.ops.object.join()
    bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
    while len(body.data.materials)>1:body.data.materials.pop(index=len(body.data.materials)-1)
    for face in body.data.polygons:face.material_index=0
    root=bpy.data.objects['PlacementRoot'];root['peripheral_spike_count']=8;root['peripheral_spike_spacing_degrees']=45
    bpy.ops.object.select_all(action='DESELECT')
    for obj in bpy.context.scene.objects:
        if obj.type in ['MESH','EMPTY']:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True,relative_remap=True)
    meta['triangles']=sum(len(o.data.polygons) for o in author.meshes());meta['final_bounds']=author.bounds(author.meshes())
    meta['spike_refinement']=dict(generator=Path(__file__).relative_to(author.ROOT).as_posix(),generator_sha256=author.sha(Path(__file__)),input_binaries=before,mesh_group=body.name,spikes=spikes,interpretation='Eight small rim projections at45-degree intervals, following user interpretation of MK0A; four large fins and central spike retained; dimensions authored')
    meta['editable_part_vertex_groups'][body.name]=[g.name for g in body.vertex_groups]
    for kind in before:meta[kind+'_sha256']=author.sha(out/('model.'+kind))
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('HIERO_SPIKES_REFINED',meta['triangles'],meta['spike_refinement'],flush=True)


if __name__=='__main__':main()
