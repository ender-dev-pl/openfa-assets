"""AC16 two-tier cast body, source-visible raised fittings and four grounded pods."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cut,cleanup,worn_coral_pbr
from remaster_achaean_missile_launcher import surface_y
PODS=[(-.98,.38,.46,.23),(-.98,-.24,.36,.18),(-.27,-.93,.28,.13),(.27,-.93,.28,.13)]


def patch(name,body,centre,outline,mat):
    # Project both sides of a closed small raised casting onto the real casing.
    tree=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons])
    def point(dx,dz,lift):
        x=centre[0]+dx;z=centre[1]+dz;hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None;return hit[0]+Vector((0,-lift,0))
    # Smooth the outline and round the relief through five source-seated rings.
    curve=[]
    for i in range(len(outline)):
        p0,p1,p2,p3=[Vector(outline[j%len(outline)]) for j in [i-1,i,i+1,i+2]]
        for j in range(8):
            t=j/8;v=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t);curve.append(v)
    n=len(curve);layers=[(.90,-.01),(1.0,.005),(.92,.030),(.70,.047),(.20,.054)]
    verts=[point(v.x*scale,v.y*scale,lift) for scale,lift in layers for v in curve];verts.extend([point(0,0,-.01),point(0,0,.055)]);faces=[]
    for layer in range(len(layers)-1):
        for i in range(n):
            j=(i+1)%n;a=layer*n;b=(layer+1)*n;faces.append((a+i,a+j,b+j,b+i))
    for i in range(n):
        j=(i+1)%n;faces.extend([(len(layers)*n,j,i),(len(layers)*n+1,(len(layers)-1)*n+i,(len(layers)-1)*n+j)])
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges) and bm.calc_volume(signed=True)>0;bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for f in mesh.polygons:
        f.use_smooth=True
        for li in f.loop_indices:
            p=mesh.vertices[mesh.loops[li].vertex_index].co;uv.data[li].uv=(p.x+.5,p.z%1)
    return o


def field(body,name,x,z,w,h,mat,dark):
    tree=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[tuple(f.vertices) for f in body.data.polygons]);hit=tree.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4);assert hit[0] is not None
    point,normal=hit[0],hit[1].normalized();assert normal.y<0;q=normal.to_track_quat('-Y','Z')
    cutter=box('temporary source field pocket',point+normal*.02,(w+.025,.20,h+.025),dark,.012);cutter.rotation_mode='QUATERNION';cutter.rotation_quaternion=q;cut(body,cutter,'Actual source field '+name)
    back=box(name+' dark back',point-normal*.065,(w+.010,.008,h+.010),dark,.008);back.rotation_mode='QUATERNION';back.rotation_quaternion=q
    pane=box(name,point-normal*.05,(w,.014,h),mat,.008);pane.rotation_mode='QUATERNION';pane.rotation_quaternion=q
    return pane


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='manoeuvring-device'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate grounded pods',(.16,.24,.29),.7,.40);dark=material(folder,'Dark source recess',(.015,.020,.025),0,.87);brass=material(folder,'Ochre raised fittings',(.35,.25,.11),.65,.46);red=material(folder,'Red source fields and stems',(.24,.006,.002),.25,.40);cyan=material(folder,'Pale blue source field',(.28,.43,.50),.12,.30,.10)
    worn_coral_pbr(coral,folder)
    base=lathe('AC16 broad ground chamber',(0,0),[(0,.64),(.08,.84),(.28,.98),(.52,.94),(.75,.75),(.88,.50),(.94,.36)],coral)
    lathe('AC16 connected narrow waist',(0,.10),[(.82,.34),(1.23,.34)],coral)
    upper=lathe('AC16 upper tear-drop chamber',(0,.10),[(1.12,.35),(1.25,.63),(1.45,.75),(1.70,.72),(1.94,.58),(2.18,.40),(2.42,.25),(2.61,.14),(2.70,.07)],coral)
    lathe('AC16 short slate tip',(0,.10),[(2.64,.055),(2.96,.055)],slate)
    top=[(-.11,-.12),(.03,-.16),(.12,-.04),(.08,.12),(-.06,.15),(-.11,.03)]
    left=[(-.13,-.10),(-.04,-.05),(.10,.01),(.11,.13),(.02,.19),(-.07,.08),(-.16,.00)]
    right=[(-.12,.16),(.00,.17),(.12,.06),(.09,-.12),(.04,-.16),(-.06,-.12),(-.05,.04)]
    for i,(centre,outline) in enumerate([((.08,2.30),top),((-.30,2.02),left),((.30,1.72),right)]):patch('AC16 upper ochre fitting '+str(i),upper,centre,outline,brass)
    patch('AC16 lower ochre fitting',base,(.60,.40),[(-.15,.11),(-.04,.16),(.06,.08),(.16,-.05),(.12,-.13),(-.03,-.10),(-.09,.02)],brass)
    field(upper,'AC16 upper red source field',0,1.38,.28,.10,red,dark)
    field(base,'AC16 pale blue source slot',0,.77,.45,.075,cyan,dark)
    for i,x in enumerate([-.18,.18]):field(base,'AC16 lower red source field '+str(i),x,.49,.13,.16,red,dark)
    for i,(x,y,h,cap) in enumerate(PODS):
        lathe('AC16 grounded slate pod '+str(i),(x,y),[(0,.12),(.03,.16),(h-.03,.15),(h,.12)],slate)
        lathe('AC16 red pod stem '+str(i),(x,y),[(h-.01,.075),(h+.07,.06),(h+cap-.03,.04),(h+cap,.02)],red)
    for o in [base,upper]:cleanup(o)
    finish(folder,dict(issue=256,id='openfa:building/legacy/166',key='AC16',name='Manoeuvring Device',culture='achaean',footprint=[2,2],definition_class=22,construction_updates=68,triangle_budget=30000,materials=6,structure_checks='checks_achaean_manoeuvring_device',state_contract='Static asteroid-engine equivalent from actual shadow/body and fixed-view catalogue. Two-tier coral body,three upper surface-seated ochre fittings,one lower fitting,pale-blue slot,three red source fields and four grounded slate/red pods in the source-visible left/front arrangement. No rear pods,unobserved thrust effect or movement inferred. Fitting functions/hidden rear interpreted. Shared ACS2 construction and client propulsion/state mapping remain separate.',scale_contract='PlacementRoot at groundZ0; Blender-Y front/+Zup. Left-quarter review shows the source-visible pod arrangement; exact camera/world/tile calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),Path(__file__).with_name('remaster_achaean_shipyard.py'),Path(__file__).with_name('remaster_achaean_missile_launcher.py'),Path(__file__).with_name('checks_achaean_shipyard.py'),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac16/model.blend'])
if __name__=='__main__':main()
