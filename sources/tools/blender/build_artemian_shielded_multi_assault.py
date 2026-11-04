"""Build the first independently authored Shielded Multi; original pixels stay reference-only."""
import hashlib,json,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import render_to,save_blend_to,stage_path,publish
from catalogue_rendering import evaluated_points,fit_camera
from terran_light_ship_parts import orient_and_chamfer
from artemian_shielded_multi_assault_parts import build,SOCKETS,PATCHES,WING,ROOF

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/ships/artemian/shielded-multi-assault'
VIEWS=[('front-quarter',(7,-12,9)),('rear-quarter',(-7,12,8)),('front',(0,-15,5)),('side',(15,0,5)),('top',(0,0,20)),('underside',(7,-8,-14))]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def wear(meshes):
    for style,name in [('hull','Shielded Multi | worn silver alloy'),('gold','Shielded Multi | worn gold alloy')]:
        surface=bpy.data.materials[name];nodes=surface.node_tree.nodes;links=surface.node_tree.links;shader=nodes.get('Principled BSDF')
        coordinates=nodes.new('ShaderNodeUVMap');coordinates.uv_map='Authored box wear'
        for kind,input_name,space in [('colour','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
            image=bpy.data.images.load(str(ROOT/f'authored-{style}-{kind}.png'));image.colorspace_settings.name=space;image.pack()
            texture=nodes.new('ShaderNodeTexImage');texture.image=image;links.new(texture.outputs['Color'],shader.inputs[input_name]);links.new(coordinates.outputs['UV'],texture.inputs['Vector'])
    for obj in meshes:
        if not any(m.name in ['Shielded Multi | worn silver alloy','Shielded Multi | worn gold alloy'] for m in obj.data.materials): continue
        while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
        uv=obj.data.uv_layers.new(name='Authored box wear');uv.active_render=True
        points=[v.co for v in obj.data.vertices];low=[min(p[a] for p in points) for a in range(3)];high=[max(p[a] for p in points) for a in range(3)]
        for face in obj.data.polygons:
            dominant=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=dominant]
            for index in face.loop_indices:
                p=obj.data.vertices[obj.data.loops[index].vertex_index].co
                uv.data[index].uv=tuple((p[a]-low[a])/max(1e-8,high[a]-low[a]) for a in axes)


def main():
    ROOT.mkdir(parents=True,exist_ok=True);scene=setup_scene(900,64)
    collection=bpy.data.collections.new('Shielded Multi independent editable first source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build();meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    # Apply the authored bevels before assigning stable UVs and exporting.
    for obj in meshes:
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
    for obj in meshes:
        if not (obj.name.startswith('Shielded Multi rear bezel') or obj.name in [WING,ROOF]): continue
        bm=bmesh.new();bm.from_mesh(obj.data)
        if obj.name in [WING,ROOF]:bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
    # glTF imports custom normals on smooth faces. Preserve authored flat/smooth
    # corner vectors explicitly so native Cycles uses the same shading contract.
    for obj in meshes:
        normals=[tuple(value.vector) for value in obj.data.corner_normals]
        for face in obj.data.polygons: face.use_smooth=True
        obj.data.normals_split_custom_set(normals)
    wear(meshes)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root);root['catalogue_id']='openfa:ship/artemian/shielded-multi-assault';root['forward_axis']='local -Y'
    for obj in meshes: obj.parent=root
    sockets=[]
    for name,(position,forward) in SOCKETS.items():
        socket=bpy.data.objects.new(name,None);collection.objects.link(socket);socket.parent=root;socket.location=position;socket.rotation_euler=Vector(forward).to_track_quat('Z','Y').to_euler();socket['forward_axis']='local +Z';socket['calibration']='authored interpretation; not recovered 3D mount';sockets.append(socket)
    bpy.context.view_layer.update();collection.asset_mark();collection.asset_data.description='First independent Shielded Multi-Assault ship; runtime calibration pending'
    points=evaluated_points(meshes)
    for name,direction in VIEWS: fit_camera(scene,points,direction);render_to(scene,ROOT/(name+'.png'))
    fit_camera(scene,points,VIEWS[0][1]);bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]+sockets: obj.select_set(True)
    bpy.context.view_layer.objects.active=root;temporary=stage_path('.glb')
    bpy.ops.export_scene.gltf(filepath=str(temporary),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True);publish(temporary,ROOT/'model.glb');save_blend_to(ROOT/'model.blend')
    meta=dict(id='openfa:ship/artemian/shielded-multi-assault',issue=1019,revision=1,name='Shielded Multi-Assault',culture='artemian',mesh_objects=len(meshes),views=[name for name,_ in VIEWS],resolution=900,
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('artemian_shielded_multi_assault_parts.py')),
        authored_wear_sha256=sha(ROOT/'authored-wear.json'),reference_sha256=sha(REPO/'docs/reconstruction/models/ship-reference-index.json'),functional_source_sha256=sha(REPO/'docs/reconstruction/models/functional-text-index.json'),
        cultural_style_sha256=sha(REPO/'docs/reconstruction/models/cultural-architecture-index.json'),cultural_style_reference=dict(culture='artemian',record=105,offset_hex='0x5734',scope='Architectural metal/alloy, edge and shell guidance is contextual for spacecraft; not recovered geometry or a vehicle material specification'),
        catalogue_sha256=sha(REPO/'content/standard/catalogues/legacy-gameplay.json'),equipment_slots=dict(declared=4,calibrated_3d_mounts=0),conformal_panels=PATCHES,function='Catalogue combat-direct-approach / role class 3; no mapped functional narrative',helper_sha256={n:sha(Path(__file__).with_name(n)) for n in ['terran_light_ship_parts.py','build_openfa_assets.py','build_refined_terran.py','catalogue_rendering.py']},blender=bpy.app.version_string,
        observed=['AR2C headings: broad flat silver-grey silhouette, raised centre, warm gold areas, blue-grey details and pale/amber marks','32 populated paletted headings; no catalogue video located'],
        inferred=['Pointed broad metal wing and low pressure body; port gold/starboard silver distribution is an authored interpretation, not recovered material calibration','Four equipment slots lack mount coordinates; fittings are not assigned to slots or labelled engines/weapons; name does not establish visible shield geometry'],
        sockets={name:dict(position=list(position),forward=list(forward),status='authored-uncalibrated') for name,(position,forward) in SOCKETS.items()},
        imported_geometry_or_textures=[],unresolved=['Final artistic acceptance','Runtime scale/orientation and 3D hardpoint calibration','Damage/operational variants; no mechanisms/timing established'],acceptance='First authored iteration; artistic refining deferred')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('ARTEMIAN_SHIELDED_MULTI_ASSAULT_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
