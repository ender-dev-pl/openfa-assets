"""Author AR03 Filtration Tanks from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/filtration-tanks';maps=root/'sources/materials/artemian/filtration-tanks';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2600301);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2600305);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cloud=.025*math.sin(9*u+2*math.sin(7*v))+.020*math.cos(13*v+math.sin(11*u));grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=max(0,math.sin(17*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.24,.39,.31)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.46,.52,.56)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.48+.05*math.cos(11*u+3*v),.09,.075,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('red-front-inset-colour',red)]:
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
    alloy=material('Used Artemian muted green alloy',(.24,.39,.31),'muted-green-alloy-colour');exposed=material('Worn exposed alloy edges',(.46,.52,.56),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour');redmat=material('Two red front insets',(.48,.09,.075),'red-front-inset-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    profile=[(.02,.68,1.08),(.08,.79,1.18),(.20,.78,1.17),(.22,.76,1.15),(.26,.68,1.08),(.37,.66,1.03),(.49,.57,.92),(.58,.43,.72),(.63,.25,.43),(.65,.02,.05)];n=96;vertices=[];faces=[]
    for z,rx,ry in profile:
        for i in range(n):a=i*math.tau/n;vertices.append((rx*math.cos(a),ry*math.sin(a),z))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))];body=solid('Filtration Tanks broad green metal carapace',vertices,faces,alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    # Broad roof faces are sampled for real shallow finish dents.
    bm=bmesh.new();bm.from_mesh(body.data);edges=[e for e in bm.edges if min(v.co.z for v in e.verts)>.45 and e.calc_length()>.04];bmesh.ops.subdivide_edges(bm,edges=edges,cuts=2,use_grid_fill=True);assert all(e.is_manifold for e in bm.edges);bm.to_mesh(body.data);bm.free()
    for v in body.data.vertices:
        p=v.co
        if p.z>.42:p.z-=min(1,(p.z-.42)/.12)*sum(depth*math.exp(-((p.x-x)/sx)**2-((p.y-y)/sy)**2) for x,y,depth,sx,sy in [(.22,-.30,.004,.10,.16),(-.20,.25,.003,.10,.14)])
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small used fitting edges','BEVEL');mod.width=min(.005,depth*.12);mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    def cube(name,centre,size,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        o.data.materials.append(mat);mod=o.modifiers.new('Worn small module corners','BEVEL');mod.width=.005;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    bpy.context.view_layer.update()
    for i,y in enumerate([.48,0,-.48]):
        hit,point,normal,_=body.ray_cast(Vector((-3,y,.13)),Vector((1,0,0)));assert hit;centre=Vector((point.x-.006,y,.18));cylinder('Filtration Tanks pale side fitting '+str(i),centre,.034,.32,exposed);cylinder('Filtration Tanks pale side cap '+str(i),(centre.x,y,.348),.042,.030,exposed)
    for i,y in enumerate([.20,.38,.56,.74]):
        hit,point,_,_=body.ray_cast(Vector((-.34,y,2)),Vector((0,0,-1)));assert hit;cube('Filtration Tanks dark module seat '+str(i),point+Vector((0,0,.009)),(.115,.13,.035),dark);cube('Filtration Tanks amber roof module '+str(i),point+Vector((0,0,.043)),(.105,.12,.045),warm)
    for i,(x,radius) in enumerate([(-.31,.060),(.06,.090)]):
        hit,point,normal,_=body.ray_cast(Vector((x,-3,.17)),Vector((0,1,0)));assert hit;cylinder('Filtration Tanks red front inset '+str(i),point+normal*.007,radius,.020,redmat,axis=normal)
        ring=cylinder('Filtration Tanks front inset rim '+str(i),point+normal*.002,radius+.012,.014,dark,axis=normal);bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=radius+.002,depth=.12,location=point);cut=bpy.context.object;cut.rotation_euler=normal.to_track_quat('Z','Y').to_euler();cut.data.materials.append(dark);bpy.context.view_layer.objects.active=ring;mod=ring.modifiers.new('Clear front rim','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    bpy.context.view_layer.update();hit,roof,_,_=body.ray_cast(Vector((.10,.60,2)),Vector((0,0,-1)));assert hit;bottom=roof.z-.06;cylinder('Filtration Tanks tall rear silver upright',(.10,.60,(bottom+1.20)/2),.040,1.20-bottom,exposed);cylinder('Filtration Tanks silver upright cap',(.10,.60,1.209),.046,.038,exposed)
    hit,roof2,_,_=body.ray_cast(Vector((-.12,.60,2)),Vector((0,0,-1)));assert hit;curve=bpy.data.curves.new('Filtration Tanks connected return bend','CURVE');curve.dimensions='3D';curve.resolution_u=10;curve.bevel_depth=.025;curve.bevel_resolution=3;curve.use_fill_caps=True;spline=curve.splines.new('BEZIER');coords=[(.10,.60,1.05),(-.035,.60,1.05),(-.12,.60,.98),(-.12,.60,roof2.z-.05)];spline.bezier_points.add(len(coords)-1)
    for p,co in zip(spline.bezier_points,coords):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new('Filtration Tanks connected return bend',curve);bpy.context.collection.objects.link(o);curve.materials.append(exposed);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    hit,roof3,_,_=body.ray_cast(Vector((.40,.28,2)),Vector((0,0,-1)));assert hit;cylinder('Filtration Tanks separate short roof upright',roof3+Vector((0,0,.065)),.030,.18,exposed)
    hit,pin,_,_=body.ray_cast(Vector((.06,.06,2)),Vector((0,0,-1)));assert hit;cylinder('Filtration Tanks tiny dark roof point',pin+Vector((0,0,.003)),.018,.012,dark)
    for i,(x,y) in enumerate([(.34,-.20),(.20,.45),(-.44,-.30)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        for m in [alloy,exposed,dark]:cut.data.materials.append(m)
        for p in cut.data.polygons:p.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before small finish chip','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Real minor alloy chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/109';root_object['footprint']=[3,3];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o==body:
            uv=o.data.uv_layers.active
            for loop in o.data.loops:
                p=o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x/1.80+p.y*.05+.5,p.y/2.60+p.z*.18+.5)
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/109',key='AR03',name='Filtration Tanks',culture='artemian',footprint=[3,3],definition_class=37,construction_updates=30,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_filtration_tanks.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Broad low green shell,three pale side fittings,four amber roof modules,two unequal red front insets and connected silver rear pipe/short upright follow actual source and reviewed concept.','Exact hidden water-treatment engineering,sections and metric dimensions are authored or unknown. No operation clip inferred from catalogue reveal or generic PB37 turntable.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar03-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_FILTRATION_TANKS_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
