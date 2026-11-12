"""Author MK18 Ruth-feror from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/ruth-feror';maps=root/'sources/materials/mikotaj/ruth-feror'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25918);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[];terminal=[]
    colour_rng=random.Random(2591803);colour_layers=[]
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
            colours.extend([max(.015,min(1,(c+cloud*1.05-stain*1.2+scratch+exposed*.60)*pedestal_tone)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.2+scratch)) for c in (.40,.19,.105)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            hot=math.exp(-((u-.5)/.23)**2-((v-.53)/.33)**2);terminal.extend([.38+.55*hot,.025+.28*hot,.012+.04*hot,1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2591807);layers=[]
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
    pixels=[];lens_rng=random.Random(2591809)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Pale mine socket insets',(.1,.3,.75),.18,.30,emission=.25)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
    pixels=[];red_rng=random.Random(2591811)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;t=.5+.18*math.sin(17*u+3*math.cos(11*v))+red_rng.uniform(-.035,.035);pixels.extend([.30+.20*t,.020+.035*t,.015+.020*t,1])
    image=bpy.data.images.new('red-socket-paint',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'red-socket-paint.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();images['red-socket-paint']=image
    red=material('Worn red mine socket paint',(.40,.025,.02),.35,.55,image='red-socket-paint')
    def modifier(obj,kind,label,**properties):
        bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new(label,kind)
        for key,value in properties.items():setattr(mod,key,value)
        bpy.ops.object.modifier_apply(modifier=mod.name)
    def plate(name,centre,width,height,depth,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);obj=bpy.context.object;obj.name=name;obj.scale=(width,depth,height);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat);modifier(obj,'BEVEL','Small worn socket corners',width=.006,segments=2);return obj
    towers=[];specs=[('taller rear-left',-.55,.20,2.45,1.0),('shorter front-right',.55,-.18,1.72,.86)]
    profiles=[(.008,.34),(.12,.39),(.28,.375),(.41,.35),(.45,.36),(.48,.39),(.57,.42),(.66,.37),(.76,.29),(.86,.18),(.94,.09),(1.0,.012)]
    profiles=[tuple((a+b)*.5 for a,b in zip(profiles[j],profiles[j+1])) if k else profiles[j] for j in range(len(profiles)-1) for k in range(2)]+[profiles[-1]]
    for index,(label,cx,cy,height,width_scale) in enumerate(specs):
        n=48;verts=[];faces=[]
        for j,(u,radius) in enumerate(profiles):
            power=.55+.30*max(0,min(1,(u-.40)*12))
            for i in range(n):
                a=i*math.tau/n;da=lambda angle:math.atan2(math.sin(a-angle),math.cos(a-angle));ridge=.13*math.exp(-((u-.65)/.12)**2-(da(-.8)/.55)**2)-.08*math.exp(-((u-.75)/.13)**2-(da(-2.1)/.40)**2);rr=radius*width_scale*(1+.070*math.sin(5*a+11*u+index)+.035*math.cos(9*a-8*u)+ridge);dx=math.copysign(abs(math.cos(a))**power,math.cos(a));dy=math.copysign(abs(math.sin(a))**power,math.sin(a));x=cx-.075*u*u+rr*dx*1.30;y=cy+rr*.77*dy*1.15;verts.append((x,y,u*height))
        for j in range(len(profiles)-1):
            for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
        faces += [tuple(reversed(range(n))),tuple((len(profiles)-1)*n+i for i in range(n))]
        obj=solid('Ruth-feror '+label+' mineral pinnacle',verts,faces,ore);obj.data.materials.append(exposed);obj.data.materials.append(dark);modifier(obj,'SUBSURF','Fine irregular mineral sampling',subdivision_type='SIMPLE',levels=1)
        noise=bpy.data.textures.new(label+' mineral use relief',type='CLOUDS');noise.noise_scale=.075;noise.noise_depth=1;modifier(obj,'DISPLACE','Minor worn mineral relief',texture=noise,texture_coords='GLOBAL',strength=.040);towers.append(obj)
        def cut(cutter,name):
            modifier(obj,'TRIANGULATE','Planar before '+name);modifier(obj,'BOOLEAN',name,operation='DIFFERENCE',solver='EXACT',object=cutter);bpy.data.objects.remove(cutter,do_unlink=True)
        bpy.context.view_layer.update();hit,point,normal,_=obj.ray_cast(Vector((cx,-4,.35)),Vector((0,1,0)));assert hit
        bpy.ops.mesh.primitive_cube_add(size=1,location=(cx,point.y-.04,.35));cutter=bpy.context.object;cutter.scale=(.235,.20,.62);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);modifier(cutter,'BEVEL','Source socket recess corners',width=.012,segments=2)
        for mat in [ore,exposed,dark]:cutter.data.materials.append(mat)
        for polygon in cutter.data.polygons:polygon.material_index=2
        cut(cutter,'Actual front socket recess')
        floor=point.y+.06;plate('Ruth-feror '+label+' red socket',(cx,floor-.008,.35),.168,.56,.018,red);plate('Ruth-feror '+label+' pale vertical strip',(cx,floor-.024,.25),.050,.26,.012,blue)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=12,radius=1,location=(cx,floor-.025,.54));lens=bpy.context.object;lens.name='Ruth-feror '+label+' pale round inset';lens.scale=(.065,.025,.065);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);lens.data.materials.append(blue)
        for chip_index,(dx,u) in enumerate([(-.12,.64),(.12,.78),(-.04,.91)]):
            bpy.context.view_layer.update();hit,p,normal,_=obj.ray_cast(Vector((cx+dx,-4,u*height)),Vector((0,1,0)));assert hit
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.020,location=p+normal*.004);chip=bpy.context.object
            for mat in [ore,exposed,dark]:chip.data.materials.append(mat)
            for polygon in chip.data.polygons:polygon.material_index=1
            cut(chip,'Small exposed mineral chip '+str(chip_index))
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=(0,.10,.12));bridge=bpy.context.object;bridge.name='Ruth-feror low connecting ore bed';bridge.scale=(.73,.34,.10);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);bridge.data.materials.append(ore)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/103';placement['footprint']=[3,3];placement['local_forward']='-Y';placement['local_up']='+Z'
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
        if obj in towers:
            uv=obj.data.uv_layers.active;index=towers.index(obj);_,cx,cy,height,width_scale=specs[index]
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=((point.x-cx)/1.40+(point.y-cy)*.17+.5,point.z/height)
        if obj==bridge:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.matrix_world@obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/1.6+.5,point.z/2.45)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        if obj in towers:
            flaps=[f for f in mesh.faces if f.calc_area()<1e-6 and sum(len(e.link_faces)==1 for e in f.edges)==2 and sum(len(e.link_faces)==3 for e in f.edges)==1]
            bmesh.ops.delete(mesh,geom=flaps,context='FACES');assert all(e.is_manifold for e in mesh.edges),'Unresolved mineral-mound topology'
        bmesh.ops.recalc_face_normals(mesh,faces=list(mesh.faces));mesh.to_mesh(obj.data);mesh.free()
        for polygon in obj.data.polygons:polygon.use_smooth=True
        normals=[tuple(n.vector) for n in obj.data.corner_normals]
        if obj in towers:
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
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/103',key='MK18',name='Ruth-feror',culture='mikotaj',
        footprint=[3,3],definition_class=8,construction_updates=48,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,
        author='sources/tools/blender/remaster_mikotaj_ruth_feror.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Two unequal pointed mineral forms,taller rear-left/shorter front-right,on darker stout pedestals with red vertical sockets and pale disc/strip details follow actual original views.',
                        'Low mineral connection,hidden sections and extraction/focusing engineering authored or unknown;no drilling or operating clip invented.'],
        scale_contract='3x3 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk18-concept-review.json',animation_clips=[],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_RUTH_FEROR_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
