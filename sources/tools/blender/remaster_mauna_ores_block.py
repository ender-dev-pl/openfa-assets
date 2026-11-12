"""Author MN19 Ores Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/ores-block';maps=root/'sources/materials/mauna/ores-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2611919);buffers={name:[] for name in ['cast-concrete-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','pale-module-colour','brass-colour']}
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Pale storage field edging and rim','pale-module-colour');dark=material('Opaque charcoal storage fields');dark.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.018,.023,.028,1)
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
    brass=material('Tarnished gold storage reinforcements','brass-colour',True);red=material('Worn red storage waist band','marking-red-colour');contacts=[];fields=[];chips=[];straps=[]
    lower=box('Ores Block grounded protected lower core',(0,0,.43),(1.06,1.06,.86),concrete,bevel=.008)
    middle=box('Ores Block tall plain middle core',(0,0,1.43),(1.06,1.06,1.18),concrete,bevel=.008)
    cap=box('Ores Block slightly projecting upper cap',(0,0,2.345),(1.10,1.10,.71),concrete,bevel=.008)
    contacts += [dict(object=middle.name,support=lower.name,point=[.3,.3,.85]),dict(object=cap.name,support=middle.name,point=[.3,.3,2.005])]
    def blind(name,body,q,n,width,height,depth=.025,backmat=dark):
        q=Vector(q);n=Vector(n);cut(body,box('Temporary real blind field',q+n*.01,(width,height,(depth+.01)*2),concrete,n,0),'Actual blind field')
        backing=box(name,q-n*(depth+.004),(width-.006,height-.006,.014),backmat,n,.001);fields.append(dict(object=backing.name,body=body.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.008));return backing
    blind('Ores Block broad dark upper front field',cap,(0,-.55,2.35),(0,-1,0),.92,.43)
    for i,y in enumerate([-.32,0,.32]):
        blind('Ores Block upper right brass inset '+str(i),cap,(.55,y,2.35),(1,0,0),.075,.42,.022,brass)
        blind('Ores Block middle right dark slot '+str(i),middle,(.53,y,1.37),(1,0,0),.070,.56,.028)
        frame=box('Ores Block pale right slot frame '+str(i),(.532,y,1.37),(.10,.60,.018),edge,(1,0,0),.001)
        cut(frame,box('Temporary slot frame aperture',(.532,y,1.37),(.072,.562,.06),edge,(1,0,0),0),'Actual open pale slot frame')
        contacts.append(dict(object=frame.name,support=middle.name,point=[.528,y+.043,1.37]))
    for i,x in enumerate([-.36,-.12,.12,.36]):blind('Ores Block faint short front mark '+str(i),middle,(x,-.53,1.30),(0,-1,0),.024,.17,.008,edge)
    blind('Ores Block blind dark roof inspection floor',cap,(0,0,2.70),(0,0,1),.29,.29,.11)
    rim=box('Ores Block raised square inspection rim',(0,0,2.7325),(.43,.43,.095),edge,bevel=.002)
    cut(rim,box('Temporary open roof rim',(0,0,2.7325),(.27,.27,.30),edge,bevel=0),'Actual inspection rim aperture')
    for x,y in [(.18,0),(-.18,0),(0,.18),(0,-.18)]:contacts.append(dict(object=rim.name,support=cap.name,point=[x,y,2.695]))
    band=box('Ores Block one continuous red waist ring',(0,0,.87),(1.09,1.09,.10),red,bevel=.001)
    cut(band,box('Temporary waist ring interior',(0,0,.87),(1.04,1.04,.30),red,bevel=0),'Actual hollow waist ring')
    for x,y in [(.525,0),(-.525,0),(0,.525),(0,-.525)]:contacts.append(dict(object=band.name,support=middle.name,point=[x,y,.87]))
    def stroke_outline(points,width):
        points=[Vector(p) for p in points];directions=[(b-a).normalized() for a,b in zip(points,points[1:])];normals=[Vector((-v.y,v.x)) for v in directions];left=[];right=[]
        for i,p in enumerate(points):
            if i==0:offset=normals[0]*width/2
            elif i==len(points)-1:offset=normals[-1]*width/2
            else:
                miter=(normals[i-1]+normals[i]).normalized();offset=miter*(width/2/miter.dot(normals[i]))
            left.append(p+offset);right.append(p-offset)
        return [tuple(p) for p in left+list(reversed(right))]
    def strap_solid(name,profile,side):
        outline=stroke_outline(profile,.055);count=len(outline);vertices=[(u,d,z) if side=='front' else (d,u,z) for d in ([-.548,-.522] if side=='front' else [.522,.548]) for u,z in outline];faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(j,(j+1)%count,(j+1)%count+count,j+count) for j in range(count)];o=solid(name,vertices,faces,brass)
        bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();mod=o.modifiers.new('Small metal edge break','BEVEL');mod.width=.0015;mod.segments=1;apply(o,mod);return o
    for side in ['front','right']:
        for i,u in enumerate([-.27,.27]):
            profile=[(u-.025,.10),(u-.025,.23),(u+.040,.37),(u-.035,.55),(u-.035,.74)];o=strap_solid('Ores Block continuous '+side+' lower brass reinforcement '+str(i),profile,side)
            witnesses=[((a[0]+b[0])/2,(a[1]+b[1])/2) for a,b in zip(profile,profile[1:])]+profile[1:-1]
            for p,z in witnesses:contacts.append(dict(object=o.name,support=lower.name,point=[p,-.526,z] if side=='front' else [.526,p,z]))
            straps.append(dict(object=o.name,face=side,profile=[list(p) for p in profile],width=.055,ground_clearance=.10))
    for obj,q,n in [(cap,Vector((-.40,.15,2.70)),Vector((0,0,1))),(lower,Vector((.40,-.53,.40)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.018,location=q+n*.012);cut(obj,bpy.context.object,'Actual shallow cast spall');chips.append(dict(body=obj.name,point=list(q),normal=list(n)))
    keep={o.name for o in [lower,middle,cap]};part_batches={}
    for mat,label in [(edge,'four faint marks three open slot frames and roof rim'),(brass,'three upper insets and four lower straps'),(red,'one continuous waist band'),(dark,'five seated dark fields')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]];assert objects
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Ores Block '+label;group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Ores Block '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/148';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z';placement['ground_level']=0;placement['preserve_ground_origin']=True
    bpy.context.view_layer.update()
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT');uv=obj.data.uv_layers.active
        for face in obj.data.polygons:
            for index in face.loop_indices:
                q=obj.data.vertices[obj.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+.6)/1.2,q.z/2.8) if abs(face.normal.x)>.5 else ((q.x+.6)/1.2,q.z/2.8) if abs(face.normal.y)>.5 else ((q.x+.6)/1.2,(q.y+.6)/1.2)
        mod=obj.modifiers.new('Stable export triangles','TRIANGULATE');apply(obj,mod);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0,obj.name;bm.to_mesh(obj.data);bm.free()
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*a,**k):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    meta=dict(schema_version=1,issue=261,id='openfa:building/legacy/148',key='MN19',name='Ores Block',culture='mauna',footprint=[2,2],definition_class=30,construction_updates=32,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_ores_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=contacts,part_batches=part_batches,physical_chips=chips,lower_reinforcements=straps,roof_inspection=dict(clear_square=.27,body_recess_depth=.11,visible_floor_z=2.593,rim_top=2.78,closed_vault=True),nonemissive=True,interpretation=['Own tall rectangular stacked tower,red waist band,upper front field/three brass insets,middle three right slots/four faint front marks,four bent lower brass reinforcements and square roof socket govern anatomy.','Exact depths,hidden engineering,rear band continuation and cell-relative proportions develop the concept as authored engineering;generic PB30 tanks and PB11/ST17 teleportation are not Mauna anatomy or operation.'],scale_contract='2x2 placement,ground0,+Z up/-Y front. Authored cell-relative dimensions,no recovered metric or calibrated client scale.',concept_review='sources/docs/reconstruction/models/mn19-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print('MAUNA_ORES_BLOCK_AUTHORED',triangles,len(meshes),len(contacts),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
