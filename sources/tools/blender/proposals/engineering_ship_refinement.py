"""Refined engineering proposal geometry and portable authored PBR materials."""
import hashlib,json,math,sys
from pathlib import Path
import bpy,bmesh,numpy as np
from mathutils import Matrix,Vector
from engineering_ship_common import Ship,sha

BUDGET=40000

class RefinedShip(Ship):
    def __init__(self,*args):
        super().__init__(*args)
        self.placement['asset_revision']=2

    def texture(self,name,array,noncolour=False):
        height,width=array.shape[:2];im=bpy.data.images.new(name,width=width,height=height,alpha=True)
        if noncolour:im.colorspace_settings.name='Non-Color'
        im.pixels.foreach_set(array.astype(np.float32).ravel());path=self.maps/(name+'.png');im.filepath_raw=str(path);im.file_format='PNG';im.save();path.write_bytes(self.clean_png(path.read_bytes()));im.reload();im.pack();return im

    def mat(self,name,colour,metal=.2,rough=.6):
        if name in self.materials:return self.materials[name]
        rng=np.random.default_rng(int(hashlib.sha256((self.culture+name).encode()).hexdigest()[:12],16));n=512;y,x=np.mgrid[0:n,0:n]/n
        cloud=np.zeros((n,n));height=np.zeros((n,n));scar=np.zeros((n,n))
        for frequency,weight in [(2,1),(5,.45),(13,.15),(31,.04)]:
            a,b=rng.uniform(0,6.28,2);cloud+=weight*np.sin(x*frequency*6.28+a)*np.sin(y*frequency*5.7+b)
        for i in range(65):
            ax,ay=rng.random(2);angle=rng.uniform(0,6.28);length=rng.uniform(.012,.075);bx=ax+math.cos(angle)*length;by=ay+math.sin(angle)*length
            dx=bx-ax;dy=by-ay;t=np.clip(((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy),0,1);distance=(x-ax-t*dx)**2+(y-ay-t*dy)**2
            mark=np.exp(-distance/(rng.uniform(.0008,.0017)**2));scar=np.maximum(scar,mark*rng.uniform(.35,1));height-=mark*.0018
        for i in range(7):
            ax,ay=rng.random(2);dent=np.exp(-((x-ax)**2+(y-ay)**2)/(rng.uniform(.009,.025)**2));height-=dent*.003
        for i in range(28):
            ax,ay=rng.random(2);angle=rng.uniform(0,6.28);u=(x-ax)*math.cos(angle)+(y-ay)*math.sin(angle);v=-(x-ax)*math.sin(angle)+(y-ay)*math.cos(angle)
            patch=np.exp(-((u/rng.uniform(.009,.030))**2+(v/rng.uniform(.003,.010))**2)*2)
            patch=np.clip((patch-.24+cloud*.035)*2.0,0,1);scar=np.maximum(scar,patch);height-=patch*.0008
        height+=cloud*.0004
        base=np.empty((n,n,4));base[:,:,:3]=np.asarray(colour)[None,None,:]*(1+cloud[:,:,None]*.12)
        # Sparse exposed scratches and darker recess stains; no panel grid.
        exposure=np.array([.48,.49,.46]) if metal>.4 else np.array([.52,.53,.50])
        base[:,:,:3]=base[:,:,:3]*(1-scar[:,:,None]*.42)+exposure*scar[:,:,None]*.42;base[:,:,3]=1;base[:,:,:3]=np.clip(base[:,:,:3],.005,.94)
        r0=.16 if 'visor' in name else max(.30,min(.70,rough-.08));m0=min(.92,metal+.12) if metal>.4 else metal
        orm=np.ones((n,n,4));orm[:,:,1]=np.clip(r0+cloud*.075+scar*.12,.20,.92);orm[:,:,2]=np.clip(m0+scar*.1,0,1)
        height*=.15 if 'visor' in name else 1
        dy,dx=np.gradient(height,1/n);normal=np.stack([-dx*.24,-dy*.24,np.ones_like(dx)],axis=-1);normal/=np.linalg.norm(normal,axis=-1)[:,:,None]
        nm=np.ones((n,n,4));nm[:,:,:3]=normal*.5+.5
        colour_im=self.texture(name,base);orm_im=self.texture(name+'-orm',orm,True);normal_im=self.texture(name+'-normal',nm,True)
        m=bpy.data.materials.new(name);m.use_nodes=True;nodes=m.node_tree.nodes;links=m.node_tree.links;p=nodes.get('Principled BSDF')
        tex=nodes.new('ShaderNodeTexImage');tex.image=colour_im;links.new(tex.outputs['Color'],p.inputs['Base Color'])
        tex=nodes.new('ShaderNodeTexImage');tex.image=orm_im;split=nodes.new('ShaderNodeSeparateColor');split.mode='RGB';links.new(tex.outputs['Color'],split.inputs[0]);links.new(split.outputs['Green'],p.inputs['Roughness']);links.new(split.outputs['Blue'],p.inputs['Metallic'])
        tex=nodes.new('ShaderNodeTexImage');tex.image=normal_im;normalnode=nodes.new('ShaderNodeNormalMap');normalnode.inputs['Strength'].default_value=1;links.new(tex.outputs['Color'],normalnode.inputs['Color']);links.new(normalnode.outputs[0],p.inputs['Normal'])
        self.materials[name]=m;return m

    def finish(self,o,name,mat,parent=None,bevel=0,smooth=False):
        o=super().finish(o,name,mat,parent,0,False)
        if bevel:
            bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Refined continuous edge radius','BEVEL');m.width=bevel;m.segments=6 if bevel>=.08 else 3 if bevel>=.025 else 2;bpy.ops.object.modifier_apply(modifier=m.name)
        for f in o.data.polygons:f.use_smooth=True
        o.data.set_sharp_from_angle(angle=math.radians(25));return o

    def cyl(self,name,p,r,depth,mat,axis=(0,0,1),parent=None,vertices=48):
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=p);o=bpy.context.object;o.rotation_euler=Vector(axis).to_track_quat('Z','Y').to_euler();o=self.finish(o,name,mat,parent,min(r*.045,depth*.12),True);o['engineering_shape']='cylinder';return o

    def ellipsoid(self,name,p,size,mat,parent=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,radius=1,location=p);o=bpy.context.object
        for v in o.data.vertices:v.co=(v.co.x*size[0]/2,v.co.y*size[1]/2,v.co.z*size[2]/2)
        return self.finish(o,name,mat,parent,0,True)

    def ring(self,name,p,outer,inner,depth,mat,axis=(0,0,1),parent=None):
        n=64 if outer>=.2 else 48;verts=[(r*math.cos(i*2*math.pi/n),r*math.sin(i*2*math.pi/n),z) for z in [-depth/2,depth/2] for r in [outer,inner] for i in range(n)];faces=[]
        for i in range(n):
            j=(i+1)%n;faces.extend([(i,j,2*n+j,2*n+i),(n+j,n+i,3*n+i,3*n+j),(j,i,n+i,n+j),(2*n+i,2*n+j,3*n+j,3*n+i)])
        q=Vector(axis).to_track_quat('Z','Y');verts=[tuple(q@Vector(v)+Vector(p)) for v in verts];o=self.solid(name,verts,faces,mat,parent=parent)
        if outer>=.2 and depth>.045:
            bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Machined ring lip radius','BEVEL');m.width=min(.012,depth*.08,(outer-inner)*.10);m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
        return o

    def box(self,name,p,size,mat,bevel=.04,parent=None):
        if self.culture=='terran' and 'integrated engine shroud' in name:
            w,l,h=size;section=[(-.36,-.50),(.36,-.50),(.50,-.34),(.50,.28),(.30,.50),(-.30,.50),(-.50,.28),(-.50,-.34)];n=len(section)
            stations=[(-.50,.82),(-.40,1),(.40,1),(.50,.82)]
            v=[(p[0]+w*x*scale,p[1]+l*y,p[2]+h*z*scale) for y,scale in stations for x,z in section]
            f=[tuple(reversed(range(n))),tuple(range(3*n,4*n))]+[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(3) for i in range(n)]
            return self.solid(name,v,f,mat,.018)
        return super().box(name,p,size,mat,bevel,parent)

    def local(self,o,parent,position,axis=(0,0,1)):
        o.parent=parent;o.matrix_parent_inverse=Matrix.Identity(4);q=Vector(axis).to_track_quat('Z','Y');o.matrix_basis=Matrix.Translation(Vector(position))@q.to_matrix().to_4x4();bpy.context.view_layer.update();return o

    def local_box(self,parent,name,p,size,mat,bevel=.008):return self.local(self.box(name,(0,0,0),size,mat,bevel,parent),parent,p)
    def local_cyl(self,parent,name,p,r,depth,mat,axis=(0,0,1),vertices=24):return self.local(self.cyl(name,(0,0,0),r,depth,mat,parent=parent,vertices=vertices),parent,p,axis)
    def local_ring(self,parent,name,p,r,inner,depth,mat):return self.local(self.ring(name,(0,0,0),r,inner,depth,mat,parent=parent),parent,p)

    def roof(self,parent,name,x,y,size,mat,depth=.022):
        top=max(v.co.z for v in parent.data.vertices)+.3;hit,point,normal,_=parent.ray_cast(Vector((x,y,top)),Vector((0,0,-1)))
        assert hit,('Missing roof surface',name,x,y)
        o=self.box(name,(0,0,0),(size[0],size[1],depth),mat,min(.012,size[0]*.10),parent);return self.local(o,parent,point+normal*(depth*.15),normal)

    def cockpit(self,p,steel,glass):
        # Sloping planar cabin panels retain the established hard-surface language.
        coordinates=[(-.39,-.34,-.16),(.39,-.34,-.16),(.39,.34,-.16),(-.39,.34,-.16),(-.30,-.24,.13),(.30,-.24,.13),(.31,.23,.16),(-.31,.23,.16)]
        verts=[tuple(Vector(v)+Vector(p)) for v in coordinates];faces=[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
        self.solid('Terran low faceted control blister',verts,faces,steel,.024)
        outline=[(-.33,-.075),(.33,-.075),(.295,.070),(-.295,.070)]
        verts=[(p[0]+x,p[1]-.34+(z+.16)*(.10/.29)+offset,p[2]+z) for offset in [.003,-.010] for x,z in outline]
        self.solid('Terran single sloped front visor',verts,[(3,2,1,0),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],glass,.004)

    def enrich(self):
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update();originals=list(self.parts)
        alloy=self.mat('machined-alloy',(.43,.46,.48),.80,.42);seal=self.mat('recess-seal',(.021,.027,.030),.05,.76);edge=self.mat('abraded-tool-steel',(.32,.30,.26),.76,.49)
        for obj in originals:
            if obj.get('engineering_shape')=='cylinder' and any(t in obj.name.lower() for t in ['bearing','hinge']):
                points=[v.co for v in obj.data.vertices];r=max(math.hypot(v.x,v.y) for v in points);half=max(abs(v.z) for v in points)
                for sign in [-1,1]:
                    self.local_ring(obj,'Retaining washer '+obj.name+' '+str(sign),(0,0,sign*half*.98),r*.86,r*.48,min(.025,half*.35),alloy)
                    for i in range(4):
                        a=i*math.pi/2;self.local_cyl(obj,'Recessed hub fastener '+obj.name+' '+str(sign)+str(i),(r*.65*math.cos(a),r*.65*math.sin(a),sign*(half+.005)),r*.065,.017,seal,vertices=6)
            if any(t in obj.name for t in ['cutter tooth','crusher tooth','grading tooth','lifting jaw','gripping jaw','clamp prong','clamp jaw','lifting claw']):
                lo=Vector([min(v.co[a] for v in obj.data.vertices) for a in range(3)]);hi=Vector([max(v.co[a] for v in obj.data.vertices) for a in range(3)]);mid=(lo+hi)/2;size=hi-lo
                self.local_box(obj,'Replaceable worn cutting insert '+str(originals.index(obj)),(mid.x,lo.y+.004,mid.z),(size.x*.83,.025,size.z*.72),edge,.005)
            if 'upper tool arm' in obj.name or 'upper link' in obj.name:
                extent=max(v.co.z for v in obj.data.vertices)-min(v.co.z for v in obj.data.vertices)
                self.local_cyl(obj,'Arm protected service conduit '+obj.name,(.105,0,0),.025,extent*.70,alloy)
                for z in [-extent*.25,extent*.25]:self.local_box(obj,'Arm conduit saddle '+obj.name+str(z),(.075,0,z),(.105,.10,.065),seal)
        self.culture_details(originals,alloy,seal,edge)

    def culture_details(self,originals,alloy,seal,edge):
        def part(text):return next(o for o in originals if text in o.name)
        if self.culture=='terran':
            body=part('solid broad utility hull');hatch=self.roof(body,'Terran gasketed rear maintenance hatch',0,.75,(.42,.31),alloy)
            for x in [-.14,.14]:
                for y in [-.09,.09]:self.local_cyl(hatch,'Terran captive hatch screw '+str(x)+str(y),(x,y,.012),.013,.015,seal,vertices=6)
            for o in originals:
                if 'one horizontal milling drum' in o.name:
                    for z in [-.77,.77]:self.local_ring(o,'Milling rotor end seal '+str(z),(0,0,z),.282,.248,.05,alloy)
        elif self.culture=='rigellian':
            body=part('smooth oval hull');self.roof(body,'Rigellian small conforming service panel',0,-.54,(.24,.25),alloy)
            for o in originals:
                if 'copper working pad' in o.name:self.roof(o,'Rigellian wear shoe '+o.name,0,0,(.17,.12),edge,.015)
        elif self.culture=='braccatian':
            plate=part('dorsal broad reinforcement');cover=self.roof(plate,'Braccatian dorsal service cassette',0,.35,(.30,.45),self.materials['ochre'])
            for y in [-.12,0,.12]:self.local_box(cover,'Braccatian cassette cooling slot '+str(y),(0,y,.013),(.20,.035,.014),seal,.006)
            collar=[o for o in originals if 'single bronze collar' in o.name]
            if collar:
                body=part('ochre barrel hull');self.roof(plate,'Braccatian rear collar inspection plate',0,.75,(.25,.24),self.materials['coral'])
        elif self.culture=='mikotaj':
            body=part('central faceted blue core')
            for x in [-.22,.22]:self.roof(body,'Mikotaj flush core service slot '+str(x),x,0,(.055,.23),seal,.015)
            for o in originals:
                if 'gold core connector' in o.name:
                    self.roof(o,'Mikotaj connector inset',0,0,(.15,.16),alloy,.018)
        elif self.culture=='artemian':
            shell=part('single silver shell')
            for o in originals:
                if 'sparse dorsal vent' in o.name:
                    p=o.location.copy();cutter=self.local_box(self.placement,'Temporary recessed cooling aperture',p,(.062,.25,.13),seal,.015);self.cut(shell,cutter);o.location.z-=.058
        elif self.culture=='mauna':
            body=part('sloping central housing') if self.role=='terraform' else part('squat slab hull')
            hatch=self.roof(body,'Mauna single recessed maintenance cassette',0,.72 if self.role=='terraform' else -.30,(.37,.31),self.materials['blue-grey'])
            for x in [-.12,.12]:
                for y in [-.09,.09]:self.local_cyl(hatch,'Mauna recessed cassette bolt '+str(x)+str(y),(x,y,.012),.014,.018,seal,vertices=6)
            if self.role=='repair':
                for o in originals:
                    if 'tower crown' in o.name:
                        for x in [-.18,.18]:self.roof(o,'Mauna tower cap fastener '+str(x)+o.name,x,0,(.055,.07),alloy,.014)
        elif self.culture=='achaean':
            for o in originals:
                if 'quiet dorsal hatch' in o.name:
                    for x in [-.095,.095]:self.local_cyl(o,'Achaean flush hatch screw '+str(x)+o.name,(x,0,.021),.012,.014,alloy,vertices=6)
            if self.role=='repair':
                body=part('long copper spindle');self.roof(body,'Achaean rear systems inlet',0,1.20,(.20,.18),seal,.015)

    def export(self,author,notes):
        self.enrich();bpy.context.view_layer.update()
        for o in self.parts:
            bpy.context.view_layer.objects.active=o;bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
            bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(island_margin=.025);bpy.ops.object.mode_set(mode='OBJECT')
            m=o.modifiers.new('Stable export triangles','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=m.name)
            bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),o.name;assert bm.calc_volume(signed=True)>0,o.name;bm.to_mesh(o.data);bm.free()
            for f in o.data.polygons:f.use_smooth=True
            o.data.set_sharp_from_angle(angle=math.radians(25));m=o.modifiers.new('Area weighted surface normals','WEIGHTED_NORMAL');m.keep_sharp=True;m.weight=50;bpy.ops.object.modifier_apply(modifier=m.name)
        concepts=json.loads((self.root/'sources/proposals/engineering-ships/concepts.json').read_text());concept,=[x for x in concepts['models'] if x['culture']==self.culture and x['role']==self.role]
        assert sha(self.root/concept['image'])==concept['sha256'];triangles=sum(len(o.data.polygons) for o in self.parts);assert triangles<BUDGET,(self.culture,self.role,triangles)
        bpy.ops.export_scene.gltf(filepath=str(self.folder/'model.glb'),export_format='GLB',export_yup=True,export_animations=True,export_animation_mode='NLA_TRACKS',export_frame_range=True,export_force_sampling=True,export_extras=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(self.folder/'model.blend'),compress=True);p=self.folder/'model.blend';p.write_bytes(self.clean_blend(p.read_bytes())[0])
        points=[o.matrix_world@v.co for o in self.parts for v in o.data.vertices]
        report=dict(issue=265,revision=2,culture=self.culture,role=self.role,status='proposed-assets-awaiting-mechanics',legacy_unit=False,runtime_integration=False,mechanics_available=False,blueprint_registered=False,package_registered=False,binaries={e:sha(self.folder/('model.'+e)) for e in ['blend','glb']},author=Path(author).relative_to(self.root).as_posix(),author_sha256=sha(author),helper='sources/tools/blender/proposals/engineering_ship_common.py',helper_sha256=sha(Path(__file__).with_name('engineering_ship_common.py')),refinement_helper=Path(__file__).relative_to(self.root).as_posix(),refinement_helper_sha256=sha(Path(__file__)),concept=concept,triangles=triangles,triangle_budget=BUDGET,meshes=len(self.parts),materials=len({m for o in self.parts for m in o.data.materials}),maps={p.relative_to(self.root).as_posix():sha(p) for p in self.maps.glob('*.png')},bounds=[min(p[a] for p in points) for a in range(3)]+[max(p[a] for p in points) for a in range(3)],joints=[o.name for o in self.joints],clips=[dict(name='ToolOperation',fps=24,frames=[1,97],seconds=4,motion=self.motion)],scale='Authored proposal units;not calibrated meters/cells or production/hangar clearance',notes=notes+['Revision 2: defined hull planes,controlled edge radii,weighted surface normals,portable colour/ORM/tangent normal maps,material wear and attached mechanical detail.'])
        (self.folder/'model.json').write_text(json.dumps(report,indent=2)+'\n');print('REFINED_PROPOSAL_EXPORTED',self.culture,self.role,triangles,len(self.parts),flush=True)
