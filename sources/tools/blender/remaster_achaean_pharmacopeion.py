"""AC07 curved medical facility with real entrance, paired banks and onion crown."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
ROOF=[(1.95,.27),(2.06,.44),(2.22,.62),(2.50,.68),(2.76,.61),(2.95,.48),(3.07,.35),(3.16,.23),(3.22,.14),(3.38,.06),(3.43,.025)]

def frame(name,w,h,border,depth,mat):
    outer=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)];inner=[(-w/2+border,-h/2+border),(w/2-border,-h/2+border),(w/2-border,h/2-border),(-w/2+border,h/2-border)];verts=[(a,d,b) for d in [-depth/2,depth/2] for a,b in outer+inner];faces=[]
    for i in range(4):
        j=(i+1)%4;f=(i,j,4+j,4+i);faces.extend([f,tuple(v+8 for v in reversed(f)),(i,i+8,j+8,j),(4+i,4+j,12+j,12+i)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x/w+.5,p.z/h+.5)
    bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Small closed rim edge radius','BEVEL');m.width=.006;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name);return o

def radial(obj,a,r,z):
    obj.rotation_euler[2]=a+math.pi/2;obj.location=(r*math.cos(a),r*math.sin(a),z);return obj

def cut(body,cutter,name):
    bpy.context.view_layer.objects.active=body;m=body.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)

def roof_panel(name,outline,mat):
    def r(z):
        for a,b in zip(ROOF,ROOF[1:]):
            if a[0]<=z<=b[0]:return a[1]+(b[1]-a[1])*(z-a[0])/(b[0]-a[0])
        return ROOF[-1][1]
    def value(z,c):
        for a,b in zip(outline,outline[1:]):
            if a[0]<=z<=b[0]:return a[c]+(b[c]-a[c])*(z-a[0])/(b[0]-a[0])
        return outline[-1][c]
    rows=25;columns=21;verts=[]
    for lift in [.025,-.006]:
        for j in range(rows):
            z=outline[0][0]+(outline[-1][0]-outline[0][0])*j/(rows-1)
            for i in range(columns):
                a=value(z,1)+value(z,2)*(2*i/(columns-1)-1);radius=r(z)*(1+.05*math.cos(8*a))+lift;verts.append((radius*math.cos(a),radius*math.sin(a),z))
    n=rows*columns;faces=[]
    for j in range(rows-1):
        for i in range(columns-1):
            a=j*columns+i;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(v+n for v in reversed(f))])
    border=[*range(columns),*[j*columns+columns-1 for j in range(1,rows)],*[(rows-1)*columns+i for i in reversed(range(columns-1))],*[j*columns for j in reversed(range(1,rows-1))]]
    for a,b in zip(border,border[1:]+border[:1]):faces.append((b,a,a+n,b+n))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=True
        for li in face.loop_indices:
            v=mesh.loops[li].vertex_index%n;uv.data[li].uv=((v%columns)/(columns-1),(v//columns)/(rows-1))

def merge(prefix,name):
    group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name.startswith(prefix)];assert group;bpy.ops.object.select_all(action='DESELECT')
    for o in group:o.select_set(True)
    bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name=name

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='pharmacopeion'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),.35,.5);amber=material(folder,'Warm windows',(.85,.42,.055),.2,.30,.7);red=material(folder,'Dark red status',(.08,.006,.003),.20,.45);brass=material(folder,'Worn brass feet',(.40,.24,.06),.65,.48)
    base=lathe('AC07 curved lower quarters',(0,0),[(0,.90),(.08,1.02),(.25,1.22),(.50,1.24),(.80,1.20),(1.0,1.13),(1.20,.93),(1.48,.40)],coral)
    for vertex in base.data.vertices:
        angle=math.atan2(vertex.co.y,vertex.co.x);wave=1.10*(1-.10*math.cos(4*angle));vertex.co.x*=wave;vertex.co.y*=wave
    base.data.update()
    # The actual opening crosses the whole lower shell; no painted black arch.
    cut(base,box('temporary entrance rectangle',(0,0,.15),(.60,3.2,.60),dark,0),'Entrance lower opening')
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.30,depth=3.2,location=(0,0,.45),rotation=(math.pi/2,0,0));cut(base,bpy.context.object,'Entrance arch')
    for side in [-1,1]:box('AC07 brass entrance foot '+str(side),(side*.39,-1.05,.045),(.18,.32,.09),brass,.025)
    neck=lathe('AC07 narrow neck',(0,0),[(1.35,.35),(1.48,.33),(1.95,.33),(2.08,.30)],coral)
    for i,a in enumerate([-math.pi/2-.34,-math.pi/2+.34,math.pi/2-.34,math.pi/2+.34]):
        cut(neck,radial(box('temporary neck inset',(0,0,0),(.12,.14,.51),dark,.025),a,.32,1.71),'Neck inset '+str(i))
        radial(box('AC07 blue neck inset '+str(i),(0,0,0),(.112,.018,.49),slate,.02),a,.326,1.71)
    upper=lathe('AC07 onion upper chamber',(0,0),ROOF,coral,.05)
    roof_panel('AC07 upper flowing casting',[(2.23,-2.10,.03),(2.37,-1.90,.44),(2.59,-1.45,.40),(2.72,-1.18,.03)],coral)
    roof_panel('AC07 lower flowing casting',[(2.03,-1.7,.025),(2.14,-1.4,.26),(2.29,-1.0,.26),(2.40,-.8,.025)],coral)
    roof_panel('AC07 side flowing casting',[(2.30,-.20,.025),(2.49,-.28,.26),(2.65,-.50,.20),(2.80,-.70,.025)],coral)
    cut(upper,box('temporary red slit',(0,-.50,2.92),(.50,.30,.075),dark,.016),'Upper red slit')
    box('AC07 upper dark red slit',(0,-.445,2.92),(.49,.018,.063),red,.012)
    # The two front banks are source-visible; understated rear banks are authored.
    for i,a in enumerate([math.atan2(-.96,-.72),math.atan2(-.96,.72),math.atan2(.96,-.72),math.atan2(.96,.72)]):
        cut(base,radial(box('temporary window pocket',(0,0,0),(.19,.30,.78),dark,.02),a,1.36,.61),'Paired window pocket '+str(i))
        radial(frame('AC07 window rim '+str(i),.25,.84,.035,.22,coral),a,1.35,.61)
        radial(box('AC07 window backing '+str(i),(0,0,0),(.18,.016,.77),dark,.014),a,1.23,.61)
        for j,(x,z) in enumerate([(-.045,.43),(.045,.43),(-.045,.59),(.045,.59),(-.045,.75),(.045,.75),(0,.32),(0,.90)]):
            obj=radial(box('AC07 warm pane '+str(i)+' '+str(j),(0,0,0),(.057,.016,.075),slate if j==7 else amber,.012),a,1.43,z);obj.location+=Vector((-math.sin(a),math.cos(a),0))*x
    cut(base,box('temporary service pocket',(0,-1.12,.99),(.43,.50,.32),dark,.025),'Central service pocket')
    box('AC07 central dark red panel',(0,-1.12,.99),(.36,.025,.25),red,.015)
    box('AC07 central amber lens',(0,-1.14,.95),(.19,.02,.06),amber,.014)
    # Clean only sub-micron Boolean artefacts and retain measured surface fidelity.
    for obj in [base,neck,upper]:
        before=[v.co.copy() for v in obj.data.vertices];original=BVHTree.FromPolygons(before,[tuple(f.vertices) for f in obj.data.polygons]);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(obj.data);bm.free();after=[v.co.copy() for v in obj.data.vertices];cleaned=BVHTree.FromPolygons(after,[tuple(f.vertices) for f in obj.data.polygons]);error=max(max(cleaned.find_nearest(p)[3] for p in before),max(original.find_nearest(p)[3] for p in after));assert error<2e-6;print('AC07_BOOLEAN_CLEANUP',obj.name,error,flush=True)
    merge('AC07 window rim ','AC07 consolidated window rims');merge('AC07 window backing ','AC07 consolidated window backs');merge('AC07 warm pane ','AC07 consolidated window panes')
    finish(folder,dict(issue=256,id='openfa:building/legacy/157',key='AC07',name='Pharmacopeion',culture='achaean',footprint=[3,3],definition_class=34,construction_updates=30,triangle_budget=35000,materials=6,structure_checks='checks_achaean_pharmacopeion',state_contract='Static medical/herbal treatment facility. Catalogue reveal/highlight does not establish operational timing. Low constant warm lights; activity/construction/damage mapping remains client integration.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Client tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
