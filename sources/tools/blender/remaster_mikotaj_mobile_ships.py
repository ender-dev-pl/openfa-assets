"""Issue246: opaque metallic Mikotaj fleet from actual paletted headings.

Reuses stable mesh/material authoring primitives from the Braccatian milestone;
palette, fitted details, scale/heading proposals and geometry decisions are separate.
"""
from pathlib import Path
import argparse,json,math,sys
import bpy,bmesh
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
import remaster_braccatian_mobile_ships as core
ROOT=Path(__file__).resolve().parents[3]
MAPS=ROOT/'sources/materials/mikotaj/mobile-ships'
VIEWS=core.VIEWS
CASES={
 'hiero':dict(name='Hiero',key='MK0A',size_class='small scout',world_size_proposal=40,slots=2,reference_side_alpha_bounds=[15,12],heading_angle=0,comparison_elevation=.65,z_scale=1),
 'ylikt-shan':dict(name='Ylikt-shan',key='MK1A',size_class='small craft',world_size_proposal=48,slots=2,reference_side_alpha_bounds=[20,6],heading_angle=0,comparison_elevation=.9,z_scale=1),
 'falari-lourn':dict(name='Falari-Lourn',key='MK2C',size_class='large combat craft',world_size_proposal=112,slots=5,reference_side_alpha_bounds=[83,13],heading_angle=0,comparison_elevation=.3,z_scale=.55),
 'ruth-strivakh':dict(name='Ruth-Strivakh',key='MK3C',size_class='large transporter',world_size_proposal=128,slots=2,reference_side_alpha_bounds=[122,18],heading_angle=-math.pi/2,comparison_elevation=.3,z_scale=.55)}
sha=core.sha
meshes=core.meshes
bounds=core.bounds
evaluated_points=core.evaluated_points
fit_camera=core.fit_camera


def folders(key):return ROOT/'sources/objects/mikotaj'/key,ROOT/'gallery/media/objects/mikotaj'/key


def tile_for(name):
    name=name.lower()
    if any(s in name for s in ['dark','carbon','seam','recess','slot']):return 4
    if 'green' in name:return 1
    if 'copper' in name:return 2
    if 'gold' in name:return 3
    if any(s in name for s in ['edge','alloy','titanium']):return 5
    return 0


def details(key,mat):
    attachments=[];old=list(meshes())
    owner_names={'hiero':['Hiero faceted hull'],'ylikt-shan':['Ylikt-shan port rail','Ylikt-shan starboard rail'],'falari-lourn':['Falari-Lourn blue pressure hull'],'ruth-strivakh':['Ruth-Strivakh central pressure body']}
    for name in owner_names[key]:
        owner=bpy.data.objects[name];tree=core.tree(owner);b=bounds([owner]);centre=Vector(tuple((a+c)/2 for a,c in zip(b[0],b[1])))
        offsets=[-.2,.2] if key=='falari-lourn' else [0]
        for offset in offsets:
            origin=centre+Vector((offset,0,-4));p,n,face,distance=tree.ray_cast(origin,Vector((0,0,1)),8)
            assert p is not None;n=n.normalized();along=Vector((0,1,0));across=along.cross(n).normalized();along=n.cross(across).normalized();rot=Matrix((across,along,n)).transposed()
            width=.085 if key=='ylikt-shan' else .14;height=width*1.8
            bezel=core.box('Authored underside service frame',p+n*.008,(width+.025,height+.025,.022),mat,rot);bezel['atlas_tile']=5
            inset=core.box('Authored underside service recess',p+n*.019,(width,height,.014),mat,rot);inset['atlas_tile']=4
            for j in range(4):
                q=p+rot@Vector((0,(j-1.5)*height/6,.030));o=core.box('Authored underside louver',q,(width*.80,height/15,.012),mat,rot);o['atlas_tile']=6
            for x in [-width*.42,width*.42]:
                for y in [-height*.42,height*.42]:
                    q=p+rot@Vector((x,y,.019));o=core.rod('Authored service fastener',q-n*.007,q+n*.008,.006,mat,10);o['atlas_tile']=5
            attachments.append(dict(owner=owner.name,point=list(p),normal=list(n),type='Surface-fitted underside service cassette; authored function-neutral detail'))
    if key=='ruth-strivakh':
        # Keep the copper frame open. Internal diagonal braces stay inside its bays.
        for side in [-1,1]:
            for index,(a,b) in enumerate(zip([.95,1.55,2.20],[1.55,2.20,2.65])):
                p=Vector((side*a,-.18,.023));q=Vector((side*b,.18,.023));o=core.rod('Authored copper bay brace',p,q,.014,mat,10);o['atlas_tile']=2
                attachments.append(dict(owner='Copper frame crossmembers',point=list(p),type='Internal open-bay diagonal brace'))
        for owner in [o for o in old if 'crossmember' in o.name]:
            b=bounds([owner]);x=(b[0][0]+b[1][0])/2
            for y in [-.20,.20]:
                p=Vector((x,y,b[1][2]));o=core.rod('Authored crossmember pin',p-Vector((0,0,.006)),p+Vector((0,0,.012)),.013,mat,12);o['atlas_tile']=5
                attachments.append(dict(owner=owner.name,point=list(p),type='Seated structural pin'))
    return attachments


def main(key):
    case=CASES[key];out,media=folders(key);out.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sources/docs/assets/reconstruction/ships/mikotaj'/key/'model.blend';baseline=sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
    original_bounds=bounds(meshes());core.MAPS=MAPS;mat=core.material();mat.name='Mikotaj | worn opaque slate green and copper';reductions=[]
    for o in list(meshes()):
        assert all(m is not None for m in o.data.materials)
        if o.animation_data:o.animation_data_clear()
        bpy.context.view_layer.objects.active=o
        for mod in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=mod.name)
        before=len(o.data.polygons);target=2000 if any(s in o.name.lower() for s in ['hull','body','pod','rail','wing','spike','keel']) else 500
        if before>target:
            mod=o.modifiers.new('Game density budget','DECIMATE');mod.ratio=target/before;mod.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=mod.name)
        reductions.append(dict(part=o.name,before_faces=before,after_faces=len(o.data.polygons)))
    attachments=details(key,mat);groups={}
    for o in meshes():
        tile=o.get('atlas_tile',tile_for(o.data.materials[0].name));core.assign_uv(o,mat,tile);groups.setdefault(core.classify(o.name),[]).append(o)
    # Imported-render feedback: large-craft baseline domes were too tall.
    # Preserve planform/open frame while lowering the opaque pressure sections.
    stretch=Matrix.Diagonal((1,1,case['z_scale'],1))
    for o in meshes():
        matrix=stretch@o.matrix_world
        for vertex in o.data.vertices:vertex.co=matrix@vertex.co
        o.parent=None;o.matrix_world=Matrix.Identity(4);o.data.update()
        if any(word in o.name.lower() for word in ['pressure hull','pressure body','terminal pod']):
            bpy.context.view_layer.objects.active=o
            if o.data.has_custom_normals:bpy.ops.mesh.customdata_custom_splitnormals_clear()
            for face in o.data.polygons:face.use_smooth=True
    for attachment in attachments:
        attachment['point']=list(stretch@Vector(attachment['point']))
        if 'normal' in attachment:attachment['normal']=list((stretch.to_3x3().inverted().transposed()@Vector(attachment['normal'])).normalized())
    root=bpy.data.objects.get('PlacementRoot')
    if root is None:root=bpy.data.objects.new('PlacementRoot',None);scene.collection.objects.link(root)
    root['catalogue_id']='openfa:ship/mikotaj/'+key;root['forward_axis']='local -Y';root['size_class']=case['size_class'];root['world_size_proposal']=case['world_size_proposal'];root['socket_calibration']='Uncalibrated; retained alignment helpers only'
    mapping={}
    for group,items in groups.items():
        mapping[group]=[o.name for o in items];bpy.ops.object.select_all(action='DESELECT')
        for o in items:
            vg=o.vertex_groups.new(name=o.name);vg.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=group;o.parent=root
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
        normals=[tuple(n.vector) for n in o.data.corner_normals]
        for face in o.data.polygons:face.use_smooth=True
        o.data.normals_split_custom_set(normals)
        while len(o.data.materials)>1:o.data.materials.pop(index=len(o.data.materials)-1)
        for face in o.data.polygons:face.material_index=0
    triangles=sum(len(o.data.polygons) for o in meshes());assert triangles<55000 and len(meshes())==4,(key,triangles,len(meshes()))
    scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
    for label,direction in VIEWS.items():fit_camera(scene,evaluated_points(meshes()),direction);scene.render.filepath=str(media/(label+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(scene,evaluated_points(meshes()),VIEWS['front-quarter']);bpy.ops.object.select_all(action='DESELECT')
    for o in scene.objects:
        if o.type in ['MESH','EMPTY']:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True,relative_remap=True)
    report=dict(id=root['catalogue_id'],issue=246,stage='mobile-ship-remaster',**case,source=source.parent.relative_to(ROOT/'sources').as_posix(),baseline_sha256=baseline,baseline_bounds=original_bounds,final_bounds=bounds(meshes()),triangles=triangles,mesh_batches=4,material_count=1,packed_maps=3,transverse_section_scale=1,editable_part_vertex_groups=mapping,attachments=attachments,reductions=reductions,generator_sha256=sha(Path(__file__)),shared_primitives_sha256=sha(Path(core.__file__)),maps_generator_sha256=sha(ROOT/'tools/author_mikotaj_ship_maps.py'),map_sha256={p.name:sha(p) for p in MAPS.glob('*.png')},blend_sha256=sha(out/'model.blend'),glb_sha256=sha(out/'model.glb'),reference_review='Actual paletted heading descriptors; no matching MK mobile-ship animation entries found in _MA',concept='Direct legacy-to-GLB feedback; no ImageGen stage',inference='Additional service details/size are authored proposals, not recovered hidden engineering or calibrated weapon mounts',visual_acceptance='Final user/game acceptance separate')
    (out/'model.json').write_text(json.dumps(report,indent=2)+'\n');print('MIKOTAJ_REMASTERED',key,triangles,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ship',choices=CASES,required=True);main(p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
