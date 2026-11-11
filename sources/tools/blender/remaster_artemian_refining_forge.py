"""Author AR23 Refining Forge from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/refining-forge';maps=root/'sources/materials/artemian/refining-forge';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2602301);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2602305);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
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


    def solid(name,verts,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();assert not mesh.validate();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    def cylinder(name,point,radius,depth,mat,axis=(0,0,1)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=point);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Used small rounded edge','BEVEL');mod.width=.002;mod.segments=3;apply(o,mod);return o
    def box(name,centre,size,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        o.data.materials.append(mat);mod=o.modifiers.new('Rounded used hardware corner','BEVEL');mod.width=.004;mod.segments=3;apply(o,mod);return o
    def lathe(name,profile,mat,point,normal):
        n=48;rotation=Vector(normal).to_track_quat('Z','Y');verts=[Vector(point)+rotation@Vector((rr*math.cos(i*math.tau/n),rr*math.sin(i*math.tau/n),z)) for z,rr in profile for i in range(n)];faces=[]
        for j in range(len(profile)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);return solid(name,verts,faces,mat)
    controls=[(0,.70),(.05,.94),(.14,1),(.29,.96),(.34,.84),(.39,.70),(.48,.67),(.72,.57),(.85,.43),(.94,.27),(1,.05)]
    def radius(t):
        zs=[q[0] for q in controls];rs=[q[1] for q in controls];slopes=[(b-a)/(y-x) for x,y,a,b in zip(zs,zs[1:],rs,rs[1:])];tangents=[slopes[0]]
        for a,b in zip(slopes,slopes[1:]):tangents.append(0 if a*b<=0 else 2*a*b/(a+b))
        tangents.append(slopes[-1]);i=min(len(zs)-2,next((j for j in range(len(zs)-1) if t<=zs[j+1]),len(zs)-2));h=zs[i+1]-zs[i];u=(t-zs[i])/h
        return (2*u**3-3*u**2+1)*rs[i]+(u**3-2*u**2+u)*h*tangents[i]+(-2*u**3+3*u**2)*rs[i+1]+(u**3-u**2)*h*tangents[i+1]
    specs=[dict(key='front',centre=[.26,-.42],radius=.55,height=.82),dict(key='right',centre=[.68,.22],radius=.47,height=.82),dict(key='rear',centre=[-.20,.30],radius=.48,height=1.02)];shells={}
    for spec in specs:
        x,y=spec['centre'];h=spec['height'];rr=spec['radius'];count=80;rings=34;verts=[];faces=[]
        for j in range(rings):
            t=j/(rings-1);z=.025+h*t;rad=rr*radius(t)
            for i in range(count):a=i*math.tau/count;verts.append((x+rad*math.cos(a),y+.86*rad*math.sin(a),z))
        for j in range(rings-1):
            for i in range(count):faces.append((j*count+i,j*count+(i+1)%count,(j+1)*count+(i+1)%count,(j+1)*count+i))
        faces.extend([tuple(reversed(range(count))),tuple((rings-1)*count+i for i in range(count))]);shells[spec['key']]=solid('Refining Forge rounded '+spec['key']+' shell chamber',verts,faces,alloy)
    wing=ellipsoid('Refining Forge low rounded left wing',(-.45,.05,.18),(1.0,.50,.18));wing.data.materials.append(alloy)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.475));cut=bpy.context.object
    for v in cut.data.vertices:v.co=(v.co.x*4,v.co.y*4,v.co.z)
    boolean(wing,cut,'Closed shared ground underside .025')
    def surface(obj,x,z):
        bpy.context.view_layer.update();hit,q,n,_=obj.ray_cast(obj.matrix_world.inverted()@Vector((x,-3,z)),Vector((0,1,0)));assert hit,(obj.name,x,z);return obj.matrix_world@q,(obj.matrix_world.to_3x3()@n).normalized()
    dark_ports=[];brass_ports=[]
    for spec in specs:
        key=spec['key'];body=shells[key];cx,cy=spec['centre'];positions=[(cx-.10,.52),(cx+.10,.52)] if key!='rear' else [(cx-.05,.77)]
        for index,(px,z) in enumerate(positions):
            q,n=surface(body,px,z);dark_ports.append(dict(chamber=key,index=index,point=list(q),normal=list(n)));cut=lathe('Temporary actual dark chamber recess',[(-.020,.032),(.07,.032)],alloy,q,n);boolean(body,cut,'Actual dark chamber recess');lathe('Refining Forge '+key+' dark point '+str(index),[(-.023,.029),(-.011,.029)],dark,q,n)
        if key!='rear':
            q,n=surface(body,cx+(.14 if key=='right' else 0),.17);brass_ports.append(dict(chamber=key,point=list(q),normal=list(n)));cut=lathe('Temporary actual lower brass socket',[(-.025,.060),(.08,.060)],alloy,q,n);boolean(body,cut,'Actual lower brass socket');lathe('Refining Forge '+key+' lower brass fitting',[(-.028,.056),(.006,.056)],brass,q,n)
    x,y=-.48,-.43;outer0=[(-.10,.87),(-.14,.94),(-.14,1.69),(-.10,1.77),(0,1.85),(.10,1.77),(.14,1.69),(.14,.94),(.10,.87),(0,.85)];inner0=[(-.050,.96),(-.083,1.00),(-.083,1.65),(-.055,1.70),(0,1.74),(.055,1.70),(.083,1.65),(.083,1.00),(.050,.96),(0,.95)];outer=[(u*.9,.72+(z-.85)*.96) for u,z in outer0];inner=[(u*.9,.72+(z-.85)*.96) for u,z in inner0];count=len(outer);verts=[(x+(u-dy)/math.sqrt(2),y+(u+dy)/math.sqrt(2),z) for dy in [-.060,.060] for contour in [outer,inner] for u,z in contour];faces=[]
    for j in range(count):
        k=(j+1)%count;faces.extend([(j,k,count+k,count+j),(2*count+j,3*count+j,3*count+k,2*count+k),(j,2*count+j,2*count+k,k),(count+j,count+k,3*count+k,3*count+j)])
    frame=solid('Refining Forge open pale capsule frame',verts,faces,exposed);mod=frame.modifiers.new('Rounded pale frame corners','BEVEL');mod.width=.005;mod.segments=3;apply(frame,mod)
    cylinder('Refining Forge continuous brass frame core',(x,y,1.2025),.034,.795,brass)
    for i,z in enumerate([1.05,1.35]):cylinder('Refining Forge brass core collar '+str(i),(x,y,z),.048,.025,brass)
    box('Refining Forge straight pale stem',(x,y,.40),(.065,.080,.75),exposed)
    for i,z in enumerate([.15,.31]):box('Refining Forge small stem joint '+str(i),(x,y,z),(.073,.088,.022),alloy)
    uprights=[]
    for i,(px,top) in enumerate([(-.90,.50),(-.68,.42)]):
        q,n=surface(wing,px,.14);py=q.y-.035;box('Refining Forge red copper pedestal '+str(i),(px,py,.125),(.11,.12,.20),copper);cylinder('Refining Forge unequal brass pin '+str(i),(px,py,(.20+top)/2),.022,top-.20,brass);uprights.append(dict(body_point=list(q),normal=list(n),rod_point=[px,py,.212],top=top))
    body=shells['rear'];bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(Vector((-.10,.36,3)),Vector((0,0,-1)));assert hit;dent=dict(chamber='rear',point=list(q),normal=list(n));bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.03,location=q+n*.025);boolean(body,bpy.context.object,'Actual small service dent')
    assembly_contacts=[dict(a='front',b='right',point=[.47,-.10,.12]),dict(a='rear',b='front',point=[.0208,-.0456,.12]),dict(a='wing',b='front',point=[-.15,-.23,.12]),dict(a='wing',b='rear',point=[-.30,.12,.12])]
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/129';root_object['footprint']=[3,3];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o in shells.values() or o==wing:
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



    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/129',key='AR23',name='Refining Forge',culture='artemian',footprint=[3,3],definition_class=255,construction_updates=38,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_refining_forge.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},chambers=specs,dark_ports=dark_ports,brass_ports=brass_ports,frame_centre=[x,y],uprights=uprights,assembly_contacts=assembly_contacts,physical_dent=dent,interpretation=['Ownsource governs3joinedgreenroundedchambers/leftwing,2darkfrontpairs/2lowerbrassfittings/1reardarkpoint,tallpaleopencapsule/brasscore/stem and2redcopperpedestals/unequalbrasspins.','Source roundedcontours override flatterconcepttops/feet. Hidden sections/contacts andcell-relative dimensions authored. Uniqueclass255/noTerraequivalent;no inventedPB/ST orownoperating phases.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/ar23-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_REFINING_FORGE_AUTHORED',triangles,len(meshes),len(created),flush=True)



if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
