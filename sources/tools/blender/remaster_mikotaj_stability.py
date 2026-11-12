"""Author MK02 Stability from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/stability';maps=root/'sources/materials/mikotaj/stability'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25902);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
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
    noise_rng=random.Random(2590207);layers=[]
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
    blue=material('Silver-noise blue optical emitter',(.055,.18,.55),.28,.17,emission=.55)
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
    # A sharp tapered wedge and two lower ridges, rather than MK01's rounded mass.
    xy=[(-.23,-.69),(.23,-.69),(.56,-.25),(.60,.20),(.30,.54),(-.26,.57),(-.58,.18),(-.53,-.28)]
    shell=shard('Main Stability mineral shard',(0,0),xy,[(.07,.68,0,0),(.48,1,0,0),(1.20,.94,0,0),(1.95,.80,0,.01),(2.55,.46,-.05,.06),(3.26,.013,-.11,.10)])
    left=shard('Left mineral buttress',(-.65,-.02),[(x*.65,y*.64) for x,y in xy],[(.08,.80,0,0),(.55,.94,0,0),(1.30,.58,.02,0),(1.92,.02,.08,.04)])
    right=shard('Right triangular focusing buttress',(.67,-.12),[(x*.70,y*.90) for x,y in xy],[(.05,.18,.28,-.28),(.40,1,0,-.05),(1.02,.76,.02,.06),(1.72,.025,.13,.13)])
    # Keep ridges rooted in the rear mass while retaining narrow front valleys.
    shard('Connected rear root',(0,.26),[(x*.90,y*.60) for x,y in xy],[(.04,.80,0,0),(.45,1,0,0),(1.30,.65,0,0),(1.90,.01,0,0)])
    bpy.context.view_layer.update()
    def seat_on(obj,x,z):
        inverse=obj.matrix_world.inverted();hit,point,normal,_=obj.ray_cast(inverse@Vector((x,-4,z)),inverse.to_3x3()@Vector((0,1,0)))
        assert hit,('Missing optic seating',obj.name,x,z)
        return obj.matrix_world@point,(obj.matrix_world.to_3x3()@normal).normalized()
    point,normal=seat_on(shell,0,1.96)
    cylinder('Upper blue optic seating',point+normal*.014,.18,.06,dark,axis=normal)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=point+normal*.050);lens=bpy.context.object;lens.name='Upper blue lens';lens.scale=(.135,.135,.026);lens.rotation_euler=normal.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);lens.data.materials.append(blue)
    # Vertical red capsule and narrow dark central slot are reference-backed.
    point,normal=seat_on(shell,-.02,1.09)
    def oval(name,position,scale,mat):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=16,radius=1,location=position)
        obj=bpy.context.object;obj.name=name;obj.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat);return obj
    # The principal surface is the flat front face at this height, normal -Y.
    oval('Vertical marker outer alloy housing',point+normal*.020,(.205,.055,.39),silver)
    oval('Vertical marker dark seal',point+normal*.065,(.170,.030,.345),dark)
    oval('Red vertical marker',point+normal*.091,(.142,.021,.315),red)
    oval('Red marker inner slot',point+normal*.112,(.027,.014,.205),dark)
    point,normal=seat_on(shell,.22,.66);cylinder('Lower red node seating',point+normal*.015,.078,.040,dark,axis=normal,vertices=24);cylinder('Lower red node',point+normal*.041,.055,.019,red,axis=normal,vertices=24)
    for i,(x,z) in enumerate([(.62,.90),(.82,.68),(.65,.47)]):
        point,normal=seat_on(right,x,z);cylinder('Lower blue seating '+str(i),point+normal*.014,.076,.044,dark,axis=normal,vertices=24);cylinder('Lower blue node '+str(i),point+normal*.042,.052,.020,blue,axis=normal,vertices=24)
    # A restrained rear access closure is authored, not recovered engineering.
    cylinder('Rear field access closure',(0,.57,.84),.12,.08,dark,axis=(0,1,0),vertices=32)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/087';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        # UV coordinates make the independently authored maps portable to glTF.
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if obj.name in ['Main Stability mineral shard','Left mineral buttress','Right triangular focusing buttress','Connected rear root']:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x,-point.y)/(2*math.pi)+.5,point.z/3.1))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data);bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/087',key='MK02',name='Stability',culture='mikotaj',
        footprint=[3,3],definition_class=24,construction_updates=78,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,
        author='sources/tools/blender/remaster_mikotaj_stability.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Opaque pointed mineral-alloy wedge, two lower buttresses, blue upper lens and red vertical marker from legacy; rear field closure and exact cross-sections authored.',
                        'No operational motion inferred from catalogue information reveal. Blue emitters are material emission, not an invented gameplay effect.'],
        scale_contract='3x3 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk02-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_STABILITY_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
