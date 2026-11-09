"""Recipe-driven canonical remaster; preserve fitted source parts and authoring names."""
from pathlib import Path
import argparse,json,sys
import bpy,bmesh
from mathutils import Matrix
sys.path.insert(0,str(Path(__file__).parent))
import remaster_braccatian_mobile_ships as core
ROOT=Path(__file__).resolve().parents[3]
MAPS=ROOT/'sources/materials/artemian/mobile-ships'
sha=core.sha


def folders(key):return ROOT/'sources/objects/artemian'/key,ROOT/'gallery/media/objects/artemian'/key


def group_for(name):
    name=name.lower()
    if any(s in name for s in ['fastener','slat','pin','trim','band']):return 'TrimAndFasteners'
    if any(s in name for s in ['slot','inset','interface','recess']):return 'RecessedMachinery'
    if any(s in name for s in ['cover','bezel','housing','bracket']):return 'ServiceAssemblies'
    return 'PrimaryHullAndArmour'


def transformed_reference_point(name,point,recipe):
    """Declared profile refinement, also used for honest baseline comparisons."""
    p=point.copy();adjustment=recipe.get('upper_shell_refinement')
    if adjustment and name in adjustment['parts']:
        t=max(0,min(1,(adjustment['transition_y']-p.y)/(adjustment['transition_y']-adjustment['old_front_y'])))
        old_width=adjustment['transition_half_width']*(1-t)+adjustment['old_front_half_width']*t
        target_width=adjustment['transition_half_width']*(1-t)+adjustment['front_half_width']*t
        p.x*=target_width/old_width
        p.y+=adjustment['front_retreat']*t
        p.z=(p.z+adjustment['front_lift']*t*max(0,min(1,(p.z+.015)/.04)))*adjustment['height_scale']
    return p


def main(key):
    out,media=folders(key);recipe_path=out/'recipe.json';recipe=json.loads(recipe_path.read_text());out.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sources'/recipe['source']/'model.blend';baseline=sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;baseline_bounds=core.bounds(core.meshes());core.MAPS=MAPS;mat=core.material();mat.name='Artemian | used alloy green bronze and silver';reductions=[];groups={}
    for o in list(core.meshes()):
        assert len(o.data.materials)==1,(key,o.name)
        old_material=o.data.materials[0].name;assert old_material in recipe['material_tiles'],old_material
        if o.animation_data:o.animation_data_clear()
        bpy.context.view_layer.objects.active=o
        for modifier in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
        bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
        adjustment=recipe.get('upper_shell_refinement',{})
        if o.name in adjustment.get('parts',[]):
            if o.data.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
            for vertex in o.data.vertices:vertex.co=transformed_reference_point(o.name,vertex.co,recipe)
            for face in o.data.polygons:face.use_smooth=False
            o.data.update()
        before=len(o.data.polygons);target=next((v for word,v in recipe['part_face_budget'].items() if word!='default' and word in o.name.lower()),recipe['part_face_budget']['default'])
        if before>target:
            modifier=o.modifiers.new('Game density budget','DECIMATE');modifier.ratio=target/before;modifier.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=modifier.name)
        reductions.append(dict(part=o.name,source_faces=before,final_faces=len(o.data.polygons),atlas_tile=recipe['material_tiles'][old_material]))
        core.assign_uv(o,mat,recipe['material_tiles'][old_material]);groups.setdefault(group_for(o.name),[]).append(o)
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
    meta=dict(**recipe,stage='mobile-ship-remaster',baseline_sha256=baseline,baseline_bounds=baseline_bounds,final_bounds=core.bounds(core.meshes()),triangles=triangles,mesh_batches=len(core.meshes()),material_count=1,packed_maps=3,editable_part_vertex_groups=mapping,reductions=reductions,generator_sha256=sha(Path(__file__)),recipe_sha256=sha(recipe_path),shared_primitives_sha256=sha(Path(core.__file__)),maps_generator_sha256=sha(ROOT/'tools/author_artemian_mobile_maps.py'),map_sha256={p.name:sha(p) for p in MAPS.glob('*.png')},blend_sha256=sha(out/'model.blend'),glb_sha256=sha(out/'model.glb'),visual_acceptance='Concept and imported-GLB feedback pending; client calibration separate')
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('ARTEMIAN_CANONICAL',key,triangles,len(core.meshes()),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ship',required=True);main(p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
