"""Author AR01 SoftCore from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/softcore';maps=root/'sources/materials/artemian/softcore';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2600101);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2600105);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cloud=.025*math.sin(9*u+2*math.sin(7*v))+.020*math.cos(13*v+math.sin(11*u));grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=max(0,math.sin(17*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.22,.28,.335)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.37,.43,.48)]+[1]);orm.extend([1,max(.22,min(.65,.39+stain*3+grain)),.84,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.46+.10*math.sin(5*u+7*v),.22+.05*math.cos(7*u-3*v),.035,1]);red.extend([.46+.05*math.cos(11*u+3*v),.025,.012,1])
    for name,pixels in [('blue-grey-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('red-nose-inset-colour',red)]:
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
    alloy=material('Used Artemian blue-grey alloy',(.22,.28,.335),'blue-grey-alloy-colour');exposed=material('Worn exposed alloy edges',(.37,.43,.48),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour',emission=.12);redmat=material('Tiny red nose inset',(.46,.025,.012),'red-nose-inset-colour',emission=.15)
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    profile=[(.02,.72,1.67),(.065,.76,1.72),(.14,.75,1.70),(.16,.73,1.68),(.19,.675,1.61),(.26,.66,1.59),(.28,.64,1.56),(.31,.59,1.49),(.38,.58,1.47),(.40,.56,1.44),(.43,.51,1.37),(.50,.49,1.34),(.56,.39,1.18),(.60,.24,.88),(.615,.02,.10)];count=96;vertices=[];faces=[]
    for j,(z,rx,ry) in enumerate(profile):
        for i in range(count):
            a=i*math.tau/count;c=math.cos(a);s=math.sin(a);x=rx*c;y=ry*s
            dent=.0018*math.sin(7*a+z*21)*math.sin(math.pi*max(0,min(1,z/.62)));vertices.append((x*(1-dent),y*(1-dent),z))
    for j in range(len(profile)-1):
        for i in range(count):faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    faces += [tuple(reversed(range(count))),tuple((len(profile)-1)*count+i for i in range(count))]
    body=solid('SoftCore continuous stepped metal carapace',vertices,faces,alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    for polygon in body.data.polygons:
        if any(abs(polygon.center.z-z)<.008 for z in [.15,.27,.39]):polygon.material_index=1
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Stable shell faces before small seam','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
    # Source cap seam follows an actual section of the authored shell.
    points=[];origin=Vector((0,-.95,.20));bpy.context.view_layer.update()
    for i in range(64):
        a=i*math.tau/64;direction=Vector((math.cos(a),0,math.sin(a)));hit,point,_,_=body.ray_cast(origin,direction);assert hit;points.append(point)
    curve=bpy.data.curves.new('Temporary front-cap seam cutter','CURVE');curve.dimensions='3D';curve.bevel_depth=.0045;curve.bevel_resolution=1;curve.resolution_u=1;curve.use_fill_caps=True;spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,v in zip(spline.points,points):p.co=(*v,1)
    spline.use_cyclic_u=True;cut=bpy.data.objects.new('Temporary front-cap seam cutter',curve);bpy.context.collection.objects.link(cut);bpy.ops.object.select_all(action='DESELECT');cut.select_set(True);bpy.context.view_layer.objects.active=cut;bpy.ops.object.convert(target='MESH');cut=bpy.context.object
    for m in [alloy,exposed,dark]:cut.data.materials.append(m)
    for p in cut.data.polygons:p.material_index=2
    bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0;bm.to_mesh(cut.data);bm.free();bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Physical front-cap seam','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    def cube(name,centre,dimensions,mat,normal=None,bevel=.005):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for vertex in o.data.vertices:vertex.co=(vertex.co.x*dimensions[0],vertex.co.y*dimensions[1],vertex.co.z*dimensions[2])
        if normal is not None:o.rotation_euler=Vector(normal).to_track_quat('Z','Y').to_euler()
        o.data.materials.append(mat);mod=o.modifiers.new('Small worn metal edges','BEVEL');mod.width=bevel;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    for i,(x,y,height) in enumerate([(.40,-1.27,.30),(.54,-.97,.42)]):
        cube('SoftCore pale front fitting '+str(i),(x,y,(height+.02)/2),(.075,.075,height-.02),exposed,bevel=.006)
        cube('SoftCore amber fitting cap '+str(i),(x,y,height+.020),(.078,.078,.044),warm,bevel=.007)
    bpy.context.view_layer.update()
    for i,y in enumerate([.04,.29]):
        hit,point,normal,_=body.ray_cast(Vector((0,y,2)),Vector((0,0,-1)));assert hit;cube('SoftCore small dark roof feature '+str(i),point+Vector((0,0,.018)),(.075,.055,.036),dark,bevel=.004)
    for name,x,mat,width in [('red nose inset',-.15,redmat,.045),('dark nose socket',.035,dark,.045)]:
        hit,point,normal,_=body.ray_cast(Vector((x,-4,.16)),Vector((0,1,0)));assert hit;cube('SoftCore '+name,point+normal*.004,(width,width,.012),mat,normal=normal,bevel=.003)
    # Sparse small physical metal chips. Broad shell bands remain readable.
    for i,(x,y) in enumerate([(.52,.70),(-.46,-.25),(.25,1.08)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        for m in [alloy,exposed,dark]:cut.data.materials.append(m)
        for p in cut.data.polygons:p.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Actual minor alloy edge chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    # Refine only broad roof edges;do not subdivide microscopic seam triangles.
    bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges)
    roof_edges=[e for e in bm.edges if min(v.co.z for v in e.verts)>.47 and e.calc_length()>.035]
    bmesh.ops.subdivide_edges(bm,edges=roof_edges,cuts=2,use_grid_fill=True);assert all(e.is_manifold for e in bm.edges);bm.to_mesh(body.data);bm.free()
    for vertex in body.data.vertices:
        p=vertex.co
        if p.z>.44:
            dent=sum(depth*math.exp(-((p.x-x)/sx)**2-((p.y-y)/sy)**2) for x,y,depth,sx,sy in [(.14,.55,.006,.10,.18),(-.20,-.10,.004,.12,.12),(.28,.90,.004,.08,.10)]);p.z-=dent*min(1,(p.z-.44)/.10)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/107';root_object['footprint']=[4,4];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o==body:
            uv=o.data.uv_layers.active
            for loop in o.data.loops:
                p=o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x/1.65+p.y*.05+.5,p.y/3.60+p.z*.24+.5)
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/107',key='AR01',name='SoftCore',culture='artemian',footprint=[4,4],definition_class=20,construction_updates=40,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_softcore.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Low elongated stepped metal shell,two unequal pale amber-capped front fittings,tiny red/dark nose details and two dark roof features follow actual source and reviewed concept.','Sparse front-cap seam,metal wear,hidden sections and engineering interpreted. No operation/opening clip inferred from catalogue reveal.'],scale_contract='4x4 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar01-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_SOFTCORE_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
