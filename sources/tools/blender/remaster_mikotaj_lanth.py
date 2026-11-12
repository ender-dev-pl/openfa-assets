"""Author MK15 Lanth from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/lanth';maps=root/'sources/materials/mikotaj/lanth'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25915);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[];terminal=[]
    colour_rng=random.Random(2591503);colour_layers=[]
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
            colours.extend([max(.015,min(1,c+cloud*1.8-stain*1.4+scratch+exposed*1.3)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.2+scratch)) for c in (.40,.19,.105)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            hot=math.exp(-((u-.5)/.23)**2-((v-.53)/.33)**2);terminal.extend([.38+.55*hot,.025+.28*hot,.012+.04*hot,1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2591507);layers=[]
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
            dx=(height[y*size+(x+1)%size]-height[y*size+(x-1)%size])*80
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*80;length=math.sqrt(1+dx*dx+dy*dy)
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
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=1.5
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    dark=material('Dark mineral recess interior',(.014,.021,.020),.35,.72)
    # Authored portable mottled lens colour/emission, never sampled from legacy.
    pixels=[];lens_rng=random.Random(2591509)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Pale cloaking lens insets',(.1,.3,.75),.18,.30,emission=.25)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
    # Source mineral knuckles are one closed union with overlapping sections.
    # Individual irregular polyhedral lobes preserve their crag shoulders.
    chunks=[]
    for index,(position,scale) in enumerate([((0,.03,1.00),(.56,.40,.97)),((-.38,-.03,.42),(.43,.43,.405)),((.39,.04,.31),(.43,.38,.295)),((0,-.17,.34),(.49,.40,.325)),((-.20,-.14,1.62),(.36,.31,.35)),((.21,-.10,1.56),(.31,.30,.32)),((-.10,.035,1.83),(.33,.27,.23)),((.05,.24,1.35),(.42,.25,.39))]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=position);obj=bpy.context.object
        for vertex in obj.data.vertices:vertex.co*=1+.11*math.sin(12*vertex.co.x+4*vertex.co.z+index)*math.cos(9*vertex.co.y-index)
        obj.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(ore);chunks.append(obj)
    body=chunks[0];body.name='Lanth continuous knobbly mineral body'
    for other in chunks[1:]:
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar ore union input','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Connected mineral knuckle','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=other;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(other,do_unlink=True)
    bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    # Restore source envelope after irregular lobe shaping, before cutting
    # the insets: roughness must not change the building's major proportions.
    lo=[min(v.co[a] for v in body.data.vertices) for a in range(3)];hi=[max(v.co[a] for v in body.data.vertices) for a in range(3)]
    for vertex in body.data.vertices:
        vertex.co.x=(vertex.co.x-(lo[0]+hi[0])*.5)*1.72/(hi[0]-lo[0]);vertex.co.y=(vertex.co.y-(lo[1]+hi[1])*.5)*1.13/(hi[1]-lo[1]);vertex.co.z=.015+(vertex.co.z-lo[2])*2.045/(hi[2]-lo[2])
    body.data.materials.append(exposed);body.data.materials.append(dark)
    def cut(obj,label):
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before '+label,'TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
        mod=body.modifiers.new(label,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=obj;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(obj,do_unlink=True);assert len(body.data.polygons)>0
    def recess(x,z,width,height,label):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        centre=Vector((x,point.y-.07,z));bpy.ops.mesh.primitive_cube_add(size=1,location=centre);cutter=bpy.context.object;depth=.35
        if label=='Source two-lens vertical inset':
            cheeks=[]
            for sx in [x-.22,x+.22]:
                for sz in [.205,.52]:
                    hit,sample,_,_=body.ray_cast(Vector((sx,-4,sz)),Vector((0,1,0)));assert hit;cheeks.append(sample.y)
            floor=max(cheeks)+.065;assert floor<.10,'Inset must remain inside solid ore'
            depth=2*(floor-centre.y)
        cutter.scale=(width,depth,height);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        mod=cutter.modifiers.new('Subtle worn recess corners','BEVEL');mod.width=.018;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name)
        for mat in [ore,exposed,dark]:cutter.data.materials.append(mat)
        for face in cutter.data.polygons:face.material_index=2
        cut(cutter,label);return point.y-.07+depth*.5
    lens_y=recess(-.17,.38,.35,.70,'Source two-lens vertical inset')
    recess(.32,.47,.12,.19,'Source lower right recess');recess(.28,1.03,.09,.16,'Source upper right recess')
    # Actual small chips complement independently authored mineral textures.
    for index,(x,z) in enumerate([(-.44,.82),(-.18,1.71),(.26,1.39),(.51,.27)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.018,location=point+normal*.005);chip=bpy.context.object
        for mat in [ore,exposed,dark]:chip.data.materials.append(mat)
        for face in chip.data.polygons:face.material_index=1
        cut(chip,'Small exposed use chip '+str(index))
    bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);assert all(e.is_manifold for e in bm.edges);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Fine mineral relief sampling','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=1;bpy.ops.object.modifier_apply(modifier=mod.name)
    noise=bpy.data.textures.new('Lanth fine weathered mineral relief',type='CLOUDS');noise.noise_scale=.075;noise.noise_depth=1;mod=body.modifiers.new('Minor used mineral dents','DISPLACE');mod.texture=noise;mod.texture_coords='GLOBAL';mod.strength=.045;bpy.ops.object.modifier_apply(modifier=mod.name)
    for index,z in enumerate([.205,.52]):
        for label,offset,radius,depth,mat in [('dark seat',-.004,.135,.050,dark),('pale lens',-.032,.112,.040,blue)]:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(-.17,lens_y+offset,z));obj=bpy.context.object;obj.name='Lanth '+label+' '+str(index);obj.scale=(radius,depth,radius);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/100';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
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
        if obj==body:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/1.9+point.y*.17+.5,point.z/2.15+point.y*.13)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        if obj==body:
            flaps=[f for f in mesh.faces if f.calc_area()<1e-6 and sum(len(e.link_faces)==1 for e in f.edges)==2 and sum(len(e.link_faces)==3 for e in f.edges)==1]
            bmesh.ops.delete(mesh,geom=flaps,context='FACES');assert all(e.is_manifold for e in mesh.edges),'Unresolved mineral-mound topology'
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        if obj==body:
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/100',key='MK15',name='Lanth',culture='mikotaj',
        footprint=[2,2],definition_class=255,construction_updates=55,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,
        author='sources/tools/blender/remaster_mikotaj_lanth.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Compact tapering knobbly mineral body, two stacked pale lenses in one front inset and two small right recesses follow actual original views.',
                        'Source overrides concept extra lowest slot. Hidden section and physical cloaking engineering unknown. No unsupported visible operating clip.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk15-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_LANTH_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
