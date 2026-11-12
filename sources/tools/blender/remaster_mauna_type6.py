"""MN2C detail author: original hull plus fitted user-concept maintenance structure."""
from pathlib import Path
import argparse,json,sys
import bpy,bmesh
from mathutils import Matrix,Vector
sys.path.insert(0,str(Path(__file__).parent))
import remaster_artemian_mobile_ship as shared
import mauna_type6_detail_parts as detail_parts
core=shared.core
sha=core.sha
ROOT=Path(__file__).resolve().parents[3]
MAPS=ROOT/'sources/materials/mauna/mobile-ships'


def transformed_reference_point(name,point,recipe):
    p=shared.transformed_reference_point(name,point,recipe)
    for change in recipe.get('part_rotations',[]):
        if name in change['parts']:
            origin=Vector(change['origin']);p=origin+Matrix.Rotation(change['angle'],3,change['axis'])@(p-origin)
    return p


def transformed_reference_direction(name,direction,recipe):
    result=Vector(direction)
    for change in recipe.get('part_rotations',[]):
        if name in change['parts']:result=Matrix.Rotation(change['angle'],3,change['axis'])@result
    return result.normalized()


def folders(key):return ROOT/'sources/objects/mauna'/key,ROOT/'gallery/media/objects/mauna'/key


def group_for(name):
    name=name.lower()
    if any(s in name for s in ['fastener','seam strip','edge rail','upper rail','small marker']):return 'TrimAndFasteners'
    if any(s in name for s in ['inset','dark','slot','interface','recess']):return 'RecessedMachinery'
    if any(s in name for s in ['service frame','service cover','bezel','bracket','housing']):return 'ServiceAssemblies'
    return 'PrimaryHullAndArmour'


def assign_uv(obj,mat,recipe):
    tiles=shared.assign_recipe_uv(obj,mat,recipe);uv=obj.data.uv_layers.active.data
    points=[v.co for v in obj.data.vertices];low=[min(p[a] for p in points) for a in range(3)];high=[max(p[a] for p in points) for a in range(3)]
    for face in obj.data.polygons:
        first=uv[face.loop_start].uv;tile=int(first.x*4)+4*int((1-first.y)*2)
        assert 0<=tile<8
        axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(face.normal[a]))]
        for loop in face.loop_indices:
            p=obj.data.vertices[obj.data.loops[loop].vertex_index].co
            u,v=[(p[a]-low[a])/max(1e-8,high[a]-low[a]) for a in axes]
            uv[loop].uv=((tile%4+.008+u*.984)/4,1-(tile//4+.008+v*.984)/2)
    return tiles


def main(key):
    out,media=folders(key);recipe_path=out/'recipe.json';recipe=json.loads(recipe_path.read_text());out.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sources'/recipe['source']/'model.blend';baseline=sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;baseline_bounds=core.bounds(core.meshes());details=detail_parts.add_details(recipe);recipe['attachment_pairs']+=details['attachment_pairs'];core.MAPS=MAPS;mat=core.material();mat.name='Mauna | used utilitarian grey and blue alloy';reductions=[];groups={}
    for o in list(core.meshes()):
        assert o.data.materials and all(m.name in recipe['material_tiles'] for m in o.data.materials),(key,o.name)
        if o.animation_data:o.animation_data_clear()
        bpy.context.view_layer.objects.active=o
        for modifier in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        adjustment=recipe.get('upper_shell_refinement',{})
        if o.name in adjustment.get('parts',[]):
            if o.data.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
            for vertex in o.data.vertices:vertex.co=shared.transformed_reference_point(o.name,vertex.co,recipe)
            for face in o.data.polygons:face.use_smooth=False
            o.data.update()
        for change in recipe.get('part_transforms',[]):
            if o.name!=change['part']:continue
            normals=[n.vector.copy() for n in o.data.corner_normals];axis=Vector(change['axis']).normalized()
            for vertex in o.data.vertices:vertex.co=shared.transformed_reference_point(o.name,vertex.co,recipe)
            o.data.update();corrected=[]
            for normal in normals:
                axial=axis*normal.dot(axis);corrected.append(((normal-axial)/change['transverse_scale']+axial/change['axial_scale']).normalized())
            o.data.normals_split_custom_set(corrected)
        for change in recipe.get('part_rotations',[]):
            if o.name not in change['parts']:continue
            normals=[n.vector.copy() for n in o.data.corner_normals];origin=Vector(change['origin']);rotation=Matrix.Rotation(change['angle'],3,change['axis'])
            for vertex in o.data.vertices:vertex.co=origin+rotation@(vertex.co-origin)
            o.data.update();o.data.normals_split_custom_set([(rotation@n).normalized() for n in normals])
        before=len(o.data.polygons);target=next((v for word,v in recipe['part_face_budget'].items() if word!='default' and word in o.name.lower()),recipe['part_face_budget']['default'])
        if before>target:
            modifier=o.modifiers.new('Game density budget','DECIMATE');modifier.ratio=target/before;modifier.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=modifier.name)
        edge_finish=recipe.get('edge_finish',{})
        if any(word in o.name.lower() for word in edge_finish.get('part_keywords',[])):
            modifier=o.modifiers.new('Manufactured edge radius','BEVEL');modifier.width=edge_finish['width'];modifier.segments=edge_finish['segments'];modifier.limit_method='ANGLE';modifier.angle_limit=edge_finish['angle_limit'];modifier.use_clamp_overlap=True
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        if o.name=='Type 6 sloped upper roof':
            # Keep the loft's vertical planar walls from inheriting cap-normal waves.
            normals=[tuple(face.normal if abs(face.normal.z)<.05 else o.data.corner_normals[loop].vector) for face in o.data.polygons for loop in face.loop_indices]
            for face in o.data.polygons:face.use_smooth=True
            o.data.normals_split_custom_set(normals)
        tile=assign_uv(o,mat,recipe)
        reductions.append(dict(part=o.name,source_faces=before,final_faces=len(o.data.polygons),atlas_tile=tile))
        groups.setdefault(group_for(o.name),[]).append(o)
    root=bpy.data.objects['PlacementRoot'];mapping={}
    for group,items in groups.items():
        mapping[group]=[o.name for o in items];bpy.ops.object.select_all(action='DESELECT')
        for o in items:
            vg=o.vertex_groups.new(name=o.name);vg.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=group;o.parent=root
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
        normals=[tuple(n.vector) for n in o.data.corner_normals]
        for face in o.data.polygons:face.use_smooth=True
        o.data.normals_split_custom_set(normals)
    for material in list(bpy.data.materials):
        if material.users==0:bpy.data.materials.remove(material)
    for image in list(bpy.data.images):
        if image.users==0:bpy.data.images.remove(image)
    triangles=sum(len(o.data.polygons) for o in core.meshes());assert triangles<recipe['max_triangles'],triangles
    root['catalogue_id']=recipe['id'];root['size_class']=recipe['size_class'];root['world_size_proposal']=recipe['world_size_proposal'];root['socket_calibration']='Uncalibrated; retained alignment helper only'
    scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
    core.fit_camera(scene,core.evaluated_points(core.meshes()),core.VIEWS['front-quarter']);bpy.ops.object.select_all(action='DESELECT')
    for o in scene.objects:
        if o.type in ['MESH','EMPTY']:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True,relative_remap=True)
    meta=dict(**recipe,detailed_parts=details,detail_parts_sha256=sha(Path(detail_parts.__file__)),detail_baseline_helpers_sha256=sha(Path(detail_parts.roof_patch.__code__.co_filename)),detail_primitives_sha256=sha(Path(detail_parts.box.__code__.co_filename)),stage='mobile-ship-remaster',baseline_sha256=baseline,baseline_bounds=baseline_bounds,final_bounds=core.bounds(core.meshes()),triangles=triangles,mesh_batches=len(core.meshes()),material_count=1,packed_maps=3,editable_part_vertex_groups=mapping,reductions=reductions,generator_sha256=sha(Path(__file__)),recipe_sha256=sha(recipe_path),shared_primitives_sha256=sha(Path(core.__file__)),shared_recipe_helpers_sha256=sha(Path(shared.__file__)),maps_generator_sha256=sha(ROOT/'tools/author_mauna_mobile_maps.py'),map_sha256={p.name:sha(p) for p in MAPS.glob('*.png')},blend_sha256=sha(out/'model.blend'),glb_sha256=sha(out/'model.glb'),visual_acceptance='Concept and imported-GLB feedback pending; client calibration separate')
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('MAUNA_CANONICAL',key,triangles,len(core.meshes()),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ship',required=True);main(p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
