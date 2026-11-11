"""Author MN04 Off-duty Block from own legacy evidence and reviewed real ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mauna/off-duty-block';maps=root/'sources/materials/mauna/off-duty-block';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2610404);buffers={name:[] for name in ['cast-concrete-colour','used-brass-colour','recess-red-colour','concrete-orm','metal-orm','cast-service-normal','window-amber-colour','window-orm']}
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
    concrete=material('Mauna rough greyblue cast concrete','cast-concrete-colour');edge=concrete;gold=material('Used brass feet and functional fittings','used-brass-colour',True);red=material('Dark red nonemissive recessed fittings','recess-red-colour');dark=material('Dark nonemissive service recesses')
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
    glass=material('Yellowgreen residential panes with authored steady light','window-amber-colour');node=glass.node_tree.nodes.get('Principled BSDF')
    for tex in glass.node_tree.nodes:
        if tex.type=='TEX_IMAGE' and tex.image==images['concrete-orm']:tex.image=images['window-orm']
    node.inputs['Emission Color'].default_value=(.30,.30,.065,1);node.inputs['Emission Strength'].default_value=.25
    body=box('Off-duty Block concrete residential shell',(0,0,1.04),(1.32,1.32,1.92),concrete,bevel=.012)
    body.data.materials.append(edge)
    def surface(face,u,z):
        n=Vector((0,-1,0)) if face=='front' else Vector((1,0,0));tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0));bpy.context.view_layer.update();inverse=body.matrix_world.inverted();hit,q,normal,_=body.ray_cast(inverse@(tangent*u+n*3+Vector((0,0,z))),inverse.to_3x3()@(-n));assert hit;return body.matrix_world@q,(body.matrix_world.to_3x3()@normal).normalized()
    rects=[]
    def recess(name,face,u,z,width,height,mat):
        q,n=surface(face,u,z);cut(body,box('Temporary actual field cutter',q+n*.015,(width,height,.11),concrete,n,0),'Actual blind field '+name);obj=box('Off-duty Block '+name,q-n*.043,(width-.006,height-.006,.014),mat,n,.001);rects.append(dict(object=obj.name,point=list(q),normal=list(n),depth=.040));return q,n
    def join_parts(objects,name):
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            group=o.vertex_groups.new(name=o.name);group.add(list(range(len(o.data.vertices))),1,'REPLACE');o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join();o=bpy.context.object;o.name=name;return o
    banks=[]
    for face in ['front','right']:
        for floor,z in enumerate([.91,1.51]):
            key=face+' bank '+str(floor);q,n=recess(key+' backing',face,0,z,1.04,.46,dark);panes=[];contacts=[]
            tangent=Vector((1,0,0)) if face=='front' else Vector((0,1,0))
            for row,dz in enumerate([-.105,.105]):
                for col,u in enumerate([-.36,-.12,.12,.36]):
                    centre=q+tangent*u+Vector((0,0,dz));panes.append(box('Pane '+face+' '+str(floor)+' '+str(row)+' '+str(col),centre-n*.026,(.19,.15,.040),glass,n,.002));contacts.append(list(centre-n*.042))
            obj=join_parts(panes,'Off-duty Block eight panes '+key);banks.append(dict(face=face,floor=floor,object=obj.name,backing='Off-duty Block '+key+' backing',contacts=contacts,centre=list(q),normal=list(n)))
    for i,u in enumerate([-.22,.23]):recess('lower red panel '+str(i),'right',u,.30,.17,.44,red)
    plinth=box('Off-duty Block small paired-stack plinth',(-.20,.15,2.04),(.42,.36,.12),concrete,bevel=.004)
    stacks=[]
    for i,(x,y,bottom,height) in enumerate([(-.12,.22,2.07,.69),(-.29,.11,2.07,.53),(.32,.18,1.98,.50)]):
        obj=box('Off-duty Block rectangular brass stack '+str(i),(x,y,bottom+height/2),(.13,.13,height),gold,bevel=.004);stacks.append(dict(index=i,object=obj.name,centre=[x,y],bottom=bottom,top=bottom+height,contact=[x,y,bottom+.008],support=plinth.name if i<2 else body.name))
    grooves=[];post=bpy.data.objects[stacks[2]['object']]
    for i,z in enumerate([2.10,2.20,2.30,2.40]):
        q=Vector((.32,.115,z));n=Vector((0,-1,0));cut(post,box('Temporary shallow brass groove',q+n*.005,(.095,.012,.022),gold,n,0),'Shallow service groove '+str(i));grooves.append(dict(point=list(q),normal=list(n),depth=.006))
    chips=[]
    for label,point,normal in [('roof',Vector((.48,.39,2.00)),Vector((0,0,1))),('lower-front',Vector((-.42,-.66,.40)),Vector((0,-1,0)))]:
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=.030,location=point+normal*.023);cut(body,bpy.context.object,'Actual shallow cast chip '+label);chips.append(dict(point=list(point),normal=list(normal)))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement);placement['catalogue_id']='openfa:building/legacy/133';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
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
    metadata=dict(schema_version=1,issue=261,id='openfa:building/legacy/133',key='MN04',name='Off-duty Block',culture='mauna',footprint=[2,2],definition_class=0,construction_updates=24,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_mauna_off_duty_block.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},rectangular_recesses=rects,window_banks=banks,roof_stacks=stacks,stack_grooves=grooves,physical_chips=chips,steady_window_emission=dict(colour=[.30,.30,.065],strength=.25,scope='Authored steady material choice preserving brightyellowgreen sourcepanes;not recovered timedlegacy lighting.'),interpretation=['Own uprightconcreteblock,fourvisible4x2windowbanks,two lowerredpanels andthree unequal rectangularbrassroofstacks govern geometry.','Plainhiddenrearwalls,blindfielddepths/stackmounts/groovepitch andcellrelative dimensions authored. PB00isTerran functioncontext,notMauna geometry/operation. No operatinganimation inferred.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Cell-relative proportions authored;no recovered metric dimensions.',concept_review='sources/docs/reconstruction/models/mn04-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('MAUNA_OFF_DUTY_BLOCK_AUTHORED',triangles,len(meshes),len(created),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
