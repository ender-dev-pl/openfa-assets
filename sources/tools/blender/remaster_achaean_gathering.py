"""AC08 Gathering Ground: central hall, two supported striped towers, three portals."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
ROOF=[(0,.64),(.10,.74),(.50,.75),(2.90,.75),(3.20,.70),(3.45,.55),(3.70,.28),(3.85,.20)]

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

def shifted(obj,centre):
    obj.location.x+=centre[0];obj.location.y+=centre[1];return obj


def cleanup(obj):
    before=[v.co.copy() for v in obj.data.vertices];original=BVHTree.FromPolygons(before,[tuple(f.vertices) for f in obj.data.polygons]);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0;bm.to_mesh(obj.data);bm.free();after=[v.co.copy() for v in obj.data.vertices];cleaned=BVHTree.FromPolygons(after,[tuple(f.vertices) for f in obj.data.polygons]);error=max(max(cleaned.find_nearest(p)[3] for p in before),max(original.find_nearest(p)[3] for p in after));assert error<2e-6;print('AC08_BOOLEAN_CLEANUP',obj.name,error,flush=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='gathering-ground'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),.35,.5);amber=material(folder,'Warm windows',(.85,.42,.055),.2,.30,.7);red=material(folder,'Dark red alloy',(.07,.0015,.0008),0,.60);brass=material(folder,'Ochre brass',(.40,.24,.06),.65,.48);blue=material(folder,'Blue entrance glass',(.025,.04,.46),.25,.25,.18)
    red.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
    hall=lathe('AC08 central hall',(0,0),ROOF,coral,.05)
    for row,z in enumerate([1.70,2.60]):
        for side,a in enumerate([-math.pi/2-.42,-math.pi/2+.42]):
            key=str(row)+' '+str(side);cut(hall,radial(box('temporary hall bank',(0,0,0),(.22,.26,.52),dark,.024),a,.70,z),'Hall bank '+key)
            radial(frame('AC08 hall rim '+key,.27,.56,.035,.15,coral),a,.71,z)
            radial(box('AC08 hall backing '+key,(0,0,0),(.21,.018,.50),dark,.02),a,.585,z)
            for j,(x,dz) in enumerate([(0,.16),(-.05,0),(.05,0),(0,-.16)]):
                obj=radial(box('AC08 hall pane '+key+' '+str(j),(0,0,0),(.065,.016,.075),amber if j in [1,2] else slate,.012),a,.765,z+dz);obj.location+=Vector((-math.sin(a),math.cos(a),0))*x
    # Seat the inset along the actual shoulder slope rather than a vertical box.
    n=Vector((0,-1,.6)).normalized();p=Vector((0,-.665,3.30));angle=-math.atan(.6)
    cutter=box('temporary upper red recess',p-n*.03,(.18,.22,.53),dark,.02);cutter.rotation_euler.x=angle;cut(hall,cutter,'Upper tilted inset')
    o=frame('AC08 upper slit frame',.23,.58,.025,.12,coral);o.location=p-n*.04;o.rotation_euler.x=angle
    o=box('AC08 upper red inset',p,(.175,.018,.52),red,.016);o.rotation_euler.x=angle
    box('AC08 central small relief',(0,-.78,2.17),(.22,.04,.10),coral,.02)
    roof_panel('AC08 long right flowing casting',[(.45,-.35,.025),(.90,-.40,.09),(2.50,-.48,.12),(3.20,-.60,.025)],coral)
    roof_panel('AC08 left flowing casting',[(.85,-2.6,.025),(1.4,-2.65,.06),(2.9,-2.6,.09),(3.3,-2.4,.025)],coral)
    lathe('AC08 central crown',(0,0),[(3.75,.17),(3.90,.27),(4.10,.32),(4.30,.29),(4.43,.14),(4.48,.075),(4.84,.075)],coral)
    for i,(z,r) in enumerate([(3.98,.301),(4.10,.323),(4.22,.308)]):lathe('AC08 crown brass band '+str(i),(0,0),[(z,r),(z+.065,r)],brass)
    for i,z in enumerate([4.05,4.17]):lathe('AC08 crown red band '+str(i),(0,0),[(z,.322),(z+.045,.322)],red)
    # Three source-visible lower entrance pavilions, with real inset blue panes.
    for i,centre in enumerate([(-1.15,-.10),(0,-.96),(1.15,-.10)]):
        cx,cy=centre;pod=lathe('AC08 entrance pavilion '+str(i),centre,[(0,.44),(.07,.50),(.32,.52),(.55,.47),(.75,.35),(.94,.12),(1.02,.05)],coral)
        cut(pod,box('temporary portal',(cx,cy-.46,.34),(.42,.40,.56),dark,.025),'Blue portal '+str(i))
        o=frame('AC08 portal rim '+str(i),.50,.56,.04,.24,coral);o.location=(cx,cy-.43,.31)
        box('AC08 portal backing '+str(i),(cx,cy-.31,.34),(.415,.016,.55),dark,.018)
        box('AC08 portal centre strip '+str(i),(cx,cy-.50,.31),(.09,.10,.56),coral,.018)
        for j,(x,z) in enumerate([(-.12,.18),(.12,.18),(-.12,.43),(.12,.43)]):box('AC08 blue portal pane '+str(i)+' '+str(j),(cx+x,cy-.48,z),(.13,.02,.16),blue,.012)
        cut(pod,box('temporary portal status',(cx,cy-.33,.64),(.21,.20,.17),dark,.015),'Portal red status '+str(i))
        box('AC08 portal red square '+str(i),(cx,cy-.365,.64),(.20,.035,.16),red,.016)
        box('AC08 portal amber lens '+str(i),(cx,cy-.39,.64),(.065,.018,.055),amber,.01)
        cleanup(pod)
    # Long towers grow from the side pavilions. No duplicate short side posts.
    for i,x in enumerate([-1.15,1.15]):
        centre=(x,.10);lathe('AC08 tower shaft '+str(i),centre,[(.50,.105),(3.70,.105),(3.78,.14)],coral)
        for j in range(14):
            z=.97+j*.19;lathe('AC08 tower band '+str(i)+' '+str(j),centre,[(z,.110),(z+.183,.110)],[slate,brass,red][j%3])
        head=lathe('AC08 tower upper chamber '+str(i),centre,[(3.64,.13),(3.73,.205),(4.20,.205),(4.32,.14),(4.40,.075),(4.70,.075)],coral)
        cut(head,box('temporary tower bank',(x,-.09,3.99),(.10,.20,.33),dark,.016),'Tower window '+str(i))
        o=frame('AC08 tower window rim '+str(i),.14,.38,.018,.085,coral);o.location=(x,-.10,3.99)
        box('AC08 tower window backing '+str(i),(x,-.035,3.99),(.10,.016,.33),dark,.01)
        for j,(dx,dz) in enumerate([(0,.12),(-.023,.035),(.023,.035),(-.023,-.035),(.023,-.035),(0,-.12)]):box('AC08 tower pane '+str(i)+' '+str(j),(x+dx,-.129,3.99+dz),(.030,.016,.04),slate if j in [0,5] else amber,.006)
        cleanup(head)
    lathe('AC08 centre portal short finial',(0,-.96),[(.94,.06),(1.05,.075),(1.68,.075),(1.74,.035)],coral)
    for j in range(4):
        z=1.06+j*.14;lathe('AC08 short finial brass band '+str(j),(0,-.96),[(z,.079),(z+.075,.079)],brass)
    cleanup(hall)
    merge('AC08 hall rim ','AC08 consolidated hall rims');merge('AC08 hall backing ','AC08 consolidated hall backs');merge('AC08 hall pane ','AC08 consolidated hall panes');merge('AC08 tower band ','AC08 consolidated tower bands');merge('AC08 blue portal pane ','AC08 consolidated blue portal panes');merge('AC08 crown brass band ','AC08 consolidated crown brass');merge('AC08 crown red band ','AC08 consolidated crown red');merge('AC08 short finial brass band ','AC08 consolidated short finial brass')
    finish(folder,dict(issue=256,id='openfa:building/legacy/158',key='AC08',name='Gathering Ground',culture='achaean',footprint=[3,3],definition_class=255,construction_updates=68,triangle_budget=45000,materials=7,structure_checks='checks_achaean_gathering',state_contract='Static cultural gathering/festival facility with constant low warm and blue emission. Catalogue reveal/highlight does not establish mechanical or blink timing. Shared ACS3 scaffolding and client state/activity/construction/damage mapping remain separate.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Client tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
