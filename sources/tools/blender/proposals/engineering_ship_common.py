"""Small editable proposal-model primitives; no runtime definitions or mechanics."""
import hashlib,json,math,random,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Ship:
    def __init__(self,root,culture,role):
        self.root=Path(root);self.culture=culture;self.role=role;self.parts=[];self.joints=[]
        self.folder=self.root/'sources/proposals/engineering-ships'/culture/role;self.folder.mkdir(parents=True,exist_ok=True)
        self.maps=self.root/'sources/materials/proposals/engineering-ships'/culture;self.maps.mkdir(parents=True,exist_ok=True)
        sys.path.insert(0,str(self.root/'tools'));from publication_support import clean_png,clean_blend
        self.clean_png=clean_png;self.clean_blend=clean_blend
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
        self.placement=bpy.data.objects.new('ProposalRoot',None);bpy.context.collection.objects.link(self.placement)
        for k,v in dict(culture=culture,role=role,status='proposal-awaiting-mechanics',runtime_integration=False,legacy_unit=False,local_up='+Z',local_forward='-Y').items():self.placement[k]=v
        self.materials={};self.motion=[]

    def mat(self,name,colour,metal=.2,rough=.6):
        if name in self.materials:return self.materials[name]
        rng=random.Random(self.culture+name);size=256;pixels=[]
        # Sparse short scuffs and mottled stains, rather than a panel grid.
        marks={}
        for i in range(65):
            x=rng.randrange(size);y=rng.randrange(size)
            for j in range(rng.randrange(2,12)):marks[((x+j)%size,(y+j//4)%size)]=rng.uniform(-.14,.12)
        phases=[rng.random()*6 for i in range(4)]
        for y in range(size):
            for x in range(size):
                delta=.022*math.sin(x*.061+phases[0])*math.sin(y*.043+phases[1])+.012*math.sin(x*.18+y*.033)+rng.uniform(-.008,.008)+marks.get((x,y),0)
                if y<12:delta-=.025*(1-y/12)
                pixels.extend([min(.95,max(.008,c+delta)) for c in colour]+[1])
        im=bpy.data.images.new(name,width=size,height=size,alpha=True);im.pixels.foreach_set(pixels);path=self.maps/(name+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();path.write_bytes(self.clean_png(path.read_bytes()));im.pack()
        m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
        t=m.node_tree.nodes.new('ShaderNodeTexImage');t.image=im;m.node_tree.links.new(t.outputs['Color'],p.inputs['Base Color']);self.materials[name]=m;return m

    def finish(self,o,name,mat,parent=None,bevel=0,smooth=False):
        o.name=name;o.data.materials.append(mat);bpy.context.view_layer.objects.active=o
        if bevel:
            m=o.modifiers.new('Readable edge bevel','BEVEL');m.width=bevel;m.segments=3;bpy.ops.object.modifier_apply(modifier=m.name)
        if smooth:
            for f in o.data.polygons:f.use_smooth=True
        bpy.context.view_layer.update();world=o.matrix_world.copy();o.parent=parent or self.placement;o.matrix_world=world;self.parts.append(o);return o

    def box(self,name,p,size,mat,bevel=.04,parent=None):
        bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object
        for v in o.data.vertices:v.co=(v.co.x*size[0],v.co.y*size[1],v.co.z*size[2])
        return self.finish(o,name,mat,parent,bevel)

    def solid(self,name,verts,faces,mat,bevel=0,parent=None):
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o)
        bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();return self.finish(o,name,mat,parent,bevel)

    def cyl(self,name,p,r,depth,mat,axis=(0,0,1),parent=None,vertices=32):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=p);o=bpy.context.object;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();return self.finish(o,name,mat,parent,0,True)

    def ellipsoid(self,name,p,size,mat,parent=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=p);o=bpy.context.object
        for v in o.data.vertices:v.co=(v.co.x*size[0]/2,v.co.y*size[1]/2,v.co.z*size[2]/2)
        return self.finish(o,name,mat,parent,0,True)

    def ring(self,name,p,outer,inner,depth,mat,axis=(0,0,1),parent=None):
        n=32;verts=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for z in [-depth/2,depth/2] for r in [outer,inner] for i in range(n)];faces=[]
        for i in range(n):
            j=(i+1)%n;faces.extend([(i,j,2*n+j,2*n+i),(n+j,n+i,3*n+i,3*n+j),(j,i,n+i,n+j),(2*n+i,2*n+j,3*n+j,3*n+i)])
        q=Vector(axis).to_track_quat('Z','Y');verts=[tuple(q@Vector(v)+Vector(p)) for v in verts];return self.solid(name,verts,faces,mat,parent=parent)

    def beam(self,name,a,b,width,thick,mat,parent=None):
        a=Vector(a);b=Vector(b);o=self.box(name,(a+b)/2,(width,thick,(b-a).length),mat,min(width,thick)*.14,parent);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();return o

    def cut(self,obj,tool):
        bpy.context.view_layer.objects.active=obj;m=obj.modifiers.new('Real inset or opening','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=tool;bpy.ops.object.modifier_apply(modifier=m.name);self.parts.remove(tool);bpy.data.objects.remove(tool,do_unlink=True)

    def joint(self,name,p,parent=None):
        o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=p;bpy.context.view_layer.update();w=o.matrix_world.copy();o.parent=parent or self.placement;o.matrix_world=w;o['purpose']='Articulated tool pivot;authored preview only,no game mechanic';self.joints.append(o);return o

    def animate(self,joint,axis,values,kind='rotation_euler'):
        scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=97
        for frame,value in values:
            getattr(joint,kind)[axis]=value;joint.keyframe_insert(data_path=kind,index=axis,frame=frame,group=joint.name)
        action=joint.animation_data.action
        for slot in action.slots:
            for layer in action.layers:
                for strip in layer.strips:
                    bag=strip.channelbag(slot,ensure=False)
                    if bag:
                        for curve in bag.fcurves:
                            for key in curve.keyframe_points:key.interpolation='LINEAR' if len(values)==2 else 'BEZIER'
        track=joint.animation_data.nla_tracks.new();track.name='ToolOperation'
        track.strips.new('ToolOperation',1,action);joint.animation_data.action=None
        self.motion.append(dict(joint=joint.name,path=kind,axis=axis,keys=values))
        scene.frame_set(1)

    def export(self,author,notes):
        bpy.context.view_layer.update()
        for o in self.parts:
            bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
            m=o.modifiers.new('Stable triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name)
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.to_mesh(o.data);bm.free()
        concepts=json.loads((self.root/'sources/proposals/engineering-ships/concepts.json').read_text());concept,=[x for x in concepts['models'] if x['culture']==self.culture and x['role']==self.role]
        assert sha(self.root/concept['image'])==concept['sha256']
        bpy.ops.export_scene.gltf(filepath=str(self.folder/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=True,export_force_sampling=True,export_extras=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(self.folder/'model.blend'),compress=True);p=self.folder/'model.blend';p.write_bytes(self.clean_blend(p.read_bytes())[0])
        points=[o.matrix_world@v.co for o in self.parts for v in o.data.vertices]
        report=dict(issue=265,culture=self.culture,role=self.role,status='proposed-assets-awaiting-mechanics',legacy_unit=False,runtime_integration=False,mechanics_available=False,blueprint_registered=False,package_registered=False,binaries={e:sha(self.folder/('model.'+e)) for e in ['blend','glb']},author=Path(author).relative_to(self.root).as_posix(),author_sha256=sha(author),helper='sources/tools/blender/proposals/engineering_ship_common.py',helper_sha256=sha(Path(__file__)),concept=concept,triangles=sum(len(o.data.polygons) for o in self.parts),meshes=len(self.parts),materials=len({m for o in self.parts for m in o.data.materials}),maps={p.relative_to(self.root).as_posix():sha(p) for p in self.maps.glob('*.png')},bounds=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)],joints=[o.name for o in self.joints],clips=[dict(name='ToolOperation',fps=24,frames=[1,97],seconds=4,motion=self.motion)],scale='Authored proposal units,not calibrated meters/cells or a production/hangar clearance contract',notes=notes)
        assert report['triangles']<15000
        (self.folder/'model.json').write_text(json.dumps(report,indent=2)+'\n');print('PROPOSAL_EXPORTED',self.culture,self.role,report['triangles'],report['meshes'],flush=True)
