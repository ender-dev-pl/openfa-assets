"""Author MK20 Merl from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/merl';maps=root/'sources/materials/mikotaj/merl'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25920);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[];terminal=[]
    colour_rng=random.Random(2592003);colour_layers=[]
    for cells,weight in [(5,.18),(19,.08),(67,.025)]:
        grid=[[colour_rng.uniform(-.5,.5) for _ in range(cells+1)] for _ in range(cells+1)]
        for row in grid:row[-1]=row[0]
        colour_layers.append((cells,weight,grid))
    def mineral_field(u,v):
        u=(u+.025*math.sin(math.tau*3*v))%1;v=max(0,min(.999999,v+.020*math.sin(math.tau*2*u)));value=0
        for cells,weight,grid in colour_layers:
            fx=u*cells;fy=v*cells;ix=min(int(fx),cells-1);iy=min(int(fy),cells-1);tx=fx-ix;ty=fy-iy;tx=tx*tx*(3-2*tx);ty=ty*ty*(3-2*ty);a=grid[iy][ix]*(1-tx)+grid[iy][ix+1]*tx;b=grid[iy+1][ix]*(1-tx)+grid[iy+1][ix+1]*tx;value+=weight*(a*(1-ty)+b*ty)
        return value
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=mineral_field(u,v)+rng.uniform(-.009,.009)
            stain=max(0,-cloud-.015)*.85
            exposed=.09*max(0,min(1,(cloud-.025)/.035))
            scratch=.075 if (x*37+y*79)%1237<2 else 0
            transition=max(0,min(1,(v-.25)/.42));transition=transition*transition*(3-2*transition);pedestal_tone=.75+.35*transition
            cleft=math.exp(-((u-.5-.012*math.sin(21*v))/.025)**2)*math.exp(-((v-.18)/.19)**4)
            colours.extend([max(.015,min(1,(c+cloud*1.05-stain*1.2+scratch+exposed*.60)*pedestal_tone*(1-.55*cleft))) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.2+scratch)) for c in (.40,.19,.105)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            hot=math.exp(-((u-.5)/.23)**2-((v-.53)/.33)**2);terminal.extend([.38+.55*hot,.025+.28*hot,.012+.04*hot,1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2592007);layers=[]
    for cells,weight in [(7,.10),(23,.04),(71,.01)]:
        grid=[[noise_rng.uniform(-.5,.5) for _ in range(cells+1)] for _ in range(cells+1)]
        for row in grid:row[-1]=row[0]
        layers.append((cells,weight,grid))
    seeds=[(noise_rng.random(),noise_rng.random()) for _ in range(16)]
    height=[]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/(size-1);value=0
            for cells,weight,grid in layers:
                fx=u*cells;fy=v*cells;ix=min(int(fx),cells-1);iy=min(int(fy),cells-1);tx=fx-ix;ty=fy-iy;tx=tx*tx*(3-2*tx);ty=ty*ty*(3-2*ty)
                a=grid[iy][ix]*(1-tx)+grid[iy][ix+1]*tx;b=grid[iy+1][ix]*(1-tx)+grid[iy+1][ix+1]*tx;value+=weight*(a*(1-ty)+b*ty)
            # Sparse broken mineral veins, not closed Voronoi/panel cells.
            for centre,phase,lo,hi in [(.27,.4,.21,.70),(.56,2.1,.43,.87),(.79,4.3,.12,.49)]:
                if lo<v<hi:
                    vein=centre+.025*math.sin(17*v+phase)+.013*math.sin(43*v-phase)
                    mask=max(0,min(1,(math.sin(31*v+phase)+.25)*2))
                    value-=.012*math.exp(-((u-vein)/.0035)**2)*mask
            height.append(value)
    normals=[]
    for y in range(size):
        for x in range(size):
            dx=(height[y*size+(x+1)%size]-height[y*size+(x-1)%size])*45
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*45;length=math.sqrt(1+dx*dx+dy*dy)
            normals.extend([.5-.5*dx/length,.5-.5*dy/length,.5+.5/length,1])
    images={}
    for name,pixels in [('mineral-base-colour',colours),('exposed-ridge-base-colour',ridge),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
        image=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name.startswith(('occlusion','mineral-fracture')):image.colorspace_settings.name='Non-Color'
        image.pixels.foreach_set(pixels);image.filepath_raw=str(maps/(name+'.png'));image.file_format='PNG';image.save()
        path=maps/(name+'.png');path.write_bytes(clean_png(path.read_bytes()));image.pack();images[name]=image
    def material(name,colour,metal=.7,rough=.4,image=None,emission=0):
        mat=bpy.data.materials.new(name);mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if image:
            node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=images[image];mat.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color'])
            packed=mat.node_tree.nodes.new('ShaderNodeTexImage');packed.image=images['occlusion-roughness-metallic'];split=mat.node_tree.nodes.new('ShaderNodeSeparateColor');mat.node_tree.links.new(packed.outputs['Color'],split.inputs[0]);mat.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);mat.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic'])
        if image and image not in ['brass-base-colour','red-terminal-colour']:
            texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=images['mineral-fracture-normal']
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.9
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    dark=material('Dark mineral recess interior',(.014,.021,.020),.35,.72)
    # Authored portable mottled lens colour/emission, never sampled from legacy.
    pixels=[];lens_rng=random.Random(2592009)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Pale plasma head lens',(.1,.3,.75),.18,.30,emission=.25)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
    pixels=[]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;hot=max(0,1-((u-.5)/.6)**2-((v-.5)/.65)**2);pixels.extend([.85+.15*hot,.45+.30*hot,.01+.04*hot,1])
    image=bpy.data.images.new('gold-pulse-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'gold-pulse-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    gold=material('Golden plasma pulse',(.95,.64,.12),0,.8,emission=2);node=gold.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;p=gold.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.015,.01,.001,1);p.inputs['Emission Strength'].default_value=3;gold.node_tree.links.new(node.outputs['Color'],p.inputs['Emission Color'])
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=5,radius=1);body=bpy.context.object;body.name='Merl broad asymmetric mineral mound'
    for v in body.data.vertices:
        q=v.co.copy();a=math.atan2(q.y,q.x);r=1+.065*math.sin(5*a+q.z*4)+.040*math.cos(9*a-q.z*3);x=q.x*.80*r;y=q.y*.60*r;z=.31+q.z*.30
        if q.z>0:
            z+=.065*math.sin(11*x+2*math.cos(7*y))*math.cos(9*y-2*x)*q.z+.016*math.sin(19*x+11*y)*q.z
        if q.z>0:
            z+=sum(height*math.exp(-((x-cx)/.17)**2-((y-cy)/.15)**2) for cx,cy,height in [(-.37,-.25,.11),(.03,-.33,.13),(.34,-.12,.09),(-.07,.15,.10)])*q.z
        x+=.13*math.exp(-((a-.12)/.45)**2)*max(0,1-abs(q.z));v.co=(x,y,z)
    body.data.materials.append(ore);body.data.materials.append(exposed)
    outline=[(-.14,.50),(.14,.50),(.135,.75),(.155,.95),(.17,1.14),(.16,1.34),(.08,1.35),(.055,1.15),(-.055,1.15),(-.085,1.40),(-.17,1.41),(-.18,1.13),(-.135,.88)]
    count=len(outline);verts=[(x,y,z) for y in [-.09,.23] for x,z in outline];faces=[tuple(reversed(range(count))),tuple(count+i for i in range(count))]+[(i,(i+1)%count,(i+1)%count+count,i+count) for i in range(count)]
    head=solid('Merl compact forked mineral head',verts,faces,ore);head.data.materials.append(exposed);bpy.context.view_layer.objects.active=head
    mod=head.modifiers.new('Worn rounded fork edges','BEVEL');mod.width=.025;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
    # Actual shoulder is part of the same ore head through a checked union.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(0,-.04,.64));shoulder=bpy.context.object
    for v in shoulder.data.vertices:v.co=(v.co.x*.20,v.co.y*.19,v.co.z*.14)
    shoulder.data.materials.append(ore);bpy.context.view_layer.objects.active=head;mod=head.modifiers.new('Continuous rounded shoulder','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=shoulder;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(shoulder,do_unlink=True)
    for index,obj in enumerate([body,head]):
        bpy.context.view_layer.objects.active=obj;noise=bpy.data.textures.new('Merl irregular used ore relief '+str(index),type='CLOUDS');noise.noise_scale=.12;noise.noise_depth=1;mod=obj.modifiers.new('Physical mineral relief','DISPLACE');mod.texture=noise;mod.texture_coords='GLOBAL';mod.strength=.025 if obj==body else .009;bpy.ops.object.modifier_apply(modifier=mod.name)
        for chip_index,(x,z) in enumerate([(-.20,.39),(.31,.26)] if obj==body else [(-.11,1.30),(.11,1.24)]):
            bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Planar before wear','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bpy.context.view_layer.update();hit,point,normal,_=obj.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.012,location=point+normal*.003);chip=bpy.context.object
            chip.data.materials.append(ore);chip.data.materials.append(exposed)
            for p in chip.data.polygons:p.material_index=1
            bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Minor physical chip '+str(chip_index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=chip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chip,do_unlink=True)
    bpy.context.view_layer.update();hit,point,normal,_=head.ray_cast(Vector((0,-4,.94)),Vector((0,1,0)));assert hit
    cylinder('Merl worn pale lens bezel',point+normal*.014,.110,.035,exposed,axis=normal)
    cylinder('Merl dark lens seat',point+normal*.035,.090,.020,dark,axis=normal)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=point+normal*.050);lens=bpy.context.object;lens.name='Merl pale blue front lens'
    for v in lens.data.vertices:q=v.co.copy();v.co=(q.x*.081,q.y*.028,q.z*.081)
    lens.data.materials.append(blue)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1);pulse=bpy.context.object;pulse.name='Merl source gold discharge'
    for v in pulse.data.vertices:
        q=v.co.copy();factor=1+.065*math.sin(7*q.x+9*q.z)*math.cos(8*q.y);v.co=q*factor
    pulse.data.materials.append(gold)
    # Authored24fps timing. Envelope follows the source rise/two bright lobes/fade.
    amplitudes=[0,.16,.30,.48,.66,.90,1,.52,.72,.90,1,.88,.70,.36,.16,0]
    for frame in range(1,34):
        index=min(15,max(0,(frame-1)/2));lo=int(index);blend=index-lo;amp=amplitudes[lo]*(1-blend)+amplitudes[min(15,lo+1)]*blend
        pulse.scale=(max(.0001,.125*amp),max(.0001,.11*amp),max(.0001,.19*amp));pulse.location=(0,.07,1.37+.10*amp) if amp>0 else (0,0,.10)
        for prop in ['location','scale']:pulse.keyframe_insert(data_path=prop,frame=frame)
    action=pulse.animation_data.action
    for fc in action.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    track=pulse.animation_data.nla_tracks.new();track.name='PlasmaDischarge';track.strips.new('PlasmaDischarge',1,action);pulse.animation_data.action=None
    bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=33;bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(1)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/105';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        # glTF omits unused material slots. Normalize actual used slots so the
        # native/import material comparison measures the same surface contract.
        used=sorted({polygon.material_index for polygon in obj.data.polygons});materials=[obj.data.materials[i] for i in used];mapping={old:new for new,old in enumerate(used)};indices=[mapping[polygon.material_index] for polygon in obj.data.polygons]
        obj.data.materials.clear()
        for material_slot in materials:obj.data.materials.append(material_slot)
        for polygon,index in zip(obj.data.polygons,indices):polygon.material_index=index
        # UV coordinates make the independently authored maps portable to glTF.
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if obj in [body,head]:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/1.9+point.y*.17+.5,point.z/1.45)
        if obj==pulse:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/2.2+.5,point.z/2.2+.5)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        bmesh.ops.remove_doubles(mesh,verts=list(mesh.verts),dist=1e-6)
        assert all(e.is_manifold for e in mesh.edges),obj.name
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        if obj==body:
            normals=[tuple((Vector(normals[loop])*.85+polygon.normal*.15).normalized()) for polygon in obj.data.polygons for loop in polygon.loop_indices]
        for polygon in obj.data.polygons:polygon.use_smooth=True
        obj.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000,triangles
    scratch=root/'artifacts/mikotaj-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/105',key='MK20',name='Merl',culture='mikotaj',
        footprint=[2,2],definition_class=17,construction_updates=35,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,
        author='sources/tools/blender/remaster_mikotaj_merl.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Low asymmetric ore mound,short forked head and pale blue front lens follow actual legacy and reviewed concept.',
                        'Actual operation overlays composed using descriptor offsets establish a gold pulse at/above the fork. Rigid scale/location encode the energetic envelope;duration/material/hidden profiles are authored. No turret rotation invented.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk20-concept-review.json',animation_clips=['PlasmaDischarge'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_MERL_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
