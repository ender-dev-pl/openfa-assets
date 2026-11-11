"""Author AR14 Arms Forge from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/arms-forge';maps=root/'sources/materials/artemian/arms-forge';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2601401);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2601405);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.29,.43,.36)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.38,.45,.46)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.55+.05*math.cos(11*u+3*v),.24,.10,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('copper-fitting-colour',red)]:
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
    alloy=material('Used Artemian muted green alloy',(.29,.43,.36),'muted-green-alloy-colour');exposed=material('Worn exposed alloy edges',(.38,.45,.46),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour');redmat=material('Copper front inset and sleeves',(.55,.24,.10),'copper-fitting-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    controls=[(.025,1.08,.90),(.065,1.12,.94),(.25,1.10,.92),(.29,1.04,.87),(.32,.98,.81),(.36,.96,.80),(.38,.94,.78),(.65,.77,.65),(.69,.72,.61),(.72,.68,.57),(.76,.66,.55),(.99,.50,.44),(1.03,.43,.38),(1.06,.39,.34),(1.10,.34,.30),(1.22,.29,.25),(1.34,.18,.16),(1.37,.11,.10),(1.383,.07,.06),(1.39,.02,.02)];profile=[]
    for a,b in zip(controls,controls[1:]):
        for step in range(3):t=step/3;profile.append(tuple(x+(y-x)*t for x,y in zip(a,b)))
    profile.append(controls[-1]);n=128;verts=[];faces=[]
    for z,rx,ry in profile:
        for i in range(n):
            a=i*math.tau/n;x=rx*math.cos(a)-.38*z/1.39;y=ry*math.sin(a)-.15*z/1.39;dent=.003*math.exp(-((x+.30)/.12)**2-((y-.20)/.12)**2) if z>.4 else 0;verts.append((x,y,z-dent))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);body=solid('Arms Forge continuous tiered shell and boss',verts,faces,alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    for face in body.data.polygons:
        z=sum(body.data.vertices[i].co.z for i in face.vertices)/len(face.vertices)
        if any(low<z<high for low,high in [(.31,.35),(.71,.75),(1.05,1.09)]):face.material_index=1
    def cube(name,centre,size,mat,normal=None):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        if normal is not None:o.rotation_euler=normal.to_track_quat('Z','Y').to_euler()
        o.data.materials.append(mat);mod=o.modifiers.new('Small worn hardware corners','BEVEL');mod.width=min(size)*.10;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    outer=[(-.05,.46),(-.10,.56),(-.10,1.55),(-.05,1.64),(0,1.70),(.05,1.64),(.10,1.55),(.10,.56),(.05,.46),(0,.42)]
    inner=[(-.029,.48),(-.072,.57),(-.072,1.54),(-.029,1.62),(0,1.66),(.029,1.62),(.072,1.54),(.072,.57),(.029,.48),(0,.455)]
    count=len(outer);verts=[(-.65+1.5*x,-.76+y,z) for y in [-.0275,.0275] for contour in [outer,inner] for x,z in contour];faces=[]
    for i in range(count):
        j=(i+1)%count;faces.extend([(i,j,count+j,count+i),(2*count+i,3*count+i,3*count+j,2*count+j),(i,2*count+i,2*count+j,j),(count+i,count+j,3*count+j,3*count+i)])
    frame=solid('Arms Forge open silver capsule frame',verts,faces,exposed);bpy.context.view_layer.objects.active=frame;mod=frame.modifiers.new('Worn frame edge radii','BEVEL');mod.width=.003;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    cube('Arms Forge central gold bar',(-.65,-.76,1.055),(.055,.040,1.23),warm);cube('Arms Forge short gold crosspiece',(-.65,-.76,1.05),(.110,.046,.048),warm)
    cube('Arms Forge silver support stem',(-.65,-.76,.33),(.045,.055,.28),exposed);cube('Arms Forge silver foot crossbar',(-.65,-.76,.205),(.21,.16,.05),exposed)
    for i,x in enumerate([-.73,-.65,-.57]):cube('Arms Forge silver foot prong '+str(i),(x,-.76,.115),(.028,.18,.18),exposed)
    bpy.context.view_layer.update()
    shoulder_ports=[]
    # Source/concept pairs occupy the right flank; the lower row lies farther
    # around that flank. Angles are authored, not recovered metric measurements.
    for level,(z,angles) in enumerate([(.83,[-56,-38]),(.49,[-41,-23])]):
        centre=Vector((-.38*z/1.39,-.15*z/1.39,z))
        for i,angle in enumerate(angles):
            direction=Vector((math.cos(math.radians(angle)),math.sin(math.radians(angle)),0))
            bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(centre+direction*3,-direction);assert hit
            cut=cube('Temporary shallow shoulder opening',point-normal*.005,(.100,.075,.040),alloy,normal)
            bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Stable opening faces','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
            mod=body.modifiers.new('Recessed shoulder opening '+str(level)+' '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
            cube('Arms Forge dark shoulder inset '+str(level)+' '+str(i),point-normal*.023,(.090,.065,.006),dark,normal)
            shoulder_ports.append(dict(level=level,index=i,angle_deg=angle,point=list(point),normal=list(normal)))
    def disk(name,point,normal,radius,depth,mat):
        bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=radius,depth=depth,location=point);o=bpy.context.object;o.name=name;o.rotation_euler=normal.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small worn inset borders','BEVEL');mod.width=.002;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    for i,x in enumerate([-.18,.18]):
        hit,point,normal,_=body.ray_cast(Vector((x,-3,.15)),Vector((0,1,0)));assert hit;disk('Arms Forge front copper rim '+str(i),point+normal*.001,normal,.075,.018,exposed);disk('Arms Forge front copper face '+str(i),point+normal*.012,normal,.058,.014,redmat)
    for i,(x,y) in enumerate([(.55,.10),(-.45,.15),(.12,.50)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        for m in [alloy,exposed,dark]:cut.data.materials.append(m)
        for f in cut.data.polygons:f.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Stable small chip faces','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Real small alloy chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    bpy.context.view_layer.update();hit,dent_point,dent_normal,_=body.ray_cast(Vector((-.25,.12,2)),Vector((0,0,-1)));assert hit
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.035,location=dent_point+dent_normal*.029);cut=bpy.context.object
    for m in [alloy,exposed,dark]:cut.data.materials.append(m)
    for f in cut.data.polygons:f.material_index=0
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Real shallow shoulder dent','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/120';root_object['footprint']=[3,3];root_object['local_forward']='-Y';root_object['local_up']='+Z'
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
                    p=o.data.vertices[o.data.loops[index].vertex_index].co;values.append(((math.atan2(p.y+.15*p.z/1.39,p.x+.38*p.z/1.39)/math.tau+.5),p.z/1.42))
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
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/120',key='AR14',name='Arms Forge',culture='artemian',footprint=[3,3],definition_class=7,construction_updates=36,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_arms_forge.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},physical_dent=dict(point=list(dent_point),normal=list(dent_normal)),shoulder_ports=shoulder_ports,interpretation=['Green tiered shell/upper boss,pale shoulder accents,open silver capsule frame/gold bar and crosspiece,rooted prong support,four small dark points and two copper front insets follow actual source/concept.','Hidden factory engineering,frame/tier/hardware sections and metric dimensions remain authored or unknown;PB07 generic turntable not Artemian operation.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar14-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_ARMS_FORGE_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
