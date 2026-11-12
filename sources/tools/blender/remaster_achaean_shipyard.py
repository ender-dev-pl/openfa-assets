"""AC11 compact Achaean shipyard: four lobes, supported spine and surface-seated fitting."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
REAR=[(0,.45),(.08,.52),(.65,.58),(1.25,.60),(1.60,.55),(1.85,.40),(2.02,.17),(2.07,.08)]
FORE=[(0,.50),(.06,.59),(.34,.64),(.61,.56),(.82,.35),(.95,.07)]

def frame(name,w,h,border,depth,mat):
    outer=[(-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2)];inner=[(-w/2+border,-h/2+border),(w/2-border,-h/2+border),(w/2-border,h/2-border),(-w/2+border,h/2-border)];verts=[(a,d,b) for d in [-depth/2,depth/2] for a,b in outer+inner];faces=[]
    for i in range(4):
        j=(i+1)%4;f=(i,j,4+j,4+i);faces.extend([f,tuple(v+8 for v in reversed(f)),(i,i+8,j+8,j),(4+i,4+j,12+j,12+i)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        for li in face.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x/w+.5,p.z/h+.5)
    bpy.context.view_layer.objects.active=o;m=o.modifiers.new('Small closed rim edge radius','BEVEL');m.width=.006;m.segments=2;bpy.ops.object.modifier_apply(modifier=m.name);return o

def cut(body,cutter,name):
    bpy.context.view_layer.objects.active=body;m=body.modifiers.new(name,'BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cutter;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(cutter,do_unlink=True)

def cleanup(obj):
    before=[v.co.copy() for v in obj.data.vertices];original=BVHTree.FromPolygons(before,[tuple(f.vertices) for f in obj.data.polygons]);bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges),obj.name;assert bm.calc_volume(signed=True)>0;bm.to_mesh(obj.data);bm.free();after=[v.co.copy() for v in obj.data.vertices];cleaned=BVHTree.FromPolygons(after,[tuple(f.vertices) for f in obj.data.polygons]);error=max(max(cleaned.find_nearest(p)[3] for p in before),max(original.find_nearest(p)[3] for p in after));assert error<2e-6;print('AC11_BOOLEAN_CLEANUP',obj.name,error,flush=True)


def tube_path(name,path,radius,mat):
    pts=[Vector(p) for p in path];verts=[];n=16
    for j,p in enumerate(pts):
        tangent=(pts[min(j+1,len(pts)-1)]-pts[max(0,j-1)]).normalized();ref=Vector((0,1,0)) if abs(tangent.y)<.9 else Vector((1,0,0));u=tangent.cross(ref).normalized();v=tangent.cross(u).normalized()
        for i in range(n):a=2*math.pi*i/n;verts.append(p+radius*(u*math.cos(a)+v*math.sin(a)))
    faces=[]
    for j in range(len(pts)-1):
        for i in range(n):faces.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    faces.extend([tuple(reversed(range(n))),tuple((len(pts)-1)*n+i for i in range(n))]);mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=len(face.vertices)==4
        for li in face.loop_indices:
            vi=mesh.loops[li].vertex_index;uv.data[li].uv=(vi%n/(n-1),(vi//n)/(len(pts)-1))
    return o


def worn_coral_pbr(mat,folder):
    # Two small authored maps add finish variation without extra geometry.
    shader=mat.node_tree.nodes.get('Principled BSDF');nodes=mat.node_tree.nodes;links=mat.node_tree.links;base=next(n.image for n in nodes if n.type=='TEX_IMAGE');colour=list(base.pixels);maps={}
    def height(x,y):return .015*math.sin(x*.11)*math.cos(y*.14)+.004*math.sin(x*.87+y*.53)
    mr=[];norm=[]
    for y in range(256):
        for x in range(256):
            brightness=colour[(y*256+x)*4]/.43;rough=max(.33,min(.78,.48+.22*(1-brightness)+.03*math.sin(x*.11)*math.cos(y*.13)));mr.extend([1,rough,.48,1]);dx=(height(x+1,y)-height(x-1,y))*4;dy=(height(x,y+1)-height(x,y-1))*4;n=Vector((-dx,-dy,1)).normalized();norm.extend([n.x*.5+.5,n.y*.5+.5,n.z*.5+.5,1])
    for name,pixels in [('Coral metal roughness',mr),('Coral fine wear normal',norm)]:
        image=bpy.data.images.new(name,width=256,height=256);image.colorspace_settings.name='Non-Color';image.pixels.foreach_set(pixels);target=ROOT/'sources/materials/achaean'/folder/(name+'.png');image.filepath_raw=str(target);image.file_format='PNG';image.save();sys.path.insert(0,str(ROOT/'tools'));from publication_support import clean_png;target.write_bytes(clean_png(target.read_bytes()));image.pack();node=nodes.new('ShaderNodeTexImage');node.image=image;maps[name]=node
    split=nodes.new('ShaderNodeSeparateColor');split.mode='RGB';links.new(maps['Coral metal roughness'].outputs['Color'],split.inputs['Color']);links.new(split.outputs['Green'],shader.inputs['Roughness']);links.new(split.outputs['Blue'],shader.inputs['Metallic']);normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.35;links.new(maps['Coral fine wear normal'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],shader.inputs['Normal'])


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='shipyard'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),0,.85);brass=material(folder,'Ochre brass',(.40,.24,.06),.65,.48);red=material(folder,'Red source optics',(.20,.003,.001),.10,.30,.05);blue=material(folder,'Blue base optics',(.025,.12,.32),.25,.25,.10);dark.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.10
    worn_coral_pbr(coral,folder)
    for i,x in enumerate([-.60,.60]):
        body=lathe('AC11 rear chamber '+str(i),(x,.20),REAR,coral)
        cut(body,box('temporary middle red optic',(x,-.36,1.38),(.16,.24,.16),dark,.015),'Middle optic pocket '+str(i))
        o=frame('AC11 middle red rim '+str(i),.205,.205,.025,.14,coral);o.location=(x,-.355,1.38)
        box('AC11 middle red glass '+str(i),(x,-.405,1.38),(.15,.016,.15),red,.015)
        box('AC11 upper red tip '+str(i),(x,.20,2.09),(.10,.10,.18),red,.02);cleanup(body)
    front=[]
    for i,x in enumerate([-.60,.60]):front.append(lathe('AC11 front chamber '+str(i),(x,-.60),FORE,coral))
    for i,dx in enumerate([-.16,.16]):
        cut(front[0],box('temporary left lower slot',(-.60+dx,-1.15,.22),(.10,.25,.14),dark,.012),'Actual lower slot '+str(i))
        box('AC11 lower slot dark floor '+str(i),(-.60+dx,-1.04,.22),(.095,.012,.135),dark,.008)
    lathe('AC11 spine pedestal',(0,-.22),[(0,.18),(.08,.20),(.15,.12),(1.15,.10)],coral)
    box('AC11 blue structural spine',(0,-.22,1.925),(.13,.16,1.65),slate,.012)
    lathe('AC11 ochre spine collar',(0,-.22),[(.75,.104),(.83,.12),(1.09,.12),(1.15,.104)],brass)
    box('AC11 small blue base',(0,-.92,.15),(.30,.24,.30),slate,.02)
    for i,(x,z) in enumerate([(-.07,.21),(.07,.11)]):box('AC11 small base blue optic '+str(i),(x,-1.048,z),(.065,.016,.065),blue,.008)
    # Surface projection establishes support for the ochre arch and coral fitting.
    body=front[1];tree=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons])
    def on_front(x,z,lift):
        hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None;return hit[0]+Vector((0,-lift,0))
    x=.60;path=[on_front(x-.14,.34,.02),on_front(x-.14,.56,.02)]
    for j in range(1,17):a=math.pi*(1-j/16);path.append(on_front(x+.14*math.cos(a),.56+.14*math.sin(a),.02))
    path.append(on_front(x+.14,.34,.02));tube_path('AC11 ochre arched fitting collar',path,.032,brass)
    path=[Vector((x,-1.225,.055)),Vector((x,-1.225,.15))]+[on_front(x,z,.025) for z in [.25,.35,.45,.55,.65]];tube_path('AC11 coral vertical fitting',path,.055,coral)
    lathe('AC11 fitting ground shoe',(x,-1.225),[(0,.075),(.10,.075)],coral)
    for o in front:cleanup(o)
    finish(folder,dict(issue=256,id='openfa:building/legacy/161',key='AC11',name='Shipyard',culture='achaean',footprint=[3,3],definition_class=25,construction_updates=45,triangle_budget=30000,materials=6,structure_checks='checks_achaean_shipyard',state_contract='Static Achaean construction/refitting facility from actual four-lobed legacy evidence. Red/blue source optics have constant low emission. Catalogue reveal/highlight does not establish crane, gate or fitting motion; no Terran shipyard cycle is inferred. Shared ACS3 construction and client activity/damage mapping remain separate.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Client tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
