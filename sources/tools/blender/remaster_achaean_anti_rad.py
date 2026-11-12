"""Legacy-led AC02 radiation screen with exposed supported conductor bank."""
import math,sys
from pathlib import Path
import bpy,bmesh
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish

def brass_patch(dome,mat):
    # Continuous curved outline on the roof profile, not a raster stair-step.
    profile=[(.98,.86),(1.04,.89),(1.18,.87),(1.36,.77),(1.53,.59),(1.66,.39),(1.74,.24),(1.79,.10)]
    outline=[(1.065,-1.0,.26),(1.14,-.93,.50),(1.28,-1.04,.73),(1.42,-.98,.78),(1.55,-1.04,.76),(1.66,-1.14,.59),(1.74,-1.1,.27),(1.765,-1.05,.06)]
    def interpolate(table,z,col):
        for a,b in zip(table,table[1:]):
            if a[0]<=z<=b[0]:return a[col]+(b[col]-a[col])*(z-a[0])/(b[0]-a[0])
        return table[-1][col]
    rows=33;columns=21;verts=[]
    for offset in [.018,-.006]:
        for j in range(rows):
            z=outline[0][0]+(outline[-1][0]-outline[0][0])*j/(rows-1);centre=interpolate(outline,z,1);half=interpolate(outline,z,2);r=interpolate(profile,z,1)+offset
            for i in range(columns):
                theta=centre+half*(2*i/(columns-1)-1);verts.append((r*math.cos(theta),.16+r*math.sin(theta),z))
    n=rows*columns;faces=[]
    for j in range(rows-1):
        for i in range(columns-1):
            a=j*columns+i;face=(a,a+1,a+1+columns,a+columns);faces.append(face);faces.append(tuple(v+n for v in reversed(face)))
    border=[*range(columns),*[j*columns+columns-1 for j in range(1,rows)],*[(rows-1)*columns+i for i in reversed(range(columns-1))],*[j*columns for j in reversed(range(1,rows-1))]]
    for a,b in zip(border,border[1:]+border[:1]):faces.append((b,a,a+n,b+n))
    mesh=bpy.data.meshes.new('Conformal uneven brass roof facing');mesh.from_pydata(verts,[],faces);mesh.update();bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free();o=bpy.data.objects.new(mesh.name,mesh);bpy.context.collection.objects.link(o);mesh.materials.append(mat);uv=mesh.uv_layers.new()
    for face in mesh.polygons:
        face.use_smooth=True
        for li in face.loop_indices:
            index=mesh.loops[li].vertex_index%n;uv.data[li].uv=((index%columns)/(columns-1),(index//columns)/(rows-1))
    return o

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    folder='anti-rad-screen';coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);gold=material(folder,'Aged brass',(.49,.34,.13),.72,.42);slate=material(folder,'Blue gray fittings',(.16,.24,.29),.7,.38);dark=material(folder,'Dark recess',(.016,.021,.026),.35,.5);red=material(folder,'Red status lens',(.26,.025,.012),.45,.28,.2)
    # Broad suspended roof, shallow arch cavity and two grounded side pods.
    profile=[(.98,.86),(1.04,.89),(1.18,.87),(1.36,.77),(1.53,.59),(1.66,.39),(1.74,.24),(1.79,.10)]
    dome=lathe('AC02 main arch dome',(0,.16),profile,coral);brass_patch(dome,gold)
    for sign in [-1,1]:
        c=(sign*.81,-.03)
        lathe('AC02 side pod '+str(sign),c,[(0,.23),(.05,.28),(.16,.29),(.95,.29),(1.02,.26)],coral)
        lathe('AC02 gold pod cap '+str(sign),c,[(1.01,.265),(1.05,.29),(1.12,.26),(1.21,.18),(1.28,.07),(1.30,.025)],gold,.035)
        lathe('AC02 cap finial '+str(sign),c,[(1.28,.026),(1.34,.026),(1.36,.009)],gold)
        lathe('AC02 pod lower collar '+str(sign),c,[(.08,.291),(.11,.291)],gold)
        box('AC02 service panel surround '+str(sign),(c[0],c[1]-.285,.48),(.22,.04,.58),slate,.025)
        box('AC02 service panel well '+str(sign),(c[0],c[1]-.309,.48),(.16,.018,.50),dark,.014)
        for j in range(4):box('AC02 service louvre '+str(sign)+' '+str(j),(c[0],c[1]-.325,.31+j*.11),(.13,.025,.035),slate,.007)
    lathe('AC02 antenna',(0,.16),[(1.74,.12),(1.82,.12),(1.84,.095),(2.18,.095),(2.22,.075),(2.24,.075),(2.26,.045),(2.55,.045),(2.58,.02)],slate)
    lathe('AC02 antenna seat',(0,.16),[(1.72,.145),(1.79,.145)],gold)
    # Six independent bars are attached to the roof by clamps and to a back
    # cross member. The bay below the roof stays open, as in the original.
    box('AC02 upper conductor support',(0,-.29,1.025),(1.02,.16,.12),slate)
    box('AC02 rear conductor cross member',(0,.14,.52),(1.5,.12,.11),slate)
    for i in range(6):
        x=(i-2.5)*.135;bottom=[.13,.035,.10,.045,.12,.19][i]
        box('AC02 exposed conductor '+str(i),(x,-.33,(1.04+bottom)/2),(.085,.095,1.04-bottom),slate,.014)
        box('AC02 conductor clamp '+str(i),(x,-.305,1.015),(.11,.15,.08),gold,.009)
        # Supported rear feed goes from the back cross member into the bar.
        box('AC02 conductor feed '+str(i),(x,-.055,.52),(.045,.44,.045),gold,.007)
    # A small round front port follows the arch brow, without a large turret.
    for name,radius,mat,y in [('port collar',.09,gold,-.735),('port well',.065,dark,-.759),('port lens',.04,red,-.774)]:
        o=lathe('AC02 '+name,(0,0),[(0,radius),(.02,radius)],mat);o.rotation_euler[0]=math.pi/2;o.location=(0,y,1.16)
    # Sparse service seams and readable fasteners; no arbitrary hull grid.
    for z,r in [(1.04,.895),(1.68,.355)]:lathe('AC02 dome seam '+str(z),(0,.16),[(z-.008,r),(z+.008,r)],dark)
    for sign in [-1,1]:
        for z in [.20,.78]:
            for dx in [-.095,.095]:
                bpy.ops.mesh.primitive_cylinder_add(vertices=8,radius=.012,depth=.012,location=(sign*.81+dx,-.337,z),rotation=(math.pi/2,0,0));o=bpy.context.object;o.name='AC02 service fastener';o.data.materials.append(gold)
        for j in range(10):
            a=j*math.pi/5
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8,ring_count=4,radius=.012,location=(sign*.81+.294*math.cos(a),-.03+.294*math.sin(a),.105));o=bpy.context.object;o.name='AC02 collar fastener';o.data.materials.append(slate)
    for mat in [coral,gold,slate,dark,red]:
        group=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.data.materials[0]==mat and any(t in o.name for t in ['louvre','fastener','conductor clamp','conductor feed'])]
        if group:
            bpy.ops.object.select_all(action='DESELECT')
            for o in group:o.select_set(True)
            bpy.context.view_layer.objects.active=group[0];bpy.ops.object.join();bpy.context.object.name='AC02 consolidated '+mat.name+' fixtures'
    finish(folder,dict(issue=256,id='openfa:building/legacy/152',key='AC02',name='Anti-Rad Screen',culture='achaean',footprint=[2,2],definition_class=5,construction_updates=32,triangle_budget=30000,materials=5,structure_checks='checks_achaean_anti_rad',state_contract='Static radiation-control facility. Actual AC02 catalogue reveal/highlight does not establish a mechanical operating cycle; construction/damage and shader activity require client integration.',scale_contract='PlacementRoot at ground Z=0, local -Y front and +Z up; tile/world calibration remains separate.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),ROOT/'tools/publication_support.py'])
if __name__=='__main__':main()
