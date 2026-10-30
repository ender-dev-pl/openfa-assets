"""Build the first independently authored Mikotaj Bruj-Mahal; original pixels stay reference-only."""
import hashlib,json,sys,math
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import render_to,save_blend_to,stage_path,publish
from catalogue_rendering import evaluated_points,fit_camera
from terran_light_ship_parts import orient_and_chamfer
from mikotaj_bruj_mahal_parts import build,SOCKETS,PATCHES,PROFILES,LOCATIONS,ROTATIONS

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/missiles/mikotaj/bruj-mahal'
VIEWS=[('front-quarter',(7,-12,9)),('rear-quarter',(-7,12,8)),('front',(0,-15,5)),('side',(15,0,5)),('top',(0,0,20)),('underside',(7,-8,-14))]


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def wear(meshes):
    for style,name in [('gold','Mikotaj Bruj-Mahal | worn green body alloy'),('red','Mikotaj Bruj-Mahal | worn grey side alloy'),('accent','Mikotaj Bruj-Mahal | worn pale green casting alloy')]:
        surface=bpy.data.materials[name];nodes=surface.node_tree.nodes;links=surface.node_tree.links;shader=nodes.get('Principled BSDF')
        coordinates=nodes.new('ShaderNodeUVMap');coordinates.uv_map='Authored box wear'
        for kind,input_name,space in [('colour','Base Color','sRGB'),('roughness','Roughness','Non-Color')]:
            image=bpy.data.images.load(str(ROOT/f'authored-{style}-{kind}.png'));image.colorspace_settings.name=space;image.pack()
            texture=nodes.new('ShaderNodeTexImage');texture.image=image;links.new(texture.outputs['Color'],shader.inputs[input_name]);links.new(coordinates.outputs['UV'],texture.inputs['Vector'])
    for obj in meshes:
        if not any(m.name in ['Mikotaj Bruj-Mahal | worn green body alloy','Mikotaj Bruj-Mahal | worn grey side alloy','Mikotaj Bruj-Mahal | worn pale green casting alloy'] for m in obj.data.materials): continue
        while obj.data.uv_layers: obj.data.uv_layers.remove(obj.data.uv_layers[0])
        uv=obj.data.uv_layers.new(name='Authored box wear');uv.active_render=True
        points=[v.co for v in obj.data.vertices];low=[min(p[a] for p in points) for a in range(3)];high=[max(p[a] for p in points) for a in range(3)]
        for face in obj.data.polygons:
            dominant=max(range(3),key=lambda a:abs(face.normal[a]));axes=[a for a in range(3) if a!=dominant]
            if obj.name in PROFILES:
                # Lathed primary bodies use one continuous angular chart rather
                # than switching box faces across a visible curved surface.
                values=[];start,end=PROFILES[obj.name][0][0],PROFILES[obj.name][-1][0]
                for index in face.loop_indices:
                    p=ROTATIONS[obj.name].transposed() @ (obj.data.vertices[obj.data.loops[index].vertex_index].co-LOCATIONS[obj.name])
                    values.append(((math.atan2(p.y,p.x)/math.tau)%1,(p.z-start)/(end-start)))
                seam=max(u for u,v in values)-min(u for u,v in values)>.5
                for index,(u,v) in zip(face.loop_indices,values):uv.data[index].uv=(u+1 if seam and u<.5 else u,v)
            else:
                for index in face.loop_indices:
                    p=obj.data.vertices[obj.data.loops[index].vertex_index].co
                    uv.data[index].uv=tuple((p[a]-low[a])/max(1e-8,high[a]-low[a]) for a in axes)


def main():
    ROOT.mkdir(parents=True,exist_ok=True);scene=setup_scene(900,64)
    collection=bpy.data.collections.new('Mikotaj Bruj-Mahal independent editable first source');scene.collection.children.link(collection)
    bpy.context.view_layer.active_layer_collection=bpy.context.view_layer.layer_collection.children[collection.name]
    build();meshes=[obj for obj in collection.objects if obj.type=='MESH'];orient_and_chamfer(meshes)
    # Apply the authored bevels before assigning stable UVs and exporting.
    for obj in meshes:
        bpy.context.view_layer.objects.active=obj
        for modifier in list(obj.modifiers): bpy.ops.object.modifier_apply(modifier=modifier.name)
    for obj in meshes:
        if obj.name not in PROFILES and not any(k in obj.name for k in ['body band','pale longitudinal casting']): continue
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.triangulate(bm,faces=list(bm.faces))
        bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free();obj.data.update()
    # glTF imports custom normals on smooth faces. Preserve authored flat/smooth
    # corner vectors explicitly so native Cycles uses the same shading contract.
    for obj in meshes:
        normals=[tuple(value.vector) for value in obj.data.corner_normals]
        for face in obj.data.polygons: face.use_smooth=True
        obj.data.normals_split_custom_set(normals)
    wear(meshes)
    root=bpy.data.objects.new('PlacementRoot',None);collection.objects.link(root);root['catalogue_id']='openfa:missile/mikotaj/bruj-mahal';root['forward_axis']='local -Y'
    for obj in meshes: obj.parent=root
    sockets=[]
    for name,(position,forward) in SOCKETS.items():
        socket=bpy.data.objects.new(name,None);collection.objects.link(socket);socket.parent=root;socket.location=position;socket.rotation_euler=Vector(forward).to_track_quat('Z','Y').to_euler();socket['forward_axis']='local +Z';socket['calibration']='authored interpretation; not recovered 3D mount';sockets.append(socket)
    bpy.context.view_layer.update();collection.asset_mark();collection.asset_data.description='First low-resolution Mikotaj Bruj-Mahal interpretation; runtime calibration pending'
    points=evaluated_points(meshes)
    for name,direction in VIEWS: fit_camera(scene,points,direction);render_to(scene,ROOT/(name+'.png'))
    fit_camera(scene,points,VIEWS[0][1]);bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes+[root]+sockets: obj.select_set(True)
    bpy.context.view_layer.objects.active=root;temporary=stage_path('.glb')
    bpy.ops.export_scene.gltf(filepath=str(temporary),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True);publish(temporary,ROOT/'model.glb');save_blend_to(ROOT/'model.blend')
    meta=dict(id='openfa:missile/mikotaj/bruj-mahal',issue=1064,revision=1,name='Mikotaj Bruj-Mahal',culture='mikotaj',mesh_objects=len(meshes),views=[name for name,_ in VIEWS],resolution=900,
        blend_sha256=sha(ROOT/'model.blend'),glb_sha256=sha(ROOT/'model.glb'),generator_sha256=sha(Path(__file__)),parts_sha256=sha(Path(__file__).with_name('mikotaj_bruj_mahal_parts.py')),
        authored_wear_sha256=sha(ROOT/'authored-wear.json'),reference_sha256=sha(REPO/'docs/reconstruction/models/missile-reference-index.json'),functional_source_sha256=sha(REPO/'docs/reconstruction/models/functional-text-index.json'),
        catalogue_sha256=sha(REPO/'content/standard/catalogues/legacy-gameplay.json'),mount_calibration='authored alignment only; no recovered gameplay mount',conformal_panels=PATCHES,function='Catalogue vortex behaviour; global type 34, ore units 8, budget cost 20; no mapped missile narrative; no mapped narrative',helper_sha256={n:sha(Path(__file__).with_name(n)) for n in ['terran_light_ship_parts.py','build_openfa_assets.py','build_refined_terran.py','catalogue_rendering.py','manufactured_vessels.py','manufactured_annuli.py']},blender=bpy.app.version_string,
        observed=['MKM5: elongated green body with pale segmented details, grey side edging and tapered green ends; flight and launch presentation differ; fourteen flight/launch states, no management preview','Exhaust-bearing states establish a forward terminal opposite the plume; effects are excluded from solid geometry'],
        inferred=['Five profiled bodies including an authored octagonal central section, three finite body bands, eight fitted pale longitudinal castings and service details','Counts, sections, proportions, physical interpretation of highlights/bands and hidden mechanisms remain authored interpretations'],
        sockets={name:dict(position=list(position),forward=list(forward),status='authored-uncalibrated') for name,(position,forward) in SOCKETS.items()},
        imported_geometry_or_textures=[],unresolved=['Final artistic acceptance','Runtime scale/orientation and 3D launcher calibration','Launch/flight/damage states, calibrated orientation/mount and exhaustive effect separation; no mechanisms established'],acceptance='First low-resolution interpretation; artistic refining deferred',cultural_style_sha256=sha(REPO/'docs/reconstruction/models/cultural-architecture-index.json'),cultural_guidance='Mikotaj mining-colony architecture is heavy and metallic; this is contextual direction, not recovered missile geometry or a mandate for home-world crystals')
    (ROOT/'model.json').write_text(json.dumps(meta,indent=2)+'\n');print('MIKOTAJ_BRUJ_MAHAL_MODEL_OK',len(meshes),flush=True)


if __name__=='__main__': main()
