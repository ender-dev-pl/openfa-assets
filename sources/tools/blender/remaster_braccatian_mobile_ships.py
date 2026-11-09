"""Issue244: restrained Braccatian mobile-ship remasters, four canonical payloads.

Actual legacy silhouettes/colour fields are preserved from reviewed baselines.
New service machinery and wear are authored; no weapon/socket calibration claimed.
"""
from pathlib import Path
import argparse,hashlib,json,math,sys
import bpy,bmesh
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from catalogue_rendering import evaluated_points,fit_camera
ROOT=Path(__file__).resolve().parents[3]
MAPS=ROOT/'sources/materials/braccatian/mobile-ships'
CASES={
 'rattlesnake':dict(name='Rattlesnake',key='BR0A',source='docs/assets/reconstruction/ships/braccatian/rattlesnake',size_class='small scout',world_size_proposal=40,slots=2),
 'widowmaker':dict(name='WidowMaker',key='BR1C',source='docs/assets/reconstruction/braccatian-refined/ships/widowmaker',size_class='large combat ship',world_size_proposal=112,slots=4),
 'heartsblood':dict(name='HeartsBlood',key='BR2C',source='docs/assets/reconstruction/braccatian-refined/ships/heartsblood',size_class='large transporter',world_size_proposal=128,slots=6),
 'morning-glory':dict(name='Morning Glory',key='BR3A',source='docs/assets/reconstruction/ships/braccatian/morning-glory',size_class='small craft',world_size_proposal=48,slots=4)}
VIEWS={'front-quarter':(7,-12,9),'rear-quarter':(-7,12,8),'side':(15,0,5),'top':(0,0,20),'underside':(7,-8,-14)}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def folders(key):return ROOT/'sources/objects/braccatian'/key,ROOT/'gallery/media/objects/braccatian'/key
def meshes():return [o for o in bpy.context.scene.objects if o.type=='MESH']
def bounds(objects):
    points=evaluated_points(objects)
    return [[min(p[a] for p in points) for a in range(3)],[max(p[a] for p in points) for a in range(3)]]


def material():
    mat=bpy.data.materials.new('Braccatian | sparse worn rose and ochre alloy');mat.use_nodes=True
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;shader=nodes.get('Principled BSDF')
    uv=nodes.new('ShaderNodeUVMap');uv.uv_map='BraccatianWearAtlas'
    for key in ['colour','orm','normal']:
        image=bpy.data.images.load(str(MAPS/(key+'.png')),check_existing=True);image.colorspace_settings.name='sRGB' if key=='colour' else 'Non-Color';image.pack();image.filepath='//'+key+'.png'
        tex=nodes.new('ShaderNodeTexImage');tex.image=image;links.new(uv.outputs['UV'],tex.inputs['Vector'])
        if key=='colour':links.new(tex.outputs['Color'],shader.inputs['Base Color'])
        elif key=='orm':
            split=nodes.new('ShaderNodeSeparateColor');links.new(tex.outputs['Color'],split.inputs[0]);links.new(split.outputs['Green'],shader.inputs['Roughness']);links.new(split.outputs['Blue'],shader.inputs['Metallic'])
        else:
            normal=nodes.new('ShaderNodeNormalMap');normal.uv_map='BraccatianWearAtlas';links.new(tex.outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],shader.inputs['Normal'])
    return mat


def tile_for(mat):
    name=mat.name.lower()
    if any(x in name for x in ['dark','carbon','recess','floor','slot']):return 6
    if any(x in name for x in ['gold','golden','brass']):return 0
    if any(x in name for x in ['rose','copper','red','pink']):return 1
    if any(x in name for x in ['grey','slate','armour']):return 2
    if any(x in name for x in ['edge','titanium','silver','alloy']):return 5
    return 4


def assign_uv(obj,mat,forced=None):
    old=list(obj.data.materials);tiles=[tile_for(m) for m in old]
    while obj.data.uv_layers:obj.data.uv_layers.remove(obj.data.uv_layers[0])
    uv=obj.data.uv_layers.new(name='BraccatianWearAtlas');uv.active_render=True
    coords=[v.co for v in obj.data.vertices];low=[min(p[a] for p in coords) for a in range(3)];high=[max(p[a] for p in coords) for a in range(3)];centre=[(a+b)/2 for a,b in zip(low,high)]
    tubular=any(x in obj.name.lower() for x in ['body','pressure hull','spindle','nose','terminal','pod shell'])
    for face in obj.data.polygons:
        tile=forced if forced is not None else tiles[face.material_index]
        axes=[a for a in range(3) if a!=max(range(3),key=lambda a:abs(face.normal[a]))]
        for i in face.loop_indices:
            p=obj.data.vertices[obj.data.loops[i].vertex_index].co
            if tubular:
                u=(math.atan2(p.z-centre[2],p.x-centre[0])/math.tau)%1;v=(p.y-low[1])/max(1e-8,high[1]-low[1])
            else:u,v=[(p[a]-low[a])/max(1e-8,high[a]-low[a]) for a in axes]
            uv.data[i].uv=((tile%4+.008+u*.984)/4,1-(tile//4+.008+v*.984)/2)
        face.material_index=0
    obj.data.materials.clear();obj.data.materials.append(mat)


def classify(name):
    n=name.lower()
    if any(w in n for w in ['bolt','stud','fastener','inlay','band','rim','trim']):return 'TrimAndFasteners'
    if any(w in n for w in ['slot','duct','floor','face','recess','stator','hub']):return 'RecessedMachinery'
    if any(w in n for w in ['service','cover','housing','cradle','collar','connector','rail']):return 'ServiceAssemblies'
    return 'PrimaryHullAndArmour'


def tree(obj):
    eo=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());m=eo.to_mesh();t=BVHTree.FromPolygons([obj.matrix_world@v.co for v in m.vertices],[tuple(p.vertices) for p in m.polygons]);eo.to_mesh_clear();return t


def box(name,p,size,mat,rotation=None):
    bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=name;o.scale=size
    if rotation:o.rotation_euler=rotation.to_euler()
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bevel=o.modifiers.new('Small machined edge','BEVEL');bevel.width=min(size)*.18;bevel.segments=2
    bpy.ops.object.modifier_apply(modifier=bevel.name);o.data.materials.append(mat);return o


def rod(name,a,b,r,mat,n=12):
    axis=Vector(b)-Vector(a);bpy.ops.mesh.primitive_cylinder_add(vertices=n,radius=r,depth=axis.length,location=(Vector(a)+Vector(b))/2)
    o=bpy.context.object;o.name=name;o.rotation_euler=axis.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat)
    for f in o.data.polygons:f.use_smooth=len(f.vertices)==4
    return o


def add_details(key,mat):
    old=list(meshes());attachments=[]
    # Service fittings sit on actual evaluated surfaces; small ships receive fewer.
    owners=[o for o in old if any(x in o.name.lower() for x in ['copper body','gold pressure hull','gold spindle'])]
    for owner in owners:
        b=bounds([owner]);y0,y1=b[0][1],b[1][1];length=y1-y0;mid=(y0+y1)/2;t=tree(owner)
        for index,(fraction,angle) in enumerate([(.36,math.pi*1.5),(.68,math.pi*1.5),(.55,.35)] if key in ['widowmaker','heartsblood'] else [(.58,math.pi*1.5)]):
            normal=Vector((math.cos(angle),0,math.sin(angle)));origin=Vector((0,y0+length*fraction,0))+normal*4
            p,n,face,dist=t.ray_cast(origin,-normal,8)
            if p is None:continue
            n=n.normalized();along=Vector((0,1,0));across=along.cross(n).normalized();along=n.cross(across).normalized();rot=Matrix((across,along,n)).transposed()
            width=.14 if key in ['rattlesnake','morning-glory'] else .20;height=width*1.7
            panel=box('Authored service frame',p+n*.009,(width+.035,height+.035,.028),mat,rot);panel['atlas_tile']=5
            inset=box('Authored service inset',p+n*.025,(width,height,.016),mat,rot);inset['atlas_tile']=6
            for j in range(5):
                q=p+rot@Vector((0,(j-2)*height/7,.039));louver=box('Authored service louver',q,(width*.84,height/15,.014),mat,rot);louver['atlas_tile']=2
            for x in [-width*.45,width*.45]:
                for y in [-height*.45,height*.45]:
                    q=p+rot@Vector((x,y,.027));bolt=rod('Authored service fastener',q-n*.010,q+n*.009,.009,mat,10);bolt['atlas_tile']=5
            attachments.append(dict(owner=owner.name,point=list(p),normal=list(n),type='surface-fitted service cassette',maximum_projection=.05))
    # Detail the four observed rear openings without assigning them a weapon type.
    for floor in [o for o in old if 'recessed duct floor' in o.name]:
        points=[floor.matrix_world@v.co for v in floor.data.vertices];c=sum(points,Vector())/len(points);front=max(v.y for v in points)
        a=Vector((c.x,front-.008,c.z));b=a+Vector((0,.065,0));hub=rod('Authored duct stator hub',a,b,.047,mat,20);hub['atlas_tile']=4
        for i in range(8):
            angle=i*math.tau/8;q=Vector((math.cos(angle),0,math.sin(angle)))
            blade=rod('Authored duct stator vane',a+q*.038+Vector((0,.014,0)),a+q*.137+Vector((0,.022,0)),.010,mat,6);blade['atlas_tile']=5
        attachments.append(dict(owner=floor.name,point=list(a),type='recessed stator, function unresolved',maximum_projection=.065))
    return attachments


def main(key):
    case=CASES[key];out,media=folders(key);out.mkdir(parents=True,exist_ok=True);media.mkdir(parents=True,exist_ok=True)
    source=ROOT/'sources'/case['source']/'model.blend';baseline=sha(source)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;bpy.context.preferences.filepaths.save_version=0
    for o in meshes():
        assert all(m is not None for m in o.data.materials)
        if o.animation_data:o.animation_data_clear()
    original_bounds=bounds(meshes());mat=material();reductions=[]
    for o in list(meshes()):
        bpy.context.view_layer.objects.active=o
        for modifier in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=modifier.name)
        before=len(o.data.polygons)
        if before>800:
            target=2200 if any(x in o.name.lower() for x in ['body','pressure hull','spindle','nose','terminal','pod shell']) else 500
            if before>target:
                dec=o.modifiers.new('Game density budget','DECIMATE');dec.ratio=target/before;dec.use_collapse_triangulate=True;bpy.ops.object.modifier_apply(modifier=dec.name)
        reductions.append(dict(part=o.name,before_faces=before,after_faces=len(o.data.polygons)))
    attachments=add_details(key,mat);parts={}
    for o in list(meshes()):
        assign_uv(o,mat,o.get('atlas_tile'));parts.setdefault(classify(o.name),[]).append(o)
    # Feedback from actual side sprites: the earlier small-craft studies were
    # too slender. Correct the transverse section without changing axial length.
    transverse_scale={'rattlesnake':2.2,'morning-glory':1.62}.get(key,1.0)
    stretch=Matrix.Diagonal((transverse_scale,1,transverse_scale,1))
    for o in meshes():
        matrix=stretch@o.matrix_world
        for v in o.data.vertices:v.co=matrix@v.co
        o.parent=None;o.matrix_world=Matrix.Identity(4);o.data.update()
    for attachment in attachments:
        attachment['point']=list(stretch@Vector(attachment['point']))
        if 'normal' in attachment:attachment['normal']=list((stretch.to_3x3().inverted().transposed()@Vector(attachment['normal'])).normalized())
    root=bpy.data.objects.get('PlacementRoot')
    if root is None:
        root=bpy.data.objects.new('PlacementRoot',None);bpy.context.scene.collection.objects.link(root)
    root['catalogue_id']='openfa:ship/braccatian/'+key;root['forward_axis']='local -Y';root['size_class']=case['size_class'];root['world_size_proposal']=case['world_size_proposal'];root['socket_calibration']='Not recovered; existing alignment empties preserved'
    mapping={}
    for group,items in parts.items():
        mapping[group]=[o.name for o in items];bpy.ops.object.select_all(action='DESELECT')
        for o in items:
            vg=o.vertex_groups.new(name=o.name);vg.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=items[0];bpy.ops.object.join();o=bpy.context.object;o.name=group;o.parent=root
        # Triangulate deterministically for identical saved-source/import shading.
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
        normals=[tuple(n.vector) for n in o.data.corner_normals]
        for face in o.data.polygons:face.use_smooth=True
        o.data.normals_split_custom_set(normals)
        while len(o.data.materials)>1:o.data.materials.pop(index=len(o.data.materials)-1)
        for face in o.data.polygons:face.material_index=0
    final_bounds=bounds(meshes());triangles=sum(len(o.data.polygons) for o in meshes());assert triangles<55000,(key,triangles)
    scene.render.engine='CYCLES';scene.cycles.samples=40;scene.cycles.use_denoising=True;scene.render.resolution_x=scene.render.resolution_y=900;scene.render.resolution_percentage=100;scene.render.film_transparent=True;scene.render.image_settings.color_mode='RGBA'
    for name,direction in VIEWS.items():
        fit_camera(scene,evaluated_points(meshes()),direction);scene.render.filepath=str(media/(name+'.png'));bpy.ops.render.render(write_still=True)
    fit_camera(scene,evaluated_points(meshes()),VIEWS['front-quarter']);bpy.ops.object.select_all(action='DESELECT')
    for o in scene.objects:
        if o.type in ['MESH','EMPTY']:o.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',use_selection=True,export_apply=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True,relative_remap=True)
    report=dict(id=root['catalogue_id'],issue=244,stage='mobile-ship-remaster',**case,baseline_sha256=baseline,baseline_bounds=original_bounds,final_bounds=final_bounds,triangles=triangles,mesh_batches=len(meshes()),material_count=1,packed_maps=3,editable_part_vertex_groups=mapping,attachments=attachments,reductions=reductions,generator_sha256=sha(Path(__file__)),maps_generator_sha256=sha(ROOT/'tools/author_braccatian_ship_maps.py'),map_sha256={p.name:sha(p) for p in MAPS.glob('*.png')},blend_sha256=sha(out/'model.blend'),glb_sha256=sha(out/'model.glb'),references='Actual paletted32 headings; source hashes in shared reference index; no matching BR ship animations in _MA archive',concept='No ImageGen stage used; direct legacy-to-GLB feedback',inference='Hidden service details and scale proposals are authored; no operational animation or calibrated weapon sockets claimed',visual_acceptance='Rendered review against legacy required; final game acceptance separate')
    report['transverse_section_scale']=transverse_scale
    report['reference_side_alpha_bounds']={'rattlesnake':[18,7],'widowmaker':[79,34],'heartsblood':[80,40],'morning-glory':[16,8]}[key]
    (out/'model.json').write_text(json.dumps(report,indent=2)+'\n');print('BRACCATIAN_REMASTERED',key,triangles,len(meshes()),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--ship',choices=CASES,required=True)
    main(parser.parse_args(sys.argv[sys.argv.index('--')+1:]).ship)
