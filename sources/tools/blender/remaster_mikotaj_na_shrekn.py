"""Author MK21 Na-Shrekn from actual legacy anatomy and the reviewed concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def main(root):
    sys.path.insert(0,str(root/'tools'))
    from publication_support import clean_blend,clean_png
    out=root/'sources/objects/mikotaj/na-shrekn';maps=root/'sources/materials/mikotaj/na-shrekn'
    out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    rng=random.Random(25921);size=512;colours=[];gold=[];orm=[];ridge=[];normals=[];terminal=[]
    colour_rng=random.Random(2592103);colour_layers=[]
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
            cleft=math.exp(-((u-.5-.012*math.sin(21*v))/.025)**2)*math.exp(-((v-.18)/.19)**4)
            colours.extend([max(.015,min(1,(c+cloud*1.05-stain*1.2+scratch+exposed*.60)*pedestal_tone*(1-.55*cleft))) for c in (.22,.30,.25)]+[1])
            gold.extend([max(.015,min(1,c+cloud*1.3-stain*1.2+scratch)) for c in (.40,.19,.105)]+[1])
            ridge.extend([max(.015,min(1,c+cloud*1.6-stain+scratch)) for c in (.34,.42,.37)]+[1])
            hot=math.exp(-((u-.5)/.23)**2-((v-.53)/.33)**2);terminal.extend([.38+.55*hot,.025+.28*hot,.012+.04*hot,1])
            orm.extend([1,max(.15,min(.8,.53+stain*.6-cloud*.25)),.65,1])
    # Deterministic nonperiodic value noise; no regular engraved panel pattern.
    noise_rng=random.Random(2592107);layers=[]
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
            normal=mat.node_tree.nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.4
            mat.node_tree.links.new(texture.outputs['Color'],normal.inputs['Color']);mat.node_tree.links.new(normal.outputs['Normal'],p.inputs['Normal'])
        if emission:p.inputs['Emission Color'].default_value=(*colour,1);p.inputs['Emission Strength'].default_value=emission
        return mat
    ore=material('Worn mineral alloy',(.22,.30,.25),image='mineral-base-colour')
    exposed=material('Exposed pale mineral facets',(.34,.42,.37),image='exposed-ridge-base-colour')
    dark=material('Dark mineral recess interior',(.014,.021,.020),.35,.72)
    # Authored portable mottled lens colour/emission, never sampled from legacy.
    pixels=[];lens_rng=random.Random(2592109)
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;tone=.45+.22*math.sin(11*u+4*math.sin(7*v))+.16*math.cos(19*v+3*math.sin(9*u))+lens_rng.uniform(-.03,.03)
            hot=math.exp(-((u-.5)/.18)**2-((v-.5)/.18)**2);pixels.extend([.015+.08*hot,.025+.30*hot,.12+.65*hot,1])
    image=bpy.data.images.new('navy-focusing-lens-colour',width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/'navy-focusing-lens-colour.png';image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack()
    blue=material('Navy photon focusing lens',(.02,.04,.30),.18,.28,emission=.4)
    node=blue.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;principled=blue.node_tree.nodes.get('Principled BSDF');blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Base Color']);blue.node_tree.links.new(node.outputs['Color'],principled.inputs['Emission Color'])
    def cylinder(name,centre,radius,depth,mat,axis=(0,-1,0),vertices=40):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre)
        obj=bpy.context.object;obj.name=name;obj.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();obj.data.materials.append(mat)
        modifier=obj.modifiers.new('Small worn seated rim','BEVEL');modifier.width=min(.015,depth*.18);modifier.segments=2;bpy.ops.object.modifier_apply(modifier=modifier.name)
        return obj
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
    images_extra={}
    for name in ['worn-red-strip-colour','blue-white-pulse-colour']:
        pixels=[]
        for y in range(size):
            for x in range(size):
                u=x/size;v=y/size;hot=max(0,1-((u-.5)/.65)**2-((v-.5)/.65)**2)
                colour=(.44+.06*math.sin(41*u+8*math.sin(19*v)),.025,.012) if name.startswith('worn') else (.025+.55*hot,.08+.75*hot,.90+.10*hot);pixels.extend([*colour,1])
        image=bpy.data.images.new(name,width=size,height=size,alpha=True);image.pixels.foreach_set(pixels);path=maps/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();images_extra[name]=image
    red=material('Two red photon flank strips',(.45,.025,.012),.28,.48,emission=.18);node=red.node_tree.nodes.new('ShaderNodeTexImage');node.image=images_extra['worn-red-strip-colour'];p=red.node_tree.nodes.get('Principled BSDF');red.node_tree.links.new(node.outputs['Color'],p.inputs['Base Color']);red.node_tree.links.new(node.outputs['Color'],p.inputs['Emission Color'])
    pulse_material=material('Blue white photon pulse',(.02,.04,.2),0,.8,emission=3);node=pulse_material.node_tree.nodes.new('ShaderNodeTexImage');node.image=images_extra['blue-white-pulse-colour'];p=pulse_material.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.001,.002,.01,1);pulse_material.node_tree.links.new(node.outputs['Color'],p.inputs['Emission Color'])
    profile=[(.02,.45),(.12,.59),(.33,.62),(.60,.60),(.90,.53),(1.15,.48),(1.35,.43),(1.45,.35),(1.47,.23),(1.46,.015)];n=64;verts=[];faces=[]
    for j,(z,r) in enumerate(profile):
        for i in range(n):
            a=i*math.tau/n;rib=.08*math.sin(5*a+.4*math.sin(2*z))+.035*math.cos(9*a-2*z);rr=r*(1+rib);angle=lambda centre:math.atan2(math.sin(a-centre),math.cos(a-centre));envelope=math.exp(-((z-.78)/.78)**4);rr-=envelope*(.17*math.exp(-(angle(-1.98)/.18)**2)+.14*math.exp(-(angle(-1.18)/.16)**2));rr+=.055*math.exp(-(angle(-1.58)/.18)**2)*envelope;front=math.exp(-(math.atan2(math.sin(a+math.pi/2),math.cos(a+math.pi/2))/.7)**2);rr+=front*(.035*math.exp(-((z-1.11)/.055)**2)+.030*math.exp(-((z-1.28)/.045)**2))
            x=rr*math.copysign(abs(math.cos(a))**.78,math.cos(a));y=rr*.86*math.copysign(abs(math.sin(a))**.78,math.sin(a));zz=z+.025*math.sin(3*a+z*4)*math.sin(math.pi*z/1.48);verts.append((x,y,zz))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]
    body=solid('Na-Shrekn ribbed upright mineral monolith',verts,faces,ore);body.data.materials.append(exposed);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Fine irregular ore sampling','SUBSURF');mod.subdivision_type='CATMULL_CLARK';mod.levels=2;bpy.ops.object.modifier_apply(modifier=mod.name)
    noise=bpy.data.textures.new('Na-Shrekn irregular worn mineral relief',type='CLOUDS');noise.noise_scale=.12;noise.noise_depth=1;mod=body.modifiers.new('Minor physical mineral relief','DISPLACE');mod.texture=noise;mod.texture_coords='GLOBAL';mod.strength=.025;bpy.ops.object.modifier_apply(modifier=mod.name)
    for index,(x,y,height) in enumerate([(-.21,.15,1.61),(.20,.15,1.62),(-.20,-.16,1.56),(.21,-.15,1.55)]):
        bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=.066,radius2=.050,depth=height-1.37,location=(x,y,(height+1.37)/2));obj=bpy.context.object;obj.name='Na-Shrekn short crown post '+str(index);obj.data.materials.append(ore);bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Used post edges','BEVEL');mod.width=.009;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)
    # Two physically carved irregular source front mineral clefts.
    body.data.materials.append(dark)
    for fracture,cx in enumerate([-.25,.18]):
        points=[];normals=[]
        for j in range(17):
            z=.18+j/16*1.13;x=cx+.022*math.sin(8*z+fracture*2)+.008*math.sin(23*z+fracture);bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit;points.append(point);normals.append(normal)
        vertices=[];faces=[]
        for j,(point,normal) in enumerate(zip(points,normals)):
            tangent=(points[min(16,j+1)]-points[max(0,j-1)]).normalized();across=tangent.cross(normal).normalized();taper=.5+.5*math.sin(math.pi*j/16);width=.026*taper
            for u,v in [(-width,-.060),(width,-.060),(width,.022),(-width,.022)]:vertices.append(point+normal*v+across*u)
        for j in range(16):
            for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
        faces += [(3,2,1,0),tuple(16*4+k for k in range(4))];cut=solid('Temporary mineral fracture cutter',vertices,faces,ore);cut.data.materials.append(exposed);cut.data.materials.append(dark)
        for polygon in cut.data.polygons:polygon.material_index=2
        bm=bmesh.new();bm.from_mesh(cut.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0 and all(e.is_manifold for e in bm.edges);bm.to_mesh(cut.data);bm.free()
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before mineral cleft','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Actual irregular front cleft '+str(fracture),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
        bpy.context.view_layer.update();depths=[]
        for j in [4,8,12]:
            before=points[j];hit,after,_,_=body.ray_cast(before+normals[j]*.3,-normals[j]);assert hit;depths.append((after-before).dot(-normals[j]))
        assert min(depths)>.025,('Actual carved mineral fracture depth',fracture,depths)
        body['fracture_depth_'+str(fracture)]=depths
    for index,(x,z) in enumerate([(-.32,.95),(.31,1.18),(-.27,.34),(.38,.27)]):
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before small wear','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.014,location=point+normal*.004);chip=bpy.context.object;chip.data.materials.append(ore);chip.data.materials.append(exposed)
        for p in chip.data.polygons:p.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Real minor mineral chip '+str(index),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=chip;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(chip,do_unlink=True)
    bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((-.06,-4,.81)),Vector((0,1,0)));assert hit
    # A real carved pocket,not an applied lamp badge.
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.120,depth=.090,location=point-normal*.025);cut=bpy.context.object;cut.rotation_euler=normal.to_track_quat('Z','Y').to_euler();cut.data.materials.append(ore);cut.data.materials.append(exposed);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Actual focusing recess','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    bezel=cylinder('Na-Shrekn worn front focusing bezel',point+normal*.004,.133,.037,exposed,axis=normal)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.114,depth=.20,location=point);cut=bpy.context.object;cut.rotation_euler=normal.to_track_quat('Z','Y').to_euler();cut.data.materials.append(exposed);bpy.context.view_layer.objects.active=bezel;mod=bezel.modifiers.new('Clear annular focusing rim','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    cylinder('Na-Shrekn dark focusing recess',point-normal*.027,.113,.016,dark,axis=normal)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=point-normal*.010);lens=bpy.context.object;lens.name='Na-Shrekn navy front focusing lens'
    for v in lens.data.vertices:q=v.co.copy();v.co=(q.x*.096,q.y*.022,q.z*.096)
    lens.data.materials.append(blue)
    for index in range(2):
        points=[];normals=[]
        for j in range(13):
            t=j/12;x=.30+.18*t;z=.32+.20*t+index*.18;hit,point,normal,_=body.ray_cast(Vector((x,-4,z)),Vector((0,1,0)));assert hit;points.append(point);normals.append(normal)
        for label,width,depth,offset,mat in [('dark strip bed',.022,.010,.005,dark),('red diagonal strip',.012,.006,.018,red)]:
            vertices=[];faces=[]
            for j,(point,normal) in enumerate(zip(points,normals)):
                tangent=(points[min(12,j+1)]-points[max(0,j-1)]).normalized();across=tangent.cross(normal).normalized()
                for u,v in [(-width,-depth),(width,-depth),(width,depth),(-width,depth)]:vertices.append(point+normal*(offset+v)+across*u)
            for j in range(12):
                for k in range(4):faces.append((j*4+k,j*4+(k+1)%4,(j+1)*4+(k+1)%4,(j+1)*4+k))
            faces += [(3,2,1,0),tuple(12*4+k for k in range(4))];solid('Na-Shrekn '+label+' '+str(index),vertices,faces,mat)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1);pulse=bpy.context.object;pulse.name='Na-Shrekn blue white crown discharge'
    for v in pulse.data.vertices:q=v.co.copy();v.co=q*(1+.035*math.sin(9*q.x+6*q.z)*math.cos(8*q.y))
    pulse.data.materials.append(pulse_material)
    amplitudes=[0,.55,.80,1,.80,.55,.80,1,.80,.55,.80,1,.80,.55,.30,0]
    for frame in range(1,34):
        index=min(15,max(0,(frame-1)/2));lo=int(index);blend=index-lo;amp=amplitudes[lo]*(1-blend)+amplitudes[min(15,lo+1)]*blend
        pulse.scale=(max(.0001,.28*amp),max(.0001,.18*amp),max(.0001,.095*amp));pulse.location=(0,0,1.73+.025*amp) if amp>0 else (0,0,.12)
        for prop in ['location','scale']:pulse.keyframe_insert(data_path=prop,frame=frame)
    action=pulse.animation_data.action
    for fc in action.fcurves:
        for key in fc.keyframe_points:key.interpolation='LINEAR'
    track=pulse.animation_data.nla_tracks.new();track.name='PhotonDischarge';track.strips.new('PhotonDischarge',1,action);pulse.animation_data.action=None
    bpy.context.scene.frame_start=1;bpy.context.scene.frame_end=33;bpy.context.scene.render.fps=24;bpy.context.scene.frame_set(1)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    placement=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(placement)
    placement['catalogue_id']='openfa:building/legacy/106';placement['footprint']=[2,2];placement['local_forward']='-Y';placement['local_up']='+Z'
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
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/1.55+point.y*.17+.5,point.z/1.80)
        if obj==lens:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/.22+.5,point.z/.22+.5)
        if obj==pulse:
            uv=obj.data.uv_layers.active
            for loop in obj.data.loops:
                point=obj.data.vertices[loop.vertex_index].co;uv.data[loop.index].uv=(point.x/2.2+.5,point.z/2.2+.5)
        triangulate=obj.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=triangulate.name)
        mesh=bmesh.new();mesh.from_mesh(obj.data)
        bmesh.ops.remove_doubles(mesh,verts=list(mesh.verts),dist=1e-6)
        assert all(e.is_manifold for e in mesh.edges),obj.name
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
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=259,id='openfa:building/legacy/106',key='MK21',name='Na-Shrekn',culture='mikotaj',
        footprint=[2,2],definition_class=18,construction_updates=57,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=6,
        author='sources/tools/blender/remaster_mikotaj_na_shrekn.py',author_sha256=sha(Path(__file__)),
        binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},
        interpretation=['Upright ribbed mineral monolith,four short crown posts,navy front lens and two narrow diagonal red right-flank strips follow actual legacy and reviewed concept.',
                        'Actual descriptor-offset operation overlays establish blue-white pulse above crown,with static body/lens/strips. Pulse duration,emission and hidden construction are authored;no rotation invented.'],
        scale_contract='2x2 placement footprint, local +Z up/-Y front. Native dimensions are authored cell-relative proportions; no metric legacy height or calibrated game scale claimed.',
        concept_review='sources/docs/reconstruction/models/mk21-concept-review.json',animation_clips=['PhotonDischarge'],game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    print('MIKOTAJ_NA_SHREKN_AUTHORED',triangles,'triangles;',len(meshes),'mesh nodes;',len(created),'export temporary directories',flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
