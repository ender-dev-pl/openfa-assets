"""Author MN20 Motion Units from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/motion-units';maps=root/'sources/materials/mauna/motion-units';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2612020);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-module-colour','brass-colour']}
    # Deterministic sparse roughcast spalls, patina streaks and fine pores.
    # These are authored surface maps,not borrowed legacy pixels.
    grids={n:[[rng.uniform(-1,1) for _ in range(n)] for _ in range(n)] for n in [5,9,19]}
    def cast_noise(n,u,v):
        x=u*n;y=v*n;ix=int(x);iy=int(y);a=x-ix;b=y-iy;a=a*a*(3-2*a);b=b*b*(3-2*b);g=grids[n]
        return (g[iy%n][ix%n]*(1-a)+g[iy%n][(ix+1)%n]*a)*(1-b)+(g[(iy+1)%n][ix%n]*(1-a)+g[(iy+1)%n][(ix+1)%n]*a)*b
    speckles={}
    for i in range(85):
        cx=rng.randrange(size);cy=rng.randrange(size);radius=rng.randrange(1,4)
        for dy in range(-radius,radius+1):
            for dx in range(-radius,radius+1):
                if dx*dx+dy*dy<radius*radius*rng.uniform(.65,1.1):speckles[((cx+dx)%size,(cy+dy)%size)]=rng.uniform(.010,.035)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=.065*cast_noise(5,u,v)+.018*cast_noise(19,u,v);grain=rng.uniform(-.025,.025);stain=max(0,cast_noise(9,u,v))*.10;aggregate=speckles.get((x,y),0);pore=.15 if rng.random()<.035 else 0;dust=.07*max(0,1-v*5)
            concrete_delta=cloud+grain+aggregate-stain-pore-dust
            buffers['cast-concrete-colour'].extend([max(.01,c+concrete_delta) for c in (.29,.34,.41)]+[1])
            scratch=.17 if ((x*7+y*31)%991<2 and rng.random()<.7) else 0
            redbase=(.26,.29,.32) if pore and grain>.007 else (.38,.018,.012)
            buffers['marking-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in redbase]+[1])
            buffers['concrete-orm'].extend([1,min(.98,max(.68,.85+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.76,max(.32,.54+grain+stain)),.50,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.035,.035),.5+rng.uniform(-.035,.035),1,1])
            buffers['pale-module-colour'].extend([max(.01,c+concrete_delta*.8) for c in (.40,.45,.51)]+[1])
            buffers['brass-colour'].extend([max(.01,c+cloud*.4+grain*.4-stain*.6+scratch*.2) for c in (.60,.44,.18)]+[1])
    images={}
    for name,pixels in buffers.items():
        im=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name.endswith('-orm') or name.endswith('-normal'):im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(pixels);path=maps/(name+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();path.write_bytes(clean_png(path.read_bytes()));im.pack();images[name]=im
    def material(name,colour=None,metal=False):
        m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Base Color'].default_value=(.012,.016,.020,1);p.inputs['Roughness'].default_value=.85
        if colour:
            tex=n.new('ShaderNodeTexImage');tex.image=images[colour];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);orm=n.new('ShaderNodeTexImage');orm.image=images['metal-orm' if metal else 'concrete-orm'];split=n.new('ShaderNodeSeparateColor');m.node_tree.links.new(orm.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic']);texn=n.new('ShaderNodeTexImage');texn.image=images['cast-service-normal'];normal=n.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.10 if metal else .45;m.node_tree.links.new(texn.outputs['Color'],normal.inputs['Color']);m.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        return m
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Pale Motion Units frame and mast','pale-module-colour');dark=material('Opaque Motion Units channels');dark.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.018,.023,.028,1)
    def apply(o,mod):bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=mod.name)
    def solid(name,verts,faces,mat):
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();assert not me.validate();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    def box(name,centre,size,mat,normal=None,bevel=.003):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        if normal is not None:
            normal=Vector(normal).normalized();v=(Vector((0,0,1))-normal*normal.z).normalized();u=v.cross(normal).normalized();o.rotation_euler=Matrix((u,v,normal)).transposed().to_euler()
        o.data.materials.append(mat)
        if bevel:
            mod=o.modifiers.new('Practical planar edge chamfer','BEVEL');mod.width=bevel;mod.segments=1;apply(o,mod)
        return o
    def cut(o,tool,label):
        mod=o.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=tool;apply(o,mod);bpy.data.objects.remove(tool,do_unlink=True)
    brass=material('Aged brass Motion Units fittings','brass-colour',True);red=material('Worn red Motion Units base band','marking-red-colour');contacts=[];fields=[];chips=[];prongs=[]
    def frustum(name,z0,z1,w0,w1,mat):
        vertices=[(x*w,y*w,z) for z,w in [(z0,w0/2),(z1,w1/2)] for x,y in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        return solid(name,vertices,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],mat)
    bottom=frustum('Motion Units grounded flared lower plinth',0,.16,1.56,1.40,concrete)
    base=frustum('Motion Units flared upper plinth',.14,.38,1.40,1.10,concrete)
    lower=box('Motion Units lower storey',(0,0,.765),(1.06,1.06,.81),concrete,bevel=.006)
    upper=box('Motion Units upper storey',(0,0,1.555),(1.06,1.06,.81),concrete,bevel=.006)
    mast=box('Motion Units supported lower mast',(0,0,2.3275),(.17,.14,.605),edge,bevel=.002)
    tip=frustum('Motion Units tapered upper mast',2.60,3.08,.145,.11,edge)
    contacts += [dict(object=base.name,support=bottom.name,point=[.3,.3,.15]),dict(object=lower.name,support=base.name,point=[.2,.2,.37]),dict(object=upper.name,support=lower.name,point=[.3,.3,1.16])]
    def blind(name,body,q,n,width,height,depth=.025,backmat=dark):
        q=Vector(q);n=Vector(n);cut(body,box('Temporary true blind field',q+n*.01,(width,height,(depth+.01)*2),concrete,n,0),'Actual blind service recess')
        backing=box(name,q-n*(depth+.004),(width-.006,height-.006,.014),backmat,n,.001);fields.append(dict(object=backing.name,body=body.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.008));return backing
    blind('Motion Units upper front brass field',upper,(0,-.53,1.57),(0,-1,0),.115,.33,.025,brass)
    for storey,z in [(lower,.79),(upper,1.57)]:
        for i,y in enumerate([-.26,.26]):blind('Motion Units right brass field '+str(z)+' '+str(i),storey,(.53,y,z),(1,0,0),.115,.33,.025,brass)
    for i,x in enumerate([-.25,.25]):
        back=blind('Motion Units lower front dark channel '+str(i),lower,(x,-.53,.76),(0,-1,0),.09,.59,.03)
        for j,z in enumerate([.74,.86]):
            marker=box('Motion Units channel brass marker '+str(i)+' '+str(j),(x,-.505,z),(.045,.055,.012),brass,(0,-1,0),.001)
            contacts.append(dict(object=marker.name,support=back.name,point=[x,-.500,z]))
    for i,z in enumerate([2.15,2.25,2.35]):blind('Motion Units mast brass marker '+str(i),mast,(0,-.07,z),(0,-1,0),.05,.045,.01,brass)
    for x in [-.503,.503]:
        for y in [-.503,.503]:
            rib=box('Motion Units structural corner '+str(x)+' '+str(y),(x,y,1.17),(.075,.075,1.62),edge,bevel=.003)
            contacts.append(dict(object=rib.name,support=lower.name,point=[x,y,.80]))
    ledge=box('Motion Units continuous middle ledge',(0,0,1.17),(1.10,1.10,.08),edge,bevel=.002)
    cut(ledge,box('Temporary middle ring hole',(0,0,1.17),(1.02,1.02,.20),edge,bevel=0),'Actual hollow middle ledge')
    for x,y in [(.525,0),(-.525,0),(0,.525),(0,-.525)]:contacts.append(dict(object=ledge.name,support=upper.name,point=[x,y,1.17]))
    cap=box('Motion Units shallow roof cap',(0,0,1.95),(1.10,1.10,.05),edge,bevel=.003)
    for x,y in [(.3,.3),(-.3,.3),(.3,-.3),(-.3,-.3)]:contacts.append(dict(object=cap.name,support=upper.name,point=[x,y,1.94]))
    roof=box('Motion Units low square mast seat',(0,0,2.00),(.43,.43,.09),edge,bevel=.003)
    contacts += [dict(object=roof.name,support=cap.name,point=[.15,.15,1.965]),dict(object=mast.name,support=roof.name,point=[0,0,2.035]),dict(object=tip.name,support=mast.name,point=[0,0,2.615])]
    for i,(a,b,support) in enumerate([((0,.04,2.54),(0,.60,3.05),mast),((0,.04,2.84),(0,.46,3.21),tip)]):
        a=Vector(a);b=Vector(b);v=b-a;o=box('Motion Units same-side brass prong '+str(i),(a+b)/2,(.04,.045,v.length),brass,bevel=0);o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
        q=a+v.normalized()*.006;contacts.append(dict(object=o.name,support=support.name,point=list(q)));prongs.append(dict(object=o.name,start=list(a),end=list(b),width=.04,thickness=.045))
    band=frustum('Motion Units continuous sloping red base band',.19,.28,1.362,1.250,red)
    tool=frustum('Temporary sloping band interior',.14,.33,1.3722222222,1.1357777778,red);cut(band,tool,'Actual hollow sloping red band')
    for x,y in [(.64,0),(-.64,0),(0,.64),(0,-.64)]:contacts.append(dict(object=band.name,support=base.name,point=[x,y,.235]))
    for obj,q,n in [(upper,Vector((-.35,-.53,1.73)),Vector((0,-1,0))),(lower,Vector((.53,.05,.66)),Vector((1,0,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.018,location=q+n*.012);cut(obj,bpy.context.object,'Actual shallow cast spall');chips.append(dict(body=obj.name,point=list(q),normal=list(n)))
    keep={o.name for o in [bottom,base,lower,upper,mast,tip]};part_batches={}
    for mat,label in [(edge,'four corners middle ledge roof cap and seat'),(brass,'five fields seven markers and two prongs'),(red,'one continuous sloping base band'),(dark,'two seated dark front channels')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]];assert objects
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Motion Units '+label;group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Motion Units '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/149';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z';placement['ground_level']=0;placement['preserve_ground_origin']=True
    bpy.context.view_layer.update()
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');uv=obj.data.uv_layers.active
        for face in obj.data.polygons:
            for index in face.loop_indices:
                q=obj.data.vertices[obj.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+.6)/1.2,q.z/3.3) if abs(face.normal.x)>.5 else ((q.x+.6)/1.2,q.z/3.3) if abs(face.normal.y)>.5 else ((q.x+.6)/1.2,(q.y+.6)/1.2)
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');apply(obj,mod);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.to_mesh(obj.data);bm.free()
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*a,**k):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    meta=dict(schema_version=1,issue=261,id='openfa:building/legacy/149',key='MN20',name='Motion Units',culture='mauna',footprint=[2,2],definition_class=22,construction_updates=66,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_motion_units.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=contacts,part_batches=part_batches,physical_chips=chips,roof_prongs=prongs,nonemissive=True,interpretation=['Own two-storey angular tower,two flared square plinths,red band,front and four right fields,roof mast and two same-side brass prongs govern anatomy.','Exact recess depths,hidden engineering,mast sections,short mark segmentation and cell-relative proportions are authored;generic PB22 spherical modules and ST04 presentation are not Mauna anatomy or operation.'],scale_contract='2x2 placement,ground0,+Z up/-Y front. Authored cell-relative dimensions,no recovered metric or calibrated client scale.',concept_review='sources/docs/reconstruction/models/mn20-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('MAUNA_MOTION_UNITS_AUTHORED',triangles,len(meshes),len(contacts),len(created),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
