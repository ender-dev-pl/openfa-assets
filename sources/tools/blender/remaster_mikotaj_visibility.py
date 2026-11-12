"""Author MK12 Visibility from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/visibility';maps=root/'sources/materials/mikotaj/visibility'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25912);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[]
    colour_rng=random.Random(2591203);colour_layers=[]
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
            flux=.5+.5*math.sin(38*u+5*math.sin(18*v+4*math.sin(12*u)));strand=math.exp(-((flux-.55)/.15)**2)
            gold.extend([.70+.25*strand,.48+.38*strand,.015+.12*strand,1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2591207);layers=[]
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
                    visibility=max(0,min(1,(math.sin(31*v+phase)+.25)*2))
                    value-=.012*math.exp(-((u-vein)/.0035)**2)*visibility
            height.append(value)
    normals=[]
    for y in range(size):
        for x in range(size):
            dx=(height[y*size+(x+1)%size]-height[y*size+(x-1)%size])*26
            dy=(height[min(y+1,size-1)*size+x]-height[max(y-1,0)*size+x])*26;length=math.sqrt(1+dx*dx+dy*dy)
            normals.extend([.5-.5*dx/length,.5-.5*dy/length,.5+.5/length,1])
    images={}
    for name,pixels in [('mineral-base-colour',colours),('brass-base-colour',gold),('exposed-ridge-base-colour',ridge),('dark-mineral-base-colour',[v*.45 if i%4!=3 else 1 for i,v in enumerate(colours)]),('occlusion-roughness-metallic',orm),('mineral-fracture-normal',normals)]:
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
    brass=material('Worn golden spiral ribbon',(.43,.30,.095),image='brass-base-colour')
    dark=material('Dark weathered exposed mineral',(.07,.12,.10),.68,.52,image='dark-mineral-base-colour')
    # Authored portable mottled lens colour/emission, never sampled from legacy.
    pixels=[];lens_rng=random.Random(2591209)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            pixels.extend([.30+.35*tone,.45+.35*tone,.65+.30*tone,1])
    image=bpy.data.images.new('pale-blue-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'pale-blue-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Blue mineral vein insets',(.1,.3,.75),.18,.16,emission=.45)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
    # One closed annular casing: actual hollow throat above a low opaque floor.
    outer=[(.025,.66),(.15,.79),(.50,.70),(.95,.59),(1.35,.49),(1.75,.43),(2.12,.40),(2.42,.47),(2.58,.51),(2.62,.46)]
    rows=outer+[(2.62,.30),(2.30,.30),(.16,.30)];n=48;vertices=[]
    def angle_distance(a,b):return abs((a-b+math.pi)%math.tau-math.pi)
    for j,(z,radius) in enumerate(rows):
        for i in range(n):
            angle=i*math.tau/n
            if j<len(outer):
                wave=.035*math.sin(5*angle+.9*z)+.018*math.cos(9*angle-z)
                cleft=(.17*math.exp(-(angle_distance(angle,-2.12+.30*math.sin(3.0*z+.4))/.19)**2)+.15*math.exp(-(angle_distance(angle,-1.08+.12*math.sin(2.5*z))/.18)**2))*min(1,max(0,(2.55-z)*3))*min(1,z*5)
                rr=max(.325,radius+wave-cleft)+.12*(1-z/2.62)**2*max(0,math.cos(angle))**3;x=rr*math.cos(angle)*(1.05+.06*(1-z/2.62));y=rr*math.sin(angle)*.90
                x+=.07*(1-z/2.62)
            else:rr=radius;x=rr*math.cos(angle);y=rr*math.sin(angle)
            vertices.append((x,y,z+.005*math.sin(7*angle+j)))
    faces=[(j*n+i,j*n+(i+1)%n,((j+1)%len(rows))*n+(i+1)%n,((j+1)%len(rows))*n+i) for j in range(len(rows)) for i in range(n)]
    body=solid('Visibility hollow mineral silo',vertices,faces,ore);body.data.materials.append(dark);body.data.materials.append(exposed)
    for face in body.data.polygons:
        j=face.index//n;i=face.index%n;a=(i+.5)*math.tau/n
        if j>=len(outer) or (j>0 and j<7 and min(angle_distance(a,-2.12+.30*math.sin(3.0*rows[j][0]+.4)),angle_distance(a,-1.08+.12*math.sin(2.5*rows[j][0])))<.19):face.material_index=1
        elif (i*11+j*7)%41==0:face.material_index=2
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Mineral relief sampling','SUBSURF');mod.subdivision_type='SIMPLE';mod.levels=2;bpy.ops.object.modifier_apply(modifier=mod.name)
    noise=bpy.data.textures.new('Visibility natural ore erosion',type='CLOUDS');noise.noise_scale=.13;noise.noise_depth=1;mod=body.modifiers.new('Used mineral surface','DISPLACE');mod.texture=noise;mod.strength=.050;mod.texture_coords='GLOBAL';bpy.ops.object.modifier_apply(modifier=mod.name)
    for polygon in body.data.polygons:
        centre=polygon.center;angle=math.atan2(centre.y,centre.x-.07*(1-centre.z/2.62));radial=Vector((centre.x,centre.y,0));inner=polygon.normal.dot(radial)<0
        cleft=.30<centre.z<2.35 and min(angle_distance(angle,-2.12+.30*math.sin(3*centre.z+.4)),angle_distance(angle,-1.08+.12*math.sin(2.5*centre.z)))<.17
        polygon.material_index=1 if inner or cleft else 0
    bpy.context.view_layer.update();bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar input for wear chips','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name)
    for index,(x,z,radius) in enumerate([(-.10,1.25,.023),(.35,.64,.025),(-.30,.42,.022),(.10,2.18,.020),(.39,1.11,.025)]):
        hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=radius,location=point+normal*(radius*.2));chip=bpy.context.object;chip.data.materials.append(ore);chip.data.materials.append(dark);chip.data.materials.append(exposed)
        for polygon in chip.data.polygons:polygon.material_index=2
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Minor mineral chip '+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=chip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chip,do_unlink=True)
    cylinder('Visibility opaque deep shaft floor',(0,0,.10),.305,.035,dark,axis=(0,0,1),vertices=48)
    for i,z in enumerate([1.67,1.84]):
        bpy.context.view_layer.update();ends=[]
        for x in [.015,.35]:
            hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit;ends.append(point-normal*.012)
        delta=ends[1]-ends[0];cylinder('Visibility mineral cross-rib '+str(i),(ends[0]+ends[1])/2,.027,delta.length+.025,exposed,axis=delta,vertices=24)
    bpy.context.view_layer.update();inv=body.matrix_world.inverted();hit,point,normal,_=body.ray_cast(inv@Vector((0,-4,.84)),Vector((0,1,0)));assert hit
    point=body.matrix_world@point;normal=(body.matrix_world.to_3x3()@normal).normalized()
    cylinder('Visibility worn single port rim',point+normal*.012,.102,.045,exposed,axis=normal)
    cylinder('Visibility port dark seal',point+normal*.039,.086,.020,dark,axis=normal)
    pixels=[]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;t=.5+.2*math.sin(13*u+4*math.cos(9*v));pixels.extend([.52+.28*t,.025+.07*t,.012+.035*t,1])
    redimage=bpy.data.images.new('red-status-lens-colour',width=size,height=size,alpha=True);redimage.pixels.foreach_set(pixels);path=maps/'red-status-lens-colour.png';redimage.filepath_raw=str(path);redimage.file_format='PNG';redimage.save();path.write_bytes(clean_png(path.read_bytes()));redimage.pack()
    red=material('Visibility red state of same lens',(.8,.06,.02),.12,.16,emission=.8);node=red.node_tree.nodes.new('ShaderNodeTexImage');node.image=redimage;p=red.node_tree.nodes.get('Principled BSDF');red.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color']);red.node_tree.links.new(node.outputs['Color'],p.inputs['Emission Color'])
    lenses=[]
    for name,mat in [('Blue',blue),('Red',red)]:
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=point+normal*.057);obj=bpy.context.object;obj.name='Visibility '+name+' state lens';obj.scale=(.075,.075,.027);obj.rotation_euler=normal.to_track_quat('Z','Y').to_euler();bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);obj.data.materials.append(mat);lenses.append(obj)
    lens_position=point+normal*.057
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
    gold_shader=brass.node_tree.nodes.get('Principled BSDF');gold_shader.inputs['Emission Color'].default_value=(1,.61,.025,1);gold_shader.inputs['Emission Strength'].default_value=1.1
    energy_orm=list(orm)
    for index in range(2,len(energy_orm),4):energy_orm[index]=.05
    image=bpy.data.images.new('energy-ribbon-orm',width=size,height=size,alpha=True);image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(energy_orm);path=maps/'energy-ribbon-orm.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    texture=brass.node_tree.nodes.new('ShaderNodeTexImage');texture.image=image;split=brass.node_tree.nodes.new('ShaderNodeSeparateColor');brass.node_tree.links.new(texture.outputs['Color'],split.inputs[0]);brass.node_tree.links.new(split.outputs['Green'],gold_shader.inputs['Roughness']);brass.node_tree.links.new(split.outputs['Blue'],gold_shader.inputs['Metallic'])
    colour_node=next(node for node in brass.node_tree.nodes if node.type=='TEX_IMAGE' and node.image==images['brass-base-colour']);brass.node_tree.links.new(colour_node.outputs['Color'],gold_shader.inputs['Emission Color'])
    # A single skinned mesh replaces the earlier160 independent strip objects.
    # The source confirms upward winding/disappearance, not mechanical hinges.
    count=96;vertices=[];faces=[];cube=[(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)];quads=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for i in range(count):vertices.extend(cube);faces.extend(tuple(i*8+j for j in f) for f in quads)
    ribbon=solid('Visibility single skinned spiral ribbon',vertices,faces,brass)
    armdata=bpy.data.armatures.new('Visibility spiral flow rig');rig=bpy.data.objects.new('Visibility spiral flow rig',armdata);bpy.context.collection.objects.link(rig);bpy.ops.object.select_all(action='DESELECT');bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for i in range(count):
        bone=armdata.edit_bones.new('Ribbon '+str(i));bone.head=(0,0,0);bone.tail=(0,1,0)
    bpy.ops.object.mode_set(mode='OBJECT')
    for i in range(count):ribbon.vertex_groups.new(name='Ribbon '+str(i)).add(list(range(i*8,i*8+8)),1,'REPLACE')
    modifier=ribbon.modifiers.new('Portable spiral skin','ARMATURE');modifier.object=rig
    def position(t):
        radius=.018+.50*t;angle=math.tau*3.25*t;return Vector((radius*math.cos(angle),radius*math.sin(angle),2.62+.30*(1-t)**.8))
    for frame in range(1,62):
        fraction=(frame-1)/30 if frame<=31 else (61-frame)/30
        for i in range(count):
            t=i/count-fraction*1.02;bone=rig.pose.bones['Ribbon '+str(i)];bone.rotation_mode='QUATERNION'
            if t<0:
                bone.location=(0,0,.06);bone.rotation_quaternion=(1,0,0,0);bone.scale=(.00002,.00002,.00002)
            else:
                a=position(t);b=position(t+1/count);tangent=(b-a).normalized();normal=Vector((0,0,1));side=normal.cross(tangent).normalized();normal=tangent.cross(side).normalized();rotation=Matrix(((tangent.x,side.x,normal.x),(tangent.y,side.y,normal.y),(tangent.z,side.z,normal.z)))
                bone.location=(a+b)/2;bone.rotation_quaternion=rotation.to_quaternion();bone.scale=((b-a).length*1.025,.125,.022)
            for data_path in ['location','rotation_quaternion','scale']:bone.keyframe_insert(data_path=data_path,frame=frame)
    action=rig.animation_data.action;action.name='Visibility original upward spiral cycle'
    for curve in action.fcurves:
        for key in curve.keyframe_points:key.interpolation='LINEAR'
    track=rig.animation_data.nla_tracks.new();track.name='LaunchFacilityCycle';track.strips.new('LaunchFacilityCycle',1,action);rig.animation_data.action=None
    bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=61;bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(1)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/097';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
    rig.parent=placement
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
            for polygon in obj.data.polygons:
                coordinates=[]
                for li in polygon.loop_indices:
                    point=obj.matrix_world@obj.data.vertices[obj.data.loops[li].vertex_index].co
                    coordinates.append((li,math.atan2(point.x,-point.y)/(2*math.pi)+.5,point.z/3.0))
                crossing=max(c[1] for c in coordinates)-min(c[1] for c in coordinates)>.5
                for li,u,v in coordinates:uv.data[li].uv=(u+1 if crossing and u<.5 else u,v)
        if obj==ribbon:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                vertex=obj.data.vertices[loop.vertex_index];segment=loop.vertex_index//8;uv.data[loop.index].uv=((segment+vertex.co.x+.5)/count,(vertex.co.y+.5)*.65+.15)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_move_up(modifier=triangulate.name) if obj==ribbon else None;bpy.ops.object.modifier_apply(modifier=triangulate.name)
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
        if obj==ribbon:normals=[tuple(polygon.normal) for polygon in obj.data.polygons for loop in polygon.loop_indices]
        obj.data.normals_split_custom_set(normals)
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000,triangles
    scratch=root/'artifacts/mikotaj-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        path=scratch/uuid.uuid4().hex;path.mkdir();created.append(path);return str(path)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_skins=True,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/097',key='MK12',name='Visibility',culture='mikotaj',
        footprint=[2,2],definition_class=9,construction_updates=24,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,
        author='sources/tools/blender/remaster_mikotaj_visibility.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Tall flared mineral casing, dark clefts, one lower red/blue status port, two upper-right mineral ribs and energetic gold spiral follow actual legacy sprites/concept.',
                        'Gold winds away leaving the shaft open; hidden routing, material, timing and metric dimensions are authored. Lens mesh visibility encodes the original colour swap without a mechanical lamp flip.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk12-concept-review.json',animation_clips=['LaunchFacilityCycle'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_VISIBILITY_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
