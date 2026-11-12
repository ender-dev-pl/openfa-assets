"""Author MK08 Fa-lanth from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/fa-lanth';maps=root/'sources/materials/mikotaj/fa-lanth'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25908);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    colour_rng=random.Random(2590803);colour_layers=[]
    for cells,weight in [(5,.18),(19,.08),(67,.025)]:
        grid=[[colour_rng.uniform(-.5,.5) for _ in range(cells+1)] for _ in range(cells+1)]
        for row in grid:row[-1]=row[0]
        colour_layers.append((cells,weight,grid))
    def mineral_field(u,v):
        value=0
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
            colours.extend([max(.015,min(1,c+cloud-stain+scratch+exposed)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*2.8-stain*1.7+scratch)) for c in (.43,.30,.095)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2590807);layers=[]
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
            dx=(height[y*size+(x+1)%size]-height[y*size+(x-1)%size])*26
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*26;length=math.sqrt(1+dx*dx+dy*dy)
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
        if image and image!='brass-base-colour':
            texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=images['mineral-fracture-normal']
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.9
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    dark=material('Dark mineral cleft interior',(.022,.032,.036),.74,.31)
    # Authored portable mottled lens colour/emission, never sampled from legacy.
    pixels=[];lens_rng=random.Random(2590809)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Pale-blue Fa-lanth oval inset',(.1,.3,.75),.18,.16,emission=.45)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    rings=[(.04,.68,.52,0),(.18,.77,.58,0),(.45,.72,.55,.01),(.84,.60,.46,0),(1.20,.51,.40,.02),(1.52,.36,.27,-.04),(1.78,.18,.17,-.045),(1.86,.10,.11,-.035)]
    n=48;vertices=[];faces=[]
    for row,(z,rx,ry,dx) in enumerate(rings):
        for i in range(n):
            a=i*2*math.pi/n;relief=1+.045*math.cos(5*a+.4)+.023*math.sin(9*a+row*.7)
            vertices.append((dx+rx*math.cos(a)*relief,ry*math.sin(a)*relief,z+.006*math.sin(7*a+row)))
    for row in range(len(rings)-1):
        for i in range(n):faces.append((row*n+i,row*n+(i+1)%n,(row+1)*n+(i+1)%n,(row+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]);mesh=bpy.data.meshes.new('Fa-lanth continuous mineral mound');mesh.from_pydata(vertices,[],faces);mesh.update();body=bpy.data.objects.new('Fa-lanth continuous mineral mound',mesh);bpy.context.collection.objects.link(body);body.data.materials.append(ore);body.data.materials.append(exposed);bpy.context.view_layer.objects.active=body
    sub=body.modifiers.new('Mineral surface sampling','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name)
    noise=bpy.data.textures.new('Natural mineral mound relief',type='CLOUDS');noise.noise_scale=.16;noise.noise_depth=1;mod=body.modifiers.new('Worn mineral stress relief','DISPLACE');mod.texture=noise;mod.strength=.043;mod.texture_coords='GLOBAL';bpy.ops.object.modifier_apply(modifier=mod.name)
    mod=body.modifiers.new('Planar input for shallow clefts','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bpy.context.view_layer.update()
    def seat(x,z):
        inv=body.matrix_world.inverted();hit,point,normal,_=body.ray_cast(inv@Vector((x,-4,z)),inv.to_3x3()@Vector((0,1,0)));assert hit,('Missing mineral seating',x,z)
        return body.matrix_world@point,(body.matrix_world.to_3x3()@normal).normalized()
    lenspoint,lensnormal=seat(0,1.06)
    clefts=[[(point,normal) for point,normal in [seat(sign*(.10+.22*i/10),1.00-.36*i/10) for i in range(11)]] for sign in [-1,1]]
    def tube(name,samples,radius,offset,mat):
        curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=radius;curve.bevel_resolution=2;curve.use_fill_caps=True;line=curve.splines.new('POLY');line.points.add(len(samples)-1)
        for vertex,(point,normal) in zip(line.points,samples):vertex.co=(*(point+normal*offset),1)
        obj=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(obj)
        if mat:obj.data.materials.append(mat)
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH');return bpy.context.object
    for i,samples in enumerate(clefts):
        cutter=tube('Temporary mineral cleft '+str(i),samples,.038,.004,None);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Actual shallow mineral cleft '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
        tube('Dark diagonal cleft '+str(i),samples,.021,-.039,dark)
    cutter=cylinder('Temporary oval inset socket',lenspoint+lensnormal*.003,.105,.24,dark,axis=lensnormal,vertices=48);cutter.scale.x=1.35;cutter.scale.y=.65;bpy.context.view_layer.objects.active=cutter;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Actual horizontal oval socket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    for name,radius,depth,offset,mat in [('Oval inset worn rim',.102,.039,-.008,exposed),('Oval inset dark seal',.091,.020,.017,dark)]:
        obj=cylinder(name,lenspoint+lensnormal*offset,radius,depth,mat,axis=lensnormal,vertices=48);obj.scale.x=1.35;obj.scale.y=.65;bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=lenspoint+lensnormal*.031);obj=bpy.context.object;obj.name='Single horizontal pale-blue oval';obj.scale=(.083*1.35,.083*.65,.025);obj.rotation_euler=lensnormal.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(blue)
    # Small authored wear cuts expose mineral alloy; no added structural panels.
    for index,(x,z,radius) in enumerate([(-.36,.45,.040),(.42,.82,.050),(-.20,1.40,.040),(.16,.35,.050),(.25,1.15,.035)]):
        point,normal=seat(x,z);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=radius,location=point+normal*(radius*.16));chip=bpy.context.object;chip.name='Temporary irregular wear chip '+str(index);chip.scale.z=.50;chip.rotation_euler=normal.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);chip.data.materials.append(ore);chip.data.materials.append(exposed)
        for polygon in chip.data.polygons:polygon.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Shallow worn mineral chip '+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=chip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chip,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/093';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
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
        if obj.name in ['Fa-lanth continuous mineral mound']:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x,-point.y)/(2*math.pi)+.5,point.z/1.90))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        if obj==body:
            flaps=[f for f in mesh.faces if f.calc_area()<1e-6 and sum(len(e.link_faces)==1 for e in f.edges)==2 and sum(len(e.link_faces)==3 for e in f.edges)==1]
            bmesh.ops.delete(mesh,geom=flaps,context='FACES');assert all(e.is_manifold for e in mesh.edges),'Unresolved mineral-mound topology'
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        if obj.name in ['Fa-lanth continuous mineral mound']:
            normals=[tuple((Vector(normals[loop])*.65+polygon.normal*.35).normalized()) for polygon in obj.data.polygons for loop in polygon.loop_indices]
        for polygon in obj.data.polygons:polygon.use_smooth=True
        obj.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000,triangles
    scratch=root/'artifacts/mikotaj-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/093',key='MK08',name='Fa-lanth',culture='mikotaj',
        footprint=[2,2],definition_class=10,construction_updates=50,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,
        author='sources/tools/blender/remaster_mikotaj_fa_lanth.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Continuous blunt mineral cone, one horizontal oval inset and two short downward-splaying dark clefts follow legacy; exact profiles and inset engineering are authored.',
                        'Catalogue Fa-lanth is described as Silence in original functional text; spiritual purpose is deliberately unspecified. No invented interior, ceremony or operating cycle.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk08-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_FA_LANTH_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
