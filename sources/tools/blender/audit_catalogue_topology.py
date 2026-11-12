"""Measure actual native/import topology; diagnostics never mutate saved sources."""
import hashlib
import json
from pathlib import Path
import bpy
import bmesh

REPO=Path(__file__).resolve().parents[2]
OUTPUT=REPO/'docs/assets/reconstruction/evidence/catalogue-topology'
TOLERANCE=1e-6


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(bm):
    bm.verts.ensure_lookup_table()
    components=[];remaining=set(bm.verts)
    while remaining:
        start=remaining.pop();group={start};stack=[start]
        while stack:
            for edge in stack.pop().link_edges:
                for vertex in edge.verts:
                    if vertex in remaining:
                        remaining.remove(vertex);group.add(vertex);stack.append(vertex)
        components.append(group)
    membership={v:i for i,group in enumerate(components) for v in group}
    volumes=[0.0]*len(components)
    for triangle in bm.calc_loop_triangles():
        a,b,c=[loop.vert.co for loop in triangle]
        volumes[membership[triangle[0].vert]]+=a.dot(b.cross(c))/6
    closed=[all(edge.is_manifold for vertex in group for edge in vertex.link_edges)
            and any(vertex.link_faces for vertex in group) for group in components]
    areas=[face.calc_area() for face in bm.faces]
    return dict(vertices=len(bm.verts),edges=len(bm.edges),faces=len(bm.faces),
        boundary_edges=sum(e.is_boundary for e in bm.edges),loose_edges=sum(not e.link_faces for e in bm.edges),
        loose_vertices=sum(not v.link_edges for v in bm.verts),
        nonmanifold_fans=sum(len(e.link_faces)>2 for e in bm.edges),
        zero_faces=sum(a<=1e-12 for a in areas),tiny_faces=sum(a<=1e-10 for a in areas),
        minimum_face_area=min(areas) if areas else None,
        components=[dict(vertices=len(group),closed=is_closed,signed_volume=volume)
                    for group,is_closed,volume in zip(components,closed,volumes)])


def inspect_scene():
    graph=bpy.context.evaluated_depsgraph_get();result={};excluded=[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH': continue
        if obj.get('preview_only'):
            excluded.append(obj.name);continue
        evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
        bm=bmesh.new();bm.from_mesh(mesh);bm.transform(evaluated.matrix_world)
        raw=metrics(bm)
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=TOLERANCE)
        welded=metrics(bm)
        result[obj.name]=dict(raw=raw,welded=welded,vertices_merged=raw['vertices']-welded['vertices'])
        bm.free();evaluated.to_mesh_clear()
    assert result,'No asset meshes'
    return result,excluded


def flags(objects):
    result={}
    for name,record in objects.items():
        value=record['welded'];issues=[]
        for key in ['boundary_edges','loose_edges','loose_vertices','nonmanifold_fans','zero_faces']:
            if value[key]: issues.append(key)
        if not value['faces']: issues.append('no_faces')
        if any(c['closed'] and c['signed_volume']<=0 for c in value['components']): issues.append('nonpositive_closed_component')
        if issues: result[name]=issues
    return result


def main():
    OUTPUT.mkdir(parents=True,exist_ok=True)
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    inventory=json.loads(inventory_path.read_text());rows=[]
    assert len(inventory['records'])==303
    for index,record in enumerate(inventory['records']):
        study=[s for s in record['available_studies'] if s['present']][-1]
        source=REPO/study['blend'];export=source.with_suffix('.glb')
        assert source.is_file() and export.is_file() and sha(source)==study['sha256']
        before=dict(blend_sha256=sha(source),glb_sha256=sha(export))
        bpy.ops.wm.open_mainfile(filepath=str(source));bpy.context.scene.frame_set(1)
        native,excluded=inspect_scene()
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(export));bpy.context.scene.frame_set(0)
        imported,imported_excluded=inspect_scene()
        assert before==dict(blend_sha256=sha(source),glb_sha256=sha(export)),'Source changed'
        report=dict(issue=1107,id=record['id'],category=record['category'],culture=record['culture'],
            blend=study['blend'],**before,native=native,imported=imported,
            native_flags=flags(native),imported_flags=flags(imported),
            object_names_equal=native.keys()==imported.keys(),excluded_preview_meshes=excluded,
            imported_excluded_preview_meshes=imported_excluded,source_assets_unchanged=True,
            final_visual_acceptance=False)
        name=f'{index:03}.json';path=OUTPUT/name;path.write_text(json.dumps(report,indent=2)+'\n')
        rows.append(dict(id=record['id'],category=record['category'],report=name,sha256=sha(path),
            native_meshes=len(native),imported_meshes=len(imported),
            native_flagged_meshes=len(report['native_flags']),imported_flagged_meshes=len(report['imported_flags']),
            object_names_equal=report['object_names_equal']))
        print('CATALOGUE_TOPOLOGY_INSPECTED',record['id'],len(report['native_flags']),len(report['imported_flags']),flush=True)
    summary=dict(issue=1107,blender=bpy.app.version_string,auditor_sha256=sha(Path(__file__)),
        inventory_sha256=sha(inventory_path),definitions=len(rows),records=rows,
        diagnostic_world_weld_tolerance=TOLERANCE,zero_face_area_threshold=1e-12,tiny_face_area_threshold=1e-10,
        scope='First-pose evaluated topology in world coordinates, raw and diagnostic-only welded. Flags require interpretation; neither final art nor complete state/UV/material/game integration acceptance.',
        final_visual_acceptance=False)
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print('CATALOGUE_TOPOLOGY_AUDIT_OK',len(rows),flush=True)


if __name__=='__main__': main()
