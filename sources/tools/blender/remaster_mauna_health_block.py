"""Author MN05 Health Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/health-block';maps=root/'sources/materials/mauna/health-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610505);buffers={name:[] for name in ['cast-concrete-colour','used-brass-colour','recess-red-colour','concrete-orm','metal-orm','cast-service-normal','window-amber-colour','window-orm','pale-alloy-colour']}
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
            buffers['recess-red-colour'].extend([max(.01,c+cloud*.7+grain*.8-stain*.8+aggregate*1.6-pore*.4) for c in (.49,.105,.070)]+[1])
            buffers['concrete-orm'].extend([1,min(.98,max(.68,.85+grain+stain)),0,1]);buffers['metal-orm'].extend([1,min(.76,max(.32,.54+grain+stain)),.72,1]);buffers['cast-service-normal'].extend([.5+rng.uniform(-.035,.035),.5+rng.uniform(-.035,.035),1,1])
            buffers['window-amber-colour'].extend([max(.01,c+cloud*.35+grain*.3-stain*.5) for c in (.56,.60,.17)]+[1])
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=material('Used pale service alloy','pale-alloy-colour',True);gold=material('Used brass feet and functional fittings','used-brass-colour',True);red=material('Dark red nonemissive recessed fittings','recess-red-colour');dark=material('Dark nonemissive service recesses')
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
    glass=material('Yellowgreen service panes with authored steady light','window-amber-colour');node=glass.node_tree.nodes.get('Principled BSDF')
    for tex in glass.node_tree.nodes:
        if tex.type=='TEX_IMAGE' and tex.image==images['concrete-orm']:tex.image=images['window-orm']
    node.inputs['Emission Color'].default_value=(.30,.30,.065,1);node.inputs['Emission Strength'].default_value=.25
    lower=box('Health Block lower concrete body',(0,0,.84),(1.40,1.40,1.52),concrete,bevel=.012)
    upper=box('Health Block smaller upper tower',(-.12,.08,2.00),(.84,.84,.88),concrete,bevel=.008)
    def surface(obj,face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inverse=obj.matrix_world.inverted();hit,q,normal,_=obj.ray_cast(inverse@(tangent*u+n*3+Vector((0,0,z))),inverse.to_3x3()@(-n));assert hit;return obj.matrix_world@q,(obj.matrix_world.to_3x3()@normal).normalized()
    fields=[]
    def recess(name,obj,face,u,z,width,height,mat,depth=.040):
        q,n=surface(obj,face,u,z);cut(obj,box('Temporary actual field cutter',q+n*.015,(width,height,2*(depth+.015)),concrete,n,0),'Actual blind field '+name);back=box('Health Block '+name,q-n*(depth+.003),(width-.006,height-.006,.014),mat,n,.001);fields.append(dict(object=back.name,body=obj.name,point=list(q),normal=list(n),depth=depth));return q,n,back
    def join_parts(objects,name):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
    panes=[];banks=[]
    specifications=[('upper front',upper,'front',-.12,2.05,2,2,.24,.24),('upper right',upper,'right',.08,2.05,2,2,.24,.24),('mid front left',lower,'front',-.45,1.27,1,2,.11,.25),('mid front right',lower,'front',-.20,1.19,1,2,.11,.25),('lower front point',lower,'front',0,.43,1,1,.065,.090)]+[('lower right '+str(i),lower,'right',u,.51,1,2,.11,.25) for i,u in enumerate([-.32,0,.32])]
    for key,obj,face,u,z,cols,rows,width,height in specifications:
        q,n,back=recess(key+' backing',obj,face,u,z,width,height,dark);tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));contacts=[];pane_width=width/cols*.72;pane_height=height/rows*.70
        for row in range(rows):
            for col in range(cols):
                centre=q+tangent*((col-(cols-1)/2)*width/cols)+Vector((0,0,(row-(rows-1)/2)*height/rows));panes.append(box('Pane '+key+' '+str(row)+' '+str(col),centre-n*.026,(pane_width,pane_height,.040),glass,n,.0015));contacts.append(list(centre-n*.042))
        banks.append(dict(key=key,body=obj.name,backing=back.name,cols=cols,rows=rows,contacts=contacts))
    join_parts(panes,'Health Block nineteen amber panes')
    for i,u in enumerate([-.45,.40]):recess('lower brass panel '+str(i),lower,'front',u,.37,.24,.50,gold,depth=.012)
    for i,(z,height) in enumerate([(.36,.53),(1.10,.46)]):recess('red corner strip '+str(i),lower,'front',.61,z,.075,height,red)
    route=[Vector((.285,0,1.85)),Vector((.43,0,1.79)),Vector((.69,0,1.67)),Vector((.755,0,1.60)),Vector((.755,0,1.03))]
    conduits=[];mounts=[];contacts=[]
    for i,y in enumerate([-.30,-.04,.22]):
        centres=[p+Vector((0,y,0)) for p in route];verts=[]
        for j,centre in enumerate(centres):
            direction=(centres[min(j+1,len(centres)-1)]-centres[max(0,j-1)]).normalized();side=Vector((-direction.z,0,direction.x)).normalized();v=Vector((0,1,0))
            for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:verts.append(centre+v*(a*.026)+side*(b*.026))
        faces=[(3,2,1,0),tuple((len(centres)-1)*4+j for j in range(4))]
        for j in range(len(centres)-1):
            for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
        conduits.append(solid('Pale angular conduit '+str(i),verts,faces,edge));mounts.append(box('Pale lower mount '+str(i),(.715,y,1.055),(.14,.10,.11),edge,bevel=.003));start=centres[0]+(centres[1]-centres[0]).normalized()*.010;end=centres[-1]+Vector((0,0,.012));contacts.append(dict(index=i,upper_contact=list(start),mount_contact=list(end),wall_contact=[.685,y,1.055],route=[list(p) for p in centres]))
    join_parts(conduits,'Health Block three angular service conduits');join_parts(mounts,'Health Block three attached lower mounts')
    roof=[]
    for i,(x,y,height) in enumerate([(-.40,-.08,.20),(-.14,.04,.55),(.17,.15,.15)]):
        obj=box('Health Block brass roof element '+str(i),(x,y,2.42+height/2),(.10,.095,height),gold,bevel=.003);roof.append(dict(object=obj.name,material='brass',contact=[x,y,2.43],top=2.42+height))
    for i,(x,y,height) in enumerate([(-.28,-.03,.44),(-.01,.24,.68)]):
        profile=[(0,.055),(.24 if i else .16,.055),(.29 if i else .21,.033),(height,.026)];verts=[(x+a*r,y+b*r,2.42+z) for z,r in profile for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]];faces=[(3,2,1,0),tuple((len(profile)-1)*4+j for j in range(4))]
        for j in range(len(profile)-1):
            for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
        obj=solid('Health Block pale roof upright '+str(i),verts,faces,edge);roof.append(dict(object=obj.name,material='pale-alloy',contact=[x,y,2.43],top=2.42+height))
    chips=[]
    for obj,label,point,normal in [(upper,'tower-roof',Vector((-.40,.33,2.44)),Vector((0,0,1))),(lower,'lower-front',Vector((-.54,-.70,.75)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.030,location=point+normal*.023);cut(obj,bpy.context.object,'Actual small cast service chip '+label);chips.append(dict(body=obj.name,point=list(point),normal=list(normal)))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/134';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
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
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/134',key='MN05',name='Health Block',culture='mauna',footprint=[2,2],definition_class=34,construction_updates=16,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,author='sources/tools/blender/remaster_mauna_health_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=fields,pane_banks=banks,conduit_contacts=contacts,roof_elements=roof,physical_chips=chips,steady_pane_emission=dict(colour=[.30,.30,.065],strength=.25,scope='Authored steady material preserving bright sourcepanes,not recovered timedlegacy lighting.'),interpretation=['Own steppedconcretebody,19smallamberpanes,two brasslowerpanels,redcornerstrips,three angular serviceconduits andfive roofelements(3brass/2pale) govern geometry.','Hiddenrearwalls,conduit/mountprofiles,blinddepths andcellrelative dimensions authored. PB34Terranopeningdome isnottransferred. No operatinganimation inferred.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn05-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_HEALTH_BLOCK_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
