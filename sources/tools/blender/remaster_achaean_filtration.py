"""AC04 water filtration: asymmetric three-vessel cluster and real filter pockets."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish,clean_png

def tube(name,a,b,radius,mat):
    a,b=Vector(a),Vector(b);length=(b-a).length;o=lathe(name,(0,0),[(0,radius),(length,radius)],mat);o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.location=a;return o

def pocket(body,name,centre,size,mat):
    cutter=box(name,centre,size,mat,.012);bpy.context.view_layer.objects.active=body;mod=body.modifiers.new(name,'BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cutter,do_unlink=True)

def hood(mat):
    outline=[(-.31,1.02),(-.31,1.20),(-.15,1.25),(.27,1.16),(.34,1.10),(.34,1.02)];verts=[(x,y,z) for y in [-.70,-.44] for x,z in outline];n=len(outline);faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new('AC04 steel connector hood');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for poly in mesh.polygons:
        for li in poly.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=((p.x+.31)/.65,(p.z-1.02)/.23)
    bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('Small casting edges','BEVEL');mod.width=.015;mod.segments=2;bpy.ops.object.modifier_apply(modifier=mod.name)

def wet_copper(mat,folder):
    # Authored local mineral/copper stains at the lower UV edge and joint bands.
    image=next(n.image for n in mat.node_tree.nodes if n.type=='TEX_IMAGE')
    # Repack the edited pixels, not the older embedded PNG from material().
    if image.packed_file:image.unpack(method='REMOVE')
    pixels=list(image.pixels)
    for y in range(256):
        for x in range(256):
            u=x/255;v=y/255;stain=.24*math.exp(-((v-.10)/.08)**2)*(math.exp(-((u-.27)/.035)**2)+math.exp(-((u-.71)/.055)**2))+.16*math.exp(-((v-.27)/.06)**2)*math.exp(-((u-.79)/.07)**2);i=(y*256+x)*4;pixels[i]*=1-stain;pixels[i+1]=min(1,pixels[i+1]+stain*.12);pixels[i+2]=min(1,pixels[i+2]+stain*.10)
    image.pixels.foreach_set(pixels);image.update();image.save();path=ROOT/'sources/materials/achaean'/folder/'Coral alloy.png';path.write_bytes(clean_png(path.read_bytes()));image.pack()

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='filtration-vats'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);wet_copper(coral,folder);gold=material(folder,'Aged brass',(.49,.34,.13),.72,.42);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),.35,.5);red=material(folder,'Red status lens',(.34,.012,.006),.4,.28,.18);amber=material(folder,'Amber status lens',(.85,.42,.055),.25,.3,.65)
    maincentre=(0,.12);left=(-.92,-.29);right=(.93,.22)
    body=lathe('AC04 central vessel',maincentre,[(0,.60),(.08,.66),(.20,.64),(1.55,.64),(1.76,.59),(1.96,.42),(2.10,.20),(2.15,.12),(2.18,.08)],coral)
    lathe('AC04 main finial',maincentre,[(2.13,.10),(2.23,.10),(2.26,.05),(2.39,.05),(2.42,.018)],coral)
    lathe('AC04 short left vessel',left,[(0,.26),(.06,.31),(.45,.31),(.64,.25),(.77,.11),(.83,.055)],coral)
    lathe('AC04 short finial',left,[(.80,.055),(.94,.055),(.98,.08),(1.04,.07),(1.08,.02)],coral)
    lathe('AC04 right neck',right,[(0,.20),(.06,.24),(.20,.22),(.96,.22),(1.04,.18),(1.14,.18)],coral)
    lathe('AC04 right bulb',right,[(1.04,.19),(1.10,.28),(1.22,.35),(1.40,.35),(1.57,.28),(1.70,.14),(1.76,.055)],coral)
    lathe('AC04 right finial',right,[(1.72,.06),(1.86,.06),(1.89,.045),(1.96,.018)],coral)
    # Stepped base joints remain visible without converting every cap to gold.
    for name,c,z,r,mat in [('main lower seam',maincentre,.08,.662,dark),('left lower collar',left,.06,.312,gold),('left dome seam',left,.45,.312,dark),('right neck collar',right,.85,.225,gold),('right bulb seam',right,1.21,.351,dark)]:lathe('AC04 '+name,c,[(z-.009,r),(z+.009,r)],mat)
    tube('AC04 low left connection',(-.57,-.10,.28),(-.65,-.24,.28),.10,coral)
    tube('AC04 low right connection',(.55,.10,.35),(.80,.18,.35),.10,coral)
    tube('AC04 hood feed',(.10,-.28,1.13),(.77,.12,1.18),.075,slate)
    hood(slate)
    for i,x in enumerate([-.16,.16]):
        pocket(body,'AC04 temporary filter cutter '+str(i),(x,-.53,.65),(.12,.44,.54),dark)
        box('AC04 filter rear wall '+str(i),(x,-.316,.65),(.115,.012,.53),dark,.003)
        for part,loc,size in [('top',(x,-.53,.94),(.20,.22,.04)),('bottom',(x,-.53,.36),(.20,.22,.04)),('left',(x-.08,-.53,.65),(.04,.22,.546)),('right',(x+.08,-.53,.65),(.04,.22,.546))]:box('AC04 filter rim '+str(i)+' '+part,loc,size,coral,.009)
        for j,z in enumerate([.47,.65,.83]):
            o=box('AC04 filter louvre '+str(i)+' '+str(j),(x,-.60,z),(.12,.045,.035),slate,.005);o.rotation_euler[0]=math.radians(12)
    # Lower broad grille is also a real shallow pocket with two open passages.
    pocket(body,'AC04 temporary lower cutter',(.13,-.50,.24),(.36,.40,.14),dark)
    box('AC04 lower grille rear',(.13,-.306,.24),(.35,.012,.13),dark,.003)
    for part,loc,size in [('top',(.13,-.50,.33),(.44,.20,.04)),('bottom',(.13,-.50,.15),(.44,.20,.04)),('left',(-.07,-.50,.24),(.04,.20,.14)),('right',(.33,-.50,.24),(.04,.20,.14))]:box('AC04 lower grille rim '+part,loc,size,coral,.008)
    box('AC04 lower grille divider',(.13,-.59,.24),(.36,.04,.018),slate,.004)
    # Dark-rimmed four-spoke red port reproduces the observed insert, not a
    # newly invented medical placard or white cross emblem.
    for name,rad,depth,mat,y in [('port casting',.15,.08,coral,-.46),('port dark well',.118,.015,dark,-.536)]:
        o=lathe('AC04 '+name,(0,0),[(0,rad),(depth,rad)],mat);o.rotation_euler[0]=math.pi/2;o.location=(0,y,1.65)
    box('AC04 red port horizontal insert',(0,-.558,1.65),(.15,.02,.045),red,.008)
    box('AC04 red port vertical insert',(0,-.558,1.65),(.045,.02,.15),red,.008)
    for i,x in enumerate([right[0]-.09,right[0]+.09]):
        box('AC04 right lamp surround '+str(i),(x,-.135,1.33),(.10,.08,.12),coral,.012)
        box('AC04 right amber lamp '+str(i),(x,-.181,1.33),(.055,.016,.075),amber,.006)
    box('AC04 left lamp surround',(left[0],-.605,.31),(.14,.08,.16),coral,.014)
    box('AC04 left amber lamp',(left[0],-.65,.31),(.075,.016,.085),amber,.006)
    box('AC04 lower status surround',(-.24,-.54,.24),(.12,.18,.22),coral,.012)
    box('AC04 lower red lens',(-.24,-.638,.29),(.065,.016,.065),red,.005)
    box('AC04 lower amber lens',(-.24,-.638,.20),(.065,.016,.055),amber,.005)
    # Small common fasteners, consolidated by material to control draw nodes.
    for x in [-.24,-.08,.08,.24]:
        for z in [.36,.94]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.011,depth=.01,location=(x,-.646,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='AC04 front fastener';o.data.materials.append(gold)
    for j in range(8):
        a=2*math.pi*j/8;bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.012,depth=.01,location=(.135*math.cos(a),-.542,1.65+.135*math.sin(a)),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='AC04 port fastener';o.data.materials.append(gold)
    group=[o for o in bpy.context.scene.objects if o.type=='MESH' and 'fastener' in o.name]
    bpy.ops.object.select_all(action='DESELECT')
    for o in group:o.select_set(True)
    bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name='AC04 consolidated brass fasteners'
    castings=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0]==coral and any(t in o.name for t in ['filter rim','lower grille rim','lamp surround','lower status surround'])]
    # Union contacting castings, not just coincident closed boxes: a plain
    # join leaves duplicated internal faces/edges at the frame corners.
    base=castings[0];bpy.context.view_layer.objects.active=base
    for other in castings[1:]:
        mod=base.modifiers.new('Closed static casting union','BOOLEAN');mod.operation='UNION';mod.solver='EXACT';mod.object=other;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(other,do_unlink=True)
    before=[v.co.copy() for v in base.data.vertices];original=BVHTree.FromPolygons(before,[tuple(f.vertices) for f in base.data.polygons])
    bm=bmesh.new();bm.from_mesh(base.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(base.data);bm.free()
    after=[v.co.copy() for v in base.data.vertices];cleaned=BVHTree.FromPolygons(after,[tuple(f.vertices) for f in base.data.polygons]);error=max(max(cleaned.find_nearest(p)[3] for p in before),max(original.find_nearest(p)[3] for p in after));assert error<2e-6;print('AC04_CASTING_CLEANUP_ERROR',error,flush=True)
    base.name='AC04 consolidated coral fittings'
    for face in base.data.polygons:face.material_index=0
    base.data.materials.clear();base.data.materials.append(coral)
    finish(folder,dict(issue=256,id='openfa:building/legacy/154',key='AC04',name='Filtration Vats',culture='achaean',footprint=[2,2],definition_class=38,construction_updates=38,triangle_budget=30000,materials=6,structure_checks='checks_achaean_filtration',state_contract='Static water extraction/purification facility. All catalogue frames are reveal/highlight; no operational timing recovered. Amber/red lenses have constant low emission, not an inferred blink sequence. Client construction/damage/activity mapping remains separate.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Tile/world scale calibration remains a client integration task.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
