"""Author AR12 Shielded Solars from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/shielded-solars';maps=root/'sources/materials/artemian/shielded-solars';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2601101);images={};base=[];edge=[];orm=[];normal=[];amber=[]
    scratch_rng=random.Random(2601105);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.32,.46,.40)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.46,.52,.56)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.50+.02*math.sin(5*u+7*v),.72+.015*math.cos(7*u-3*v),.77+grain*.4+scratch*.1,1])
    for name,pixels in [('green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('pale-cyan-collector-colour',amber)]:
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
    alloy=material('Used Artemian green alloy',(.32,.46,.40),'green-alloy-colour');exposed=material('Worn exposed alloy edges',(.46,.52,.56),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Pale protected collector faces',(.46,.22,.035),'pale-cyan-collector-colour')
    shader=warm.node_tree.nodes.get('Principled BSDF')
    for socket,value in [('Metallic',.15),('Roughness',.52)]:
        for link in list(socket_link for socket_link in warm.node_tree.links if socket_link.to_socket==shader.inputs[socket]):warm.node_tree.links.remove(link)
        shader.inputs[socket].default_value=value
    for node in warm.node_tree.nodes:
        if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.12
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    # Upright rounded shielded tower;its top shoulder rises toward the right.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,0));body=bpy.context.object;body.name='Shielded Solars green upright shell'
    for v in body.data.vertices:
        v.co.x*=.64;v.co.y*=.34;v.co.z=.025 if v.co.z<0 else 2.20+(v.co.x+.32)/.64*.35
    body.data.materials.append(alloy);body.data.materials.append(exposed);body.data.materials.append(dark);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Rounded metal shell edges','BEVEL');mod.width=.070;mod.segments=5;bpy.ops.object.modifier_apply(modifier=mod.name)
    def plate(name,coords,centre,depth,mat,side=False):
        vertices=[]
        for d in [-depth/2,depth/2]:
            for u,z in coords:vertices.append((centre[0]+(d if side else u),centre[1]+(u if side else d),centre[2]+z))
        n=len(coords);faces=[tuple(reversed(range(n))),tuple(n+i for i in range(n))]+[(i,(i+1)%n,n+(i+1)%n,n+i) for i in range(n)];o=solid(name,vertices,faces,mat);bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Small protective face edge rounding','BEVEL');mod.width=.003;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    def oval(rx,rz,n=48,power=1):return [(rx*math.copysign(abs(math.cos(a))**power,math.cos(a)),rz*math.sin(a)) for a in [i*math.tau/n for i in range(n)]]
    def collector(label,x,z,rx,rz,shape='hex'):
        coords=[(-.44*rx,-rz),(.44*rx,-rz),(rx,-.45*rz),(rx,.45*rz),(.44*rx,rz),(-.44*rx,rz),(-rx,.45*rz),(-rx,-.45*rz)] if shape=='hex' else oval(rx,rz)
        if shape=='hex':
            rounded=[]
            for i,c in enumerate(coords):
                previous=coords[i-1];following=coords[(i+1)%len(coords)];a=tuple(c[k]+.20*(previous[k]-c[k]) for k in range(2));b=tuple(c[k]+.20*(following[k]-c[k]) for k in range(2))
                for step in range(5):
                    t=step/4;rounded.append(tuple((1-t)**2*a[k]+2*t*(1-t)*c[k]+t*t*b[k] for k in range(2)))
            coords=rounded
        plate('Shielded Solars '+label+' seat',coords,(x,-.166,z),.022,dark)
        plate('Shielded Solars '+label+' face',[(u*.92,v*.96) for u,v in coords],(x,-.177,z),.012,warm)
    collector('upper collector',.015,1.91,.155,.385);collector('lower collector',.015,.78,.145,.34)
    collector('middle small spot',-.205,1.34,.075,.09,'oval');collector('lower small spot',-.205,.39,.044,.055,'oval');collector('foot small spot',-.16,.20,.038,.064,'oval')
    for i,(z,h) in enumerate([(2.18,.43),(1.35,.82),(.49,.43)]):
        coords=oval(.080,h/2,power=.30);plate('Shielded Solars side collector '+str(i)+' seat',coords,(.313,.015,z),.018,exposed,True);plate('Shielded Solars side collector '+str(i)+' face',[(u*.84,v*.95) for u,v in coords],(.326,.015,z),.010,warm,True)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.025,depth=.37,location=(.20,.045,2.64));mast=bpy.context.object;mast.name='Shielded Solars short top mast';mast.data.materials.append(exposed);mod=mast.modifiers.new('Small mast edge wear','BEVEL');mod.width=.003;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    for i,(x,z) in enumerate([(-.245,1.63),(.24,.30),(-.20,2.31),(-.245,1.60)]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2 if i==3 else 1,radius=.026 if i==3 else .006,location=(x,-.191 if i==3 else -.172,z));cut=bpy.context.object
        for m in [alloy,exposed,dark]:cut.data.materials.append(m)
        for f in cut.data.polygons:f.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Actual minor shield casing chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/118';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/118',key='AR12',name='Shielded Solars',culture='artemian',footprint=[2,2],definition_class=28,construction_updates=46,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,author='sources/tools/blender/remaster_artemian_shielded_solars.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Slender upright green shielded tower,two large pale front collectors,one mid-left spot,two tiny lower spots,three side strips and short top mast follow actual source/concept.','Collector sections,hidden solar engineering and metric height remain authored or unknown;generic Terran folding petals are not Artemian anatomy or operation.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar12-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_SHIELDED_SOLARS_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
