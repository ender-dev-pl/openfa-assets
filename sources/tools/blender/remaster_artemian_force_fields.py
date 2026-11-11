"""Author AR19 Force Fields from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/force-fields';maps=root/'sources/materials/artemian/force-fields';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2601901);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2601905);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.29,.43,.36)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.60,.67,.70)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.55+.05*math.cos(11*u+3*v),.24,.10,1])
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
    alloy=material('Used Artemian muted green alloy',(.29,.43,.36),'muted-green-alloy-colour');exposed=material('Pale oxidized alloy face and edge lips',(.60,.67,.70),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber cores and tip caps - steady authored emission',(.46,.22,.035),'amber-fitting-colour',emission=.8);redmat=material('Dull copper centre inset',(.55,.24,.10),'copper-fitting-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    bpy.ops.mesh.primitive_uv_sphere_add(segments=96,ring_count=48,radius=1,location=(0,0,.315));body=bpy.context.object;body.name='Force Fields low rounded green housing'
    for v in body.data.vertices:v.co=(v.co.x*.90,v.co.y*.45,v.co.z*.285)
    body.data.materials.append(alloy)
    def boolean(obj,cut,label,operation='DIFFERENCE'):
        bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(label,'BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,-.445));cut=bpy.context.object
    for v in cut.data.vertices:v.co=(v.co.x*3,v.co.y*3,v.co.z)
    boolean(body,cut,'Closed flat underside at ground .055')
    bpy.ops.mesh.primitive_cube_add(size=1,location=(1.55,0,.315));cut=bpy.context.object
    for v in cut.data.vertices:v.co=(v.co.x*2,v.co.y*3,v.co.z*3)
    boolean(body,cut,'Flat right end for source broad pale closure')
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=64):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small used sensor edges','BEVEL');mod.width=min(.003,depth*.10);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    def lathe(name,profile,mat,n=96,origin=(0,0,0),axis=(0,0,1),closed_profile=False):
        origin=Vector(origin);rotation=Vector(axis).normalized().to_track_quat('Z','Y');verts=[];faces=[]
        for z,r in profile:
            for i in range(n):
                a=i*math.tau/n;verts.append(origin+rotation@Vector((r*math.cos(a),r*math.sin(a),z)))
        for j in range(len(profile)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        if closed_profile:
            for i in range(n):faces.append(((len(profile)-1)*n+i,(len(profile)-1)*n+(i+1)%n,(i+1)%n,i))
        else:faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))])
        return solid(name,verts,faces,mat)
    pillars=[(-.52,-.22),(-.28,.20)];supports=[]
    outer=[(-.12,.60),(-.18,.67),(-.18,1.40),(-.15,1.50),(-.085,1.60),(-.065,1.80),(.065,1.80),(.085,1.60),(.15,1.50),(.18,1.40),(.18,.67),(.12,.60)]
    inner=[(-.075,.70),(-.11,.74),(-.11,1.30),(-.11,1.36),(-.075,1.42),(-.03,1.43),(.03,1.43),(.075,1.42),(.11,1.36),(.11,1.30),(.11,.74),(.075,.70)]
    def rounded_contour(points):
        # Two corner-cutting passes stay inside the original contour; unlike
        # an interpolating spline they cannot backtrack along uneven segments.
        for iteration in range(2):
            out=[]
            for a,b in zip(points,points[1:]+points[:1]):
                out.extend([tuple(.75*x+.25*y for x,y in zip(a,b)),tuple(.25*x+.75*y for x,y in zip(a,b))])
            points=out
        return points
    outer=rounded_contour(outer);inner=rounded_contour(inner)
    for i,(x,y) in enumerate(pillars):
        bpy.context.view_layer.update();hit,roof,_,_=body.ray_cast(Vector((x,y,3))-body.location,Vector((0,0,-1)));assert hit;roof=body.matrix_world@roof;bottom=roof.z-.025;supports.append(dict(x=x,y=y,roof=list(roof)))
        cylinder('Force Fields seated capsule stalk '+str(i),(x,y,(bottom+.655)/2),.033,.655-bottom,alloy)
        count=len(outer);verts=[(x+u,y+dy,z) for dy in [-.045,.045] for contour in [outer,inner] for u,z in contour];faces=[]
        for j in range(count):
            k=(j+1)%count;faces.extend([(j,k,count+k,count+j),(2*count+j,3*count+j,3*count+k,2*count+k),(j,2*count+j,2*count+k,k),(count+j,count+k,3*count+k,3*count+j)])
        frame=solid('Force Fields open green capsule frame '+str(i),verts,faces,alloy);frame.data.materials.append(exposed);bpy.context.view_layer.objects.active=frame;mod=frame.modifiers.new('Restrained worn open-frame edge lips','BEVEL');mod.width=.003;mod.segments=3;mod.material=1;mod.limit_method='ANGLE';mod.angle_limit=.35;bpy.ops.object.modifier_apply(modifier=mod.name)
        cylinder('Force Fields central segment support '+str(i),(x,y,1.09),.015,.87,exposed,vertices=32)
        for j,z in enumerate([.81,1.06,1.31]):cylinder('Force Fields amber segment '+str(i)+' '+str(j),(x,y,z),.057,.18,warm,vertices=48)
        cylinder('Force Fields gold tip cap '+str(i),(x,y,1.84),.058,.11,warm,vertices=48)
    bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((3,0,.315))-body.location,Vector((-1,0,0)));assert hit;point=body.matrix_world@point
    large_port=dict(point=list(point),normal=list(normal));cut=lathe('Temporary true copper centre recess',[(-.035,.078),(.08,.078)],alloy,64,point,normal);boolean(body,cut,'True blind copper centre recess')
    count=96;vertices=[];faces=[];section=(1-(.55/.90)**2)**.5
    for t,kind in [(-.12,'outer'),(.008,'outer'),(.015,'bevel'),(.015,'inner'),(-.12,'inner')]:
        for j in range(count):
            a=j*math.tau/count;ry,rz=(.073,.073) if kind=='inner' else (.45*section,.285*section)
            if kind=='bevel':ry*=.98;rz*=.98
            vertices.append(point+Vector((t,ry*math.cos(a),rz*math.sin(a))))
    for row in range(5):
        for j in range(count):faces.append((row*count+j,row*count+(j+1)%count,((row+1)%5)*count+(j+1)%count,((row+1)%5)*count+j))
    solid('Force Fields broad pale circular face',vertices,faces,exposed)
    lathe('Force Fields recessed copper centre',[(-.038,.070),(.005,.070)],redmat,64,point,normal)
    small_ports=[]
    for i,z in enumerate([.45,.26]):
        hit,q,n,_=body.ray_cast(Vector((-.28,-3,z))-body.location,Vector((0,1,0)));assert hit;q=body.matrix_world@q;small_ports.append(dict(point=list(q),normal=list(n)))
        cut=lathe('Temporary small front recess',[(-.018,.028),(.05,.028)],alloy,48,q,n);boolean(body,cut,'True small dark front recess '+str(i))
        lathe('Force Fields small dark front point '+str(i),[(-.021,.026),(-.014,.026)],dark,48,q,n)
        lathe('Force Fields small front point rim '+str(i),[(-.008,.039),(.008,.039),(.008,.029),(-.008,.029)],exposed,48,q,n,closed_profile=True)
    def box(name,centre,size,mat,rounded=False):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);obj=bpy.context.object;obj.name=name
        for vertex in obj.data.vertices:vertex.co=(vertex.co.x*size[0],vertex.co.y*size[1],vertex.co.z*size[2])
        obj.data.materials.append(mat)
        if rounded:
            mod=obj.modifiers.new('Small worn rail edges','BEVEL');mod.width=.004;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
        return obj
    surface_points=[]
    for z in [.20,.40]:
        hit,q,n,_=body.ray_cast(Vector((-.50,-3,z))-body.location,Vector((0,1,0)));assert hit;surface_points.append(body.matrix_world@q)
    rail_y=min(q.y for q in surface_points)-.035;rail_centre=Vector((-.50,rail_y,.295));box('Force Fields pale front vertical rail',rail_centre,(.040,.040,.43),exposed,True);brackets=[]
    for i,q in enumerate(surface_points):
        front=rail_y-.005;back=q.y+.012;box('Force Fields hidden front rail bracket '+str(i),(-.50,(front+back)/2,q.z),(.030,back-front,.032),alloy);brackets.append(dict(body_point=list(q),rail_point=[-.50,rail_y+.005,q.z]))
    rail=dict(centre=list(rail_centre),brackets=brackets)
    hit,q,n,_=body.ray_cast(Vector((-.25,-3,.14))-body.location,Vector((0,1,0)));assert hit;q=body.matrix_world@q;toe=Vector((-.25,q.y-.012,.1275));cylinder('Force Fields short lower toe',toe,.032,.165,alloy,vertices=48)
    for i,(x,y) in enumerate([(-.05,.08),(.20,-.03),(.45,.04)]):
        bpy.context.view_layer.update();hit,q,n,_=body.ray_cast(Vector((x,y,3))-body.location,Vector((0,0,-1)));assert hit;q=body.matrix_world@q;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.005,location=q+n*.0015);boolean(body,bpy.context.object,'Actual small housing chip '+str(i))
    hit,q,n,_=body.ray_cast(Vector((.12,-.20,3))-body.location,Vector((0,0,-1)));assert hit;dent_point=body.matrix_world@q;dent_normal=n;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.03,location=dent_point+n*.025);boolean(body,bpy.context.object,'Actual shallow housing dent')
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/125';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
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
                    p=o.matrix_world@o.data.vertices[o.data.loops[index].vertex_index].co;values.append(((math.atan2(p.y,p.x)/math.tau+.5),(p.z-.055)/.55))
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/125',key='AR19',name='Force Fields',culture='artemian',footprint=[2,2],definition_class=10,construction_updates=30,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_force_fields.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},pillars=supports,large_port=large_port,small_ports=small_ports,front_rail=rail,toe=list(toe),physical_dent=dict(point=list(dent_point),normal=list(dent_normal)),optical_interpretation=dict(emission_material='Amber cores and tip caps - steady authored emission',strength=.8,scope='Steady authored optical treatment of bright amber source cores/caps;no recovered Artemian pulse or gameplay state calibration.'),interpretation=['Own source has2upright open green bottle capsules with3amber segments each and2gold caps,low rounded green housing,broad pale face/copper centre,front rail/two small points/lower toe.','No own operating overlays;generic PB10/ST23 glow/rotation does not establish Artemian movement or pulse. Hidden engineering and metric dimensions authored;steady warm emission is explicitly an optical interpretation.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar19-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_FORCE_FIELDS_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
