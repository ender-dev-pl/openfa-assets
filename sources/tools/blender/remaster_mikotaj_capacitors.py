"""Author MK14 Capacitors from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/capacitors';maps=root/'sources/materials/mikotaj/capacitors'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25914);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    colour_rng=random.Random(2591403);colour_layers=[]
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
            colours.extend([max(.015,min(1,c+cloud-stain+scratch+exposed)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.4+scratch)) for c in (.46,.21,.16)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            orm.extend([1,max(.15,min(.8,.45+stain*1.5-cloud*1.8)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2591407);layers=[]
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
                    capacitors=max(0,min(1,(math.sin(31*v+phase)+.25)*2))
                    value-=.012*math.exp(-((u-vein)/.0035)**2)*capacitors
            height.append(value)
    normals=[]
    for y in range(size):
        for x in range(size):
            dx=(height[y*size+(x+1)%size]-height[y*size+(x-1)%size])*26
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*26;length=math.sqrt(1+dx*dx+dy*dy)
            normals.extend([.5-.5*dx/length,.5-.5*dy/length,.5+.5/length,1])
    images={}
    for name,pixels in [('mineral-base-colour',colours),('copper-cap-base-colour',gold),('exposed-ridge-base-colour',ridge),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
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
        if image and image not in ['copper-cap-base-colour','red-terminal-colour']:
            texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=images['mineral-fracture-normal']
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.9
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    brass=material('Tarnished reddish copper crown',(.46,.21,.16),image='copper-cap-base-colour')
    dark=material('Dark mineral cleft interior',(.035,.060,.045),.45,.75)
    # Boolean-unioned ore lobes preserve one connected body, not loose props.
    chunks=[]
    for index,(position,scale) in enumerate([((-.13,.07,.30),(.64,.52,.36)),((-.50,-.03,.22),(.36,.36,.23)),((.03,-.27,.20),(.43,.29,.22)),((.38,-.10,.19),(.40,.32,.20)),((.65,.12,.15),(.23,.25,.16)),((-.15,.30,.31),(.44,.32,.28))]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=position);obj=bpy.context.object;obj.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for vertex in obj.data.vertices:vertex.co*=1+.035*math.sin(17*vertex.co.x+index)*math.cos(13*vertex.co.y-index)
        obj.data.materials.append(ore);chunks.append(obj)
    body=chunks[0];body.name='Capacitors connected irregular ore mound';bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    for chunk in chunks[1:]:
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Union connected ore lobe','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=chunk;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chunk,do_unlink=True);print('ORE_UNION_FACES',len(body.data.polygons),flush=True);assert len(body.data.polygons)>0,'Ore union must remain nonempty'
    body.data.materials.clear();body.data.materials.append(ore);body.data.materials.append(exposed);body.data.materials.append(dark)
    mod=body.modifiers.new('Stable cut input','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.mesh.primitive_cube_add(size=2,location=(0,0,1.015));clip=bpy.context.object;clip.scale=(2,2,1);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Ground seating plane','BOOLEAN');mod.operation='INTERSECT';mod.solver='EXACT';mod.object=clip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(clip,do_unlink=True);print('ORE_GROUND_CLIP_FACES',len(body.data.polygons),flush=True);assert len(body.data.polygons)>0,'Ground clipping must retain ore volume'
    bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((-.50,-4,.35)),Vector((0,1,0)));assert hit
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=point+normal*.025);cutter=bpy.context.object
    for vertex in cutter.data.vertices:vertex.co*=1+.12*math.sin(13*vertex.co.x+8*vertex.co.z)
    cutter.scale=(.100,.060,.195);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for mat in [ore,exposed,dark]:cutter.data.materials.append(mat)
    for polygon in cutter.data.polygons:polygon.material_index=2
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Source left-front dark cleft','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);print('ORE_AFTER_CUT',len(body.data.polygons),flush=True);assert len(body.data.polygons)>0,'Ore cut must retain body'
    for index,(x,y) in enumerate([(-.30,-.28),(.12,-.31),(.38,.03),(.52,.23)]):
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar input before each wear cut','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.022,location=point+normal*.004);cutter=bpy.context.object
        for mat in [ore,exposed,dark]:cutter.data.materials.append(mat)
        for polygon in cutter.data.polygons:polygon.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Exposed mineral chip '+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True);print('ORE_AFTER_CUT',len(body.data.polygons),flush=True);assert len(body.data.polygons)>0,'Ore cut must retain body'
    bpy.context.view_layer.objects.active=body
    mesh=bmesh.new();mesh.from_mesh(body.data);bmesh.ops.remove_doubles(mesh,verts=list(mesh.verts),dist=1e-6)
    flaps=[f for f in mesh.faces if f.calc_area()<1e-6 and sum(len(e.link_faces)==1 for e in f.edges)==2 and sum(len(e.link_faces)==3 for e in f.edges)==1]
    bmesh.ops.delete(mesh,geom=flaps,context='FACES');assert all(e.is_manifold for e in mesh.edges),'Closed ore before fine relief';bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(body.data);mesh.free()
    mod=body.modifiers.new('Fine non-panel mineral relief sampling','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=1;bpy.ops.object.modifier_apply(modifier=mod.name)
    noise=bpy.data.textures.new('Small natural ore use relief',type='CLOUDS');noise.noise_scale=.065;noise.noise_depth=1;mod=body.modifiers.new('Fine worn ore surface','DISPLACE');mod.texture=noise;mod.strength=.012;mod.texture_coords='GLOBAL';bpy.ops.object.modifier_apply(modifier=mod.name)
    profiles=[(.46,.23),(.59,.34),(.65,.35),(.70,.32),(.76,.27),(.790,.22),(.790,.16),(.755,.12),(.755,.055),(.755,.012)];n=64;vertices=[];faces=[]
    for row,(z,radius) in enumerate(profiles):
        for i in range(n):
            angle=i*math.tau/n;rr=radius*(1+.015*math.sin(5*angle+.6));vertices.append((-.13+rr*math.cos(angle),.10+rr*math.sin(angle),z+(.001*math.sin(7*angle+row*.4) if radius>.20 else 0)))
    for row in range(len(profiles)-1):
        for i in range(n):faces.append((row*n+i,row*n+(i+1)%n,(row+1)*n+(i+1)%n,(row+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profiles)-1)*n+i for i in range(n))]
    mesh=bpy.data.meshes.new('Rounded copper crown with shallow depression');mesh.from_pydata(vertices,[],faces);mesh.update();cap=bpy.data.objects.new('Capacitors seated reddish copper crown',mesh);bpy.context.collection.objects.link(cap);cap.data.materials.append(brass);bpy.context.view_layer.objects.active=cap
    mod=cap.modifiers.new('Fine copper dent sampling','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=1;bpy.ops.object.modifier_apply(modifier=mod.name)
    micro=[];micro_rng=random.Random(2591411)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;dx=.020*math.sin(247*u+4*math.sin(19*v))+micro_rng.uniform(-.008,.008);dy=.009*math.sin(103*v+13*u);micro.extend([.5+.5*dx,.5+.5*dy,.5+.5*math.sqrt(1-dx*dx-dy*dy),1])
    image=bpy.data.images.new('copper-use-normal',width=size,height=size,alpha=True);image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(micro);path=maps/'copper-use-normal.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();texture=brass.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image;normal=brass.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35;brass.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);brass.node_tree.links.new(normal.outputs['Normal'],brass.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/099';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    for obj in meshes:
        print('AUTHOR_MESH_FACES',obj.name,len(obj.data.polygons),flush=True);assert len(obj.data.polygons)>0,obj.name
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        # glTF omits unused material slots. Normalize actual used slots so the
        # native/import material comparison measures the same surface contract.
        used=sorted({polygon.material_index for polygon in obj.data.polygons});materials=[obj.data.materials[i] for i in used];mapping={old:new for new,old in enumerate(used)};indices=[mapping[polygon.material_index] for polygon in obj.data.polygons]
        obj.data.materials.clear()
        for material_slot in materials:obj.data.materials.append(material_slot)
        for polygon,index in zip(obj.data.polygons,indices):polygon.material_index=index
        # UV coordinates make the independently authored maps portable to glTF.
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if obj in [body,cap]:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x+(.13 if obj==cap else 0),-(point.y-(.10 if obj==cap else 0)))/(2*math.pi)+.5,point.z/.95))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        if obj==cap:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.matrix_world@obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((point.x+.13)/.80+.5,(point.y-.10)/.80+.5)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        if obj==body:
            bmesh.ops.remove_doubles(mesh,verts=list(mesh.verts),dist=1e-6)
            flaps=[f for f in mesh.faces if f.calc_area()<1e-6 and sum(len(e.link_faces)==1 for e in f.edges)==2 and sum(len(e.link_faces)==3 for e in f.edges)==1]
            bmesh.ops.delete(mesh,geom=flaps,context='FACES');assert all(e.is_manifold for e in mesh.edges),'Unresolved mineral-mound topology'
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
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/099',key='MK14',name='Capacitors',culture='mikotaj',
        footprint=[2,2],definition_class=28,construction_updates=40,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,
        author='sources/tools/blender/remaster_mikotaj_capacitors.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Low connected ore knuckles, darker left cleft and compact reddish copper crown follow original views and reviewed concept.',
                        'Crown depression, hidden section, dents and physical energy storage engineering are authored or unknown. No unsupported charging or mechanical lid clip.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk14-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_CAPACITORS_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
