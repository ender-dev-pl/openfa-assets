"""AC09 Market: curved trading hall, supported side rooms and real blue portholes."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
ROOF=[(0,.57),(.10,.65),(.40,.72),(.95,.75),(1.10,.75),(1.22,.68),(1.80,.70),(2.05,.62),(2.28,.43),(2.50,.17)]

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

def cleanup(obj):
    before=[v.co.copy() for v in obj.data.vertices];original=BVHTree.FromPolygons(before,[tuple(f.vertices) for f in obj.data.polygons]);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0;bm.to_mesh(obj.data);bm.free();after=[v.co.copy() for v in obj.data.vertices];cleaned=BVHTree.FromPolygons(after,[tuple(f.vertices) for f in obj.data.polygons]);error=max(max(cleaned.find_nearest(p)[3] for p in before),max(original.find_nearest(p)[3] for p in after));assert error<2e-6;print('AC09_BOOLEAN_CLEANUP',obj.name,error,flush=True)


def cross(name,width,arm,depth,mat):
    r=width/2;s=arm/2;outline=[(-s,-r),(s,-r),(s,-s),(r,-s),(r,s),(s,s),(s,r),(-s,r),(-s,s),(-r,s),(-r,-s),(-s,-s)];n=len(outline);verts=[(x,y,z) for z in [-depth/2,depth/2] for x,y in outline];faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)];mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x/width+.5,p.y/width+.5)
    bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Tiny glass/frame edge radius','BEVEL');m.width=.003;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name);return o


def surface_medallion(body,mat):
    centre=Vector((0,-.55,2.15));normal=Vector((0,-1,.85)).normalized();right=Vector((1,0,0));up=Vector((0,.85,1)).normalized();tree=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons]);polar=[(0,0)]
    for j in range(1,5):
        for i in range(48):
            a=2*math.pi*i/48;polar.append((.21*j/4*math.cos(a),.21*j/4*math.sin(a)))
    verts=[]
    for lift in [.014,-.018]:
        for x,y in polar:
            hit=tree.ray_cast(centre+right*x+up*y+normal*.70,-normal,2);assert hit[0] is not None;verts.append(hit[0]+normal*lift)
    n=len(polar);front=[]
    for i in range(48):front.append((0,1+i,1+(i+1)%48))
    for j in range(3):
        for i in range(48):
            a=1+j*48+i;b=1+j*48+(i+1)%48;front.append((a,b,b+48,a+48))
    faces=front+[tuple(v+n for v in reversed(f)) for f in front]
    for i in range(48):
        a=1+3*48+i;b=1+3*48+(i+1)%48;faces.append((b,a,a+n,b+n))
    mesh=bpy.data.meshes.new('AC09 upper circular coral casting');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=True
        for li in face.loop_indices:
            x,y=polar[mesh.loops[li].vertex_index%n];uv.data[li].uv=(x/.42+.5,y/.42+.5)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='market'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),0,.85);amber=material(folder,'Warm cross windows',(.85,.42,.055),.2,.30,.7);red=material(folder,'Dark red status',(.15,.002,.001),0,.50);blue=material(folder,'Blue porthole glass',(.025,.12,.32),.25,.25,.10);red.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12;dark.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.10
    hall=lathe('AC09 central market hall',(0,0),ROOF,coral,.05)
    for i,a in enumerate([-math.pi/2-.55,-math.pi/2+.55]):
        cut(hall,radial(box('temporary warm bank',(0,0,0),(.22,.30,.30),dark,.02),a,.68,1.50),'Warm window recess '+str(i))
        radial(frame('AC09 warm window rim '+str(i),.28,.36,.035,.14,coral),a,.69,1.50)
        radial(box('AC09 warm window backing '+str(i),(0,0,0),(.21,.018,.29),dark,.014),a,.55,1.50)
        o=cross('AC09 warm cross '+str(i),.17,.055,.016,amber);o.rotation_euler=(math.pi/2,0,a+math.pi/2);o.location=(.735*math.cos(a),.735*math.sin(a),1.50)
        for j,(x,dz) in enumerate([(-.075,-.075),(.075,-.075),(-.075,.075),(.075,.075)]):
            o=radial(box('AC09 corner blue cell '+str(i)+' '+str(j),(0,0,0),(.035,.014,.035),slate,.005),a,.733,1.50+dz);o.location+=Vector((-math.sin(a),math.cos(a),0))*x
    cut(hall,box('temporary central dark opening',(0,-.67,1.50),(.25,.30,.32),dark,.016),'Central dark opening')
    o=frame('AC09 central opening rim',.30,.38,.025,.12,coral);o.location=(0,-.68,1.50)
    box('AC09 central opening dark floor',(0,-.535,1.50),(.24,.016,.31),dark,.01)
    cut(hall,box('temporary red recess',(0,-.74,.78),(.23,.28,.20),dark,.016),'Lower red recess')
    o=frame('AC09 red status rim',.28,.25,.025,.13,coral);o.location=(0,-.74,.78)
    box('AC09 lower red status',(0,-.78,.78),(.225,.018,.19),red,.014)
    surface_medallion(hall,coral)
    roof_panel('AC09 right flowing casting',[(.24,-.3,.025),(.65,-.35,.10),(1.10,-.45,.08),(1.85,-.5,.05),(2.15,-.6,.025)],coral)
    roof_panel('AC09 left flowing casting',[(.30,-2.6,.025),(.85,-2.6,.08),(1.1,-2.7,.08),(1.9,-2.7,.025)],coral)
    lathe('AC09 coral crown neck',(0,0),[(2.46,.13),(2.58,.08),(2.66,.15),(2.90,.15)],coral)
    lathe('AC09 slate crown hood',(0,0),[(2.82,.17),(2.94,.18),(3.10,.18),(3.18,.10),(3.28,.04)],slate)
    normal=Vector((0,-1,.15)).normalized();q=normal.to_track_quat('Z','Y')
    for i,x in enumerate([-.80,.80]):
        cy=-.40;pod=lathe('AC09 fore pavilion '+str(i),(x,cy),[(0,.38),(.08,.48),(.32,.50),(.52,.44),(.74,.26),(.86,.06)],coral);p=Vector((x,cy-.435,.45))
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.105,depth=.20,location=p-normal*.04);cutter=bpy.context.object;cutter.rotation_euler=q.to_euler();cut(pod,cutter,'Actual round porthole '+str(i))
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.115,depth=.016,location=p-normal*.075);o=bpy.context.object;o.name='AC09 porthole dark floor '+str(i);o.rotation_euler=q.to_euler();o.data.materials.append(dark)
        bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.100,depth=.014,location=p-normal*.01);o=bpy.context.object;o.name='AC09 blue porthole glass '+str(i);o.rotation_euler=q.to_euler();o.data.materials.append(blue)
        bpy.ops.mesh.primitive_torus_add(major_radius=.112,minor_radius=.015,major_segments=48,minor_segments=8,location=p+normal*.02);o=bpy.context.object;o.name='AC09 porthole rim '+str(i);o.rotation_euler=q.to_euler();o.data.materials.append(slate)
        o=cross('AC09 porthole separator '+str(i),.19,.020,.012,slate);o.location=p+normal*.006;o.rotation_euler=q.to_euler();cleanup(pod)
        # Structural stem seated in the fore pavilion, not a floating side room.
        lathe('AC09 side room support '+str(i),(x*1.25,-.03),[(.15,.105),(1.18,.105)],coral)
        lathe('AC09 raised side room '+str(i),(x*1.25,-.03),[(.95,.23),(1.05,.34),(1.40,.36),(1.65,.25),(1.76,.07),(2.03,.045)],coral)
        # Concealed short corridor overlaps the body and side chamber.
        o=lathe('AC09 side room link '+str(i),(0,0),[(0,.19),(.45,.19)],coral);o.rotation_euler.y=math.pi/2 if i else -math.pi/2;o.location=(.62 if i else -.62,-.03,1.30)
    cleanup(hall)
    merge('AC09 warm window rim ','AC09 consolidated warm rims');merge('AC09 warm window backing ','AC09 consolidated warm backs');merge('AC09 corner blue cell ','AC09 consolidated corner cells')
    finish(folder,dict(issue=256,id='openfa:building/legacy/159',key='AC09',name='Market',culture='achaean',footprint=[3,3],definition_class=255,construction_updates=76,triangle_budget=35000,materials=6,structure_checks='checks_achaean_market',state_contract='Static trade/visiting facility. Catalogue reveal/highlight does not establish operating timing. Constant low warm/blue emission; ACS3 construction and client state/activity/damage mapping remain separate.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Client tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
