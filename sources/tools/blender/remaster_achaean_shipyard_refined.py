"""AC11 visual revision: articulated cast chambers and constructed source fittings.

The previous AC11 author remains immutable as a bound helper for later models.
"""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cut,cleanup,worn_coral_pbr
REAR=[(0,.46),(.04,.54),(.10,.56),(.13,.54),(.55,.61),(1.15,.62),(1.45,.55),(1.61,.43),(1.65,.41),(1.67,.39),(1.69,.40),(1.85,.22),(1.98,.12),(2.03,.085)]
FORE=[(0,.48),(.035,.57),(.10,.62),(.13,.60),(.40,.67),(.65,.64),(.85,.57),(.96,.49),(.98,.47),(1.00,.49),(1.10,.35),(1.20,.26),(1.27,.23),(1.35,.20),(1.39,.115)]


def revised_finish(coral,folder):
    worn_coral_pbr(coral,folder)
    shader=coral.node_tree.nodes['Principled BSDF'];base=next(n.image for n in coral.node_tree.nodes if n.type=='TEX_IMAGE' and n.image.name.startswith('Coral alloy'));old=list(base.pixels);mr=[];normal=[];colour=[]
    def height(x,y):
        pit=-.035 if (x*37+y*73)%1093<5 else 0
        return .030*math.sin(x*.10)*math.cos(y*.12)+.004*math.sin(x*.83+y*.71)+pit
    for y in range(256):
        for x in range(256):
            i=(y*256+x)*4;grain=((x*1597+y*3571)%1021)/1020;stain=.08*(.5+.5*math.sin(x*.047+y*.018));factor=1-stain
            colour.extend([old[i+j]*factor for j in range(3)]+[1]);rough=.39+.12*grain+.10*(.5+.5*math.cos(x*.043-y*.079))+.09*(1-old[i]/.43);mr.extend([1,min(.74,rough),.68+.08*grain,1]);dx=(height(x+1,y)-height(x-1,y))*4;dy=(height(x,y+1)-height(x,y-1))*4;n=Vector((-dx,-dy,1)).normalized();normal.extend([n.x*.5+.5,n.y*.5+.5,n.z*.5+.5,1])
    sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png
    for image,pixels in [(base,colour),(bpy.data.images['Coral metal roughness'],mr),(bpy.data.images['Coral fine wear normal'],normal)]:
        if image.packed_file:image.unpack(method='REMOVE')
        image.pixels.foreach_set(pixels);image.update();target=ROOT/'sources/materials/achaean'/folder/(image.name.replace(' authored weathering','')+'.png');image.filepath_raw=str(target);image.file_format='PNG';image.save();target.write_bytes(clean_png(target.read_bytes()));image.pack()


def closed_mesh(name,verts,faces,mat):
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x%1,p.z%1)
    bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Constructed fitting edge radius','BEVEL');m.width=.008;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name);return o


def faceted_coupling(name,centre,profile,mat):
    n=8;verts=[(centre[0]+radius*math.cos(2*math.pi*i/n),centre[1]+radius*math.sin(2*math.pi*i/n),z) for z,radius in profile for i in range(n)];faces=[]
    for j in range(len(profile)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(profile)-1)*n+i for i in range(n))]);return closed_mesh(name,verts,faces,mat)


def projected_arch(body,mat):
    tree=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons])
    def seat(x,z,lift):
        hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None;return hit[0]+Vector((0,-lift,0))
    path=[Vector((.40,0,.30)),Vector((.40,0,.70))]
    for i in range(1,17):a=math.pi*(1-i/16);path.append(Vector((.60+.20*math.cos(a),0,.70+.20*math.sin(a))))
    path.append(Vector((.80,0,.30)));verts=[]
    for i,p in enumerate(path):
        t=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized();n=Vector((t.z,0,-t.x))
        for side,lift in [(-1,-.01),(1,-.01),(1,.045),(-1,.045)]:
            q=p+n*side*.05;verts.append(seat(q.x,q.z,lift))
    faces=[]
    for i in range(len(path)-1):
        for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    faces.extend([(3,2,1,0),tuple(4*(len(path)-1)+j for j in range(4))]);return closed_mesh('AC11 broad constructed ochre arch',verts,faces,mat)


def fixture(body,mat):
    tree=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons])
    path=[Vector((.60,-1.30,.055)),Vector((.60,-1.30,.22)),Vector((.60,-1.25,.45))]
    for z in [.65,.85]:
        hit=tree.ray_cast(Vector((.60,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None;path.append(hit[0]+Vector((0,-.045,0)))
    verts=[]
    for i,p in enumerate(path):
        t=(path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized();u=Vector((1,0,0));v=t.cross(u).normalized()
        for a,b in [(-1,-1),(1,-1),(1,1),(-1,1)]:verts.append(p+u*a*.09+v*b*.08)
    faces=[]
    for i in range(len(path)-1):
        for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    faces.extend([(3,2,1,0),tuple(4*(len(path)-1)+j for j in range(4))]);return closed_mesh('AC11 constructed coral service fixture',verts,faces,mat)


def bolt(name,point,mat):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.015,depth=.012,location=point);o=bpy.context.object;o.name=name;o.rotation_euler[0]=math.pi/2;bpy.ops.object.transform_apply(location=False,rotation=True,scale=True);o.data.materials.append(mat);return o


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='shipyard'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),0,.85);brass=material(folder,'Ochre brass',(.40,.24,.06),.65,.48);red=material(folder,'Red source optics',(.20,.003,.001),.10,.30,.05);blue=material(folder,'Blue base optics',(.025,.12,.32),.25,.25,.10);paint=material(folder,'Blue equipment housings',(.035,.085,.20),.50,.42);dark.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.10;revised_finish(coral,folder)
    front=[]
    for i,x in enumerate([-.60,.60]):
        lathe('AC11 rear chamber '+str(i),(x,.20),REAR,coral);lathe('AC11 rear red optic seat '+str(i),(x,.20),[(1.96,.12),(2.035,.12)],coral);box('AC11 rear red optic '+str(i),(x,.20,2.065),(.13,.14,.15),red,.018)
        front.append(lathe('AC11 front chamber '+str(i),(x,-.60),FORE,coral));box('AC11 front red optic '+str(i),(x,-.60,1.425),(.13,.14,.14),red,.018)
    for i,dx in enumerate([-.17,.17]):
        cut(front[0],box('temporary actual lower slot',(-.60+dx,-1.22,.23),(.10,.25,.16),dark,.012),'Actual lower slot '+str(i));box('AC11 lower slot dark floor '+str(i),(-.60+dx,-1.105,.23),(.095,.014,.15),dark,.008)
    lathe('AC11 spine pedestal',(0,-.35),[(0,.14),(.08,.18),(.16,.11),(1.23,.10)],coral)
    box('AC11 blue structural spine',(0,-.35,1.94),(.15,.18,1.72),slate,.022)
    faceted_coupling('AC11 stepped ochre spine coupling',(0,-.35),[(.91,.10),(.96,.14),(1.04,.14),(1.065,.12),(1.10,.16),(1.18,.16),(1.20,.13),(1.24,.14),(1.33,.14)],brass)
    for i,z in enumerate([1.75,2.30]):
        box('AC11 spine strap '+str(i),(0,-.35,z),(.19,.22,.055),slate,.008)
        for j,x in enumerate([-.055,.055]):bolt('AC11 spine strap fastener '+str(i)+' '+str(j),(x,-.467,z),dark)
    box('AC11 source-visible spine side housing',(.12,-.35,2.05),(.12,.16,.26),paint,.015);box('AC11 spine side blue field',(.12,-.438,2.05),(.055,.012,.11),blue,.008)
    for i,(x,y,h,w) in enumerate([(-.12,-1.08,.33,.16),(.055,-1.12,.23,.16),(.20,-1.08,.15,.12)]):
        box('AC11 blue base housing '+str(i),(x,y,h/2),(w,.20,h),paint,.018);box('AC11 blue base field '+str(i),(x,y-.107,h*.68),(w*.45,.012,h*.33),blue,.006)
    projected_arch(front[1],brass);fixture(front[1],coral);box('AC11 fixture ground shoe',(.60,-1.30,.07),(.27,.25,.14),coral,.015)
    for i,x in enumerate([.40,.80]):
        tree=BVHTree.FromPolygons([v.co.copy() for v in front[1].data.vertices],[tuple(f.vertices) for f in front[1].data.polygons]);hit=tree.ray_cast(Vector((x,-2,.37)),Vector((0,1,0)),4);assert hit[0] is not None;bolt('AC11 arch foot fastener '+str(i),(x,hit[0].y-.053,.37),dark)
    for body in front:cleanup(body)
    finish(folder,dict(issue=256,id='openfa:building/legacy/161',key='AC11',name='Shipyard',culture='achaean',footprint=[3,3],definition_class=25,construction_updates=45,triangle_budget=30000,materials=7,structure_checks='checks_achaean_shipyard_refined',visual_revision='construction-detail-and-profile-refinement',supersedes_binaries=dict(blend='80ed5af69eebe7695788cf4ca51654db8958239c7651ba9abe3ab0c75832400c',glb='4212ce95c1a737aeea2ca323c394227f5d499d5f84f530a04d85c6a378837782'),state_contract='Static Achaean construction/refitting facility from four-lobed legacy source. Articulated front shoulders/necks with four seated red fields,broad constructed ochre arch/service fixture,stepped spine coupling,source-visible side fitting and three-part blue equipment cluster. Structural seams/fasteners/hidden rear are conservative authored detail. Red/blue low emission constant; no crane/gate cycle inferred from catalogue reveal. Shared ACS3 and client state/FPS remain separate.',scale_contract='PlacementRoot at groundZ0; Blender-Y front/+Zup. Legacy-led proportions,exact tile/world calibration and final user artistic acceptance separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),Path(__file__).with_name('remaster_achaean_shipyard.py'),Path(__file__).with_name('checks_achaean_shipyard.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
