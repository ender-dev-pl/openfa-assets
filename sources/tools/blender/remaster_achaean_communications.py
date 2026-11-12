"""AC10 Communications Central: asymmetric pods, actual roof bores and 18-cell strip."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
ROOF=[(0,.63),(.10,.72),(1.65,.74),(2.40,.74),(2.75,.66),(2.95,.49),(3.20,.40),(3.42,.36),(3.52,.46),(3.64,.47),(3.75,.35),(3.83,.27)]
LEFT=[(0,.72),(.09,.83),(.37,.83),(.52,.72),(.62,.65),(.90,.54),(1.12,.32),(1.24,.08)]
RIGHT=[(0,.70),(.10,.83),(.26,.83),(.34,.76),(.43,.78),(.51,.70),(.59,.65),(.80,.60),(1.05,.44),(1.20,.21),(1.24,.07)]

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

def roof_panel(name,outline,mat,profile=None,centre=(0,0),wave=.05):
    profile=ROOF if profile is None else profile
    def r(z):
        for a,b in zip(profile,profile[1:]):
            if a[0]<=z<=b[0]:return a[1]+(b[1]-a[1])*(z-a[0])/(b[0]-a[0])
        return profile[-1][1]
    def value(z,c):
        for a,b in zip(outline,outline[1:]):
            if a[0]<=z<=b[0]:return a[c]+(b[c]-a[c])*(z-a[0])/(b[0]-a[0])
        return outline[-1][c]
    rows=25;columns=21;verts=[]
    for lift in [.025,-.006]:
        for j in range(rows):
            z=outline[0][0]+(outline[-1][0]-outline[0][0])*j/(rows-1)
            for i in range(columns):
                a=value(z,1)+value(z,2)*(2*i/(columns-1)-1);radius=r(z)*(1+wave*math.cos(8*a))+lift;verts.append((centre[0]+radius*math.cos(a),centre[1]+radius*math.sin(a),z))
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

def cleanup(obj):
    before=[v.co.copy() for v in obj.data.vertices];original=BVHTree.FromPolygons(before,[tuple(f.vertices) for f in obj.data.polygons]);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0;bm.to_mesh(obj.data);bm.free();after=[v.co.copy() for v in obj.data.vertices];cleaned=BVHTree.FromPolygons(after,[tuple(f.vertices) for f in obj.data.polygons]);error=max(max(cleaned.find_nearest(p)[3] for p in before),max(original.find_nearest(p)[3] for p in after));assert error<2e-6;print('AC10_BOOLEAN_CLEANUP',obj.name,error,flush=True)


def cylinder(name,p,normal,radius,depth,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=p);o=bpy.context.object;o.name=name;o.rotation_euler=normal.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);return o


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='communications-central'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),0,.85);cyan=material(folder,'Cyan front glass',(.06,.21,.29),.15,.20,.12);blue=material(folder,'Deep blue strip',(.009,.009,.16),0,.60,.15);violet=material(folder,'Violet strip',(.285,.090,.42),0,.60,.15);light=material(folder,'Cold blue strip',(.10,.205,.425),0,.60,.15);red=material(folder,'Dark red terminal',(.15,.002,.001),0,.50);dark.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.10;red.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
    for m in [blue,violet,light]:m.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.10
    tower=lathe('AC10 central information tower',(0,0),ROOF,coral,.05)
    lathe('AC10 tiered slate hood',(0,0),[(3.75,.28),(3.84,.30),(4.13,.30),(4.25,.24),(4.30,.18),(4.44,.18),(4.52,.10),(4.66,.04)],slate)
    roof_panel('AC10 upper coral casting',[(2.93,-2.2,.025),(3.05,-1.7,.40),(3.15,-1.4,.43),(3.25,-1.3,.025)],coral)
    cut(tower,box('temporary strip pocket',(0,-.74,1.45),(.16,.35,1.84),dark,.015),'Front strip recess')
    o=frame('AC10 long coral display case',.24,2.02,.04,.22,coral);o.location=(0,-.77,1.45)
    box('AC10 strip dark back',(0,-.59,1.45),(.155,.016,1.83),dark,.008)
    for i in range(18):box('AC10 display cell '+str(i),(0,-.865,.60+i*.10),(.13,.014,.09),[blue,violet,light][i%3],.006)
    lathe('AC10 display brow',(0,-.77),[(2.42,.12),(2.53,.11),(2.60,.03)],coral)
    left=lathe('AC10 left receiver chamber',(-1.05,-.03),LEFT,coral)
    lathe('AC10 left base seam',(-1.05,-.03),[(.045,.80),(.065,.80)],slate)
    for i in range(3):
        a=[-2.8,-1.6,-.4][i];roof_panel('AC10 left rosette casting '+str(i),[(.58,a,.03),(.70,a+.10,.25),(.90,a+.25,.38),(1.10,a+.50,.25),(1.22,a+.65,.015)],coral,LEFT,(-1.05,-.03),0)
    lathe('AC10 left short post',(-1.20,.07),[(1.04,.05),(1.52,.05),(1.56,.03)],coral)
    for i,a in enumerate([-math.pi/2-.35,-math.pi/2+.35]):
        n=Vector((math.cos(a),math.sin(a),0));p=Vector((-1.05+.80*math.cos(a),-.03+.80*math.sin(a),.23));cut(left,cylinder('temporary front glass bore',p-n*.02,n,.09,.16,dark),'Left front bore '+str(i));cylinder('AC10 front window dark back '+str(i),p-n*.055,n,.10,.016,dark);o=cylinder('AC10 cyan glass '+str(i),p-n*.005,n,.082,.014,cyan);bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Small glass edge','BEVEL');m.width=.004;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
        bpy.ops.mesh.primitive_torus_add(major_radius=.094,minor_radius=.012,major_segments=48,minor_segments=8,location=p+n*.025);o=bpy.context.object;o.name='AC10 cyan window rim '+str(i);o.rotation_euler=n.to_track_quat('Z','Y').to_euler();o.data.materials.append(slate)
    right=lathe('AC10 right aperture chamber',(1.05,-.03),RIGHT,coral)
    for i,(dx,dy) in enumerate([(-.23,-.28),(.24,-.40)]):
        r=math.hypot(dx,dy)
        if i==0:z=1.05+(.44-r)/(.44-.21)*.15;slope=(.44-.21)/.15
        else:z=.80+(.60-r)/(.60-.44)*.25;slope=(.60-.44)/.25
        n=Vector((dx/r,dy/r,slope)).normalized();p=Vector((1.05+dx,-.03+dy,z));cut(right,cylinder('temporary roof bore',p-n*.07,n,.09,.24,dark),'Actual roof aperture '+str(i));cylinder('AC10 roof aperture dark floor '+str(i),p-n*.07,n,.092,.012,dark)
        bpy.ops.mesh.primitive_torus_add(major_radius=.100,minor_radius=.018,major_segments=48,minor_segments=8,location=p+n*.005);o=bpy.context.object;o.name='AC10 roof aperture cast lip '+str(i);o.rotation_euler=n.to_track_quat('Z','Y').to_euler();o.data.materials.append(coral)
    terminal=lathe('AC10 foreground terminal',(0,-.92),[(0,.17),(.03,.23),(.25,.23),(.44,.15),(.49,.05)],coral)
    cut(terminal,box('temporary red terminal pocket',(0,-1.12,.23),(.12,.16,.12),dark,.012),'Red terminal recess')
    o=frame('AC10 red terminal rim',.17,.17,.025,.10,coral);o.location=(0,-1.10,.23)
    box('AC10 red terminal glass',(0,-1.125,.23),(.112,.014,.112),red,.01)
    for o in [tower,left,right,terminal]:cleanup(o)
    merge('AC10 display cell ','AC10 eighteen display cells')
    finish(folder,dict(issue=256,id='openfa:building/legacy/160',key='AC10',name='Communications Central',culture='achaean',footprint=[3,3],definition_class=24,construction_updates=36,triangle_budget=35000,materials=8,structure_checks='checks_achaean_communications',state_contract='Static information-evaluation and communication facility. Eighteen authored blue/violet/cold-blue cells follow the actual visible palette sequence, with constant low emission. Catalogue reveal/highlight does not establish antenna motion, blinking or data scrolling. Shared ACS3 construction and client state/activity/damage mapping remain separate.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Client tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
