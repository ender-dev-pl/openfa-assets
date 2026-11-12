"""Author MK16 Sharir from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/sharir';maps=root/'sources/materials/mikotaj/sharir'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25916);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    colour_rng=random.Random(2591603);colour_layers=[]
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
            exposed=.15*max(0,min(1,(cloud+.005)/.055))
            scratch=.075 if (x*37+y*79)%1237<2 else 0
            pale_trace=.085*math.exp(-((u-.58-.035*math.sin(13*v))/.080)**2)*max(0,min(1,(v-.36)*7))*(.65+.35*math.sin(27*v)**2)
            colours.extend([max(.015,min(1,c+cloud*1.5-stain+scratch+exposed+pale_trace)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.4+scratch)) for c in (.46,.21,.16)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            orm.extend([1,max(.15,min(.8,.45+stain*1.5-cloud*1.8)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2591607);layers=[]
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
                    sharir=max(0,min(1,(math.sin(31*v+phase)+.25)*2))
                    value-=.012*math.exp(-((u-vein)/.0035)**2)*sharir
            height.append(value)
    normals=[]
    for y in range(size):
        for x in range(size):
            dx=(height[y*size+(x+1)%size]-height[y*size+(x-1)%size])*65
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*65;length=math.sqrt(1+dx*dx+dy*dy)
            normals.extend([.5-.5*dx/length,.5-.5*dy/length,.5+.5/length,1])
    images={}
    for name,pixels in [('mineral-base-colour',colours),('copper-fitting-base-colour',gold),('exposed-ridge-base-colour',ridge),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
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
        if image and image not in ['copper-fitting-base-colour','red-terminal-colour']:
            texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=images['mineral-fracture-normal']
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=1.25
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    brass=material('Tarnished reddish copper fitting',(.46,.21,.16),image='copper-fitting-base-colour')
    dark=material('Dark mineral inset interior',(.035,.060,.045),.45,.75)
    # Boolean-unioned ore lobes preserve one connected body, not loose props.
    pixels=[];lens_rng=random.Random(2591609)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.55+.15*math.sin(11*u+4*math.sin(7*v))+.12*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.025,.025);pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Pale production-focuser insets',(.15,.32,.65),.18,.28,emission=.25);node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def apply(obj,kind,label,**values):
        bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(label,kind)
        for key,value in values.items():setattr(mod,key,value)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    def ore_chunk(name,position,scale,index):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=position);obj=bpy.context.object;obj.name=name
        for vertex in obj.data.vertices:vertex.co*=1+.080*math.sin(12*vertex.co.x+4*vertex.co.z+index)*math.cos(9*vertex.co.y-index)
        obj.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(ore);return obj
    def union(obj,other):
        apply(obj,'TRIANGULATE','Planar union input');apply(obj,'BOOLEAN','Connected source mineral knuckle',operation='UNION',solver='EXACT',object=other);bpy.data.objects.remove(other,do_unlink=True)
    def bake(obj):
        bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    base=ore_chunk('Sharir irregular low ore footing',(0,.02,.28),(.67,.48,.27),1)
    for index,(position,scale) in enumerate([((-.40,-.04,.27),(.40,.39,.25)),((.41,.03,.30),(.40,.40,.28))]):union(base,ore_chunk('Source footing knuckle',position,scale,index+2))
    bake(base)
    head=ore_chunk('Sharir upright ovoid mineral mass',(-.06,.04,1.76),(.67,.37,.75),4);bake(head)
    # Lower copper fitting and its actual narrow support are one closed volume.
    profiles=[(.20,-.24,-.20,.20,.18),(.30,-.24,-.20,.35,.26),(.44,-.23,-.18,.46,.30),(.61,-.18,-.11,.43,.27),(.77,-.13,-.04,.29,.21),(.90,-.10,.015,.18,.15),(1.10,-.08,.04,.16,.13),(1.19,-.07,.04,.13,.12)]
    n=48;vertices=[];faces=[]
    for j,(z,x,y,rx,ry) in enumerate(profiles):
        for i in range(n):
            a=i*math.tau/n;rr=1+.018*math.sin(5*a+.4*j);vertices.append((x+rx*math.cos(a)*rr,y+ry*math.sin(a)*rr,z+.003*math.sin(7*a+j)))
    for j in range(len(profiles)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profiles)-1)*n+i for i in range(n))]
    mesh=bpy.data.meshes.new('Sloping copper fitting with narrow neck');mesh.from_pydata(vertices,[],faces);mesh.update();copper=bpy.data.objects.new('Sharir lower copper fitting and support',mesh);bpy.context.collection.objects.link(copper);copper.data.materials.append(brass)
    # Sloping copper shoulder across the right of the footing, not selection ink.
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.28,.08,.52));strap=bpy.context.object;strap.scale=(.73,.10,.10);strap.rotation_euler[1]=.65;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);strap.data.materials.append(brass);apply(strap,'BEVEL','Worn copper shoulder edges',width=.025,segments=3);union(copper,strap)
    for obj in [base,head,copper]:
        obj.data.materials.append(exposed);obj.data.materials.append(dark)
    def cut(obj,cutter,label):
        apply(obj,'TRIANGULATE','Planar cut input');apply(obj,'BOOLEAN',label,operation='DIFFERENCE',solver='EXACT',object=cutter);bpy.data.objects.remove(cutter,do_unlink=True)
    def recess(obj,x,z,radius,name):
        bpy.context.view_layer.update();hit,point,normal,_=obj.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=point);cutter=bpy.context.object;cutter.scale=(radius*1.25,.055,radius*1.25);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for mat in obj.data.materials:cutter.data.materials.append(mat)
        for polygon in cutter.data.polygons:polygon.material_index=2
        cut(obj,cutter,'Actual '+name+' inset recess')
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=point+Vector((0,.015,0)));lens=bpy.context.object;lens.name='Sharir '+name+' pale inset';lens.scale=(radius,.030,radius);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);lens.data.materials.append(blue)
    recess(head,-.35,2.12,.060,'small upper');recess(copper,-.23,.46,.125,'larger lower')
    for obj,samples in [(base,[(-.37,.31),(.43,.22)]),(head,[(-.23,2.30),(.26,1.72),(-.35,1.52)])]:
        for index,(x,z) in enumerate(samples):
            bpy.context.view_layer.update();hit,point,normal,_=obj.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.018,location=point+normal*.005);chip=bpy.context.object
            for mat in obj.data.materials:chip.data.materials.append(mat)
            for polygon in chip.data.polygons:polygon.material_index=1
            cut(obj,chip,'Exposed small mineral wear chip '+str(index))
    for obj in [base,head,copper]:
        bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges),obj.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(obj.data);bm.free()
        apply(obj,'SUBSURF','Fine surface sampling',subdivision_type='SIMPLE',levels=1)
        if obj in [base,head]:
            noise=bpy.data.textures.new(obj.name+' worn mineral relief',type='CLOUDS');noise.noise_scale=.075;noise.noise_depth=1;apply(obj,'DISPLACE','Minor mineral surface dents',texture=noise,texture_coords='GLOBAL',strength=.035)
    micro=[];micro_rng=random.Random(2591611)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;dx=.020*math.sin(247*u+4*math.sin(19*v))+micro_rng.uniform(-.008,.008);dy=.009*math.sin(103*v+13*u);micro.extend([.5+.5*dx,.5+.5*dy,.5+.5*math.sqrt(1-dx*dx-dy*dy),1])
    image=bpy.data.images.new('copper-use-normal',width=size,height=size,alpha=True);image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(micro);path=maps/'copper-use-normal.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();texture=brass.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image;normal=brass.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.65;brass.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);brass.node_tree.links.new(normal.outputs['Normal'],brass.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/101';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
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
        if obj in [base,head,copper]:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/1.85+point.y*.17+.5,point.z/2.65+point.y*.13)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        if obj in [base,head,copper]:
            flaps=[f for f in mesh.faces if f.calc_area()<1e-6 and sum(len(e.link_faces)==1 for e in f.edges)==2 and sum(len(e.link_faces)==3 for e in f.edges)==1]
            bmesh.ops.delete(mesh,geom=flaps,context='FACES');assert all(e.is_manifold for e in mesh.edges),'Unresolved mineral-mound topology'
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        if obj in [base,head]:
            normals=[tuple((Vector(normals[loop])*.75+polygon.normal*.25).normalized()) for polygon in obj.data.polygons for loop in polygon.loop_indices]
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/101',key='MK16',name='Sharir',culture='mikotaj',
        footprint=[3,3],definition_class=7,construction_updates=34,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,
        author='sources/tools/blender/remaster_mikotaj_sharir.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Upright asymmetric mineral ovoid on narrow copper support above lower sloping copper fitting and low ore footing follows actual original views.',
                        'Smaller upper and larger lower pale insets retained. Hidden sections and focusing/manufacturing engineering unknown; no unsupported operating clip.'],
        scale_contract='3x3 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk16-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_SHARIR_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
