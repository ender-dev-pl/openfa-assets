"""Author AR07 House of the Axe from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/house-of-the-axe';maps=root/'sources/materials/artemian/house-of-the-axe';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2600701);images={};base=[];edge=[];orm=[];normal=[];amber=[];
    scratch_rng=random.Random(2600705);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cloud=.025*math.sin(9*u+2*math.sin(7*v))+.020*math.cos(13*v+math.sin(11*u));grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=max(0,math.sin(17*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.20,.25,.30)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.46,.52,.56)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.26+.04*math.cos(7*u-3*v),.12,1])
    for name,pixels in [('slate-blue-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber)]:
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
    alloy=material('Used Artemian slate-blue alloy',(.20,.25,.30),'slate-blue-alloy-colour');exposed=material('Worn exposed alloy edges',(.46,.52,.56),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    # Four shallow nested overlapping armour terraces,one connected low shell.
    controls=[(.025,1.04,.99),(.07,1.13,1.08),(.14,1.13,1.08),(.22,1.08,1.03),(.235,1.00,.96),(.25,.96,.92),(.30,.96,.92),(.36,.91,.87),(.375,.84,.80),(.39,.80,.76),(.44,.80,.76),(.50,.74,.71),(.515,.67,.64),(.53,.63,.60),(.58,.61,.58),(.62,.53,.50),(.64,.40,.38),(.65,.02,.02)];profile=[]
    for j in range(len(controls)-1):
        p0=controls[max(0,j-1)];p1=controls[j];p2=controls[j+1];p3=controls[min(len(controls)-1,j+2)]
        for step in range(3):
            t=step/3;values=[.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in [1,2]];profile.append((p1[0]+(p2[0]-p1[0])*t,max(.02,values[0]),max(.02,values[1])))
    profile.append(controls[-1]);n=128;vertices=[];faces=[]
    for z,rx,ry in profile:
        for i in range(n):a=i*math.tau/n;vertices.append((rx*math.cos(a)*(.90+.12*math.sin(a)),ry*math.sin(a)+.10*z/.65,z))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))];body=solid('House of the Axe layered slate civic shell',vertices,faces,alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    bm=bmesh.new();bm.from_mesh(body.data);edges=[e for e in bm.edges if min(v.co.z for v in e.verts)>.28 and e.calc_length()>.075];bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True);assert all(e.is_manifold for e in bm.edges);bm.to_mesh(body.data);bm.free()
    for v in body.data.vertices:
        q=v.co
        if q.z>.28:q.z-=min(1,(q.z-.28)/.10)*sum(depth*math.exp(-((q.x-x)/sx)**2-((q.y-y)/sy)**2) for x,y,depth,sx,sy in [(-.25,-.28,.003,.12,.12),(-.22,.20,.003,.12,.12)])
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=48):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small used fitting edges','BEVEL');mod.width=min(.006,depth*.12);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=(.28,.22,.65));dome=bpy.context.object;dome.name='House of the Axe low pale roof lobe'
    for v in dome.data.vertices:v.co=(v.co.x*.25,v.co.y*.27,v.co.z*.13)
    dome.data.materials.append(exposed)
    bpy.context.view_layer.update()
    for label,x,top,radius,mat in [('silver',-.64,1.23,.040,exposed),('copper',-.30,.43,.034,warm)]:
        hit,point,_,_=body.ray_cast(Vector((x,-3,.11)),Vector((0,1,0)));assert hit;y=point.y-.020;cylinder('House of the Axe '+label+' base sleeve',(x,y,.125),.082 if label=='silver' else .074,.20,mat);cylinder('House of the Axe '+label+' upright',(x,y,(.205+top)/2),radius,top-.205,mat)
    for label,x,y,radius,mat,segments in [('copper roof inset',-.25,.15,.096,warm,8),('dark roof point 0',-.12,-.35,.036,dark,48),('dark roof point 1',.06,-.35,.036,dark,48)]:
        hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;cylinder('House of the Axe '+label,point+normal*.005,radius,.026,mat,axis=normal,vertices=segments)
        ring=cylinder('House of the Axe '+label+' clear rim',point+normal*.001,radius+.009,.016,dark if mat==warm else exposed,axis=normal);bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius+.001,depth=.15,location=point);cut=bpy.context.object;cut.rotation_euler=normal.to_track_quat('Z','Y').to_euler();cut.data.materials.append(dark);bpy.context.view_layer.objects.active=ring;mod=ring.modifiers.new('Open rim preserves roof inset centre','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    for i,(x,y) in enumerate([(-.34,.20),(-.18,-.45),(-.35,.40)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        for m in [alloy,exposed,dark]:cut.data.materials.append(m)
        for q in cut.data.polygons:q.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before small finish chip','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Real minor alloy chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/113';root_object['footprint']=[3,3];root_object['local_forward']='-Y';root_object['local_up']='+Z'
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
                    p=o.data.vertices[o.data.loops[index].vertex_index].co;values.append(((math.atan2(p.y-.10*p.z/.65,p.x)/math.tau+.5),p.z/.8))
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/113',key='AR07',name='House of the Axe',culture='artemian',footprint=[3,3],definition_class=255,construction_updates=48,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,author='sources/tools/blender/remaster_artemian_house_of_the_axe.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Low slate-blue layered wedge carapace,pale roof lobe,copper inset,two dark roof points and contrasting silver/copper front uprights with wider sleeves follow actual source and reviewed concept.','Hidden civic/ritual spaces,hardware sections and metric dimensions remain authored or unknown. No ritual/operating cycle inferred from catalogue reveal.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar07-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_HOUSE_OF_THE_AXE_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
