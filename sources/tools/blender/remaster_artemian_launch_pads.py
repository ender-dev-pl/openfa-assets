"""Author AR09 Launch Pads from actual paletted legacy and reviewed ImageGen concept."""
import argparse,hashlib,json,math,random,sys,tempfile,uuid
from pathlib import Path
import bpy,bmesh
from mathutils import Vector,Matrix


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main(root):
    sys.path.insert(0,str(root/'tools'));from publication_support import clean_blend,clean_png
    out=root/'sources/objects/artemian/launch-pads';maps=root/'sources/materials/artemian/launch-pads';out.mkdir(parents=True,exist_ok=True);maps.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    size=512;rng=random.Random(2600901);images={};base=[];edge=[];orm=[];normal=[];amber=[];red=[]
    scratch_rng=random.Random(2600905);scratches=[(scratch_rng.uniform(.05,.95),scratch_rng.uniform(.05,.95),scratch_rng.uniform(.025,.10),scratch_rng.uniform(-.45,.45),scratch_rng.uniform(.0008,.0018)) for _ in range(38)]
    for y in range(size):
        for x in range(size):
            u=x/size;v=y/size;cap_weight=max(0,min(1,(.85-v)/.35));cloud=cap_weight*.025*math.sin(2*math.tau*u+2*math.sin(7*v))+.018*math.cos(13*v);grain=rng.uniform(-.005,.005);scratch=.07 if rng.random()<.003 else 0;stain=cap_weight*max(0,math.sin(3*math.tau*u+3*math.cos(11*v))-.65)*.10
            for cx,cy,length,angle,width in scratches:
                du=u-cx;dv=v-cy;t=du*math.sin(angle)+dv*math.cos(angle);distance=abs(du*math.cos(angle)-dv*math.sin(angle))
                if abs(t)<length/2 and distance<width:scratch=max(scratch,.12*(1-distance/width))
            scratch*=.25+.75*cap_weight
            base.extend([max(.01,c+cloud+grain+scratch-stain) for c in (.24,.39,.31)]+[1]);edge.extend([max(.01,c+cloud*.7+grain+scratch-stain) for c in (.46,.52,.56)]+[1]);orm.extend([1,max(.22,min(.65,.50+stain*3+grain)),.72,1])
            nx=.003*math.sin(311*v+21*math.sin(17*u))+rng.uniform(-.006,.006);ny=.004*math.sin(537*u+math.sin(23*v))+rng.uniform(-.004,.004);normal.extend([.5+nx,.5+ny,1,1])
            amber.extend([.60+.08*math.sin(5*u+7*v),.38+.04*math.cos(7*u-3*v),.08,1]);red.extend([.55+.05*math.cos(11*u+3*v),.24,.10,1])
    for name,pixels in [('muted-green-alloy-colour',base),('exposed-alloy-edge-colour',edge),('occlusion-roughness-metallic',orm),('used-metal-normal',normal),('amber-fitting-colour',amber),('copper-fitting-colour',red)]:
        image=bpy.data.images.new(name,width=size,height=size,alpha=True)
        if name in ['occlusion-roughness-metallic','used-metal-normal']:image.colorspace_settings.name='Non-Color'
        image.pixels.foreach_set(pixels);path=maps/(name+'.png');image.filepath_raw=str(path);image.file_format='PNG';image.save();path.write_bytes(clean_png(path.read_bytes()));image.pack();images[name]=image
    def material(name,colour,image=None,emission=0,metal=.84,rough=.4):
        m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*colour,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        if image:
            tex=m.node_tree.nodes.new('ShaderNodeTexImage');tex.image=images[image];m.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color']);packed=m.node_tree.nodes.new('ShaderNodeTexImage');packed.image=images['occlusion-roughness-metallic'];split=m.node_tree.nodes.new('ShaderNodeSeparateColor');m.node_tree.links.new(packed.outputs['Color'],split.inputs[0]);m.node_tree.links.new(split.outputs['Green'],p.inputs['Roughness']);m.node_tree.links.new(split.outputs['Blue'],p.inputs['Metallic'])
            n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=images['used-metal-normal'];nm=m.node_tree.nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.5;m.node_tree.links.new(n.outputs['Color'],nm.inputs['Color']);m.node_tree.links.new(nm.outputs['Normal'],p.inputs['Normal'])
            if emission:m.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value=emission;return m
    alloy=material('Used Artemian muted green alloy',(.24,.39,.31),'muted-green-alloy-colour');exposed=material('Worn exposed alloy edges',(.46,.52,.56),'exposed-alloy-edge-colour');dark=material('Dark recessed fittings',(.014,.019,.023),metal=.35,rough=.65);warm=material('Amber fitting caps',(.46,.22,.035),'amber-fitting-colour');redmat=material('Copper front inset and sleeves',(.55,.24,.10),'copper-fitting-colour')
    def solid(name,vertices,faces,mat):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vertices,[],faces);mesh.update();assert not mesh.validate();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o
    controls=[(.025,.86,.84),(.08,.91,.85),(.18,.87,.83),(.30,.73,.72),(.34,.69,.67),(.44,.58,.58),(.53,.44,.45),(.58,.27,.32),(.59,.02,.10)];profile=[]
    for j in range(len(controls)-1):
        p0=controls[max(0,j-1)];p1=controls[j];p2=controls[j+1];p3=controls[min(len(controls)-1,j+2)]
        for step in range(3):
            t=step/3;values=[.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in [1,2]];profile.append((p1[0]+(p2[0]-p1[0])*t,max(.02,values[0]),max(.02,values[1])))
    profile.append(controls[-1]);n=128;vertices=[];faces=[]
    for z,rx,ry in profile:
        for i in range(n):a=i*math.tau/n;vertices.append((rx*math.cos(a)*(.94+.06*math.sin(a)),ry*math.sin(a)+.06*z/.59,z))
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces += [tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))];body=solid('Launch Pads low green landing shell',vertices,faces,alloy);body.data.materials.append(exposed);body.data.materials.append(dark)
    bm=bmesh.new();bm.from_mesh(body.data);edges=[e for e in bm.edges if min(v.co.z for v in e.verts)>.28 and e.calc_length()>.075];bmesh.ops.subdivide_edges(bm,edges=edges,cuts=1,use_grid_fill=True);assert all(e.is_manifold for e in bm.edges);bm.to_mesh(body.data);bm.free()
    for v in body.data.vertices:
        q=v.co
        if q.z>.28:q.z-=min(1,(q.z-.28)/.10)*sum(depth*math.exp(-((q.x-x)/sx)**2-((q.y-y)/sy)**2) for x,y,depth,sx,sy in [(-.25,-.20,.003,.10,.12),(.35,.20,.003,.10,.12)])
    def cylinder(name,centre,radius,depth,mat,axis=(0,0,1),vertices=48):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=depth,location=centre);o=bpy.context.object;o.name=name;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);mod=o.modifiers.new('Small used fitting edges','BEVEL');mod.width=min(.005,depth*.12);mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    def cube(name,centre,size,mat):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object;o.name=name
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        o.data.materials.append(mat);mod=o.modifiers.new('Rounded architectural rail edges','BEVEL');mod.width=.004;mod.segments=3;bpy.ops.object.modifier_apply(modifier=mod.name);return o
    # True blind oval well with closed dark floor and inner walls in canonical shell.
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=1,depth=.90,location=(.08,.20,.76));cut=bpy.context.object
    for v in cut.data.vertices:v.co.x*=.25;v.co.y*=.22
    for mat in [alloy,exposed,dark]:cut.data.materials.append(mat)
    for face in cut.data.polygons:face.material_index=2
    bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar roof before true recessed well','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Real dark recessed roof well','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    for i,offset in enumerate([-.15,-.05,.05,.15]):
        half=.22*math.sqrt(1-(offset/.25)**2)+.008;cube('Launch Pads recessed grey baffle '+str(i),(.08+offset,.20,.415),(.014,half*2,.25),exposed)
    bpy.context.view_layer.update();anchors=[]
    for i,(x,top) in enumerate([(-.60,1.18),(-.36,1.10)]):
        hit,point,_,_=body.ray_cast(Vector((x,-3,.12)),Vector((0,1,0)));assert hit;y=point.y-.015;anchors.append(Vector((x,y,.82)));cylinder('Launch Pads copper base sleeve '+str(i),(x,y,.12),.070,.18,redmat);cube('Launch Pads tall brass rail '+str(i),(x,y,(.195+top)/2),(.050,.045,top-.195),warm)
        for j,z in enumerate([.255,.315]):cylinder('Launch Pads copper coupling '+str(i)+' '+str(j),(x,y,z),.041,.022,redmat)
    vector=anchors[1]-anchors[0];cylinder('Launch Pads brass crosspiece',(anchors[0]+anchors[1])/2,.029,vector.length+.025,warm,axis=vector,vertices=6)
    for i,x in enumerate([-.04,.28]):
        hit,point,normal,_=body.ray_cast(Vector((x,-3,.18)),Vector((0,1,0)));assert hit;radius=.064;cylinder('Launch Pads copper front inset '+str(i),point+normal*.005,radius,.025,redmat,axis=normal);ring=cylinder('Launch Pads copper inset clear rim '+str(i),point+normal*.001,radius+.009,.016,dark,axis=normal);bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius+.001,depth=.15,location=point);cut=bpy.context.object;cut.rotation_euler=normal.to_track_quat('Z','Y').to_euler();cut.data.materials.append(dark);bpy.context.view_layer.objects.active=ring;mod=ring.modifiers.new('Open copper inset rim','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    for i,(x,y) in enumerate([(-.34,.20),(.18,-.45),(-.35,.40)]):
        bpy.context.view_layer.update();hit,point,normal,_=body.ray_cast(Vector((x,y,2)),Vector((0,0,-1)));assert hit;bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=.006,location=point+normal*.002);cut=bpy.context.object
        for mat in [alloy,exposed,dark]:cut.data.materials.append(mat)
        for face in cut.data.polygons:face.material_index=1
        bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Planar before small finish chip','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);mod=body.modifiers.new('Real minor alloy chip '+str(i),'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
    # User-requested functional extension: the source-shaped upper shell is two
    # hinged doors. Preserve its closed contour and the small ribbed recess.
    aperture=.78;leaf_radius=.775;hinge_x=.815;hinge_z=.17;moving={};lifting={};diagonal=Matrix.Rotation(-math.radians(35),4,'Z')
    def boolean(obj,cut,operation):
        bpy.context.view_layer.objects.active=obj;mod=obj.modifiers.new('Functional hangar '+operation,'BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=cut;bpy.ops.object.modifier_apply(modifier=mod.name)
    def raw_box(centre,size):
        bpy.ops.mesh.primitive_cube_add(size=1,location=centre);o=bpy.context.object
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        return o
    for side in [-1,1]:
        leaf=body.copy();leaf.data=body.data.copy();bpy.context.collection.objects.link(leaf);leaf.name='Launch Pads hinged roof '+str(side)
        bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=leaf_radius,depth=3,location=(0,0,0));cut=bpy.context.object;boolean(leaf,cut,'INTERSECT');bpy.data.objects.remove(cut,do_unlink=True)
        cut=raw_box(diagonal@Vector((side*1.001,0,1.17)),(2,4,2));cut.rotation_euler.z=-math.radians(35);boolean(leaf,cut,'INTERSECT');bpy.data.objects.remove(cut,do_unlink=True)
        moving[leaf]=side
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=aperture,depth=4,location=(0,0,0));cut=bpy.context.object
    for m in [alloy,exposed,dark]:cut.data.materials.append(m)
    for face in cut.data.polygons:face.material_index=2
    boolean(body,cut,'DIFFERENCE');bpy.data.objects.remove(cut,do_unlink=True)
    for i in range(4):
        original=bpy.data.objects['Launch Pads recessed grey baffle '+str(i)]
        for side in [-1,1]:
            part=original.copy();part.data=original.data.copy();bpy.context.collection.objects.link(part);part.name=original.name+' '+str(side)
            cut=raw_box(diagonal@Vector((side*1.001,0,1)),(2,4,4));cut.rotation_euler.z=-math.radians(35);boolean(part,cut,'INTERSECT');bpy.data.objects.remove(cut,do_unlink=True)
            if part.data.polygons:moving[part]=side
            else:bpy.data.objects.remove(part,do_unlink=True)
        bpy.data.objects.remove(original,do_unlink=True)

    # Watertight annular underground shaft. The black floor is below the whole
    # demonstrated transit corridor; it is not a concrete plate at ground level.
    vv=[];ff=[];n=128
    for radius,z in [(.825,-1.50),(.825,.12),(.78,.12),(.78,-1.50)]:
        for i in range(n):a=i*math.tau/n;vv.append((radius*math.cos(a),radius*math.sin(a),z))
    for j in range(4):
        for i in range(n):ff.append((j*n+i,j*n+(i+1)%n,((j+1)%4)*n+(i+1)%n,((j+1)%4)*n+i))
    solid('Launch Pads dark underground shaft',vv,ff,dark)
    cylinder('Launch Pads black shaft floor',(0,0,-1.525),.82,.05,dark,vertices=96)
    for side in [-1,1]:
        axle=cylinder('Launch Pads lifting hinge axle '+str(side),(side*hinge_x,0,hinge_z),.012,.66,exposed,axis=(0,1,0));lifting[axle]=side
        for i,y in enumerate([-.18,.18]):
            bearing=cube('Launch Pads lifting bearing '+str(side)+' '+str(i),(side*.824,y,.165),(.040,.07,.13),exposed);lifting[bearing]=side
            cylinder('Launch Pads fixed lift guide '+str(side)+' '+str(i),(side*.824,y,.285),.025,.54,exposed,vertices=24)
            rod=cylinder('Launch Pads captive lift rod '+str(side)+' '+str(i),(side*.824,y,.13),.014,.21,exposed,vertices=24);lifting[rod]=side
        for i,y in enumerate([-.19,.19]):
            lug=cube('Launch Pads attached hinge lug '+str(side)+' '+str(i),(side*.774,y,.205),(.14,.07,.07),exposed);moving[lug]=side
    # Recess the hidden backs of copper fittings flush to the flight bore.
    # Their source-visible fronts remain; no fitting may protrude into the shaft.
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=aperture,depth=4,location=(0,0,0));trim=bpy.context.object
    for fitting in list(bpy.context.scene.objects):
        if fitting.type=='MESH' and fitting.name.startswith('Launch Pads copper '):boolean(fitting,trim,'DIFFERENCE')
    bpy.data.objects.remove(trim,do_unlink=True)
    # Local fixed guide feet bridge the asymmetric legacy shell to all guides.
    # They are merged into its actual closed wall, then trimmed to the bore.
    for side in [-1,1]:
        for y in [-.18,.18]:
            foot=cylinder('Temporary fixed guide foot',diagonal@Vector((side*.81,y,.10)),.040,.10,alloy,vertices=24);boolean(body,foot,'UNION');bpy.data.objects.remove(foot,do_unlink=True)
    bpy.ops.mesh.primitive_cylinder_add(vertices=128,radius=aperture+.0005,depth=4,location=(0,0,0));trim=bpy.context.object;boolean(body,trim,'DIFFERENCE');bpy.data.objects.remove(trim,do_unlink=True)
    for obj in bpy.context.scene.objects:
        if obj.type=='MESH' and any(label in obj.name for label in ['lifting hinge axle','lifting bearing','fixed lift guide','captive lift rod','attached hinge lug']):obj.matrix_world=diagonal@obj.matrix_world
    pivots={};carriages={}
    for side in [-1,1]:
        carriage=bpy.data.objects.new('HangarLiftPort' if side<0 else 'HangarLiftStarboard',None);bpy.context.collection.objects.link(carriage);carriage.location=diagonal@Vector((side*hinge_x,0,hinge_z));carriage.rotation_euler.z=-math.radians(35);carriages[side]=carriage
        pivot=bpy.data.objects.new('HangarDoorPort' if side<0 else 'HangarDoorStarboard',None);bpy.context.collection.objects.link(pivot);pivot.parent=carriage;pivot.location=(0,0,0);pivots[side]=pivot
    bpy.context.view_layer.update()
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];root_object=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root_object);root_object['catalogue_id']='openfa:building/legacy/115';root_object['footprint']=[2,2];root_object['local_forward']='-Y';root_object['local_up']='+Z'
    root_object['ground_level']=0.;root_object['preserve_ground_origin']=True
    for carriage in carriages.values():carriage.parent=root_object
    for o in meshes:
        if o in moving:
            o.parent=pivots[moving[o]];o.matrix_parent_inverse=o.parent.matrix_world.inverted()
        elif o in lifting:o.parent=carriages[lifting[o]];o.matrix_parent_inverse=o.parent.matrix_world.inverted()
        else:o.parent=root_object
        bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True);used=sorted({p.material_index for p in o.data.polygons});materials=[o.data.materials[i] for i in used];mapping={a:b for b,a in enumerate(used)};indices=[mapping[p.material_index] for p in o.data.polygons];o.data.materials.clear()
        for m in materials:o.data.materials.append(m)
        for p,index in zip(o.data.polygons,indices):p.material_index=index
        assert len(o.data.polygons)>0,('Empty authored part',o.name);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
        if o==body:
            uv=o.data.uv_layers.active
            for face in o.data.polygons:
                values=[]
                for index in face.loop_indices:
                    p=o.data.vertices[o.data.loops[index].vertex_index].co;values.append(((math.atan2(p.y-.06*p.z/.59,p.x)/math.tau+.5),p.z/.8))
                seam=max(u for u,v in values)-min(u for u,v in values)>.5
                for index,(u,v) in zip(face.loop_indices,values):uv.data[index].uv=(u+1 if seam and u<.5 else u,v)
        mod=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=mod.name);bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
        assert all(e.is_manifold for e in bm.edges),o.name;bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert bm.calc_volume(signed=True)>0,o.name
        for e in bm.edges:e.smooth=e.calc_face_angle(0)<.60
        bm.to_mesh(o.data);bm.free()
        for p in o.data.polygons:p.use_smooth=True
        o.data.normals_split_custom_set([tuple(n.vector) for n in o.data.corner_normals])
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=97
    for side,pivot in pivots.items():
        pivot.rotation_mode='XYZ'
        for frame,weight in [(1,0),(9,0),(25,1),(73,1),(89,0),(97,0)]:pivot.rotation_euler.y=side*math.radians(110)*weight;pivot.keyframe_insert(data_path='rotation_euler',frame=frame)
        action=pivot.animation_data.action;action.name='HangarExitCycle';track=pivot.animation_data.nla_tracks.new();track.name='HangarExitCycle';track.strips.new('HangarExitCycle',1,action);pivot.animation_data.action=None
        for fc in action.fcurves:
            for key in fc.keyframe_points:key.interpolation='LINEAR'
    for side,carriage in carriages.items():
        for frame,lift in [(1,0),(9,.34),(25,.34),(73,.34),(89,.34),(97,0)]:carriage.location.z=.17+lift;carriage.keyframe_insert(data_path='location',frame=frame)
        action=carriage.animation_data.action;action.name='HangarExitCycle';track=carriage.animation_data.nla_tracks.new();track.name='HangarExitCycle';track.strips.new('HangarExitCycle',1,action);carriage.animation_data.action=None
        for fc in action.fcurves:
            for key in fc.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(1)
    bpy.context.view_layer.update();triangles=sum(len(o.data.polygons) for o in meshes);assert triangles<30000
    scratch=root/'artifacts/artemian-building-export-temp';scratch.mkdir(parents=True,exist_ok=True);created=[];old=tempfile.mkdtemp
    def mk(*args,**kwargs):
        p=scratch/uuid.uuid4().hex;p.mkdir();created.append(p);return str(p)
    tempfile.mkdtemp=mk
    try:bpy.ops.export_scene.gltf(filepath=str(out/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_force_sampling=True,export_extras=True)
    finally:tempfile.mkdtemp=old
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'model.blend'),compress=True);blend=out/'model.blend';blend.write_bytes(clean_blend(blend.read_bytes())[0])
    metadata=dict(schema_version=1,issue=260,id='openfa:building/legacy/115',key='AR09',name='Launch Pads',culture='artemian',footprint=[2,2],definition_class=26,construction_updates=18,triangles=triangles,triangle_budget=30000,mesh_nodes=len(meshes),materials=5,author='sources/tools/blender/remaster_artemian_launch_pads.py',author_sha256=sha(Path(__file__)),binaries=dict(blend=sha(blend),glb=sha(out/'model.glb')),textures={p.name:sha(p) for p in sorted(maps.glob('*.png'))},interpretation=['Low green shell,real dark recessed roof well with four grey baffles,two tall brass rails/crosspiece/copper sleeves and couplings,two copper front insets follow actual source and reviewed concept.','Hidden engineering and metric dimensions remain authored. Hinged roof opening is an explicit functional extension,not recovered AR09 animation. Preserve ground origin0 for underground shaft;use closed-pose horizontal bounds for placement.'],scale_contract='2x2 placement footprint,+Zup/-Yfront. Native dimensions are authored cell-relative proportions;no recovered metric height or calibrated client scale claimed.',concept_review='sources/docs/reconstruction/models/ar09-concept-review.json',animation_clips=['HangarExitCycle'],hangar=dict(aperture_radius=.78,shaft_floor=-1.50,transit_min_z=-1.25,ground_level=0,preserve_ground_origin=True,hinge_x=.815,hinge_z=.17,lift_height=.34,fully_lifted_frame=9,fully_closed_lifted_frame=89,hinge_azimuth_degrees=-35,open_angle_degrees=110,closed_frame=1,open_first_frame=25,open_last_frame=73,cycle_end_frame=97),functional_extension='User-requested opening hangar exit. Own AR09 sprites do not recover an operating mechanism;two attached hinged roof halves and4second cycle are authored. Closed source contour and small ribbed recess retained;fixed shaft is genuinely open beneath them. Ship clearance uses independent canonical GLB geometry and explicit game/proposed world scales.',game_client_integration=False,final_user_artistic_acceptance=False)
    (out/'model.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8');print('ARTEMIAN_LAUNCH_PADS_AUTHORED',triangles,len(meshes),len(created),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True);args=parser.parse_args(sys.argv[sys.argv.index('--')+1:]);main(args.root.resolve())
