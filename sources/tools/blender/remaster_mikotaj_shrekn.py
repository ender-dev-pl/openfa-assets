"""Author MK17 Shrekn from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/shrekn';maps=root/'sources/materials/mikotaj/shrekn'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25917);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    colour_rng=random.Random(2591703);colour_layers=[]
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
            colours.extend([max(.015,min(1,c+cloud*1.5-stain+scratch+exposed)) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.4+scratch)) for c in (.48,.56,.60)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            orm.extend([1,max(.15,min(.8,.45+stain*1.5-cloud*1.8)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2591707);layers=[]
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
                    shrekn=max(0,min(1,(math.sin(31*v+phase)+.25)*2))
                    value-=.012*math.exp(-((u-vein)/.0035)**2)*shrekn
            height.append(value)
    normals=[]
    for y in range(size):
        for x in range(size):
            dx=(height[y*size+(x+1)%size]-height[y*size+(x-1)%size])*65
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*65;length=math.sqrt(1+dx*dx+dy*dy)
            normals.extend([.5-.5*dx/length,.5-.5*dy/length,.5+.5/length,1])
    images={}
    for name,pixels in [('mineral-base-colour',colours),('silver-cap-base-colour',gold),('exposed-ridge-base-colour',ridge),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
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
        if image and image not in ['silver-cap-base-colour','red-terminal-colour']:
            texture=mat.node_tree.nodes.new('ShaderNodeTexImage');texture.image=images['mineral-fracture-normal']
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=1.25
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    brass=material('Scuffed silver mushroom cap',(.48,.56,.60),image='silver-cap-base-colour')
    dark=material('Dark mineral inset interior',(.035,.060,.045),.45,.75)
    # Boolean-unioned ore lobes preserve one connected body, not loose props.
    pixels=[];lens_rng=random.Random(2591709)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Blue Shrekn status port',(.1,.3,.75),.18,.24,emission=.40)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
    # The hollow casing and its two side chambers are one closed mineral mesh.
    outer=[(.025,.52),(.16,.49),(.42,.45),(.68,.43),(.94,.42),(1.20,.43),(1.52,.40),(1.78,.41),(1.86,.43)]
    outer=[tuple((a+b)*.5 for a,b in zip(outer[j],outer[j+1])) if k else outer[j] for j in range(len(outer)-1) for k in range(2)]+[outer[-1]]; rows=outer+[(1.86,.285),(.15,.285)];n=64;vertices=[]
    def ad(a,b):return abs((a-b+math.pi)%math.tau-math.pi)
    for j,(z,radius) in enumerate(rows):
        for i in range(n):
            a=i*math.tau/n
            if j<len(outer):
                side=(.025*math.exp(-(ad(a,0)/.42)**4)+.020*math.exp(-(ad(a,math.pi)/.42)**4))*math.exp(-((z-.53)/.37)**4)
                cleft=(.065*math.exp(-(ad(a,-1.95+.10*math.sin(5*z))/.18)**2)+.060*math.exp(-(ad(a,-1.21+.10*math.cos(4*z))/.18)**2))*min(1,z*5)*min(1,(1.85-z)*5)
                rr=max(.345,radius+side-cleft+.018*math.sin(7*a+9*z));x=rr*math.cos(a)+.025*(1-z/1.86);y=rr*math.sin(a)*.85
                radial=math.hypot(x,y)
                if radial<.36:x*=.36/radial;y*=.36/radial
            else:x=radius*math.cos(a);y=radius*math.sin(a)
            vertices.append((x,y,z))
    faces=[(j*n+i,j*n+(i+1)%n,((j+1)%len(rows))*n+(i+1)%n,((j+1)%len(rows))*n+i) for j in range(len(rows)) for i in range(n)]
    body=solid('Shrekn hollow mineral casing and side chambers',vertices,faces,ore);body.data.materials.append(dark);body.data.materials.append(exposed)
    for polygon in body.data.polygons:
        polygon.material_index=1 if polygon.index//n>=len(outer) else 0
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Fine source mineral profile sampling','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=1;bpy.ops.object.modifier_apply(modifier=mod.name)
    noise=bpy.data.textures.new('Shrekn worn mineral relief',type='CLOUDS');noise.noise_scale=.095;noise.noise_depth=1;mod=body.modifiers.new('Small worn mineral dents','DISPLACE');mod.texture=noise;mod.texture_coords='GLOBAL';mod.strength=.035;bpy.ops.object.modifier_apply(modifier=mod.name)
    # Rounded side chambers are real overlapping ore lobes. Reboring after
    # union keeps their inward portions from blocking the canonical shaft.
    for index,(position,scale) in enumerate([((-.46,-.015,.51),(.34,.40,.38)),((.49,-.015,.53),(.39,.43,.43))]):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=position);lobe=bpy.context.object
        for vertex in lobe.data.vertices:vertex.co*=1+.045*math.sin(13*vertex.co.x+6*vertex.co.z+index)*math.cos(11*vertex.co.y-index)
        lobe.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        for mat in [ore,dark,exposed]:lobe.data.materials.append(mat)
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar lobe union input','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Actual rounded side chamber','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=lobe;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(lobe,do_unlink=True)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.305,depth=2.2,location=(0,0,1.20));bore=bpy.context.object
    for mat in [ore,dark,exposed]:bore.data.materials.append(mat)
    for polygon in bore.data.polygons:polygon.material_index=1
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar shaft recut input','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Full clear shaft after chamber union','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=bore;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(bore,do_unlink=True)
    for index,(x,z) in enumerate([(-.18,1.25),(.25,.83),(-.42,.45),(.16,1.65)]):
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before each wear cut','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.020,location=point+normal*.004);chip=bpy.context.object
        for mat in [ore,dark,exposed]:chip.data.materials.append(mat)
        for polygon in chip.data.polygons:polygon.material_index=2
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Actual small mineral chip '+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=chip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chip,do_unlink=True)
    cylinder('Shrekn opaque deep shaft floor',(0,0,.095),.315,.035,dark,axis=(0,0,1),vertices=48)
    bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((0,-4,.52)),Vector((0,1,0)));assert hit
    cylinder('Shrekn worn port rim',point+normal*.012,.11,.040,exposed,axis=normal)
    cylinder('Shrekn port dark seal',point+normal*.035,.09,.020,dark,axis=normal)
    pixels=[]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;t=.5+.2*math.sin(13*u+4*math.cos(9*v));pixels.extend([.52+.28*t,.025+.07*t,.012+.035*t,1])
    redimage=bpy.data.images.new('red-status-lens-colour',width=size,height=size,alpha=True);redimage.pixels.foreach_set(pixels);path=maps/'red-status-lens-colour.png';redimage.filepath_raw=str(path);redimage.file_format='PNG';redimage.save();path.write_bytes(clean_png(path.read_bytes()));redimage.pack()
    red=material('Shrekn red state of same lens',(.8,.06,.02),.12,.16,emission=.8);node=red.node_tree.nodes.new('ShaderNodeTexImage');node.image=redimage;p=red.node_tree.nodes.get('Principled BSDF');red.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color']);red.node_tree.links.new(node.outputs['Color'],p.inputs['Emission Color'])
    lenses=[]
    for name,mat in [('Blue',blue),('Red',red)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=point+normal*.054);obj=bpy.context.object;obj.name='Shrekn '+name+' state lens';obj.scale=(.075,.075,.027);obj.rotation_euler=normal.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat);lenses.append(obj)
    lens_position=point+normal*.054
    for frame in range(1,62):
        fraction=(frame-1)/30 if frame<=31 else (61-frame)/30;is_blue=(int(fraction*14)//2)%2==0 and fraction<.999
        for index,obj in enumerate(lenses):
            visible=(index==0)==is_blue;obj.location=lens_position if visible else Vector((0,0,.08));obj.scale=(1,1,1) if visible else (.001,.001,.001)
            for data_path in ['location','scale']:obj.keyframe_insert(data_path=data_path,frame=frame)
    for obj in lenses:
        action=obj.animation_data.action
        for curve in action.fcurves:
            for key in curve.keyframe_points:key.interpolation='CONSTANT'
        track=obj.animation_data.nla_tracks.new();track.name='LaunchFacilityCycle';track.strips.new('LaunchFacilityCycle',1,action);obj.animation_data.action=None
    cap_control=bpy.data.objects.new('Shrekn rigid cap carriage',None);bpy.context.collection.objects.link(cap_control)
    rail_control=bpy.data.objects.new('Shrekn telescoping guide extension',None);bpy.context.collection.objects.link(rail_control)
    profile=[(1.89,.54),(1.915,.57),(1.95,.54),(2.00,.45),(2.06,.33),(2.115,.16),(2.14,.008)];n=64;vertices=[];faces=[]
    for j,(z,radius) in enumerate(profile):
        for i in range(n):
            a=i*math.tau/n;vertices.append((radius*math.cos(a),radius*math.sin(a),z+.0015*math.sin(7*a+j)))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]
    cap=solid('Shrekn one-piece silver mushroom dome',vertices,faces,brass);cap.parent=cap_control
    bpy.context.view_layer.objects.active=cap;mod=cap.modifiers.new('Fine silver surface sampling','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=1;bpy.ops.object.modifier_apply(modifier=mod.name)
    # A closed thin tubular groove follows the same rigid cap surface. This is
    # physical relief,not separately opening rings or an energetic ribbon.
    curve=bpy.data.curves.new('Source cap spiral relief','CURVE');curve.dimensions='3D';curve.resolution_u=1;curve.bevel_depth=.015;curve.bevel_resolution=1;curve.resolution_u=1;curve.use_fill_caps=True
    line=curve.splines.new('POLY');line.points.add(192)
    for index,p in enumerate(line.points):
        t=index/192;r=.04+.47*t;a=math.tau*3.0*t
        k=next((j for j in range(len(profile)-1) if profile[j][1]>=r>=profile[j+1][1]),1)
        while k<len(profile)-2 and not profile[k][1]>=r>=profile[k+1][1]:k+=1
        z=profile[k][0]+(profile[k+1][0]-profile[k][0])*(profile[k][1]-r)/(profile[k][1]-profile[k+1][1]);p.co=(r*math.cos(a),r*math.sin(a),z+.004,1)
    obj=bpy.data.objects.new('Shrekn attached rigid spiral groove',curve);bpy.context.collection.objects.link(obj);curve.materials.append(dark);bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj;bpy.ops.object.convert(target='MESH');groove=bpy.context.object;groove.parent=cap_control
    # Compact authored telescopic slides keep the whole cap physically carried.
    # Both fixed and moving guide parts are outside the clear launch aperture.
    def tube(name,x,y0,y1,z,outer,inner,mat):
        n=24;verts=[(x+r*math.cos(i*math.tau/n),y,z+r*math.sin(i*math.tau/n)) for y,r in [(y0,outer),(y1,outer),(y1,inner),(y0,inner)] for i in range(n)];faces=[(j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i) for j in range(4) for i in range(n)];return solid(name,verts,faces,mat)
    for index,x in enumerate([-.40,.40]):
        cylinder('Shrekn fixed guide support '+str(index),(x,.08,1.75),.043,.21,exposed,axis=(0,0,1),vertices=24)
        tube('Shrekn fixed telescopic sleeve '+str(index),x,.05,.60,1.84,.028,.018,brass)
        rod=cylinder('Shrekn sliding guide rod '+str(index),(x,.025,1.84),.015,.75,brass,axis=(0,1,0),vertices=24);rod.parent=rail_control
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-.05,1.87));carrier=bpy.context.object;carrier.name='Shrekn cap bearing '+str(index);carrier.scale=(.075,.10,.09);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);carrier.data.materials.append(dark);mod=carrier.modifiers.new('Small worn bearing corners','BEVEL');mod.width=.008;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name);carrier.parent=cap_control
    for obj,distance in [(cap_control,1.15),(rail_control,.90)]:
        for frame in range(1,62):
            fraction=(frame-1)/30 if frame<=31 else (61-frame)/30;obj.location=(0,distance*fraction,0);obj.keyframe_insert(data_path='location',frame=frame)
        action=obj.animation_data.action
        for fc in action.fcurves:
            for key in fc.keyframe_points:key.interpolation='LINEAR'
        track=obj.animation_data.nla_tracks.new();track.name='LaunchFacilityCycle';track.strips.new('LaunchFacilityCycle',1,action);obj.animation_data.action=None
    bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=61;bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(1)
    micro=[];micro_rng=random.Random(2591711)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;dx=.020*math.sin(247*u+4*math.sin(19*v))+micro_rng.uniform(-.008,.008);dy=.009*math.sin(103*v+13*u);micro.extend([.5+.5*dx,.5+.5*dy,.5+.5*math.sqrt(1-dx*dx-dy*dy),1])
    image=bpy.data.images.new('silver-use-normal',width=size,height=size,alpha=True);image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(micro);path=maps/'silver-use-normal.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();texture=brass.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image;normal=brass.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35;brass.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);brass.node_tree.links.new(normal.outputs['Normal'],brass.node_tree.nodes.get('Principled BSDF').inputs['Normal'])
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/102';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    cap_control.parent=placement;rail_control.parent=placement
    for obj in meshes:
        print('AUTHOR_MESH',obj.name,len(obj.data.vertices),len(obj.data.polygons),flush=True)
        repaired=obj.data.validate(verbose=True,clean_customdata=False);print('MESH_VALIDATE_REPAIRED',repaired,flush=True)
        assert not repaired,'Invalid author mesh: '+obj.name
        if obj.parent is None:obj.parent=placement
        bpy.context.view_layer.objects.active=obj;bpy.ops.object.select_all(action='DESELECT');obj.select_set(True)
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
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/1.85+point.y*.15+.5,point.z/2.20+point.y*.11)
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
            normals=[tuple((Vector(normals[loop])*.80+polygon.normal*.20).normalized()) for polygon in obj.data.polygons for loop in polygon.loop_indices]
        for polygon in obj.data.polygons:polygon.use_smooth=True
        obj.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000,triangles
    scratch=root/'artifacts/mikotaj-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_skins=False,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/102',key='MK17',name='Shrekn',culture='mikotaj',
        footprint=[2,2],definition_class=14,construction_updates=32,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,
        author='sources/tools/blender/remaster_mikotaj_shrekn.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Hollow mineral neck with rounded asymmetric side chambers,single red/blue port and a rigid silver mushroom cap carrying spiral relief follow actual legacy and prior user-confirmed rear stow.',
                        'Compact telescopic rear guides,shaft floor,continuous timing and exact hidden engineering are authored. Alternate tiny lens stow encodes colour change,not mechanical lamp motion.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk17-concept-review.json',animation_clips=['LaunchFacilityCycle'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_SHREKN_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
