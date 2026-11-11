"""Author MK04 Fulfilment from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/fulfilment';maps=root/'sources/materials/mikotaj/fulfilment'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25904);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size
            cloud=.03*math.sin(17*u+4*math.cos(11*v))+.025*math.cos(23*v-5*u)+rng.uniform(-.012,.012)
            stain=.055*max(0,math.sin(8*u+7*v))**7
            scratch=.075 if (x*37+y*79)%1237<2 else 0
            colours.extend([max(.015,min(1,c+cloud-stain+scratch)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*2.8-stain*1.7+scratch)) for c in (.43,.30,.095)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2590407);layers=[]
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
    for name,pixels in [('mineral-base-colour',colours),('brass-base-colour',gold),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
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
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.55
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    brass=material('Worn brass focusing collar',(.43,.30,.095),image='brass-base-colour')
    amber=material('Small amber band indicator',(.65,.22,.018),.25,.20,emission=.35)
    dark=material('Recessed emitter mounting alloy',(.022,.032,.036),.74,.31)
    blue=material('Pale blue environmental focusing lens',(.055,.18,.55),.28,.17,emission=.12)
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def mineral(name,rings,flutes):
        n=48;vertices=[];faces=[]
        for row,(z,rx,ry,dx,dy) in enumerate(rings):
            for i in range(n):
                angle=i*2*math.pi/n
                relief=1+flutes*math.cos(5*angle+.3)+.035*math.sin(9*angle+.7)+.018*math.sin(13*angle+row*.6)
                # A dark front cleft is broad mineral relief, not a panel joint.
                cleft=1-.25*math.exp(-(((angle-4.65+math.pi)%(2*math.pi)-math.pi)/.30)**2)
                vertices.append((dx+rx*math.cos(angle)*relief*cleft,dy+ry*math.sin(angle)*relief*cleft,z+.008*math.sin(7*angle+row)))
        for j in range(len(rings)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        faces.extend([tuple(reversed(range(n))),tuple((len(rings)-1)*n+i for i in range(n))]);mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(ore)
        bpy.context.view_layer.objects.active=obj;sub=obj.modifiers.new('Continuous irregular mineral strata','SUBSURF');sub.subdivision_type='SIMPLE';sub.levels=2;bpy.ops.object.modifier_apply(modifier=sub.name)
        texture=bpy.data.textures.get('Mineral shallow stress') or bpy.data.textures.new('Mineral shallow stress',type='CLOUDS');texture.noise_scale=.15;texture.noise_depth=1
        disp=obj.modifiers.new('Authored shallow mineral erosion','DISPLACE');disp.texture=texture;disp.texture_coords='GLOBAL';disp.strength=.027;bpy.ops.object.modifier_apply(modifier=disp.name)
        return obj
    base=mineral('Continuous fluted foundation',[(.035,.84,.62,0,0),(.15,.87,.65,0,0),(.41,.66,.51,0,.015),(.72,.43,.35,0,0),(.98,.34,.29,0,0),(1.18,.34,.29,0,0)],.14)
    head=mineral('Asymmetric blunt mineral head',[(1.16,.34,.28,0,0),(1.35,.39,.31,-.04,0),(1.64,.44,.33,-.12,.02),(1.88,.33,.30,-.04,.02),(2.14,.18,.20,.14,.03),(2.27,.10,.13,.18,.03)],.055)
    def ring(name,z,height,rx,ry,mat):
        n=64;vertices=[];faces=[]
        for radius,zz in [(1,z-height/2),(1,z+height/2),(.88,z-height/2),(.88,z+height/2)]:
            vertices.extend((rx*radius*math.cos(i*2*math.pi/n),ry*radius*math.sin(i*2*math.pi/n),zz) for i in range(n))
        for i in range(n):
            j=(i+1)%n;faces.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+i,n+j,3*n+j,3*n+i)])
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);bpy.context.view_layer.objects.active=obj;bevel=obj.modifiers.new('Worn collar edges','BEVEL');bevel.width=.007;bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name);return obj
    band=ring('Single brass waist collar',1.105,.17,.405,.346,brass)
    ring('Upper dark collar seal',1.205,.025,.374,.318,dark);ring('Lower dark collar seal',1.005,.025,.374,.318,dark)
    # A tiny inset on the left-front of the single band is present in the source.
    normal=Vector((-.35,-1,0)).normalized();point=Vector((-.19,-.306,1.105))
    obj=cylinder('Amber indicator alloy seating',point+normal*.007,.042,.034,dark,axis=normal,vertices=32);obj.scale.x=1.5
    obj=cylinder('Amber band indicator',point+normal*.028,.029,.013,amber,axis=normal,vertices=32);obj.scale.x=1.5
    for i,angle in enumerate([3.7,4.15,5.05,5.55]):
        normal=Vector((math.cos(angle)/.405,math.sin(angle)/.346,0)).normalized();point=Vector((.406*math.cos(angle),.347*math.sin(angle),1.105))
        cylinder('Collar joint fastener '+str(i),point,.014,.012,dark,axis=normal,vertices=12)
    bpy.context.view_layer.update();inverse=base.matrix_world.inverted();hit,point,normal,_=base.ray_cast(inverse@Vector((.23,-4,.18)),inverse.to_3x3()@Vector((0,1,0)));assert hit
    point=base.matrix_world@point;normal=(base.matrix_world.to_3x3()@normal).normalized()
    cylinder('Low blue lens brass seating',point+normal*.014,.096,.050,brass,axis=normal)
    cylinder('Low blue lens dark seal',point+normal*.043,.079,.023,dark,axis=normal)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=point+normal*.064);obj=bpy.context.object;obj.name='Single low blue lens';obj.scale=(.063,.063,.028);obj.rotation_euler=normal.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(blue)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/089';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        # UV coordinates make the independently authored maps portable to glTF.
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if obj.name in ['Continuous fluted foundation','Asymmetric blunt mineral head']:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x,-point.y)/(2*math.pi)+.5,point.z/2.27))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data);bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        if obj.name in ['Continuous fluted foundation','Asymmetric blunt mineral head'] or obj.name.endswith(' lens'):
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/089',key='MK04',name='Fulfilment',culture='mikotaj',
        footprint=[2,2],definition_class=37,construction_updates=50,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,
        author='sources/tools/blender/remaster_mikotaj_fulfilment.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Asymmetric blunt mineral head, connected fluted base, one brass waist band, small amber band inset and single low blue lens follow legacy; precise cross-sections, flutes and fasteners are authored.',
                        'Nourishment function is original lore, its mechanism explicitly unknown. No operational motion inferred from catalogue information reveal.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk02-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_FULFILMENT_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
