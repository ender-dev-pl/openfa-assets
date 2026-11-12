"""AC03 Environmental Control: bell casing, real intake pocket and paired plumbing."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
PROFILE=[(0,.79),(.06,.83),(.14,.80),(.22,.65),(.28,.60),(1.14,.60),(1.24,.64),(1.42,.65),(1.64,.61),(1.86,.52),(2.04,.37),(2.15,.20),(2.19,.12)]

def radius(z):
    for a,b in zip(PROFILE,PROFILE[1:]):
        if a[0]<=z<=b[0]:return a[1]+(b[1]-a[1])*(z-a[0])/(b[0]-a[0])
    return PROFILE[-1][1]

def facing(name,outline,mat,rows=25,columns=17):
    def value(z,col):
        for a,b in zip(outline,outline[1:]):
            if a[0]<=z<=b[0]:return a[col]+(b[col]-a[col])*(z-a[0])/(b[0]-a[0])
        return outline[-1][col]
    verts=[]
    for offset in [.015,-.006]:
        for j in range(rows):
            z=outline[0][0]+(outline[-1][0]-outline[0][0])*j/(rows-1);centre=value(z,1);half=value(z,2);r=radius(z)+offset
            for i in range(columns):
                theta=centre+half*(2*i/(columns-1)-1);verts.append((r*math.cos(theta),r*math.sin(theta),z))
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
            index=mesh.loops[li].vertex_index%n;uv.data[li].uv=((index%columns)/(columns-1),(index//columns)/(rows-1))
    return o

def pipe(name,y,mat):
    path=[(.50,y,1.65),(.72,y,1.65)]
    for i in range(1,13):
        a=math.pi/2*(1-i/12);path.append((.72+.14*math.cos(a),y,1.51+.14*math.sin(a)))
    path.append((.86,y,.35));verts=[];faces=[];n=16
    for j,p in enumerate(path):
        tangent=Vector(path[min(j+1,len(path)-1)])-Vector(path[max(0,j-1)]);tangent.normalize();side=Vector((0,1,0));other=tangent.cross(side).normalized()
        for i in range(n):
            a=2*math.pi*i/n;q=Vector(p)+.045*(math.cos(a)*side+math.sin(a)*other);verts.append(tuple(q))
    for j in range(len(path)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(path)-1)*n+i for i in range(n))]);mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=len(face.vertices)==4
        for li in face.loop_indices:
            index=mesh.loops[li].vertex_index;uv.data[li].uv=((index%n)/(n-1),(index//n)/(len(path)-1))
    return o

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='environmental-control'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);gold=material(folder,'Aged brass',(.49,.34,.13),.72,.42);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),.35,.5);red=material(folder,'Red status lens',(.4,.025,.009),.45,.28,.35)
    body=lathe('AC03 bell casing',(0,0),PROFILE,coral)
    # Genuine inset volume: a grille placed over an uncut solid wall would not
    # reproduce the depth in the reviewed concept.
    cutter=box('AC03 temporary intake cutter',(0,-.60,.65),(.34,.50,.60),dark,.015);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new('Real recessed intake pocket','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)
    facing('AC03 upper brass facing',[(1.23,-.78,.05),(1.34,-.92,.45),(1.54,-.78,.58),(1.76,-.84,.61),(1.95,-.95,.50),(2.10,-1.1,.18),(2.14,-1.1,.025)],gold)
    facing('AC03 lower left inspection facing',[(1.38,-2.0,.03),(1.45,-2.0,.24),(1.58,-2.05,.25),(1.67,-2.05,.03)],gold,17,13)
    facing('AC03 upper left inspection facing',[(1.87,-2.0,.025),(1.92,-2.0,.15),(2.00,-2.0,.15),(2.04,-2.0,.025)],gold,13,11)
    lathe('AC03 top bulb',(0,0),[(2.15,.12),(2.26,.12),(2.32,.20),(2.42,.23),(2.50,.19),(2.57,.08),(2.61,.04)],coral,.015)
    lathe('AC03 finial',(0,0),[(2.58,.04),(2.77,.04),(2.80,.015)],slate)
    for name,z,r,mat in [('lower seam',.14,.801,dark),('shoulder seam',1.22,.635,gold),('bulb neck collar',2.22,.125,gold)]:lathe('AC03 '+name,(0,0),[(z-.009,r),(z+.009,r)],mat)
    # Four open frame strips and a rear well, with 2 vertical/4 horizontal bars.
    for name,loc,size in [('top',(0,-.575,.98),(.46,.10,.06)),('bottom',(0,-.575,.32),(.46,.10,.06)),('left',(-.20,-.575,.65),(.06,.10,.60)),('right',(.20,-.575,.65),(.06,.10,.60))]:box('AC03 intake rim '+name,loc,size,slate,.012)
    box('AC03 intake dark rear wall',(0,-.356,.65),(.335,.012,.59),dark,.004)
    for i,x in enumerate([-.0567,.0567]):box('AC03 vertical grille bar '+str(i),(x,-.605,.65),(.014,.04,.60),slate,.004)
    for i,z in enumerate([.47,.59,.71,.83]):box('AC03 horizontal grille bar '+str(i),(0,-.605,z),(.34,.04,.014),slate,.004)
    # Status indicator is seated against the curved casing, no gameplay state
    # animation or timing is inferred from the catalogue highlight effect.
    box('AC03 status surround',(.34,-.53,.75),(.105,.09,.42),gold,.018)
    box('AC03 status recess',(.34,-.58,.75),(.065,.016,.35),dark,.012)
    box('AC03 red vertical status lens',(.34,-.596,.75),(.045,.018,.30),red,.01)
    for i,y in enumerate([-.23,.23]):
        centre=(.86,y);lathe('AC03 blue pump '+str(i),centre,[(0,.15),(.04,.18),(.09,.15),(.32,.15),(.39,.12),(.43,.065)],slate)
        pipe('AC03 copper riser '+str(i),y,coral)
        for z in [.43,1.02]:lathe('AC03 riser collar '+str(i)+' '+str(z),centre,[(z-.025,.060),(z+.025,.060)],gold)
        flange=lathe('AC03 shoulder pipe seat '+str(i),(0,0),[(0,.085),(.045,.085)],gold);flange.rotation_euler[1]=math.pi/2;flange.location=(.56,y,1.65)
        port=lathe('AC03 pump port '+str(i),(0,0),[(0,.058),(.023,.058)],gold);port.rotation_euler[0]=math.pi/2;port.location=(.86,y-.148,.21)
    for x in [-.20,.20]:
        for z in [.32,.98]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.015,depth=.012,location=(x,-.632,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='AC03 intake fastener';o.data.materials.append(gold)
    for j in range(16):
        a=2*math.pi*j/16
        bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.012,location=(.637*math.cos(a),.637*math.sin(a),1.22));o=bpy.context.object;o.name='AC03 shoulder fastener';o.data.materials.append(slate)
    for mat in [coral,gold,slate,dark,red]:
        group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0]==mat and 'fastener' in o.name]
        if group:
            bpy.ops.object.select_all(action='DESELECT')
            for o in group:o.select_set(True)
            bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name='AC03 consolidated '+mat.name+' fasteners'
    finish(folder,dict(issue=256,id='openfa:building/legacy/153',key='AC03',name='Environmental Control',culture='achaean',footprint=[2,2],definition_class=35,construction_updates=36,triangle_budget=30000,materials=5,structure_checks='checks_achaean_environmental',state_contract='Static environmental control and emergency reserves. All catalogue phases are reveal/highlight; no operational timing established. Construction/damage/activity mappings remain client integration.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up; game tile/world scale requires calibration.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
