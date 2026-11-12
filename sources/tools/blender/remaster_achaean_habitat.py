"""AC06 low inhabited surface crown: lobed roof, paired windows and four real ports."""
import math,sys
from pathlib import Path
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
ROOF=[(.48,.76),(.68,.98),(.90,1.0),(1.12,.92),(1.34,.72),(1.54,.43),(1.61,.27)]
PORT_RADIUS=.26
PORT_Z=1.59+(.39-PORT_RADIUS)/(.39-.18)*.10

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
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='habitat'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),.35,.5);amber=material(folder,'Warm habitat windows',(.85,.42,.055),.2,.30,.7)
    drum=lathe('AC06 inhabited lower drum',(0,0),[(0,.58),(.04,.65),(.12,.64),(.46,.64),(.52,.62)],coral)
    roof=lathe('AC06 broad lobed roof',(0,0),ROOF,coral,.05)
    roof_panel('AC06 upper flowing casting',[(1.061,-1.4,.04),(1.152,-1.5,.60),(1.226,-1.8,.60),(1.287,-2.1,.03)],coral)
    roof_panel('AC06 lower flowing casting',[(.50,-1.3,.04),(.64,-1.7,.65),(.793,-1.7,.80),(.874,-1.3,.40),(.915,-1.0,.03)],coral)
    roof_panel('AC06 right flowing casting',[(.56,-.30,.04),(.793,-.28,.30),(1.017,-.40,.35),(1.274,-.55,.25),(1.487,-.70,.04)],coral)
    cap=lathe('AC06 blue roof cap',(0,0),[(1.55,.30),(1.59,.39),(1.69,.18),(1.77,.065),(1.81,.025)],slate)
    # Ten window banks give roughly five paired banks on the visible half.
    # Their rear distribution is an authored continuation, not a recovered view.
    for i in range(10):
        a=2*math.pi*i/10
        cutter=radial(box('AC06 temporary window cutter', (0,0,0),(.10,.10,.26),dark,.008),a,.61,.24);cut(drum,cutter,'Recessed window '+str(i))
        radial(frame('AC06 window rim '+str(i),.14,.30,.02,.09,coral),a,.63,.24)
        radial(box('AC06 window back '+str(i),(0,0,0),(.095,.012,.25),dark,.003),a,.565,.24)
        for j,z in enumerate([.165,.295]):radial(box('AC06 warm pane '+str(i)+' '+str(j),(0,0,0),(.105,.014,.065),amber,.006),a,.655,z)
        for z in [.12,.36]:
            for side in [-1,1]:
                p=Vector((.676*math.cos(a),.676*math.sin(a),z))+Vector((-math.sin(a),math.cos(a),0))*side*.058;bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.009,location=p);o=bpy.context.object;o.name='AC06 fixture bolt';o.data.materials.append(slate)
    lathe('AC06 lower drum seam',(0,0),[(.035,.652),(.048,.652)],slate)
    for i in range(4):
        a=math.pi/4+i*math.pi/2;normal=Vector((math.cos(a),math.sin(a),2.1)).normalized();p=Vector((PORT_RADIUS*math.cos(a),PORT_RADIUS*math.sin(a),PORT_Z))
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.042,depth=.08,location=p-normal*.015);cutter=bpy.context.object;cutter.rotation_euler=normal.to_track_quat('Z','Y').to_euler();cut(cap,cutter,'Actual top opening '+str(i))
        bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=.045,depth=.008,location=p-normal*.022);o=bpy.context.object;o.name='AC06 port dark floor '+str(i);o.rotation_euler=normal.to_track_quat('Z','Y').to_euler();o.data.materials.append(dark)
        bpy.ops.mesh.primitive_torus_add(major_radius=.044,minor_radius=.007,major_segments=32,minor_segments=8,location=p+normal*.002);o=bpy.context.object;o.name='AC06 fixture port lip';o.rotation_euler=normal.to_track_quat('Z','Y').to_euler();o.data.materials.append(slate)
    # Remove sub-micron Boolean slivers without changing the cap silhouette.
    before=[v.co.copy() for v in cap.data.vertices];original=BVHTree.FromPolygons(before,[tuple(f.vertices) for f in cap.data.polygons])
    bm=bmesh.new();bm.from_mesh(cap.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6);bmesh.ops.dissolve_degenerate(bm,edges=list(bm.edges),dist=1e-6);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;bm.to_mesh(cap.data);bm.free()
    after=[v.co.copy() for v in cap.data.vertices];cleaned=BVHTree.FromPolygons(after,[tuple(f.vertices) for f in cap.data.polygons]);error=max(max(cleaned.find_nearest(p)[3] for p in before),max(original.find_nearest(p)[3] for p in after));assert error<2e-6;print('AC06_CAP_CLEANUP_ERROR',error,flush=True)
    # Disjoint closed castings can be batched without coincident frame corners.
    merge('AC06 window rim ','AC06 consolidated window rims');merge('AC06 window back ','AC06 consolidated window backs');merge('AC06 warm pane ','AC06 twenty warm panes');merge('AC06 fixture','AC06 consolidated blue fixtures')
    finish(folder,dict(issue=256,id='openfa:building/legacy/156',key='AC06',name='Habitat',culture='achaean',footprint=[2,2],definition_class=0,construction_updates=56,triangle_budget=30000,materials=4,structure_checks='checks_achaean_habitat',state_contract='Static low surface habitat crown; most rooms/tunnels are underground in legacy lore and are not externally invented. Catalogue reveal/highlight does not establish mechanical operation. Warm windows have low constant emission; activity/construction/damage mapping remains client integration.',scale_contract='PlacementRoot at ground Z=0, local -Y front/+Z up. Client tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
