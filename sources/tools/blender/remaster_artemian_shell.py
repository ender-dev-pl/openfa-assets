"""Author AR13 Shell from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/shell';maps=root/'sources/materials/artemian/shell';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2601301);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2601305);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.30,.45,.37)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.32,.39,.38)]+[1]);orm.extend([1,max(.22,min(.65,.54+stain*2+grain)),.60,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.70+.05*math.sin(5*u+7*v),.52+.03*math.cos(7*u-3*v),.14,1]);red.extend([.52+.04*math.cos(11*u+3*v),.23,.15,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('copper-fitting-colour',red)]:
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
    alloy=material('Used Artemian muted green alloy',(.30,.45,.37),'muted-green-alloy-colour');exposed=material('Worn exposed alloy edges',(.32,.39,.38),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.025,.04,.065),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour');redmat=material('Copper front inset and sleeves',(.55,.24,.10),'copper-fitting-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    bpy.ops.mesh.primitive_uv_sphere_add(segments=128,ring_count=96,radius=1);body=bpy.context.object;body.name='Shell continuous ribbed green carapace'
    for v in body.data.vertices:
        p=v.co.copy();x=.90*p.x;y=.62*p.y;z=.07+(.44*p.z if p.z>=0 else .045*p.z)
        if p.z>0:
            z+=.055*p.z*sum(math.exp(-((p.x-q)/.08)**2) for q in [-.15,.10,.35,.60,.78]);z-=.003*math.exp(-((x+.30)/.10)**2-((y-.05)/.12)**2)
        v.co=(x,y,z)
    body.data.materials.append(alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    def cube(name,centre,size,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        o.data.materials.append(mat);mod=o.modifiers.new('Rounded used fitting corners','BEVEL');mod.width=min(size)*.12;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    for i,(x,centres,h,rodcentre,rodheight) in enumerate([(-.24,[.090,.210],.13,.385,.24),(.12,[.085,.195],.12,.355,.22)]):
        for j,z in enumerate(centres):cube('Shell copper block '+str(i)+' '+str(j),(x,-.605,z),(.18,.18,h),redmat)
        cube('Shell brass pin '+str(i),(x,-.605,rodcentre),(.060,.060,rodheight),warm)
    def disk(name,point,normal,radius,depth,mat):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=point);o=bpy.context.object;o.name=name;o.rotation_euler=normal.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small worn inset edges','BEVEL');mod.width=.002;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.context.view_layer.update()
    for i,(x,y) in enumerate([(-.63,-.18),(.42,-.45)]):
        hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;disk('Shell dark point rim '+str(i),point+normal*.001,normal,.058,.014,exposed);disk('Shell dark point inset '+str(i),point+normal*.008,normal,.045,.010,dark)
    for i,(x,y) in enumerate([(.60,.12),(-.55,.10),(.10,.40)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        for m in [alloy,exposed,dark]:cut.data.materials.append(m)
        for p in cut.data.polygons:p.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Stable triangles before tiny casing chip','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Real small casing chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/119';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
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
                    p=o.data.vertices[o.data.loops[index].vertex_index].co;values.append(((math.atan2(p.y/.62,p.x/.90)/math.tau+.5),(p.z-.025)/.54))
                seam=max(u for u,v in values)-min(u for u,v in values)>.5
                for index,(u,v) in zip(face.loop_indices,values):uv.data[index].uv=(u+1 if seam and u<.5 else u,v)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=True if o==body else e.calc_face_angle(0)<.60
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/119',key='AR13',name='Shell',culture='artemian',footprint=[2,2],definition_class=255,construction_updates=44,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_shell.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Low broad green integral-rib shell,two unequal double copper-block/brass-pin front fittings and two small dark points follow actual source/concept.','Hidden cloaking engineering,rib/fitting sections and metric height remain unknown/authored. Unique class255 has no indexed MAprofile;no cloak/operation animation inferred.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar13-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_SHELL_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
