"""Author AR21 Rare Ore Extractor from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/rare-ore-extractor';maps=root/'sources/materials/artemian/rare-ore-extractor';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2602101);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2602105);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.29,.43,.36)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.60,.67,.70)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.55+.05*math.cos(11*u+3*v),.24,.12,1])
    oxidized_orm=[.35 if i%4==2 else value for i,value in enumerate(orm)]
    for name,pixels in [('oxidized-alloy-orm',oxidized_orm),('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('copper-fitting-colour',red)]:
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
    alloy=material('Used Artemian muted green shell',(.29,.43,.36),'muted-green-alloy-colour');exposed=material('Pale oxidized capsule and stem',(.60,.67,.70),'exposed-alloy-edge-colour');dark=material('Dark hood points and lower fitting rim',(.014,.019,.023),metal=.35,rough=.65);brass=material('Worn brass core and lower fitting',(.60,.38,.08),'amber-fitting-colour');copper=material('Red copper short banded upright',(.55,.24,.10),'copper-fitting-colour')
    def apply(o,mod):
        bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    def boolean(o,cut,label):
        mod=o.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;apply(o,mod);bpy.data.objects.remove(cut,do_unlink=True)
    def ellipsoid(name,centre,radii):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*radii[0],v.co.y*radii[1],v.co.z*radii[2])
        return o

    controls=[(.025,.92,.72),(.065,.98,.78),(.22,.94,.74),(.36,.84,.65),(.41,.78,.61),(.46,.63,.52),(.54,.61,.50),(.82,.46,.39),(.97,.32,.28),(1.08,.18,.16),(1.11,.04,.04)];profile=[]
    def smooth_radius(z,column):
        zs=[p[0] for p in controls];rs=[p[column] for p in controls];slopes=[(b-a)/(y-x) for x,y,a,b in zip(zs,zs[1:],rs,rs[1:])];tangents=[slopes[0]]
        for a,b in zip(slopes,slopes[1:]):tangents.append(0 if a*b<=0 else 2*a*b/(a+b))
        tangents.append(slopes[-1]);i=min(len(zs)-2,next((j for j in range(len(zs)-1) if z<=zs[j+1]),len(zs)-2));h=zs[i+1]-zs[i];t=(z-zs[i])/h
        return (2*t**3-3*t**2+1)*rs[i]+(t**3-2*t**2+t)*h*tangents[i]+(-2*t**3+3*t**2)*rs[i+1]+(t**3-t**2)*h*tangents[i+1]
    for j in range(60):
        z=.025+(1.11-.025)*j/59;profile.append((z,smooth_radius(z,1),smooth_radius(z,2)))
    count=128;verts=[];faces=[]
    for z,rx,ry in profile:
        for i in range(count):
            a=i*math.tau/count;front=max(0,-math.sin(a));low=max(0,1-z/.48);wave=1+.16*front*low*math.cos(6*a+.4);lip=.12*math.exp(-((math.atan2(math.sin(a),math.cos(a)))/.22)**2)*low
            verts.append((rx*math.cos(a)*wave-.13*z/1.11+lip,ry*math.sin(a)*wave+.07*z/1.11,z))
    for j in range(len(profile)-1):
        for i in range(count):faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
    faces.extend([tuple(reversed(range(count))),tuple((len(profile)-1)*count+i for i in range(count))])
    mesh=bpy.data.meshes.new('Continuous low scalloped shell and raised hood');mesh.from_pydata(verts,[],faces);mesh.update();body=bpy.data.objects.new('Rare Ore Extractor continuous scalloped shell and raised hood',mesh);bpy.context.collection.objects.link(body);body.data.materials.append(alloy)
    def solid(name,verts,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    def cylinder(name,point,radius,depth,mat,axis=(0,0,1)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=point);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Used rounded fitting edges','BEVEL');mod.width=.002;mod.segments=3;apply(o,mod);return o
    def lathe(name,profile,mat,point=(0,0,0),normal=(0,0,1),closed=False):
        n=64;rotation=Vector(normal).to_track_quat('Z','Y');verts=[Vector(point)+rotation@Vector((r*math.cos(i*math.tau/n),r*math.sin(i*math.tau/n),z)) for z,r in profile for i in range(n)];faces=[]
        for j in range(len(profile)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        if closed:
            for i in range(n):faces.append(((len(profile)-1)*n+i,(len(profile)-1)*n+(i+1)%n,(i+1)%n,i))
        else:faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
        return solid(name,verts,faces,mat)
    def surface(x,z):
        bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(Vector((x,-3,z)),Vector((0,1,0)));assert hit,(x,z);return q,n
    upper_ports=[]
    for i,x in enumerate([-.22,.10]):
        q,n=surface(x,.73);upper_ports.append(dict(point=list(q),normal=list(n)));cut=lathe('Temporary upper dark recess',[(-.020,.031),(.07,.031)],alloy,q,n);boolean(body,cut,'Actual blind upper point recess '+str(i));lathe('Rare Ore Extractor upper dark point '+str(i),[(-.023,.028),(-.011,.028)],dark,q,n)
    q,n=surface(.30,.21);lower_port=dict(point=list(q),normal=list(n));cut=lathe('Temporary lower copper recess',[(-.025,.062),(.08,.062)],alloy,q,n);boolean(body,cut,'Actual blind lower copper socket');lathe('Rare Ore Extractor lower brass fitting',[(-.028,.058),(.005,.058)],brass,q,n)
    lathe('Rare Ore Extractor lower dark annular rim',[(-.025,.079),(.008,.079),(.008,.064),(-.025,.064)],dark,q,n,True)
    x,y=-.75,-.55;outer=[(-.10,.87),(-.14,.94),(-.14,1.69),(-.10,1.77),(0,1.85),(.10,1.77),(.14,1.69),(.14,.94),(.10,.87),(0,.85)];inner=[(-.050,.96),(-.083,1.00),(-.083,1.65),(-.055,1.70),(0,1.74),(.055,1.70),(.083,1.65),(.083,1.00),(.050,.96),(0,.95)]
    n=len(outer);verts=[(x+(u-dy)/math.sqrt(2),y+(u+dy)/math.sqrt(2),z) for dy in [-.060,.060] for contour in [outer,inner] for u,z in contour];faces=[]
    for j in range(n):
        k=(j+1)%n;faces.extend([(j,k,n+k,n+j),(2*n+j,3*n+j,3*n+k,2*n+k),(j,2*n+j,2*n+k,k),(n+j,n+k,3*n+k,3*n+j)])
    frame=solid('Rare Ore Extractor open pale capsule frame',verts,faces,exposed);mod=frame.modifiers.new('Gently rounded pale capsule corners','BEVEL');mod.width=.006;mod.segments=3;apply(frame,mod)
    cylinder('Rare Ore Extractor continuous brass core',(x,y,1.365),.045,.85,brass)
    for i,z in enumerate([1.20,1.47]):cylinder('Rare Ore Extractor brass core collar '+str(i),(x,y,z),.060,.032,brass)
    cylinder('Rare Ore Extractor straight pale stem',(x,y,.46),.037,.87,exposed);supports=[]
    for i,z in enumerate([.18,.32]):
        q,n=surface(-.65,z);a=q-n*.025;b=Vector((x-.010,y-.010,z));axis=b-a;cylinder('Rare Ore Extractor short stem mount '+str(i),(a+b)/2,.027,axis.length,alloy,axis);supports.append(dict(body_point=list(q),body_interior=list(a),stem_point=[x,y,z]))
    q,n=surface(-.56,.20);toe=Vector((-.56,q.y-.020,.205));lathe('Rare Ore Extractor short red copper banded upright',[(.025,.057),(.075,.057),(.075,.066),(.095,.066),(.095,.057),(.185,.057),(.185,.066),(.205,.066),(.205,.057),(.315,.057),(.315,.066),(.335,.066),(.335,.057),(.385,.057)],copper,(-.56,q.y-.020,0))
    toe_contact=list(q-n*.012)
    hit,q,n,_=body.ray_cast(Vector((.12,.12,3)),Vector((0,0,-1)));assert hit;dent=dict(point=list(q),normal=list(n));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.03,location=q+n*.025);boolean(body,bpy.context.object,'Actual tiny service dent')
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/127';root_object['footprint']=[3,3];root_object['local_forward']='-Y';root_object['local_up']='+Z'
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


    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/127',key='AR21',name='Rare Ore Extractor',culture='artemian',footprint=[3,3],definition_class=21,construction_updates=40,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_rare_ore_extractor.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},upper_ports=upper_ports,lower_port=lower_port,stem_mounts=supports,frame_centre=[x,y],toe_contact=toe_contact,physical_dent=dent,interpretation=['Own low scalloped green shell,raised tapered hood,2upper darkpoints,1lower copper fitting,leftpale opencapsule/brasscore/straightstem andshortredcopper upright govern anatomy.','Hidden mounts/backside/sections andcell-relative dimensions authored;two brasscore collars interpret source highlights. No own operating overlays;PB21/ST24 isTerran functionalcontext,not Artemian motion.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/ar21-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_RARE_ORE_EXTRACTOR_AUTHORED',triangles,len(meshes),len(created),flush=True)



if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
