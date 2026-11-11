"""Author AR20 Advanced Ore Extractor from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/advanced-ore-extractor';maps=root/'sources/materials/artemian/advanced-ore-extractor';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2602001);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2602005);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.29,.43,.36)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.60,.67,.70)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.55+.05*math.cos(11*u+3*v),.34,.12,1])
    oxidized_orm=[.35 if i%4==2 else value for i,value in enumerate(orm)]
    for name,pixels in [('oxidized-alloy-orm',oxidized_orm),('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('copper-fitting-colour',red)]:
        image=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name in ['occlusion-roughness-metallic','oxidized-alloy-orm','used-metal-normal']:image.colorspace_settings.name='Non-Color'
        image.pixels.foreach_set(pixels);path=maps/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();images[name]=image
    def material(name,colour,image=None,emission=0,metal=.84,rough=.4):
        m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if image:
            tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=images[image];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);packed=m.node_tree.nodes.new('ShaderNodeTexImage');packed.image=images['oxidized-alloy-orm' if image in ['exposed-alloy-edge-colour','copper-fitting-colour'] else 'occlusion-roughness-metallic'];split=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(packed.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic'])
            n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=images['used-metal-normal'];nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;m.node_tree.links.new(n.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
            if emission:m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color'])

        p.inputs['Emission Strength'].default_value=emission;return m
    alloy=material('Used Artemian muted green shell',(.29,.43,.36),'muted-green-alloy-colour');exposed=material('Pale oxidized vertical rod',(.60,.67,.70),'exposed-alloy-edge-colour');dark=material('Dark right side point',(.014,.019,.023),metal=.35,rough=.65);brass=material('Worn brass arch and copper fittings',(.55,.30,.10),'copper-fitting-colour')

    def apply(o,mod):
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    def boolean(o,cut,label):
        mod=o.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;apply(o,mod);bpy.data.objects.remove(cut,do_unlink=True)
    def ellipsoid(name,centre,radii):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*radii[0],v.co.y*radii[1],v.co.z*radii[2])
        return o
    front=ellipsoid('Temporary front leaf',(-.35,-.40,.17),(.90,.42,.24));front.rotation_euler.z=math.pi/4
    hood=ellipsoid('Temporary taller hood',(.22,.25,.31),(.65,.60,.58))
    for v in hood.data.vertices:
        upper=max(0,v.co.z/.58);v.co.x-=.27*upper;v.co.y-=.12*upper

    bpy.ops.object.select_all(action='DESELECT');front.select_set(True);hood.select_set(True);bpy.context.view_layer.objects.active=hood;bpy.ops.object.join();body=hood;body.name='Advanced Ore Extractor continuous two-lobed green shell'
    mod=body.modifiers.new('Continuous source lobes','REMESH');mod.mode='VOXEL';mod.voxel_size=.018;mod.use_smooth_shade=True;apply(body,mod)
    mod=body.modifiers.new('Quiet joined alloy contour','SMOOTH');mod.factor=.8;mod.iterations=5;apply(body,mod)
    mod=body.modifiers.new('Game shell budget','DECIMATE');mod.ratio=.23;apply(body,mod);body.data.materials.append(alloy)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.475));cut=bpy.context.object
    for v in cut.data.vertices:v.co=(v.co.x*4,v.co.y*4,v.co.z)
    boolean(body,cut,'Closed flat underside at .025');bpy.context.view_layer.update()
    def surface(x,z):
        hit,q,n,_=body.ray_cast(body.matrix_world.inverted()@Vector((x,-3,z)),Vector((0,1,0)));assert hit,(x,z);return body.matrix_world@q,(body.matrix_world.to_3x3()@n).normalized()
    def solid(name,verts,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    def cylinder(name,point,radius,depth,mat,axis=(0,0,1)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=point);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Used small rounded edge','BEVEL');mod.width=.003;mod.segments=3;apply(o,mod);return o
    def lathe(name,profile,mat,point,normal):
        n=64;rotation=Vector(normal).to_track_quat('Z','Y');verts=[Vector(point)+rotation@Vector((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z)) for z,r in profile for i in range(n)];faces=[]
        for j in range(len(profile)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);return solid(name,verts,faces,mat)
    ports=[]
    for i,(x,z) in enumerate([(-.55,.22),(-.20,.31)]):
        q,n=surface(x,z);ports.append(dict(point=list(q),normal=list(n)));cut=lathe('Temporary real front socket',[(-.025,.066),(.08,.066)],alloy,q,n);boolean(body,cut,'Blind copper front recess '+str(i))
        lathe('Advanced Ore Extractor copper front fitting '+str(i),[(-.028,.061),(.004,.061),(.009,.054)],brass,q,n)
        # A visible rim is a closed ring, not an opaque disc hiding the recess.
        ring=cylinder('Temporary rim',q-n*.010,.078,.040,brass,n);cut=cylinder('Temporary rim centre',q+n*.002,.067,.1,brass,n);boolean(ring,cut,'True annular copper lip');ring.name='Advanced Ore Extractor front fitting rim '+str(i)
    q,n=surface(.78,.21);small=dict(point=list(q),normal=list(n));cut=lathe('Temporary dark point recess',[(-.02,.026),(.07,.026)],alloy,q,n);boolean(body,cut,'Actual small right point recess');lathe('Advanced Ore Extractor small dark right point',[(-.023,.023),(-.013,.023)],dark,q,n)
    # Continuous open-bottom horseshoe ribbon follows the actual curved hood.
    x=.35;outer=[(x-.115,.17+j*.46/24) for j in range(25)];inner=[(x-.074,.17+j*.46/24) for j in range(25)]
    for j in range(1,25):
        a=math.pi-j*math.pi/24;outer.append((x+.115*math.cos(a),.63+.13*math.sin(a)));inner.append((x+.074*math.cos(a),.63+.09*math.sin(a)))
    outer.extend((x+.115,.63-j*.46/24) for j in range(1,25));inner.extend((x+.074,.63-j*.46/24) for j in range(1,25));count=len(outer);width=8;layer=count*(width+1);verts=[];faces=[]
    for offset in [-.015,.012]:
        for j in range(count):
            for k in range(width+1):
                t=k/width;px=(1-t)*outer[j][0]+t*inner[j][0];pz=(1-t)*outer[j][1]+t*inner[j][1];q,n=surface(px,pz);verts.append((px,q.y-offset,pz))
    for j in range(count-1):
        for k in range(width):
            a=j*(width+1)+k;b=a+1;c=b+width+1;d=a+width+1;faces.extend([(a,b,c,d),(layer+a,layer+d,layer+c,layer+b)])
        a=j*(width+1);b=(j+1)*(width+1);faces.append((a,layer+a,layer+b,b));a=j*(width+1)+width;b=(j+1)*(width+1)+width;faces.append((a,b,layer+b,layer+a))
    for j in [0,count-1]:
        for k in range(width):
            a=j*(width+1)+k;b=a+1;faces.append((a,layer+a,layer+b,b))
    arch=solid('Advanced Ore Extractor narrow open-bottom brass arch',verts,faces,brass);arch_contacts=[]
    for px,pz in [(x-.095,.28),(x-.095,.55),(x+.095,.28),(x+.095,.55),(x,.742)]:
        q,n=surface(px,pz);arch_contacts.append([px,q.y+.007,pz])
    points=[surface(x,z)[0] for z in [.20,.42,.55]];rail_y=min(q.y for q in points)-.025;rod=cylinder('Advanced Ore Extractor straight pale vertical rod',(x,rail_y,.31),.030,.56,exposed);supports=[]
    for i,z in enumerate([.20,.53]):
        q,n=surface(x,z);back=q.y+.017;front_y=rail_y+.010;point=Vector((x,(back+front_y)/2,z));cylinder('Advanced Ore Extractor hidden rod support '+str(i),point,.019,back-front_y,alloy,(0,1,0));supports.append(dict(body_point=list(q),rod_point=[x,rail_y+.015,z]))
    bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(body.matrix_world.inverted()@Vector((-.10,-.50,3)),Vector((0,0,-1)));assert hit;q=body.matrix_world@q;dent=dict(point=list(q),normal=list(n));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.03,location=q+n*.025);boolean(body,bpy.context.object,'Actual shallow service dent')
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/126';root_object['footprint']=[3,3];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o==body:
            uv=o.data.uv_layers.active
            for face in o.data.polygons:
                for index in face.loop_indices:
                    point=o.matrix_world@o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((point.x+1.1)/2.1,(point.y+1.15+point.z*.12)/2.1)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=e.calc_face_angle(0)<.60
        bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.use_smooth=True
        o.data.normals_split_custom_set([tuple(n.vector) for n in o.data.corner_normals])
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);print('MEASURED_TRIANGLES',triangles,flush=True);assert triangles<30000
    scratch=root/'artifacts/artemian-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])

    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/126',key='AR20',name='Advanced Ore Extractor',culture='artemian',footprint=[3,3],definition_class=13,construction_updates=34,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,author='sources/tools/blender/remaster_artemian_advanced_ore_extractor.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},front_ports=ports,small_point=small,arch_contacts=arch_contacts,rod_supports=supports,rod_centre=[x,rail_y,.31],physical_dent=dent,interpretation=['Own low two-lobed shell,2front copper fittings,narrow brass arch,straight pale rod and1tiny dark right point govern geometry.','No own operating overlays;genericPB13/ST01 is functional Terran context,not Artemian motion. Hidden backside/sections/cell-relative dimensions are authored.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/ar20-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_ADVANCED_ORE_EXTRACTOR_AUTHORED',triangles,len(meshes),len(created),flush=True)



if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
