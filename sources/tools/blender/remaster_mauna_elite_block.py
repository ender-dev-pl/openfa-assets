"""Author MN07 Elite Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/elite-block';maps=root/'sources/materials/mauna/elite-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610707);buffers={name:[] for name in ['cast-concrete-colour','used-brass-colour','band-blue-colour','concrete-orm','metal-orm','cast-service-normal','window-amber-colour','window-orm','pale-alloy-colour']}
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
            buffers['band-blue-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in (.018,.030,.28)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Matte pale coated sensor masts','pale-alloy-colour');gold=material('Used brass feet and functional fittings','used-brass-colour',True);blue=material('Deep cobalt nonemissive colour fields','band-blue-colour');dark=material('Dark nonemissive service recesses')
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
    mainbody=box('Elite Block main concrete body',(0,0,1.23),(1.30,1.30,2.30),concrete,bevel=.009)
    roof=box('Elite Block main roof lip',(0,0,2.38),(1.38,1.38,.10),concrete,bevel=.005)
    tower=box('Elite Block upper command sensor tower',(-.06,.07,2.75),(.54,.54,.70),concrete,bevel=.006)
    def mast(name,x,y,height):
        z=3.08;verts=[(x+a*.05,y+b*.05,z) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]+[(x+a*.05,y+b*.05,z+height-(.035 if a<0 else 0)) for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        return solid(name,verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],edge)
    tall=mast('Elite Block tall point-bearing pale mast',.02,0,.67);short=mast('Elite Block shorter pale mast',-.12,.07,.48)
    def surface(obj,face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inverse=obj.matrix_world.inverted();hit,q,normal,_=obj.ray_cast(inverse@(tangent*u+n*3+Vector((0,0,z))),inverse.to_3x3()@(-n));assert hit;return obj.matrix_world@q,(obj.matrix_world.to_3x3()@normal).normalized()
    fields=[]
    def recess(name,obj,face,u,z,width,height,mat,depth=.025):
        q,n=surface(obj,face,u,z);cut(obj,box('Temporary field cutter',q+n*.015,(width,height,2*(depth+.015)),concrete,n,0),'Actual blind field '+name);back=box('Elite Block '+name,q-n*(depth+.003),(width-.006,height-.006,.014),mat,n,.001);fields.append(dict(object=back.name,body=obj.name,point=list(q),normal=list(n),depth=depth));return q,n,back
    def join_parts(objects,name):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            g=o.vertex_groups.new(name=o.name);g.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
    specifications=[('main front high',mainbody,'front',-.27,2.04,1,2,.065,.16,.025)]
    for level,z in [('middle',1.50),('lower',.55)]:
        for i,u in enumerate([-.27,.15]):specifications.append(('main front '+level+' '+str(i),mainbody,'front',u,z,1,2,.065,.16,.025))
    for level,z in [('high',2.03),('middle',1.56),('lower',.55)]:
        for i,u in enumerate([-.40,0,.40]):
            cols=2 if i==2 and level!='lower' else 1;rows=3 if level=='lower' else 2;specifications.append(('main right '+level+' '+str(i),mainbody,'right',u,z,cols,rows,.17 if cols==2 else .065,.24 if rows==3 else .16,.025))
    specifications += [('tower front',tower,'front',-.06,2.70,1,2,.065,.14,.025),('tower right low',tower,'right',.07,2.67,1,2,.065,.14,.025),('tower right high',tower,'right',.07,2.92,1,2,.065,.14,.025),('mast points',tall,'front',.02,3.38,1,3,.055,.21,.012)]
    backings=[];panes=[];banks=[]
    for key,obj,face,u,z,cols,rows,width,height,depth in specifications:
        q,n,back=recess(key+' backing',obj,face,u,z,width,height,dark,depth);backings.append(back);tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));contacts=[]
        for row in range(rows):
            for col in range(cols):
                centre=q+tangent*((col-(cols-1)/2)*width/cols)+Vector((0,0,(row-(rows-1)/2)*height/rows));panes.append(box('Amber point '+key+' '+str(row)+' '+str(col),centre-n*(depth-.004),(width/cols*.70,height/rows*.70,.018),glass,n,.001));contacts.append(list(centre-n*(depth+.002)))
        banks.append(dict(key=key,cols=cols,rows=rows,contacts=contacts))
    backingnames={o.name for o in backings};join_parts(backings,'Elite Block eighteen dark field backings');join_parts(panes,'Elite Block fortyfour amber points')
    for field in fields:
        if field['object'] in backingnames:field['object']='Elite Block eighteen dark field backings'
    blueparts=[]
    for key,face,u,z,w,h in [('front upper blue','front',-.56,1.28,.10,.72),('front lower blue','front',-.56,.37,.10,.56),('right near lower blue','right',-.56,.37,.12,.56),('right middle lower blue','right',.08,.25,.13,.30)]:
        _,_,part=recess(key,mainbody,face,u,z,w,h,blue);blueparts.append(part);fields[-1]['object']='Elite Block four straight blue fields'
    join_parts(blueparts,'Elite Block four straight blue fields')
    outline=list(reversed([(-.62,1.19),(.62,1.19),(.62,1.11),(-.50,1.11),(-.50,.80),(-.62,.80)]))
    def lprism(name,a,b,mat):
        v=[(x,y,z) for x in [a,b] for y,z in outline];count=len(outline);f=[tuple(reversed(range(count))),tuple(range(count,count*2))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)];return solid(name,v,f,mat)
    cut(mainbody,lprism('Temporary L field cutter',.615,.68,concrete),'Actual cobalt L-shaped recess');lprism('Elite Block blue L field',.609,.621,blue)
    lchecks=[[.65,0,1.15],[.65,.50,1.15],[.65,-.56,.90]]
    frames=[];centres=[];panels=[]
    for i,u in enumerate([-.22,.10]):
        q,n=surface(mainbody,'front',u,.98);cut(mainbody,box('Temporary brass panel field',q+n*.015,(.22,.20,.12),concrete,n,0),'Blind brass frame field');frame=box('Brass frame '+str(i),q-n*.028,(.21,.19,.040),gold,n,.002);fields.append(dict(object='Elite Block two brass front frames',body=mainbody.name,point=list(q),normal=list(n),depth=.045,contact_depth=.0465));face=q-n*.008;cut(frame,box('Temporary frame centre',face+n*.008,(.075,.10,.044),gold,n,0),'Actual small dark panel centre');centres.append(box('Dark panel centre '+str(i),face-n*.015,(.069,.094,.012),dark,n,.001));frames.append(frame);panels.append(dict(face=list(face),normal=list(n),depth=.014,contact=list(face-n*.017)))
    join_parts(frames,'Elite Block two brass front frames');join_parts(centres,'Elite Block two dark panel centres')
    pins=[];pinmeta=[]
    for i,(x,y,bottom,height,support) in enumerate([(-.50,-.25,2.415,.14,roof.name),(-.40,-.15,2.415,.10,roof.name),(.47,.28,2.415,.16,roof.name),(-.25,.10,3.085,.09,tower.name),(.17,.10,3.085,.30,tower.name)]):
        pins.append(box('Angular brass roof pin '+str(i),(x,y,bottom+height/2),(.045,.045,height),gold,bevel=.001));pinmeta.append(dict(index=i,support=support,contact=[x,y,bottom+.008],top=bottom+height))
    join_parts(pins,'Elite Block five unequal brass roof pins')
    chips=[]
    for obj,point,normal in [(roof,Vector((.52,-.44,2.43)),Vector((0,0,1))),(mainbody,Vector((.32,-.65,1.86)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.025,location=point+normal*.018);cut(obj,bpy.context.object,'Actual shallow cast service chip');chips.append(dict(body=obj.name,point=list(point),normal=list(normal)))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/136';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
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
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/136',key='MN07',name='Elite Block',culture='mauna',footprint=[3,3],definition_class=16,construction_updates=56,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,author='sources/tools/blender/remaster_mauna_elite_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,point_banks=banks,blue_l_witnesses=lchecks,brass_panel_centres=panels,roof_pins=pinmeta,physical_chips=chips,steady_point_emission=dict(colour=[.30,.24,.10],strength=.25,scope='Authored steady colourpreservation,not recovered timedlighting.'),interpretation=['Own tallbody/upperbox/splitmast,44smallpointreading,bluefields/Lband,two brassframes/five roofpins govern geometry.','Hiddenrearwalls,pointgridreading/fielddepths,pinprofiles andcellrelative dimensions authored. GenericPB16/PB24/ST12context doesnotestablishMauna anatomy/rotation. No operatinganimationinferred.'],scale_contract='3x3 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn07-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_ELITE_BLOCK_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
