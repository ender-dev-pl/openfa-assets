"""Recipe-driven canonical remaster; preserve fitted source parts and authoring names."""
from pathlib import Path
import argparse,json,sys
import bpy,bmesh
from mathutils import Matrix,Vector
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
    for change in recipe.get('part_transforms',[]):
        if name!=change['part']:continue
        origin=Vector(change['origin']);axis=Vector(change['axis']).normalized();delta=p-origin;axial=axis*delta.dot(axis)
        p=origin+(delta-axial)*change['transverse_scale']+axial*change['axial_scale']
    return p


def assign_recipe_uv(obj,mat,recipe):
    names=[m.name for m in obj.data.materials]
    assert names and all(name in recipe['material_tiles'] for name in names),(obj.name,names)
    layout=recipe.get('surface_regions',{}).get(obj.name)
    if layout:
        obj['material_layout']=layout['interpretation']
        # Material boundaries must cross large faces continuously instead of
        # classifying whole triangles into a visibly serrated colour stripe.
        bm=bmesh.new();bm.from_mesh(obj.data)
        planes={(band['axis'],value) for band in layout['bands'] for value in [band['minimum'],band['maximum']]}
        for axis,value in sorted(planes):
            index='xyz'.index(axis);point=[0,0,0];point[index]=value;normal=[0,0,0];normal[index]=1
            bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=point,plane_no=normal,clear_inner=False,clear_outer=False)
        bm.to_mesh(obj.data);bm.free();obj.data.update()
    if len(names)==1 and not layout:
        tile=recipe['material_tiles'][names[0]];core.assign_uv(obj,mat,tile);return tile
    tiles=[]
    for face in obj.data.polygons:
        tile=recipe['material_tiles'][names[face.material_index]]
        if layout:
            tile=layout['default_tile'];centre=face.center
            for band in layout['bands']:
                value=centre['xyz'.index(band['axis'])]
                if band['minimum']<=value<=band['maximum']:tile=band['tile']
        assert 0<=tile<8;tiles.append(tile)
    # Reuse the proven projection with a zero tile; apply explicit per-face
    # atlas offsets after it clears source materials. No face index is lost.
    core.assign_uv(obj,mat,0);uv=obj.data.uv_layers.active.data
    for face,tile in zip(obj.data.polygons,tiles):
        for loop in face.loop_indices:
            uv[loop].uv.x+=(tile%4)/4;uv[loop].uv.y-=(tile//4)/2
    return sorted(set(tiles))


def main(key):
    out,media=folders(key);recipe_path=out/'recipe.json';recipe=json.loads(recipe_path.read_text());out.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sources'/recipe['source']/'model.blend';baseline=sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene;baseline_bounds=core.bounds(core.meshes());core.MAPS=MAPS;mat=core.material();mat.name='Artemian | used alloy green bronze and silver';reductions=[];groups={}
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
            for vertex in o.data.vertices:vertex.co=transformed_reference_point(o.name,vertex.co,recipe)
            for face in o.data.polygons:face.use_smooth=False
            o.data.update()
        for change in recipe.get('part_transforms',[]):
            if o.name!=change['part']:continue
            normals=[n.vector.copy() for n in o.data.corner_normals];axis=Vector(change['axis']).normalized()
            for vertex in o.data.vertices:vertex.co=transformed_reference_point(o.name,vertex.co,recipe)
            o.data.update();corrected=[]
            for normal in normals:
                axial=axis*normal.dot(axis);corrected.append(((normal-axial)/change['transverse_scale']+axial/change['axial_scale']).normalized())
            o.data.normals_split_custom_set(corrected)
        before=len(o.data.polygons);target=next((v for word,v in recipe['part_face_budget'].items() if word!='default' and word in o.name.lower()),recipe['part_face_budget']['default'])
        if before>target:
            modifier=o.modifiers.new('Game density budget','DECIMATE');modifier.ratio=target/before;modifier.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=modifier.name)
        edge_finish=recipe.get('edge_finish',{})
        if any(word in o.name.lower() for word in edge_finish.get('part_keywords',[])):
            modifier=o.modifiers.new('Manufactured edge radius','BEVEL');modifier.width=edge_finish['width'];modifier.segments=edge_finish['segments'];modifier.limit_method='ANGLE';modifier.angle_limit=edge_finish['angle_limit'];modifier.use_clamp_overlap=True
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        tile=assign_recipe_uv(o,mat,recipe)
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
    meta=dict(**recipe,stage='mobile-ship-remaster',baseline_sha256=baseline,baseline_bounds=baseline_bounds,final_bounds=core.bounds(core.meshes()),triangles=triangles,mesh_batches=len(core.meshes()),material_count=1,packed_maps=3,editable_part_vertex_groups=mapping,reductions=reductions,generator_sha256=sha(Path(__file__)),recipe_sha256=sha(recipe_path),shared_primitives_sha256=sha(Path(core.__file__)),maps_generator_sha256=sha(ROOT/'tools/author_artemian_mobile_maps.py'),map_sha256={p.name:sha(p) for p in MAPS.glob('*.png')},blend_sha256=sha(out/'model.blend'),glb_sha256=sha(out/'model.glb'),visual_acceptance='Concept and imported-GLB feedback pending; client calibration separate')
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('ARTEMIAN_CANONICAL',key,triangles,len(core.meshes()),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ship',required=True);main(p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
