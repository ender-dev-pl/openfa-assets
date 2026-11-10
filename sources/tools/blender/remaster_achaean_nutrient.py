"""Legacy-led AC05 nutrient processor: tiered copper vessel and conformal castings."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
PROFILE=[(0,.68),(.08,.75),(.34,.78),(.55,.72),(.68,.59),(.78,.54),(1.20,.54),(1.30,.66),(1.40,.77),(1.54,.79),(1.66,.75),(1.75,.63),(1.80,.55),(1.88,.57),(2.10,.64),(2.35,.63),(2.56,.48),(2.70,.26),(2.74,.10)]

def radius(z):
    for a,b in zip(PROFILE,PROFILE[1:]):
        if a[0]<=z<=b[0]:return a[1]+(b[1]-a[1])*(z-a[0])/(b[0]-a[0])
    return PROFILE[-1][1]

def panel(name,outline,mat,offset=.015,rows=25,columns=17):
    def at(z,c):
        for a,b in zip(outline,outline[1:]):
            if a[0]<=z<=b[0]:return a[c]+(b[c]-a[c])*(z-a[0])/(b[0]-a[0])
        return outline[-1][c]
    verts=[]
    for lift in [offset,-.006]:
        for j in range(rows):
            z=outline[0][0]+(outline[-1][0]-outline[0][0])*j/(rows-1);r=radius(z)+lift
            for i in range(columns):
                a=at(z,1)+at(z,2)*(2*i/(columns-1)-1);verts.append((r*math.cos(a),r*math.sin(a),z))
    n=rows*columns;faces=[]
    for j in range(rows-1):
        for i in range(columns-1):
            a=j*columns+i;face=(a,a+1,a+columns+1,a+columns);faces.extend([face,tuple(v+n for v in reversed(face))])
    border=[*range(columns),*[j*columns+columns-1 for j in range(1,rows)],*[(rows-1)*columns+i for i in reversed(range(columns-1))],*[j*columns for j in reversed(range(1,rows-1))]]
    for a,b in zip(border,border[1:]+border[:1]):faces.append((b,a,a+n,b+n))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=True
        for li in face.loop_indices:
            v=mesh.loops[li].vertex_index%n;uv.data[li].uv=((v%columns)/(columns-1),(v//columns)/(rows-1))
    return obj

def frame(name,x,y,z,w,h,border,depth,mat):
    outer=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)];inner=[(-w/2+border,-h/2+border),(w/2-border,-h/2+border),(w/2-border,h/2-border),(-w/2+border,h/2-border)];verts=[(x+a,y+d,z+b) for d in [-depth/2,depth/2] for a,b in outer+inner];faces=[]
    for i in range(4):
        j=(i+1)%4;f=(i,j,4+j,4+i);faces.extend([f,tuple(v+8 for v in reversed(f)),(i,i+8,j+8,j),(4+i,4+j,12+j,12+i)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        for li in face.loop_indices:
            v=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((v.x-x)/w+.5,(v.z-z)/h+.5)
    bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Closed cast rim edge radius','BEVEL');m.width=.006;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name)
    return o

def pocket(body,name,centre,size,dark):
    cutter=box(name,centre,size,dark,.009);bpy.context.view_layer.objects.active=body;m=body.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)

def service_pipe(mat):
    path=[(.59,-.30,1.49),(.66,-.30,1.49)]
    for j in range(1,13):
        a=math.pi/2*(1-j/12);path.append((.66+.12*math.cos(a),-.30,1.37+.12*math.sin(a)))
    path.append((.78,-.30,.56));verts=[];faces=[];n=16
    for j,p in enumerate(path):
        tangent=(Vector(path[min(j+1,len(path)-1)])-Vector(path[max(0,j-1)])).normalized();side=Vector((0,1,0));other=tangent.cross(side).normalized()
        for i in range(n):
            a=2*math.pi*i/n;verts.append(tuple(Vector(p)+.045*(math.cos(a)*side+math.sin(a)*other)))
    for j in range(len(path)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(path)-1)*n+i for i in range(n))]);mesh=bpy.data.meshes.new('AC05 brass service pipe');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=len(face.vertices)==4
        for li in face.loop_indices:
            v=mesh.loops[li].vertex_index;uv.data[li].uv=((v%n)/(n-1),(v//n)/(len(path)-1))

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='nutrient-vats'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);gold=material(folder,'Aged brass',(.49,.34,.13),.72,.42);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),.35,.5);red=material(folder,'Red status lens',(.35,.012,.006),.4,.28,.22);amber=material(folder,'Amber status lens',(.85,.42,.055),.25,.3,.6)
    body=lathe('AC05 tiered main casing',(0,0),PROFILE,coral)
    lathe('AC05 small brass finial',(0,0),[(2.71,.045),(2.89,.045),(2.93,.018)],gold)
    # Closed conformal facing/casting strips maintain the actual rounded tiering.
    panel('AC05 upper right brass',[(1.90,-.65,.025),(2.02,-.65,.30),(2.25,-.70,.36),(2.48,-.82,.30),(2.61,-.95,.02)],gold)
    panel('AC05 upper left brass',[(2.34,-2.12,.02),(2.43,-2.08,.25),(2.56,-1.98,.28),(2.63,-1.85,.02)],gold,rows=17,columns=13)
    panel('AC05 upper lower-left brass',[(1.85,-2.25,.02),(1.91,-2.25,.22),(2.06,-2.33,.20),(2.16,-2.35,.02)],gold,rows=17,columns=13)
    panel('AC05 curved upper casting',[(1.84,-1.43,.095),(2.00,-1.52,.12),(2.16,-1.18,.13),(2.32,-.99,.13),(2.52,-1.25,.12),(2.67,-1.40,.075)],coral,.032)
    panel('AC05 middle brass sweep',[(1.43,-1.4,.02),(1.48,-1.6,.38),(1.54,-1.8,.55),(1.59,-2.0,.25),(1.63,-2.1,.02)],gold)
    panel('AC05 middle right brass',[(1.32,-.42,.02),(1.41,-.40,.25),(1.54,-.40,.25),(1.61,-.45,.02)],gold,rows=17,columns=13)
    panel('AC05 middle raised casting',[(1.31,-1.05,.09),(1.43,-1.18,.11),(1.54,-1.38,.12),(1.64,-1.34,.11),(1.70,-1.20,.075)],coral,.026,rows=17,columns=13)
    for name,z,r,mat in [('base seam',.08,.752,dark),('waist collar',.78,.545,gold),('cap seat',1.80,.554,gold)]:lathe('AC05 '+name,(0,0),[(z-.009,r),(z+.009,r)],mat)
    for i,x in enumerate([-.20,.20]):
        pocket(body,'AC05 temporary base pocket '+str(i),(x,-.65,.35),(.23,.44,.33),dark)
        frame('AC05 base grille rim '+str(i),x,-.71,.35,.29,.39,.03,.20,slate)
        box('AC05 base grille rear '+str(i),(x,-.436,.35),(.225,.012,.325),dark,.003)
        for j,z in enumerate([.24,.35,.46]):box('AC05 base louvre '+str(i)+' '+str(j),(x,-.77,z),(.23,.035,.022),slate,.004)
    for i,x in enumerate([-.12,.12]):
        pocket(body,'AC05 temporary waist pocket '+str(i),(x,-.47,.99),(.09,.34,.22),dark)
        frame('AC05 waist panel rim '+str(i),x,-.50,.99,.13,.28,.02,.12,slate)
        box('AC05 waist panel rear '+str(i),(x,-.306,.99),(.085,.012,.215),slate if i==0 else gold,.003)
    centre=(.80,-.30);lathe('AC05 side service module',centre,[(0,.14),(.06,.18),(.42,.17),(.56,.13),(.62,.07)],slate)
    box('AC05 side module back rib',(1.0,-.12,.29),(.12,.22,.58),slate,.025)
    service_pipe(gold)
    for z in [.62,1.11]:lathe('AC05 service pipe collar '+str(z),(.78,-.30),[(z-.025,.060),(z+.025,.060)],gold)
    seat=lathe('AC05 pipe shoulder seat',(0,0),[(0,.085),(.045,.085)],gold);seat.rotation_euler[1]=math.pi/2;seat.location=(.72,-.30,1.49)
    frame('AC05 red indicator rim',.80,-.468,.26,.105,.39,.02,.07,gold)
    box('AC05 red vertical indicator',(.80,-.509,.26),(.065,.018,.33),red,.01)
    box('AC05 amber indicator housing',(.70,-.32,.60),(.16,.18,.15),slate,.02)
    box('AC05 amber indicator',(.70,-.416,.60),(.10,.015,.07),amber,.006)
    for x in [-.345,-.055,.055,.345]:
        for z in [.155,.545]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.011,depth=.01,location=(x,-.815,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='AC05 grille fastener';o.data.materials.append(gold)
    for j in range(16):
        a=2*math.pi*j/16;bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.01,location=(.556*math.cos(a),.556*math.sin(a),1.80));o=bpy.context.object;o.name='AC05 cap fastener';o.data.materials.append(gold)
    group=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'fastener' in o.name];bpy.ops.object.select_all(action='DESELECT')
    for o in group:o.select_set(True)
    bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name='AC05 consolidated brass fasteners'
    finish(folder,dict(issue=256,id='openfa:building/legacy/155',key='AC05',name='Nutrient Vats',culture='achaean',footprint=[2,2],definition_class=37,construction_updates=40,triangle_budget=30000,materials=6,structure_checks='checks_achaean_nutrient',state_contract='Static nutrient-processing vessel and internal spice-growing cells. Catalogue reveal/highlight does not establish operational timing; constant low indicator emission is not a recovered blink sequence. Client construction/damage/activity mapping remains separate.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Game tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
