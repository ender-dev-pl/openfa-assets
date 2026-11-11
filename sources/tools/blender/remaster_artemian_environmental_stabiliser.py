"""Author AR02 Environmental Stabiliser from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/environmental-stabiliser';maps=root/'sources/materials/artemian/environmental-stabiliser';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2600201);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2600205);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cloud=.025*math.sin(9*u+2*math.sin(7*v))+.020*math.cos(13*v+math.sin(11*u));grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=max(0,math.sin(17*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.24,.39,.31)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.46,.52,.56)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.46+.10*math.sin(5*u+7*v),.22+.05*math.cos(7*u-3*v),.035,1]);red.extend([.62+.05*math.cos(11*u+3*v),.22,.075,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('orange-monitor-colour',red)]:
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
    alloy=material('Used Artemian muted green alloy',(.24,.39,.31),'muted-green-alloy-colour');exposed=material('Worn exposed alloy edges',(.46,.52,.56),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour');redmat=material('Orange monitoring inset',(.62,.22,.075),'orange-monitor-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    controls=[(-1.30,.025,.04),(-1.18,.12,.12),(-.95,.21,.23),(-.65,.31,.40),(-.30,.43,.60),(.10,.55,.78),(.45,.61,.91),(.70,.58,.90),(.82,.46,.76),(.91,.20,.45),(.93,.015,.24)]
    def section(y):
        j=next((i for i in range(len(controls)-1) if controls[i][0]<=y<=controls[i+1][0]),len(controls)-2);t=(y-controls[j][0])/(controls[j+1][0]-controls[j][0]);result=[]
        for k in [1,2]:
            a=controls[max(0,j-1)][k];b=controls[j][k];c=controls[j+1][k];d=controls[min(len(controls)-1,j+2)][k];result.append(max(.012,.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
        return result
    rows=[]
    for j in range(len(controls)-1):
        for k in range(4):rows.append(controls[j][0]+(controls[j+1][0]-controls[j][0])*k/4)
    rows.append(controls[-1][0]);n=48;vertices=[];faces=[]
    for y in rows:
        rx,h=section(y)
        for i in range(n+1):
            a=i*math.pi/n;x=rx*math.cos(a);z=.02+h*math.sin(a);dent=.0035*math.exp(-((x-.20)/.12)**2-((y-.25)/.20)**2)+.0025*math.exp(-((x+.20)/.12)**2-((y-.45)/.15)**2);z-=dent*math.sin(a);vertices.append((x,y,z))
    width=n+1
    for j in range(len(rows)-1):
        for i in range(width):faces.append((j*width+i,j*width+(i+1)%width,(j+1)*width+(i+1)%width,(j+1)*width+i))
    faces += [tuple(reversed(range(width))),tuple((len(rows)-1)*width+i for i in range(width))]
    body=solid('Environmental Stabiliser tapered green metal shell',vertices,faces,alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    for band,y in enumerate([-.62,-.10,.40]):
        vertices=[];faces=[];count=32
        for i in range(count+1):
            a=i*math.pi/count
            for yy,offset in [(y-.022,-.008),(y-.022,.015),(y+.022,.015),(y+.022,-.008)]:
                rx,h=section(yy);vertices.append(((rx+offset)*math.cos(a),yy,.02+(h+offset)*math.sin(a)))
        for i in range(count):
            for k in range(4):faces.append((i*4+k,i*4+(k+1)%4,(i+1)*4+(k+1)%4,(i+1)*4+k))
        faces += [(3,2,1,0),tuple(count*4+k for k in range(4))];solid('Environmental Stabiliser silver arch '+str(band),vertices,faces,exposed)
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small worn edge bevel','BEVEL');mod.width=min(.005,depth*.12);mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    bpy.context.view_layer.update()
    for i,y in enumerate([-.98,-.76]):
        _,h=section(y);z=.02+h*.64;hit,point,normal,_=body.ray_cast(Vector((3,y,z)),Vector((-1,0,0)));assert hit
        cylinder('Environmental Stabiliser dark front spot '+str(i),point+normal*.004,.043,.014,dark,axis=normal)
        # Tiny annular pale edge around the source dark spot.
        ring=cylinder('Environmental Stabiliser small spot rim '+str(i),point+normal*.002,.051,.012,exposed,axis=normal);bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=.044,depth=.10,location=point);cut=bpy.context.object;cut.rotation_euler=normal.to_track_quat('Z','Y').to_euler();cut.data.materials.append(exposed);bpy.context.view_layer.objects.active=ring;mod=ring.modifiers.new('Clear small circular rim','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    hit,point,normal,_=body.ray_cast(Vector((3,.56,.40)),Vector((-1,0,0)));assert hit
    cylinder('Environmental Stabiliser orange monitoring inset',point+normal*.009,.103,.024,redmat,axis=normal)
    main=cylinder('Environmental Stabiliser rear silver upright',(-.10,.63,(.83+1.50)/2),.035,1.50-.83,exposed)
    cylinder('Environmental Stabiliser small amber upright cap',(-.10,.63,1.514),.040,.055,warm)
    curve=bpy.data.curves.new('Environmental Stabiliser continuous return pipe','CURVE');curve.dimensions='3D';curve.resolution_u=10;curve.bevel_depth=.024;curve.bevel_resolution=2;curve.use_fill_caps=True;spline=curve.splines.new('BEZIER');points=[(-.10,.63,1.34),(.035,.63,1.34),(.11,.63,1.26),(.11,.63,.86)];spline.bezier_points.add(len(points)-1)
    for p,co in zip(spline.bezier_points,points):p.co=co;p.handle_left_type='AUTO';p.handle_right_type='AUTO'
    o=bpy.data.objects.new('Environmental Stabiliser continuous return pipe',curve);bpy.context.collection.objects.link(o);curve.materials.append(exposed);bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o;bpy.ops.object.convert(target='MESH')
    # A few small physical finish chips,not dense panel divisions.
    for i,(x,y) in enumerate([(.20,-.25),(-.20,.24),(.35,.45)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        for m in [alloy,exposed,dark]:cut.data.materials.append(m)
        for p in cut.data.polygons:p.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before small alloy chip','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Actual small finish chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/108';root_object['footprint']=[3,3];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    for o in meshes:
        o.parent=root_object;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o==body:
            uv=o.data.uv_layers.active
            for loop in o.data.loops:
                p=o.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(p.x/1.40+p.y*.07+.5,p.y/2.50+p.z*.18+.5)
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/108',key='AR02',name='Environmental Stabiliser',culture='artemian',footprint=[3,3],definition_class=35,construction_updates=26,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_environmental_stabiliser.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Tapered green metal shell,three silver arches,two dark front spots,one orange flank inset and connected rear capped upright/return bend follow actual source and reviewed concept.','Exact pipe/body sections,hidden engineering and operating processes remain interpreted or unknown. No AR02 operation clip inferred from catalogue reveal or generic PB35 turntable.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar02-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_ENVIRONMENTAL_STABILISER_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
