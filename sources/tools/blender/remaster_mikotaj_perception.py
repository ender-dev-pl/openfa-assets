"""Author MK13 Perception from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/perception';maps=root/'sources/materials/mikotaj/perception'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25913);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[];terminal=[]
    colour_rng=random.Random(2591303);colour_layers=[]
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
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.2+scratch)) for c in (.40,.19,.105)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            hot=math.exp(-((u-.5)/.23)**2-((v-.53)/.33)**2);terminal.extend([.38+.55*hot,.025+.28*hot,.012+.04*hot,1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2591307);layers=[]
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
    for name,pixels in [('mineral-base-colour',colours),('brass-base-colour',gold),('red-terminal-colour',terminal),('exposed-ridge-base-colour',ridge),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
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
    brass=material('Worn copper sensor trace',(.43,.30,.095),image='brass-base-colour')
    red=material('Amber-red sensor status cells',(.45,.055,.025),.25,.28,image='red-terminal-colour',emission=.6)
    red_shader=red.node_tree.nodes.get('Principled BSDF');red_texture=next(node for node in red.node_tree.nodes if node.type=='TEX_IMAGE' and node.image==images['red-terminal-colour']);red.node_tree.links.new(red_texture.outputs['Color'],red_shader.inputs['Emission Color'])
    dark=material('Dark mineral cleft interior',(.022,.032,.036),.74,.31)
    # Authored portable mottled lens colour/emission, never sampled from legacy.
    pixels=[];lens_rng=random.Random(2591309)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Upper blue sensor inset',(.1,.3,.75),.18,.16,emission=.45)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
    # Connected low ore bed with source-specific knuckles, no loose sphere pile.
    n=64;steps=14;knuckles=[(-.24,.10,.94,.38),(.07,.08,.65,.35),(.34,-.03,.43,.29),(.04,-.23,.30,.27),(.52,.14,.22,.23)]
    def top(x,y):
        return .16+max(h*math.exp(-(((x-cx)**2+(y-cy)**2)/(radius*radius))**2) for cx,cy,h,radius in knuckles)+.012*math.sin(18*x+5*y)*math.cos(17*y)
    vertices=[(.06,0,top(.06,0))]
    for j in range(1,steps+1):
        fraction=j/steps
        for i in range(n):
            angle=i*math.tau/n;outline=1+.08*math.sin(3*angle+.8)+.055*math.cos(5*angle-.2);x=.06+.72*fraction*outline*math.cos(angle);y=.49*fraction*outline*math.sin(angle);vertices.append((x,y,top(x,y)))
    faces=[(0,1+i,1+(i+1)%n) for i in range(n)]
    for j in range(steps-1):
        for i in range(n):faces.append((1+j*n+i,1+(j+1)*n+i,1+(j+1)*n+(i+1)%n,1+j*n+(i+1)%n))
    outer=1+(steps-1)*n;bottom=len(vertices)
    for i in range(n):vertices.append((vertices[outer+i][0],vertices[outer+i][1],.025))
    for i in range(n):faces.append((outer+i,bottom+i,bottom+(i+1)%n,outer+(i+1)%n))
    faces.append(tuple(reversed(range(bottom,bottom+n))))
    body=solid('Perception connected mineral knuckle foundation',vertices,faces,ore);body.data.materials.append(exposed)
    # Thin uneven mineral blade at the rear-left edge of the low foundation.
    rows=[(.03,-.45,.045,.13,.12),(.38,-.47,.025,.135,.115),(.78,-.48,.015,.115,.10),(1.35,-.49,.015,.105,.095),(1.85,-.48,.015,.095,.085),(2.30,-.50,.015,.085,.075),(2.80,-.48,.02,.075,.065),(3.15,-.49,.02,.055,.05),(3.42,-.45,.02,.030,.027)]
    n=12;vertices=[];faces=[]
    for j,(z,x,y,rx,ry) in enumerate(rows):
        for i in range(n):
            angle=i*math.tau/n;relief=1+.07*math.sin(5*angle+j*.8);vertices.append((x+rx*1.4*math.cos(angle)*relief,y+ry*1.4*math.sin(angle)*relief,z+.004*math.sin(3*angle+j)))
    for j in range(len(rows)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(rows)-1)*n+i for i in range(n))]
    mast=solid('Perception slender rear-left mineral mast',vertices,faces,ore);mast.data.materials.append(exposed)
    for obj,levels,strength in [(body,1,.030),(mast,2,.018)]:
        bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Ore relief sampling','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=levels;bpy.ops.object.modifier_apply(modifier=mod.name)
        noise=bpy.data.textures.new(obj.name+' weathering',type='CLOUDS');noise.noise_scale=.10;mod=obj.modifiers.new('Material appropriate worn relief','DISPLACE');mod.texture=noise;mod.strength=strength;mod.texture_coords='GLOBAL';bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Planar wear input','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
    for index,(x,y) in enumerate([(-.20,-.15),(.15,-.20),(.37,.05),(-.45,.07)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.025,location=point+normal*.005);chip=bpy.context.object;chip.data.materials.append(ore);chip.data.materials.append(exposed)
        for polygon in chip.data.polygons:polygon.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Mineral foundation chip '+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=chip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chip,do_unlink=True)
    def seat(x,z):
        bpy.context.view_layer.update();hit,point,normal,_=mast.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit,('Missing mast seat',x,z)
        return point,normal.normalized()
    # Small physical mineral chips preserve the overall slender silhouette.
    for index,(x,z,radius) in enumerate([(-.49,.63,.018),(-.55,1.65,.013),(-.45,2.18,.012),(-.51,2.93,.012)]):
        point,normal=seat(x,z);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=radius,location=point+normal*radius*.2);chip=bpy.context.object;chip.data.materials.append(ore);chip.data.materials.append(exposed)
        for polygon in chip.data.polygons:polygon.material_index=1
        bpy.context.view_layer.objects.active=mast;mod=mast.modifiers.new('Minor mineral chip '+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=chip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chip,do_unlink=True)
    point,normal=seat(-.525,2.53)
    for name,offset,scale,mat in [('Upper blue inset worn border',.002,(.045,.019,.140),exposed),('Upper blue inset dark seal',.013,(.037,.020,.131),dark),('Single upper blue vertical inset',.025,(.030,.018,.120),blue)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=point+normal*offset);obj=bpy.context.object;obj.name=name;obj.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
    def plate(name,centre,width,height,depth,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);obj=bpy.context.object;obj.name=name;obj.scale=(width,depth,height);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat);mod=obj.modifiers.new('Tiny worn cell edge','BEVEL');mod.width=.003;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);return obj
    for i,z in enumerate([.89,1.035,1.18,1.325]):
        point,normal=seat(-.485,z)
        plate('Lower status cell border '+str(i),point+normal*.006,.055,.085,.024,exposed)
        plate('Lower status cell dark seal '+str(i),point+normal*.018,.045,.075,.020,dark)
        plate('Lower amber-red status cell '+str(i),point+normal*.033,.036,.060,.013,red)
    controls=[(-.475,1.46),(-.475,1.76),(-.445,1.88),(-.445,2.16),(-.452,2.44),(-.447,2.80),(-.423,2.92),(-.423,3.04),(-.463,3.10),(-.452,3.32)]
    samples=[]
    for i in range(len(controls)-1):
        for j in range(5):
            t=j/5;x=controls[i][0]*(1-t)+controls[i+1][0]*t;z=controls[i][1]*(1-t)+controls[i+1][1]*t;point,normal=seat(x,z);samples.append((point,normal))
    samples.append(seat(*controls[-1]));vertices=[];faces=[];n=12
    for i,(point,normal) in enumerate(samples):
        tangent=(samples[min(i+1,len(samples)-1)][0]-samples[max(i-1,0)][0]).normalized();across=normal.cross(tangent).normalized();centre=point+normal*.009
        for j in range(n):
            a=j*math.tau/n;vertices.append(tuple(centre+across*.019*math.cos(a)+normal*.014*math.sin(a)))
    for i in range(len(samples)-1):
        for j in range(n):faces.append((i*n+j,i*n+(j+1)%n,(i+1)*n+(j+1)%n,(i+1)*n+j))
    faces += [tuple(reversed(range(n))),tuple((len(samples)-1)*n+j for j in range(n))]
    solid('Perception surface-seated copper dogleg trace',vertices,faces,brass)
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.018,radius2=.006,depth=.25,location=(-.45,.002,3.535));obj=bpy.context.object;obj.name='Perception slender bare copper summit stalk';obj.data.materials.append(brass)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/098';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
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
        if obj in [body,mast]:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x+(.48 if obj==mast else -.06),-point.y)/(2*math.pi)+.5,point.z/3.75))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        if obj.name.startswith('Lower amber-red status cell '):
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/.036+.5,point.z/.060+.5)
        if obj.name=='Perception surface-seated copper dogleg trace':
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                index=loop.vertex_index;uv.data[loop.index].uv=((index%12)/12,(index//12)/(len(samples)-1))
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        if obj==body:
            flaps=[f for f in mesh.faces if f.calc_area()<1e-6 and sum(len(e.link_faces)==1 for e in f.edges)==2 and sum(len(e.link_faces)==3 for e in f.edges)==1]
            bmesh.ops.delete(mesh,geom=flaps,context='FACES');assert all(e.is_manifold for e in mesh.edges),'Unresolved mineral-mound topology'
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        if obj in [body,mast]:
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/098',key='MK13',name='Perception',culture='mikotaj',
        footprint=[2,2],definition_class=16,construction_updates=36,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,
        author='sources/tools/blender/remaster_mikotaj_perception.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Rear-left slender mineral mast and copper stalk rise from a low right-projecting knuckle foundation; one upper blue inset and four lower amber-red cells follow actual original views.',
                        'Copper trace thinner than ImageGen concept to match original. Hidden sections, joint engineering and wear authored. No unobserved rotating/scanning mechanism.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk13-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_PERCEPTION_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
