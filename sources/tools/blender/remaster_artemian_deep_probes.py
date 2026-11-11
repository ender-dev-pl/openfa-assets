"""Author AR10 Deep Probes from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/deep-probes';maps=root/'sources/materials/artemian/deep-probes';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2601001);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2601005);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.24,.39,.31)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.40,.56,.52)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.50+.05*math.cos(11*u+3*v),.06,.055,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('red-sensor-housing-colour',red)]:
        image=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name in ['occlusion-roughness-metallic','used-metal-normal']:image.colorspace_settings.name='Non-Color'
        image.pixels.foreach_set(pixels);path=maps/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();images[name]=image
    def material(name,colour,image=None,emission=0,metal=.84,rough=.4):
        m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if image:
            tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=images[image];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);packed=m.node_tree.nodes.new('ShaderNodeTexImage');packed.image=images['occlusion-roughness-metallic'];split=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(packed.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic'])
            n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=images['used-metal-normal'];nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;m.node_tree.links.new(n.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
            if emission:m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value=emission;return m
    alloy=material('Used Artemian muted green alloy',(.24,.39,.31),'muted-green-alloy-colour');exposed=material('Pale teal mast and exposed alloy edges',(.40,.56,.52),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour');redmat=material('Red sensor housings',(.50,.06,.055),'red-sensor-housing-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    profile=[(.025,.29,.25),(.04,.37,.30),(.09,.35,.29),(.13,.27,.23),(.15,.05,.04)];n=128;vertices=[];faces=[]
    for z,rx,ry in profile:
        for i in range(n):a=i*math.tau/n;vertices.append((rx*math.cos(a),ry*math.sin(a),z))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))];body=solid('Deep Probes low green oval plinth',vertices,faces,alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    for v in body.data.vertices:
        q=v.co
        if q.z>.08:q.z-=.0015*math.exp(-((q.x+.20)/.05)**2-((q.y-.05)/.07)**2)
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=64):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small used sensor edges','BEVEL');mod.width=min(.003,depth*.10);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    bpy.context.view_layer.update();hit,roof,_,_=body.ray_cast(Vector((0,.04,1)),Vector((0,0,-1)));assert hit;bottom=roof.z-.035;cylinder('Deep Probes central teal mast',(0,.04,(bottom+2.49)/2),.028,2.49-bottom,exposed)
    outer=[(-.10,1.34),(-.14,1.40),(-.14,2.34),(-.08,2.41),(0,2.46),(.08,2.41),(.14,2.34),(.14,1.40),(.10,1.34),(0,1.29)]
    inner=[(-.078,1.36),(-.11,1.41),(-.11,2.33),(-.063,2.39),(0,2.43),(.063,2.39),(.11,2.33),(.11,1.41),(.078,1.36),(0,1.32)]
    count=len(outer);verts=[(x,.04+y,z) for y in [-.0225,.0225] for contour in [outer,inner] for x,z in contour];f=[]
    for i in range(count):
        j=(i+1)%count;f.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),(i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)])
    frame=solid('Deep Probes open brass capsule frame',verts,f,warm);bpy.context.view_layer.objects.active=frame;mod=frame.modifiers.new('Worn frame corner edges','BEVEL');mod.width=.002;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    hit,roof,_,_=body.ray_cast(Vector((.14,.055,1)),Vector((0,0,-1)));assert hit;bottom=roof.z-.03;cylinder('Deep Probes short brass rod',(.14,.055,(bottom+.78)/2),.025,.78-bottom,warm)
    for i,(x,y) in enumerate([(-.11,-.12),(.10,-.055)]):
        hit,roof,_,_=body.ray_cast(Vector((x,y,1)),Vector((0,0,-1)));assert hit;bottom=roof.z-.025;top=roof.z+.065;cylinder('Deep Probes short dark housing support '+str(i),(x,y,(bottom+top)/2),.032,top-bottom,dark)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(x,y,top+.025));o=bpy.context.object;o.name='Deep Probes red rounded housing '+str(i)
        for v in o.data.vertices:v.co=(v.co.x*.065,v.co.y*.065,v.co.z*.050)
        o.data.materials.append(redmat)
    for i,(x,y) in enumerate([(-.22,.05),(.23,-.10),(-.10,.20)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,1)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.004,location=point+normal*.001);cut=bpy.context.object
        for mat in [alloy,exposed,dark]:cut.data.materials.append(mat)
        for face in cut.data.polygons:face.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before minor finish chips','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Real small alloy chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/116';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o==body:
            uv=o.data.uv_layers.active
            for face in o.data.polygons:
                values=[]
                for index in face.loop_indices:
                    p=o.data.vertices[o.data.loops[index].vertex_index].co;values.append(((math.atan2(p.y,p.x)/math.tau+.5),p.z/.2))
                seam=max(u for u,v in values)-min(u for u,v in values)>.5
                for index,(u,v) in zip(face.loop_indices,values):uv.data[index].uv=(u+1 if seam and u<.5 else u,v)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=e.calc_face_angle(0)<.60
        bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.use_smooth=True
        o.data.normals_split_custom_set([tuple(n.vector) for n in o.data.corner_normals])
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/artemian-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/116',key='AR10',name='Deep Probes',culture='artemian',footprint=[2,2],definition_class=16,construction_updates=34,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_deep_probes.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Small low green plinth,slender teal mast with open brass capsule frame,one short brass rod and two red housings follow actual source and reviewed concept.','Hidden sensor engineering,frame/housing sections and metric dimensions remain authored or unknown. Generic PB16 turntable and ST12 different housing do not establish AR10 operation.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar10-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_DEEP_PROBES_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
