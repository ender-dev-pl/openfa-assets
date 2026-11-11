"""Author MK06 Dream from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/dream';maps=root/'sources/materials/mikotaj/dream'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25906);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    colour_rng=random.Random(2590603);colour_layers=[]
    for cells,weight in [(5,.18),(19,.08),(67,.025)]:
        grid=[[colour_rng.uniform(-.5,.5) for _ in range(cells+1)] for _ in range(cells+1)];colour_layers.append((cells,weight,grid))
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
    noise_rng=random.Random(2590607);layers=[]
    for cells,weight in [(7,.10),(23,.04),(71,.01)]:
        grid=[[noise_rng.uniform(-.5,.5) for _ in range(cells+1)] for _ in range(cells+1)];layers.append((cells,weight,grid))
    seeds=[(noise_rng.random(),noise_rng.random()) for _ in range(16)]
    height=[]
    for y in range(size):
        for x in range(size):
            u=x/(size-1);v=y/(size-1);value=0
            for cells,weight,grid in layers:
                fx=u*cells;fy=v*cells;ix=min(int(fx),cells-1);iy=min(int(fy),cells-1);tx=fx-ix;ty=fy-iy;tx=tx*tx*(3-2*tx);ty=ty*ty*(3-2*ty)
                a=grid[iy][ix]*(1-tx)+grid[iy][ix+1]*tx;b=grid[iy+1][ix]*(1-tx)+grid[iy+1][ix+1]*tx;value+=weight*(a*(1-ty)+b*ty)
            distances=sorted((u-a)**2+(v-b)**2 for a,b in seeds);edge=math.sqrt(distances[1])-math.sqrt(distances[0]);value-=.05*math.exp(-(edge/.008)**2)
            height.append(value)
    normals=[]
    for y in range(size):
        for x in range(size):
            dx=(height[y*size+min(x+1,size-1)]-height[y*size+max(x-1,0)])*26
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*26;length=math.sqrt(1+dx*dx+dy*dy)
            normals.extend([.5-.5*dx/length,.5-.5*dy/length,.5+.5/length,1])
    images={}
    for name,pixels in [('mineral-base-colour',colours),('brass-base-colour',gold),('exposed-ridge-base-colour',ridge),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
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
    brass=material('Worn brass focusing collar',(.43,.30,.095),image='brass-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    dark=material('Recessed emitter mounting alloy',(.022,.032,.036),.74,.31)
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
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(ore);obj.data.materials.append(exposed)
        for j in range(len(profile)-1):
            for i in [1,n-1]:obj.data.polygons[j*n+i].material_index=1
        bpy.context.view_layer.objects.active=obj;bevel=obj.modifiers.new('Narrow worn mineral edges','BEVEL');bevel.width=.018;bevel.segments=2;bpy.ops.object.modifier_apply(modifier=bevel.name)
        subdivision=obj.modifiers.new('Mineral surface relief sampling','SUBSURF');subdivision.subdivision_type='SIMPLE';subdivision.levels=2;bpy.ops.object.modifier_apply(modifier=subdivision.name)
        noise=bpy.data.textures.get('Fitted mineral stress relief') or bpy.data.textures.new('Fitted mineral stress relief',type='CLOUDS');noise.noise_scale=.18;noise.noise_depth=1
        displacement=obj.modifiers.new('Restrained mineral stress relief','DISPLACE');displacement.texture=noise;displacement.strength=.038;displacement.texture_coords='GLOBAL';bpy.ops.object.modifier_apply(modifier=displacement.name)
        return obj
    xy=[(-.75,-.75),(.06,-.94),(.82,-.66),(.94,-.12),(.72,.74),(-.04,.86),(-.81,.62),(-.94,-.08)]
    base=shard('Broad continuous Dream foundation',(0,0),xy,[(.045,1,0,0),(.16,1,0,0),(.51,.93,0,0),(.91,.80,0,0),(1.26,.60,0,.02),(1.30,.56,0,.02)])
    spire=shard('Central mineral focusing spire',(0,0),[(x*.31,y*.31) for x,y in xy],[(1.12,.70,0,0),(1.49,1,0,0),(1.76,.72,.035,0),(2.05,.27,-.01,0),(2.20,.09,-.01,0)])
    post=shard('Integrated left mineral arch support',(-.82,-.08),[(x*.10,y*.10) for x,y in xy],[(.10,.9,0,0),(.80,.85,0,0),(1.24,.54,0,0)])
    # A dark split in the ore, not a human doorway. Planar Boolean inputs.
    bpy.context.view_layer.objects.active=base;tri=base.modifiers.new('Planar socket input','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.03,-.79,.35));cutter=bpy.context.object;cutter.name='Temporary narrow mineral slit';cutter.scale=(.105,.42,.96);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bpy.context.view_layer.objects.active=base;mod=base.modifiers.new('Actual narrow front mineral split','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(.03,-.579,.39));back=bpy.context.object;back.name='Dark recessed mineral slit interior';back.scale=(.10,.025,.77);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);back.data.materials.append(dark)
    cylinder('Slender brass summit rod',(-.01,0,2.385),.026,.40,brass,axis=(0,0,1),vertices=32)
    # Supported left arch, not a free halo. Closed capped curve becomes mesh.
    path=[(-.82,-.08,1.24),(-.78,-.08,1.51),(-.63,-.08,1.78),(-.49,-.09,1.84),(-.33,-.10,1.71),(-.17,-.10,1.49)]
    curve=bpy.data.curves.new('Single supported brass arch','CURVE');curve.dimensions='3D';curve.resolution_u=16;curve.bevel_depth=.026;curve.bevel_resolution=2;curve.use_fill_caps=True
    spline=curve.splines.new('BEZIER');spline.bezier_points.add(len(path)-1)
    for point,co in zip(spline.bezier_points,path):point.co=co;point.handle_left_type='AUTO';point.handle_right_type='AUTO'
    arch=bpy.data.objects.new('Single supported brass arch',curve);bpy.context.collection.objects.link(arch);arch.data.materials.append(brass);bpy.ops.object.select_all(action='DESELECT');arch.select_set(True);bpy.context.view_layer.objects.active=arch;bpy.ops.object.convert(target='MESH')
    cylinder('Left arch mineral seated ferrule',(-.82,-.08,1.245),.047,.055,dark,axis=(0,0,1),vertices=24)
    cylinder('Spire arch seated ferrule',(-.17,-.10,1.49),.044,.052,dark,axis=(.65,0,-1),vertices=24)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/091';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
    for obj in meshes:
        obj.parent=placement;bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
        # UV coordinates make the independently authored maps portable to glTF.
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if obj.name in ['Broad continuous Dream foundation','Central mineral focusing spire','Integrated left mineral arch support']:
            uv=obj.data.uv_layers.active
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x,-point.y)/(2*math.pi)+.5,point.z/2.58))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data);bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        if obj.name in ['Broad continuous Dream foundation','Central mineral focusing spire','Integrated left mineral arch support']:
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/091',key='MK06',name='Dream',culture='mikotaj',
        footprint=[3,3],definition_class=255,construction_updates=38,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=4,
        author='sources/tools/blender/remaster_mikotaj_dream.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Broad mineral foundation, narrow front split, central spire, slender brass summit rod and supported left brass arch follow legacy; exact sections, socket engineering and hidden surfaces are authored.',
                        'Mind-treatment function is original lore; no human medical machinery, visible emitter or operating cycle is inferred.'],
        scale_contract='3x3 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk06-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_DREAM_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
