"""Author MN08 Construction Area from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/construction-area';maps=root/'sources/materials/mauna/construction-area';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610808);buffers={name:[] for name in ['cast-concrete-colour','used-brass-colour','marking-red-colour','concrete-orm','metal-orm','cast-service-normal','window-amber-colour','window-orm','pale-alloy-colour']}
    # Deterministic sparse roughcast spalls, patina streaks and fine pores.
    # These are authored surface maps,not borrowed legacy pixels.
    grids={n:[[rng.uniform(-1,1) for _ in range(n)] for _ in range(n)] for n in [5,9,19]}
    def cast_noise(n,u,v):
        x=u*n;y=v*n;ix=int(x);iy=int(y);a=x-ix;b=y-iy;a=a*a*(3-2*a);b=b*b*(3-2*b);g=grids[n]
        return (g[iy%n][ix%n]*(1-a)+g[iy%n][(ix+1)%n]*a)*(1-b)+(g[(iy+1)%n][ix%n]*(1-a)+g[(iy+1)%n][(ix+1)%n]*a)*b
    speckles={}
    for i in range(85):
        cx=rng.randrange(size);cy=rng.randrange(size);radius=rng.randrange(2,7)
        for dy in range(-radius,radius+1):
            for dx in range(-radius,radius+1):
                if dx*dx+dy*dy<radius*radius*rng.uniform(.65,1.1):speckles[((cx+dx)%size,(cy+dy)%size)]=rng.uniform(.035,.10)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=.040*cast_noise(5,u,v)+.018*cast_noise(19,u,v);grain=rng.uniform(-.025,.025);stain=max(0,cast_noise(9,u,v))*.065;aggregate=speckles.get((x,y),0);pore=.15 if rng.random()<.035 else 0;dust=.07*max(0,1-v*5)
            concrete_delta=cloud+grain+aggregate-stain-pore-dust
            buffers['cast-concrete-colour'].extend([max(.01,c+concrete_delta) for c in (.29,.34,.41)]+[1])
            scratch=.17 if ((x*7+y*31)%991<2 and rng.random()<.7) else 0
            buffers['used-brass-colour'].extend([max(.01,c+cloud*.7+grain*.5-stain*.9+scratch-pore*.3) for c in (.55,.36,.10)]+[1])
            buffers['marking-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in (.32,.018,.012)]+[1])
            buffers['concrete-orm'].extend([1,min(.98,max(.68,.85+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.76,max(.32,.54+grain+stain)),.72,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.035,.035),.5+rng.uniform(-.035,.035),1,1])
            buffers['window-amber-colour'].extend([max(.01,c+cloud*.35+grain*.3-stain*.5) for c in (.70,.58,.31)]+[1])
            buffers['window-orm'].extend([1,.30,0,1])
            buffers['pale-alloy-colour'].extend([max(.01,c+cloud*.5+grain*.5-stain*.5+scratch*.3) for c in (.46,.51,.57)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Matte pale coated sensor masts','pale-alloy-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);blue=material('Deep cobalt nonemissive colour fields','marking-red-colour');dark=material('Dark nonemissive service recesses')
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
    glass=material('Warm amber service points with authored steady light','window-amber-colour');node=glass.node_tree.nodes.get('Principled BSDF')
    for tex in glass.node_tree.nodes:
        if tex.type=='TEX_IMAGE' and tex.image==images['concrete-orm']:tex.image=images['window-orm']
    node.inputs['Emission Color'].default_value=(.30,.24,.10,1);node.inputs['Emission Strength'].default_value=.25
    red=material('Worn solid red source emblem','marking-red-colour')
    # Reuse the authored mottled map through a red tint, not source pixels.
    node=red.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(.32,.018,.012,1)
    def prism(name,outline,a,b,axis,mat):
        verts=[(x,u,v) if axis=='X' else (u,x,v) for x in [a,b] for u,v in outline];count=len(outline)
        faces=[tuple(reversed(range(count))),tuple(range(count,2*count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
        o=solid(name,verts,faces,mat);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();return o
    body=prism('Construction Area inclined main concrete block',[(-.65,.08),(.55,.08),(.55,1.65),(-.34,1.65)],-1.1,.05,'X',concrete)
    base=box('Construction Area low projecting plinth',(-.0775,-.05,.1975),(2.035,1.18,.235),concrete,bevel=.006)
    nose=prism('Construction Area sloping service nose',[(.92,.08),(1.42,.08),(1.24,.32),(.92,.32)],-.65,.55,'Y',concrete)
    attachments=[]
    def anchored(name,centre,size,mat,support,point):
        o=box(name,centre,size,mat,bevel=.003);attachments.append(dict(object=o.name,support=support.name,point=point));return o
    pale=anchored('Construction Area pale roof upright',(-.49,-.04,2.055),(.085,.085,.84),edge,body,[-.49,-.04,1.64])
    brass=anchored('Construction Area brass roof upright',(-.66,-.14,1.985),(.050,.05,.70),gold,body,[-.66,-.14,1.64])
    # Three structural bridges actually join the two roof uprights.
    bridges=[]
    a=Vector((-.66,-.14,0));b=Vector((-.49,-.04,0))
    for i,z in enumerate([1.80,1.99,2.18]):
        delta=b-a;o=box('Construction Area roof bridge '+str(i),(a+b)/2+Vector((0,0,z)),(delta.length+.04,.032,.028),edge,bevel=.001);o.rotation_euler.z=math.atan2(delta.y,delta.x);bridges.append(o)
    rail=anchored('Construction Area tall pale service rail',(.115,.32,.93),(.15,.10,1.26),edge,base,[.115,.32,.31])
    posts=[]
    for i,(x,y,h,w) in enumerate([(.55,-.36,1.14,.065),(.93,.10,1.04,.08),(1.035,.22,.43,.075),(.36,-.40,.25,.055)]):
        posts.append(anchored('Construction Area brass floor upright '+str(i),(x,y,.30+h/2),(w,w,h),gold,nose if i==2 else base,[x,y,.31]))
    # Three small collars attach the service rail to the body and rail.
    for i,z in enumerate([.43,.95,1.43]):
        anchored('Construction Area pale rail collar '+str(i),(.075,.32,z),(.17,.14,.045),edge,body,[.045,.32,z])
    def surface(obj,face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inverse=obj.matrix_world.inverted();hit,q,normal,_=obj.ray_cast(inverse@(tangent*u+n*3+Vector((0,0,z))),inverse.to_3x3()@(-n));assert hit;return obj.matrix_world@q,(obj.matrix_world.to_3x3()@normal).normalized()
    fields=[];contacts=[]
    def field(name,obj,face,u,z,width,height,mat,depth=.018):
        q,n=surface(obj,face,u,z);cut(obj,box('Temporary field cutter',q+n*.01,(width,height,2*(depth+.01)),concrete,n,0),'Actual blind '+name)
        part=box('Construction Area '+name,q-n*(depth+.002),(width-.006,height-.006,.012),mat,n,.001);fields.append(dict(object=part.name,body=obj.name,point=list(q),normal=list(n),depth=depth,contact_depth=depth+.005));return q,n,part
    panes=[]
    for i,(obj,face,u,z) in enumerate([(body,'front',-.54,.77),(body,'front',-.54,.60),(body,'front',-.94,.40),(body,'front',-.28,.38),(base,'front',.58,.20)]):
        q,n,back=field('amber point backing '+str(i),obj,face,u,z,.055,.060,dark,.014)
        pane=box('Construction Area amber point '+str(i),q-n*.010,(.035,.038,.012),glass,n,.001);panes.append(pane);contacts.append(dict(object=pane.name,support=back.name,point=list(q-n*.015)))
    # Source dark slots and paired pale slats on the tall right wall.
    for i,(u,z) in enumerate([(-.23,1.39),(.10,1.48),(-.23,1.19)]):field('upper dark port '+str(i),body,'right',u,z,.055,.085,dark)
    for i,z in enumerate([1.05,.94,.83]):
        for j,u in enumerate([-.26,-.13]):field('pale wall slat '+str(i)+' '+str(j),body,'right',u,z,.052,.035,edge,.012)
    for i,z in enumerate([.63,.51,.39]):field('small brass wall field '+str(i),body,'right',-.27,z,.06,.04,gold,.012)
    # Two attached open U-handles: no levitating ornamental uprights.
    for i,(u,z,h) in enumerate([(-.12,.55,.42),(.22,1.02,.48)]):
        for k,zz in enumerate([z-h/2,z+h/2]):anchored('Construction Area handle foot '+str(i)+' '+str(k),(.13,u,zz),(.19,.052,.052),gold,body,[.045,u,zz])
        anchored('Construction Area handle stem '+str(i),(.205,u,z),(.052,.052,h+.04),gold,bpy.data.objects['Construction Area handle foot '+str(i)+' 0'],[.205,u,z-h/2+.01])
    # End projections overlap the actual sloping service nose; own source has two.
    for i,y in enumerate([-.39,.20]):
        anchored('Construction Area two end feet '+str(i),(1.33,y,.14),(.19,.09,.24),gold,nose,[1.25,y-.02,.19])
    q,n,back=field('end slatted service inset',nose,'right',-.30,.22,.18,.075,dark,.022)
    for i,u in enumerate([-.35,-.25]):
        # Locate at the same slope depth through the actual field frame.
        pane=box('Construction Area end inset pale slat '+str(i),q+Vector((0,u+.30,0))-n*.018,(.065,.022,.012),edge,n,.001);contacts.append(dict(object=pane.name,support=back.name,point=list(q+Vector((0,u+.30,0))-n*.021)))
    # Source emblem follows the inclined plane; physical thin paint is seated.
    q,n=surface(body,'front',-.64,1.20)
    emblem=[]
    for name,dx,dz,w,h in [('top mark',0,.16,.16,.032),('T crossbar',0,.055,.25,.055),('T stem',-.055,-.055,.055,.19),('lower hook',0,-.13,.16,.05),('right return',.055,-.065,.05,.14)]:
        pos=q+Vector((dx,0,dz));pos.y=-.65+(.31/1.57)*(pos.z-.08)
        o=box('Construction Area red emblem '+name,pos-n*.001,(w,h,.006),red,n,0);emblem.append(o);contacts.append(dict(object=o.name,support=body.name,point=list(pos-n*.002)))
    # Union touching thin paint pieces so the hooked glyph has no coplanar overlaps.
    glyph=emblem[1]
    for piece in emblem[2:]:
        mod=glyph.modifiers.new('Union contiguous source glyph paint','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=piece;apply(glyph,mod);bpy.data.objects.remove(piece,do_unlink=True)
    contacts=[c for c in contacts if not c['object'].startswith('Construction Area red emblem') or c['object'] in [emblem[0].name,glyph.name]]
    # Solid red stripe on the far edge of the sloping service nose.
    stripe=prism('Construction Area red end stripe',[(1.2505,.31),(1.4155,.09),(1.4075,.09),(1.2425,.31)],.36,.42,'Y',red)
    contacts.append(dict(object=stripe.name,support=nose.name,point=[1.329,.39,.20]))
    chips=[]
    for obj,point,normal in [(body,Vector((-.90,-.10,1.65)),Vector((0,0,1))),(base,Vector((.74,-.64,.20)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.025,location=point+normal*.018);cut(obj,bpy.context.object,'Actual shallow cast chip');chips.append(dict(body=obj.name,point=list(point),normal=list(normal)))

    # Batch accessories by material, retaining each closed part as a named vertex group.
    part_batches={}
    keep={body.name,base.name,nose.name}
    for mat,label in [(edge,'pale service assemblies'),(gold,'brass service assemblies'),(dark,'dark field backings'),(glass,'amber service points'),(red,'red source markings')]:
        objects=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in keep and list(o.data.materials)==[mat]]
        if not objects:continue
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            part_batches[o.name]='Construction Area '+label;g=o.vertex_groups.new(name=o.name);g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();bpy.context.object.name='Construction Area '+label
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/137';placement['footprint']=[4,4];placement['local_forward']='-Y';placement['local_up']='+Z'
    for o in meshes:
        o.parent=placement;bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);materials=[];indices=[]
        for f in o.data.polygons:
            mat=o.data.materials[f.material_index]
            if mat not in materials:materials.append(mat)
            indices.append(materials.index(mat))
        o.data.materials.clear()
        for mat in materials:o.data.materials.append(mat)
        for f,index in zip(o.data.polygons,indices):f.material_index=index
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        uv=o.data.uv_layers.active
        for f in o.data.polygons:
            for index in f.loop_indices:
                q=o.data.vertices[o.data.loops[index].vertex_index].co;uv.data[index].uv=((q.y+1.2)/2.4,q.z/2.8) if abs(f.normal.x)>.5 else ((q.x+1.2)/2.4,q.z/2.8) if abs(f.normal.y)>.5 else ((q.x+1.2)/2.4,(q.y+1.2)/2.4)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');apply(o,mod);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name;bm.to_mesh(o.data);bm.free()
        for f in o.data.polygons:f.use_smooth=False
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/mauna-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/137',key='MN08',name='Construction Area',culture='mauna',footprint=[4,4],definition_class=25,construction_updates=32,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,author='sources/tools/blender/remaster_mauna_construction_area.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,attachment_contacts=attachments+contacts,part_batches=part_batches,physical_chips=chips,steady_point_emission=dict(colour=[.30,.24,.10],strength=.25,scope='Authored steady colour preservation,not recovered timed lighting.'),interpretation=['Own inclined tallblock,lowprojectingplinth,pairedroofmast,staggeredserviceuprights,handles,redemblem/endstripe,smallpoints andendfeet guide geometry.','Hiddenwalls,attachmentengineering,recessdepths,pointreading andcellrelative dimensions authored. GenericTerranPB25crane/closingdeck doesnotestablish Mauna operation. No own animation inferred.'],scale_contract='4x4 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn08-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_CONSTRUCTION_AREA_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
