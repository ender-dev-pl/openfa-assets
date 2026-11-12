"""Author MN02 Shielding Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/shielding-block';maps=root/'sources/materials/mauna/shielding-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610202);buffers={name:[] for name in ['cast-concrete-colour','chipped-concrete-edge-colour','used-brass-colour','recess-red-colour','concrete-orm','metal-orm','cast-service-normal']}
    # Deterministic sparse roughcast spalls, patina streaks and fine pores.
    # These are authored surface maps,not borrowed legacy pixels.
    speckles={}
    for i in range(85):
        cx=rng.randrange(size);cy=rng.randrange(size);radius=rng.randrange(2,7)
        for dy in range(-radius,radius+1):
            for dx in range(-radius,radius+1):
                if dx*dx+dy*dy<radius*radius*rng.uniform(.65,1.1):speckles[((cx+dx)%size,(cy+dy)%size)]=rng.uniform(.035,.10)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=.024*math.sin(17*u+3*math.cos(11*v))+.018*math.cos(13*v+5*u);grain=rng.uniform(-.025,.025);stain=max(0,math.sin(33*u+2*math.cos(13*v))-.35)*.12;aggregate=speckles.get((x,y),0);pore=.15 if rng.random()<.035 else 0;dust=.07*max(0,1-v*5)
            concrete_delta=cloud+grain+aggregate-stain-pore-dust
            buffers['cast-concrete-colour'].extend([max(.01,c+concrete_delta) for c in (.29,.34,.41)]+[1]);buffers['chipped-concrete-edge-colour'].extend([max(.01,c+concrete_delta) for c in (.40,.45,.51)]+[1])
            scratch=.17 if ((x*7+y*31)%991<2 and rng.random()<.7) else 0
            buffers['used-brass-colour'].extend([max(.01,c+cloud*.7+grain*.5-stain*.9+scratch-pore*.3) for c in (.55,.36,.10)]+[1])
            buffers['recess-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in (.49,.105,.070)]+[1])
            buffers['concrete-orm'].extend([1,min(.98,max(.68,.85+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.76,max(.32,.54+grain+stain)),.72,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.035,.035),.5+rng.uniform(-.035,.035),1,1])
    images={}
    for name,pixels in buffers.items():
        im=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name.endswith('-orm') or name.endswith('-normal'):im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(pixels);path=maps/(name+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();path.write_bytes(clean_png(path.read_bytes()));im.pack();images[name]=im
    def material(name,colour=None,metal=False):
        m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.012,.016,.020,1);p.inputs['Roughness'].default_value=.85
        if colour:
            tex=n.new('ShaderNodeTexImage');tex.image=images[colour];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);orm=n.new('ShaderNodeTexImage');orm.image=images['metal-orm' if metal else 'concrete-orm'];split=n.new('ShaderNodeSeparateColor');m.node_tree.links.new(orm.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic']);texn=n.new('ShaderNodeTexImage');texn.image=images['cast-service-normal'];normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.10 if metal else .45;m.node_tree.links.new(texn.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        return m
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Mauna exposed aggregate edge','chipped-concrete-edge-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);red=material('Dark red nonemissive recessed fittings','recess-red-colour');# Four material roles only; dark well interiors are the shadowed red lining.
    def apply(o,mod):bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    def solid(name,verts,faces,mat):
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();assert not me.validate();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    def box(name,centre,size,mat,normal=None,bevel=.003):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        if normal is not None:
            normal=Vector(normal).normalized();v=(Vector((0,0,1))-normal*normal.z).normalized();u=v.cross(normal).normalized();o.rotation_euler=Matrix((u,v,normal)).transposed().to_euler()
        o.data.materials.append(mat)
        if bevel:
            mod=o.modifiers.new('Practical planar edge chamfer','BEVEL');mod.width=bevel;mod.segments=1;apply(o,mod)
        return o
    def cut(o,tool,label):
        mod=o.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;apply(o,mod);bpy.data.objects.remove(tool,do_unlink=True)
    profile=[(.08,.99),(.22,1.0),(.90,.76)]
    verts=[(x*h,y*h,z) for z,h in profile for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    faces=[]
    for j in range(len(profile)-1):
        for i in range(4):faces.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
    faces.extend([(3,2,1,0),tuple((len(profile)-1)*4+i for i in range(4))])
    body=solid('Shielding Block squat concrete shell',verts,faces,concrete);body.data.materials.append(edge);body.data.materials.append(red)
    mod=body.modifiers.new('Small cast perimeter chamfers','BEVEL');mod.width=.006;mod.segments=2;mod.material=1;apply(body,mod)
    roof=box('Shielding Block red four-well roof',(0,0,.901),(1.52,1.52,.052),red,bevel=.004)
    wells=[]
    for i,(x,y) in enumerate([(-.345,-.345),(.345,-.345),(-.345,.345),(.345,.345)]):
        cutter=box('Temporary blind well cutter',(x,y,.825),(.52,.52,.53),concrete,bevel=0);cutter.data.materials.append(edge);cutter.data.materials.append(red)
        for face in cutter.data.polygons:face.material_index=2
        cut(body,cutter,'Actual blind red-lined roof well '+str(i))
        cutter=box('Temporary roof opening cutter',(x,y,.92),(.52,.52,.20),red,bevel=0);cut(roof,cutter,'Four actual square roof openings')
        wells.append(dict(index=i,centre=[x,y],floor=.56,roof_top=.927,width=.52))
    # Body and roof physically overlap between the wells; the same bore width keeps all openings unobstructed.
    def surface(face,u,z):
        angle=face*math.pi/2;normal=Vector((math.sin(angle),-math.cos(angle),0));tangent=Vector((math.cos(angle),math.sin(angle),0));origin=tangent*u+normal*3+Vector((0,0,z));bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(origin,-normal);assert hit;return q,n,tangent,normal
    def join_parts(objects,name):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
    ribs=[];feet=[];rib_contacts=[];foot_contacts=[]
    for face in range(4):
        group=[]
        for i,u in enumerate([-.50,0,.50]):
            q,n,tangent,normal=surface(face,u,.60);rib=box('Pale cast rib '+str(face)+' '+str(i),q+n*.016,(.105,.32,.060),edge,n,.004);group.append(rib);rib_contacts.append(dict(face=face,index=i,point=list(q-n*.007),normal=list(n)))
            # Feet overlap the lower perimeter; no unsupported floating caps.
            q,n,tangent,normal=surface(face,u,.205);centre=tangent*u+normal*1.015+Vector((0,0,.175));foot=box('Used brass foot '+str(face)+' '+str(i),centre,(.15,.14,.33),gold,bevel=.004);foot.rotation_euler.z=face*math.pi/2;feet.append(foot);foot_contacts.append(dict(face=face,index=i,point=list(tangent*u+normal*.97+Vector((0,0,.205)))))
        ribs.append(join_parts(group,'Shielding Block three pale ribs face '+str(face)))
    join_parts(feet,'Shielding Block twelve brass feet')
    # Real local chips complement sparse authored material wear; no invented machinery.
    chips=[]
    for label,target,point,normal,radius,offset in [('roof-lip',roof,Vector((.66,-.18,.927)),Vector((0,0,1)),.028,.021),('concrete-face',body,None,None,.030,.023)]:
        if point is None:point,normal,_,_=surface(1,-.73,.48)
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=radius,location=point+normal*offset);tool=bpy.context.object
        for mat in target.data.materials:tool.data.materials.append(mat)
        cut(target,tool,'Small actual service chip '+label);chips.append(dict(label=label,object=target.name,point=list(point),normal=list(normal),expected_depth=radius-offset))
    for i,point in enumerate([Vector((-.68,-.10,.927)),Vector((.12,-.70,.927)),Vector((.69,.54,.927)),Vector((-.12,.70,.927))]):
        normal=Vector((0,0,1));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.023,location=point+normal*.017);cut(roof,bpy.context.object,'Sparse roof lip edge chip '+str(i));chips.append(dict(label='roof-lip-'+str(i),object=roof.name,point=list(point),normal=list(normal),expected_depth=.006))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/131';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
    for o in meshes:
        o.parent=placement;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);materials=[];indices=[]
        for f in o.data.polygons:
            mat=o.data.materials[f.material_index]
            if mat not in materials:materials.append(mat)
            indices.append(materials.index(mat))
        o.data.materials.clear()
        for mat in materials:o.data.materials.append(mat)
        for f,index in zip(o.data.polygons,indices):f.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        uv=o.data.uv_layers.active
        for f in o.data.polygons:
            for index in f.loop_indices:
                q=o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1.2)/2.4,q.z/1.1) if abs(f.normal.x)>.5 else ((q.x+1.2)/2.4,q.z/1.1) if abs(f.normal.y)>.5 else ((q.x+1.2)/2.4,(q.y+1.2)/2.4)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');apply(o,mod);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name;bm.to_mesh(o.data);bm.free()
        for f in o.data.polygons:f.use_smooth=False
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/131',key='MN02',name='Shielding Block',culture='mauna',footprint=[3,3],definition_class=5,construction_updates=30,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,author='sources/tools/blender/remaster_mauna_shielding_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},roof_wells=wells,rib_contacts=rib_contacts,foot_contacts=foot_contacts,physical_chips=chips,interpretation=['Own squat angular concrete shell,four red roof wells,three pale wall ribs andthree brassfeet pervisibleface govern geometry.','Hiddenrear rib/footrepeat,well depths/internalfloor andcell-relative dimensions authored. PB05isTerran functioncontext,notMauna operation. No own operating overlays/glow inferred.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn02-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_SHIELDING_BLOCK_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
