"""Author MN01 Base Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/base-block';maps=root/'sources/materials/mauna/base-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610101);buffers={name:[] for name in ['cast-concrete-colour','chipped-concrete-edge-colour','used-brass-colour','recess-red-colour','concrete-orm','metal-orm','cast-service-normal']}
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cloud=.025*math.sin(17*u+3*math.cos(11*v))+.020*math.cos(13*v+5*u);grain=rng.uniform(-.018,.018);stain=max(0,math.sin(21*u+2*math.cos(13*v))-.6)*.09;aggregate=.065 if rng.random()<.025 else 0
            buffers['cast-concrete-colour'].extend([max(.01,c+cloud+grain+aggregate-stain) for c in (.29,.34,.41)]+[1]);buffers['chipped-concrete-edge-colour'].extend([max(.01,c+cloud+grain+aggregate-stain) for c in (.40,.45,.51)]+[1]);buffers['used-brass-colour'].extend([max(.01,c+cloud*.6+grain*.5-stain*.5) for c in (.55,.36,.10)]+[1]);buffers['recess-red-colour'].extend([max(.01,c+cloud*.4+grain*.4-stain*.4) for c in (.42,.055,.035)]+[1]);buffers['concrete-orm'].extend([1,min(.96,max(.65,.82+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.7,max(.3,.49+grain+stain)),.72,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.022,.022),.5+rng.uniform(-.022,.022),1,1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Mauna exposed aggregate edge','chipped-concrete-edge-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);red=material('Dark red nonemissive recessed fittings','recess-red-colour');dark=material('Dark service slots and roof cells')
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
    profile=[(.20,.95),(.38,.94),(1.03,.80),(1.07,.78),(2.08,.63)];verts=[(x*h,y*h,z) for z,h in profile for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]];faces=[]
    for j in range(len(profile)-1):
        for i in range(4):faces.append((j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i))
    faces.extend([(3,2,1,0),tuple((len(profile)-1)*4+i for i in range(4))]);body=solid('Base Block tapered concrete core',verts,faces,concrete);body.data.materials.append(edge);mod=body.modifiers.new('Small cast edge chamfers','BEVEL');mod.width=.006;mod.segments=1;mod.material=1;apply(body,mod)
    def half(z):
        for (a,ra),(b,rb) in zip(profile,profile[1:]):
            if z<=b:return ra+(rb-ra)*(z-a)/(b-a)
        return profile[-1][1]
    def surface(face,u,z):
        origin=Vector((u,-3,z)) if face=='front' else Vector((3,u,z));direction=Vector((0,1,0)) if face=='front' else Vector((-1,0,0));bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(origin,direction);assert hit,(face,u,z);return q,n
    panel_q,panel_n=surface('front',0,1.55);tool=box('Temporary broad source-field recess',panel_q+panel_n*.012,(.64,.88,.074),concrete,panel_n,0);cut(body,tool,'Shallow practical upper front panel field')
    rects=[]
    for family,face,positions,z,height,width,mat in [('long-red','front',[-.16,.16],1.55,.62,.075,red),('upper-dark','right',[.18,.35],1.55,.24,.065,dark),('short-red','right',[-.14,.10],1.12,.23,.065,red)]:
        for index,u in enumerate(positions):
            q,n=surface(face,u,z);tool=box('Temporary actual rectangular service recess',q+n*.012,(width,height,.084),concrete,n,0);cut(body,tool,'Actual rectangular recess '+family+str(index));box('Base Block '+family+' inset '+str(index),q-n*.032,(width-.006,height-.006,.012),mat,n,.001);rects.append(dict(family=family,index=index,point=list(q),normal=list(n),depth=.030))
    points=[]
    for family,face,positions in [('upper-amber','right',[(-.17,z) for z in [1.35,1.55,1.75]]),('lower-amber','right',[(u,.89) for u in [-.60,-.20,.20,.60]])]:
        for index,(u,z) in enumerate(positions):
            q,n=surface(face,u,z);bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.047,depth=.10,location=q+n*.022);tool=bpy.context.object;tool.rotation_euler=Vector(n).to_track_quat('Z','Y').to_euler();cut(body,tool,'Blind amber fitting socket');bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.044,depth=.034,location=q-n*.014);o=bpy.context.object;o.name='Base Block '+family+' fitting '+str(index);o.rotation_euler=Vector(n).to_track_quat('Z','Y').to_euler();o.data.materials.append(gold);mod=o.modifiers.new('Used brass fitting lip','BEVEL');mod.width=.002;mod.segments=2;apply(o,mod);points.append(dict(family=family,index=index,point=list(q),normal=list(n),depth=.028))
    roof=box('Base Block raised square roof pad',(0,0,2.12),(.52,.52,.12),concrete,bevel=.004);roof_cells=[]
    for i,(x,y) in enumerate([(-.11,-.11),(.11,-.11),(-.11,.11),(.11,.11)]):
        cut(roof,box('Temporary roof cell',(x,y,2.18),(.10,.10,.08),concrete,bevel=0),'True blind square roof cell');box('Base Block dark roof cell '+str(i),(x,y,2.139),(.092,.092,.012),dark,bevel=.001);roof_cells.append([x,y,2.138])
    def join_parts(objects,name):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
    feet=[];fins_meta=[]
    for face in range(4):
        angle=face*math.pi/2;normal=Vector((math.sin(angle),-math.cos(angle),0));tangent=Vector((math.cos(angle),math.sin(angle),0));fins=[]
        for index,u in enumerate([-.69,-.23,.23,.69]):
            outline=[(half(.78)+.010,.78),(half(.74)-.060,.74),(.88,.30),(1.05,.30)];verts=[tangent*(u+du)+normal*n+Vector((0,0,z)) for du in [-.055,.055] for n,z in outline];faces_fin=[(3,2,1,0),(4,5,6,7)]+[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)];fins.append(solid('Concrete buttress '+str(face)+' '+str(index),verts,faces_fin,concrete));centre=tangent*u+normal*1.035+Vector((0,0,.185));foot=box('Brass foot '+str(face)+' '+str(index),centre,(.15,.14,.32),gold,bevel=.004);foot.rotation_euler.z=angle;feet.append(foot);fins_meta.append(dict(face=face,index=index,body_contact=list(tangent*u+normal*(half(.755)-.015)+Vector((0,0,.755))),foot_contact=list(tangent*u+normal*1.0+Vector((0,0,.32)))))
        join_parts(fins,'Base Block concrete buttress group '+str(face))
    join_parts(feet,'Base Block sixteen brass foot caps')
    bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(Vector((.35,.28,3)),Vector((0,0,-1)));assert hit;spall=dict(point=list(q),normal=list(n));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.04,location=q+n*.032);tool=bpy.context.object;tool.data.materials.append(concrete);tool.data.materials.append(edge)
    for f in tool.data.polygons:f.material_index=1
    cut(body,tool,'Actual shallow cast concrete spall')
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/130';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
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
        if o==body:
            uv=o.data.uv_layers.active
            for face in o.data.polygons:
                for index in face.loop_indices:
                    q=o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1.2)/2.4,q.z/2.3) if abs(face.normal.x)>.5 else ((q.x+1.2)/2.4,q.z/2.3) if abs(face.normal.y)>.5 else ((q.x+1.2)/2.4,(q.y+1.2)/2.4)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');apply(o,mod);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=e.calc_face_angle(0)<.35
        bm.to_mesh(o.data);bm.free()
        for f in o.data.polygons:f.use_smooth=True
        o.data.normals_split_custom_set([tuple(n.vector) for n in o.data.corner_normals])
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/artemian-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])




    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/130',key='MN01',name='Base Block',culture='mauna',footprint=[3,3],definition_class=20,construction_updates=35,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_base_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=rects,amber_fittings=points,roof_cells=roof_cells,buttress_contacts=fins_meta,physical_spall=spall,interpretation=['Own angular greyblue concrete block,slopedskirt/roofpad,2longredslots/3upperamberpoints/2darkslots/2shortredslots/4loweramberpoints and4goldtippedbuttressespervisibleface govern geometry.','Hidden rearfoot symmetry andfourcellreading ofsmall roofmark,practicalpanelrecess andcell-relative dimensions authored. PB20isTerran functioncontext,not Mauna operation. No own operating phases/glow inferred.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn01-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_BASE_BLOCK_AUTHORED',triangles,len(meshes),len(created),flush=True)



if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
