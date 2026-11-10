"""Author MK01 Base Crystal from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/base-crystal';maps=root/'sources/materials/mikotaj/base-crystal'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25901);size=512;colours=[];gold=[];orm=[]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=.03*math.sin(17*u+4*math.cos(11*v))+.025*math.cos(23*v-5*u)+rng.uniform(-.012,.012)
            stain=.055*max(0,math.sin(8*u+7*v))**7
            scratch=.075 if (x*37+y*79)%1237<2 else 0
            colours.extend([max(.015,min(1,c+cloud-stain+scratch)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*.5-stain*.6+scratch)) for c in (.43,.30,.095)]+[1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    images={}
    for name,pixels in [('mineral-base-colour',colours),('brass-base-colour',gold),('occlusion-roughness-metallic',orm)]:
        image=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name.startswith('occlusion'):image.colorspace_settings.name='Non-Color'
        image.pixels.foreach_set(pixels);image.filepath_raw=str(maps/(name+'.png'));image.file_format='PNG';image.save()
        path=maps/(name+'.png');path.write_bytes(clean_png(path.read_bytes()));image.pack();images[name]=image
    def material(name,colour,metal=.7,rough=.4,image=None,emission=0):
        mat=bpy.data.materials.new(name);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if image:
            node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=images[image];mat.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
            packed=mat.node_tree.nodes.new('ShaderNodeTexImage');packed.image=images['occlusion-roughness-metallic'];split=mat.node_tree.nodes.new('ShaderNodeSeparateColor');mat.node_tree.links.new(packed.outputs['Color'],split.inputs[0]);mat.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);mat.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    brass=material('Aged brass collars',(.43,.30,.095),image='brass-base-colour')
    dark=material('Recessed emitter mounting alloy',(.022,.032,.036),.74,.31)
    blue=material('Silver-noise blue optical emitter',(.055,.18,.55),.20,.23,emission=1.0)
    # Irregular joined mineral-metal anatomy; no unsupported sharp-shard cluster.
    forms=[('Left crown',(-.38,.26,2.04),(.62,.57,.95)),('Right crown',(.34,.09,1.96),(.68,.52,1.01)),
           ('Crown ridge',(-.08,-.21,1.85),(.36,.42,.70)),('Lower rear mass',(0,.30,1.13),(.64,.55,.86)),
           ('Left supporting lobe',(-.74,.06,.43),(.47,.61,.41)),('Right supporting lobe',(.73,.02,.43),(.48,.64,.41)),
           ('Continuous left ore flank',(-.68,.18,1.13),(.40,.48,1.08)),('Continuous right ore flank',(.69,.19,1.13),(.39,.48,1.08)),('Mineral emitter seat',(0,-.32,1.66),(.43,.53,.49)),('Rear foundation',(0,.39,.31),(.78,.51,.29)),('Front foot',(-.05,-.46,.24),(.43,.43,.22))]
    rocks=[]
    for name,position,scale in forms:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=position);obj=bpy.context.object;obj.name=name;obj.scale=scale
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);rocks.append(obj)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in rocks:obj.select_set(True)
    bpy.context.view_layer.objects.active=rocks[0];bpy.ops.object.join();shell=bpy.context.object;shell.name='Joined ore-like crown and supporting flanks'
    remesh=shell.modifiers.new('Connected mineral body','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.065;remesh.use_smooth_shade=True;bpy.ops.object.modifier_apply(modifier=remesh.name)
    smooth=shell.modifiers.new('Broad worn contours','SMOOTH');smooth.factor=.55;smooth.iterations=2;bpy.ops.object.modifier_apply(modifier=smooth.name)
    noise=bpy.data.textures.new('Authored mineral stress relief',type='CLOUDS');noise.noise_scale=.27;noise.noise_depth=1
    modifier=shell.modifiers.new('Shallow stress relief','DISPLACE');modifier.texture=noise;modifier.strength=.075;modifier.texture_coords='GLOBAL';bpy.ops.object.modifier_apply(modifier=modifier.name)
    shell.data.materials.append(ore)
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=48):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        bevel=obj.modifiers.new('Readable seated rims','BEVEL');bevel.width=min(.018,depth*.15);bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name)
        return obj
    cylinder('Central lower focusing neck',(0,-.43,.87),.405,1.10,ore)
    for z in [.62,.91]:cylinder('Brass focusing collar '+str(z),(0,-.43,z),.43,.145,brass,vertices=64)
    for z in [.515,.73,.805,1.02]:cylinder('Dark collar separator '+str(z),(0,-.43,z),.409,.027,dark)
    # Front optic faces -Y and is mechanically seated into the central body.
    cutter=cylinder('Temporary actual optic recess',(0,-.87,1.56),.263,.50,dark,axis=(0,-1,0),vertices=48)
    bpy.context.view_layer.objects.active=shell
    recess=shell.modifiers.new('Seated front optic recess','BOOLEAN');recess.operation='DIFFERENCE';recess.solver='EXACT';recess.object=cutter
    bpy.ops.object.modifier_apply(modifier=recess.name);bpy.data.objects.remove(cutter,do_unlink=True)
    cylinder('Blue emitter backed seating',(0,-.68,1.56),.258,.24,ore,axis=(0,-1,0))
    cylinder('Emitter outer bezel',(0,-.82,1.56),.250,.095,dark,axis=(0,-1,0),vertices=64)
    cylinder('Emitter metal rim',(0,-.87,1.56),.217,.034,brass,axis=(0,-1,0),vertices=64)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.187,location=(0,-.897,1.56));lens=bpy.context.object;lens.name='Main blue optical face';lens.scale=(1,.16,1);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);lens.data.materials.append(blue)
    # Smaller blue nodes are placed from rays against the actual joined shell.
    bpy.context.view_layer.update()
    for i,(x,z) in enumerate([(-.13,.23),(.63,.38),(.91,.53),(.69,.78),(-.76,.52)]):
        inv=shell.matrix_world.inverted();start=inv@Vector((x,-3,z));direction=inv.to_3x3()@Vector((0,1,0));hit,point,normal,_=shell.ray_cast(start,direction)
        assert hit,('unseated lower node',i);position=shell.matrix_world@point;outward=(shell.matrix_world.to_3x3()@normal).normalized()
        cylinder('Lower node bezel '+str(i),position+outward*.015,.072,.052,dark,axis=outward,vertices=24)
        cylinder('Lower blue node '+str(i),position+outward*.047,.050,.021,blue,axis=outward,vertices=24)
    # Sparse functional rear access geometry, interpreted rather than recovered.
    cylinder('Rear focusing service port',(0,.86,1.13),.15,.16,dark,axis=(0,1,0),vertices=32)
    cylinder('Rear inspection closure',(0,.956,1.13),.112,.032,brass,axis=(0,1,0),vertices=32)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/086';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        # UV coordinates make the independently authored maps portable to glTF.
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if obj==shell:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x,-point.y)/(2*math.pi)+.5,point.z/3.1))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data);bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        for polygon in obj.data.polygons:polygon.use_smooth=True
        obj.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000,triangles
    scratch=root/'artifacts/mikotaj-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/086',key='MK01',name='Base Crystal',culture='mikotaj',
        footprint=[3,3],definition_class=20,construction_updates=50,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,
        author='sources/tools/blender/remaster_mikotaj_base_crystal.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Opaque ore-like alloy anatomy, not transparent home-world crystal; precise sections/backside service port are authored.',
                        'No operational motion inferred from catalogue information reveal. Blue emitters are material emission, not an invented gameplay effect.'],
        scale_contract='3x3 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk01-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_BASE_CRYSTAL_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
