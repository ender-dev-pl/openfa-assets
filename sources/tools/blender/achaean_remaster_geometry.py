"""Shared Achaean geometry and portable worn-material authoring primitives."""
import hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'tools'))
from publication_support import clean_blend,clean_png
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def lathe(name, centre, profile, material, lobes=0):
    verts=[];faces=[];n=64
    for j,(z,r) in enumerate(profile):
        for i in range(n):
            a=2*math.pi*i/n; dent=.002*math.sin(7*a+j*.8)*math.sin(j*1.7)
            radius=max(.001,r*(1+lobes*math.cos(8*a))+dent)
            verts.append((centre[0]+radius*math.cos(a),centre[1]+radius*math.sin(a),z))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(material)
    uv=mesh.uv_layers.new(name='Authored wear UV')
    for p in mesh.polygons:
        p.use_smooth=len(p.vertices)==4
        for li in p.loop_indices:
            vi=mesh.loops[li].vertex_index;uv.data[li].uv=(vi%n/(n-1),(vi//n)/(len(profile)-1))
    return obj

def box(name,loc,size,mat,bevel=.015):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat)
    if bevel:
        m=o.modifiers.new('Small worn edge radii','BEVEL');m.width=bevel;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
    return o

def material(folder,name,colour,metal,rough,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True;s=m.node_tree.nodes.get('Principled BSDF');s.inputs['Base Color'].default_value=(*colour,1);s.inputs['Metallic'].default_value=metal;s.inputs['Roughness'].default_value=rough
    if emission:s.inputs['Emission Color'].default_value=(*(c*emission for c in colour),1);s.inputs['Emission Strength'].default_value=1
    else:
        texture=ROOT/'sources/materials/achaean'/folder/f'{name}.png';texture.parent.mkdir(parents=True,exist_ok=True);image=bpy.data.images.new(name+' authored weathering',width=256,height=256);rng=random.Random(name);pixels=[]
        for y in range(256):
            for x in range(256):
                u=x/255;v=y/255;stain=.37*math.exp(-((v-.06)/.12)**2)+.22*math.exp(-((u-.55)/.13)**2)*math.exp(-((v-.6)/.3)**2);grain=rng.uniform(-.045,.045);scratch=.46 if (x*73+y*19)%997<2 else 0
                pixels.extend([max(0,min(1,c*(1-stain+grain+scratch))) for c in colour]+[1])
        image.pixels.foreach_set(pixels);image.filepath_raw=str(texture);image.file_format='PNG';image.save();texture.write_bytes(clean_png(texture.read_bytes()));image.pack();t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=image;m.node_tree.links.new(t.outputs['Color'],s.inputs['Base Color'])
    return m

def finish(folder,metadata,author,helpers):
    output=ROOT/'sources/objects/achaean'/folder;output.mkdir(parents=True,exist_ok=True)
    bpy.context.preferences.filepaths.save_version=0
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    root=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root)
    root['catalogue_id']=metadata['id'];root['footprint']=metadata['footprint'];root['forward_axis']='-Y';root['dorsal_axis']='+Z'
    for obj in meshes:
        obj.parent=root;bpy.context.view_layer.objects.active=obj
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        for poly in obj.data.polygons:poly.use_smooth=True
        obj.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update()
    count=sum(len(o.data.polygons) for o in meshes);assert count<metadata['triangle_budget']
    temp=ROOT/'artifacts/achaean-building-export-temp';temp.mkdir(parents=True,exist_ok=True);original=tempfile.mkdtemp
    def mk(*a,**k):
        p=temp/uuid.uuid4().hex;p.mkdir();return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(output/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=original
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'model.blend'),compress=True)
    p=output/'model.blend';p.write_bytes(clean_blend(p.read_bytes())[0])
    metadata.update(mesh_nodes=len(meshes),triangles=count,author=Path(author).relative_to(ROOT).as_posix(),author_sha256=sha(Path(author)),helpers={Path(p).relative_to(ROOT).as_posix():sha(Path(p)) for p in helpers},binaries={ext:sha(output/f'model.{ext}') for ext in ['blend','glb']},final_artistic_acceptance=False,game_client_integration=False)
    (output/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('ACHAEAN_AUTHORED',metadata['key'],count,len(meshes),flush=True)
