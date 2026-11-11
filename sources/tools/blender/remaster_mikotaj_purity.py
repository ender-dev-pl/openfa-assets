"""Author MK03 Purity from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/purity';maps=root/'sources/materials/mikotaj/purity'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25903);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=.03*math.sin(17*u+4*math.cos(11*v))+.025*math.cos(23*v-5*u)+rng.uniform(-.012,.012)
            stain=.055*max(0,math.sin(8*u+7*v))**7
            scratch=.075 if (x*37+y*79)%1237<2 else 0
            colours.extend([max(.015,min(1,c+cloud-stain+scratch)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*.5-stain*.6+scratch)) for c in (.43,.30,.095)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2590307);layers=[]
    for cells,weight in [(7,.40),(23,.12),(71,.025)]:
        grid=[[noise_rng.uniform(-.5,.5) for _ in range(cells+1)] for _ in range(cells+1)];layers.append((cells,weight,grid))
    seeds=[(noise_rng.random(),noise_rng.random()) for _ in range(16)]
    height=[]
    for y in range(size):
        for x in range(size):
            u=x/(size-1);v=y/(size-1);value=0
            for cells,weight,grid in layers:
                fx=u*cells;fy=v*cells;ix=min(int(fx),cells-1);iy=min(int(fy),cells-1);tx=fx-ix;ty=fy-iy;tx=tx*tx*(3-2*tx);ty=ty*ty*(3-2*ty)
                a=grid[iy][ix]*(1-tx)+grid[iy][ix+1]*tx;b=grid[iy+1][ix]*(1-tx)+grid[iy+1][ix+1]*tx;value+=weight*(a*(1-ty)+b*ty)
            distances=sorted((u-a)**2+(v-b)**2 for a,b in seeds);edge=math.sqrt(distances[1])-math.sqrt(distances[0]);value-=.025*math.exp(-(edge/.008)**2)
            height.append(value)
    normals=[]
    for y in range(size):
        for x in range(size):
            dx=(height[y*size+min(x+1,size-1)]-height[y*size+max(x-1,0)])*12
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*12;length=math.sqrt(1+dx*dx+dy*dy)
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
        if image:
            texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=images['mineral-fracture-normal']
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    silver=material('Exposed mineral ridges',(.34,.42,.37),image='exposed-ridge-base-colour')
    red=material('Red focusing marker',(.47,.018,.013),.35,.25,emission=.35)
    dark=material('Recessed emitter mounting alloy',(.022,.032,.036),.74,.31)
    blue=material('Pale blue environmental focusing lens',(.055,.18,.55),.28,.17,emission=.12)
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def shard(name,centre,xy,profile):
        vertices=[];faces=[];n=len(xy)
        for z,scale,dx,dy in profile:
            vertices += [(centre[0]+x*scale+dx,centre[1]+y*scale+dy,z) for x,y in xy]
        for j in range(len(profile)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(ore);obj.data.materials.append(silver)
        for j in range(len(profile)-1):
            for i in [1,n-1]:obj.data.polygons[j*n+i].material_index=1
        bpy.context.view_layer.objects.active=obj;bevel=obj.modifiers.new('Narrow worn mineral edges','BEVEL');bevel.width=.018;bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name)
        subdivision=obj.modifiers.new('Mineral surface relief sampling','SUBSURF');subdivision.subdivision_type='SIMPLE';subdivision.levels=1;bpy.ops.object.modifier_apply(modifier=subdivision.name)
        noise=bpy.data.textures.get('Fitted mineral stress relief') or bpy.data.textures.new('Fitted mineral stress relief',type='CLOUDS');noise.noise_scale=.18;noise.noise_depth=1
        displacement=obj.modifiers.new('Restrained mineral stress relief','DISPLACE');displacement.texture=noise;displacement.strength=.016;displacement.texture_coords='GLOBAL';bpy.ops.object.modifier_apply(modifier=displacement.name)
        return obj
    # Source-backed single pointed mineral mass and broad, low left buttress.
    xy=[(-.27,-.45),(.08,-.61),(.51,-.29),(.54,.20),(.24,.48),(-.31,.47),(-.59,.13),(-.52,-.27)]
    shell=shard('Main Purity mineral wedge',(0,0),xy,[(.04,.88,0,0),(.34,1,0,0),(.90,.88,0,.02),(1.54,.67,-.04,.05),(2.07,.40,-.09,.06),(2.61,.012,-.13,.08)])
    left=shard('Low left mineral buttress',(-.42,.04),[(x*.55,y*.62) for x,y in xy],[(.08,.65,0,0),(.46,1,0,0),(.93,.56,.03,0),(1.18,.03,.08,.05)])
    bpy.context.view_layer.update()
    def seat_on(obj,x,z):
        inverse=obj.matrix_world.inverted();hit,point,normal,_=obj.ray_cast(inverse@Vector((x,-4,z)),inverse.to_3x3()@Vector((0,1,0)))
        assert hit,('Missing optic seating',obj.name,x,z)
        return obj.matrix_world@point,(obj.matrix_world.to_3x3()@normal).normalized()
    # Blue column: one upper lens plus two lower lenses, never a third.
    for name,x,z,radius in [('Upper blue',-.045,1.65,.145),('Lower blue 0',-.13,.70,.083),('Lower blue 1',-.13,.29,.079)]:
        point,normal=seat_on(shell,x,z)
        cylinder(name+' alloy rim',point+normal*.008,radius*1.35,.042,silver,axis=normal)
        cylinder(name+' dark seat',point+normal*.034,radius*1.15,.024,dark,axis=normal)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=point+normal*.047)
        lens=bpy.context.object;lens.name=name+' lens';lens.scale=(radius,radius,.026 if radius>.1 else .018);lens.rotation_euler=normal.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);lens.data.materials.append(blue)
    # Recess-like layered diagonal inserts seated against the right facet.
    from mathutils import Matrix
    def bar(name,p1,p2,width,depth,offset,mat):
        point1,normal1=seat_on(shell,*p1);point2,normal2=seat_on(shell,*p2);normal=(normal1+normal2).normalized()
        along=(point2-point1).normalized();across=normal.cross(along).normalized();normal=along.cross(across).normalized()
        bpy.ops.mesh.primitive_cube_add(size=1,location=(point1+point2)/2+normal*offset)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Matrix((along,across,normal)).transposed().to_euler();obj.scale=((point2-point1).length,width,depth)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat)
        bevel=obj.modifiers.new('Rounded seated slit ends','BEVEL');bevel.width=min(width*.22,depth*.4);bevel.segments=3;bpy.ops.object.modifier_apply(modifier=bevel.name)
        return obj
    for i,(start,end) in enumerate([((.13,1.02),(.31,1.25)),((.12,.70),(.40,1.03)),((.11,.32),(.46,.73))]):
        cutter=bar('Temporary recessed slit cutter',start,end,.117,.22,-.035,dark)
        bpy.context.view_layer.objects.active=shell;modifier=shell.modifiers.new('Actual inset slot '+str(i),'BOOLEAN');modifier.operation='DIFFERENCE';modifier.solver='EXACT';modifier.object=cutter;bpy.ops.object.modifier_apply(modifier=modifier.name);bpy.data.objects.remove(cutter,do_unlink=True)
        bar('Red slit '+str(i)+' alloy rim',start,end,.102,.070,-.042,silver)
        bar('Red slit '+str(i)+' dark recessed surround',start,end,.078,.020,-.002,dark)
        bar('Red diagonal slit '+str(i),start,end,.046,.012,.010,red)
    # Sparse long irregular ore ridges follow the actual body surface. Their
    # exact fine contours are authored, rather than a repeating panel lattice.
    def ore_seam(name,path,width):
        vertices=[];faces=[]
        for x,z in path:
            point,normal=seat_on(shell,x,z);tangent=Vector((1,0,0));tangent=(tangent-normal*tangent.dot(normal)).normalized();across=normal.cross(tangent).normalized()
            for j in range(6):
                angle=j*2*math.pi/6;vertices.append(tuple(point+normal*.002+tangent*(width*math.cos(angle))+normal*(width*.65*math.sin(angle))))
        for i in range(len(path)-1):
            for j in range(6):faces.append((i*6+j,i*6+(j+1)%6,(i+1)*6+(j+1)%6,(i+1)*6+j))
        faces.extend([tuple(reversed(range(6))),tuple((len(path)-1)*6+j for j in range(6))]);mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(silver)
    for i,path in enumerate([[(-.11,2.40),(-.13,2.12),(-.10,1.95),(-.12,1.84)], [(-.30,1.98),(-.26,1.78),(-.29,1.52),(-.24,1.33),(-.29,1.06)], [(-.40,.83),(-.34,.66),(-.37,.43),(-.32,.16)],[(.10,2.05),(.13,1.90),(.16,1.72),(.13,1.52)],[(.02,1.28),(-.01,1.12),(.015,.94)],[(.40,.55),(.42,.42),(.42,.22)]]):ore_seam('Irregular exposed mineral ridge '+str(i),path,.012 if i%2 else .016)
    cylinder('Authored rear service closure',(0,.46,.68),.095,.055,dark,axis=(0,1,0),vertices=32)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/088';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        # UV coordinates make the independently authored maps portable to glTF.
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if obj.name in ['Main Purity mineral wedge','Low left mineral buttress']:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x,-point.y)/(2*math.pi)+.5,point.z/2.61))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data);bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        if obj.name.endswith(' lens'):
            for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/088',key='MK03',name='Purity',culture='mikotaj',
        footprint=[2,2],definition_class=5,construction_updates=52,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,
        author='sources/tools/blender/remaster_mikotaj_purity.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Single pointed mineral-alloy mass, low left buttress, one upper blue lens, two lower blue lenses and three diagonal red slits follow legacy; precise sections, inset engineering and rear closure are authored.',
                        'No operational motion inferred from catalogue information reveal. Blue emitters are material emission, not an invented gameplay effect.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk02-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_PURITY_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
