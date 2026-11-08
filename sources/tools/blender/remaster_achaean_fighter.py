"""AC1C Dedicated Fighter, issue236; independent proportions and forward crescents."""
from pathlib import Path
import hashlib
import json
import math
import sys
import bpy
from mathutils import Vector

sys.path.insert(0,str(Path(__file__).parent))
import remaster_achaean_transporter as shared

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'sources/objects/achaean/dedicated-fighter'
MEDIA=ROOT/'gallery/media/objects/achaean/dedicated-fighter'
ID='openfa:ship/achaean/dedicated-fighter'
PROFILE=[(-2.65,.024,.024),(-2.20,.05,.045),(-1.65,.11,.11),(-1.10,.32,.27),
         (-.50,.48,.38),(.10,.52,.40),(.60,.42,.33),(.95,.24,.20),(1.18,.09,.07)]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def hull(y,a,offset=0):
    w,h=shared.section(y);c,s=math.cos(a),math.sin(a)
    point=Vector((w*c,y,h*s))
    return point+Vector((c/w,0,s/h)).normalized()*offset


def crescent(side,t,v,depth=0):
    a=abs(t);s=math.sin(t*math.pi/2);taper=1-a**2.5
    return Vector((side*(.95+.04*a+.018*math.sin(math.pi*v)*taper+depth),
                   .55-3.05*a**1.65+(v-.5)*.58*taper,
                   .94*s*(1-.48*a*a)+(v-.5)*.22*s*taper))


def body():
    ys=sorted(set([PROFILE[0][0]+(PROFILE[-1][0]-PROFILE[0][0])*i/72 for i in range(73)]+[r[0] for r in PROFILE]))
    vs=[tuple(hull(y,math.tau*i/48)) for y in ys for i in range(48)]
    fs=[tuple(range(47,-1,-1)),tuple((len(ys)-1)*48+i for i in range(48))]
    fs.extend((j*48+i,j*48+(i+1)%48,(j+1)*48+(i+1)%48,(j+1)*48+i) for j in range(len(ys)-1) for i in range(48))
    shared.emit('PressureHull',vs,fs,0)
    for j,(lo,hi) in enumerate([(-1.59,-.98),(-.95,-.20),(-.17,.50),(.53,.98)]):
        for side in [-1,1]:
            a=math.pi/2+side*.50
            shared.hull_panel('FormedHullSkins',lo,hi,a-.43,a+.43,7 if j%2 else 12,.012,9,8)
        shared.hull_panel('BellyCargoHatches',lo,hi,math.pi*1.12,math.pi*1.88,6,.010,8,10)
    shared.rod('ForeTerminal',(0,-2.78,0),(0,-2.60,0),.017,0,20)
    for y in [-2.17,-1.94]:
        shared.hull_panel('FormedHullSkins',y,y+.06,.1,math.pi-.1,5,.006,3,12)
    shared.rod('AftTerminal',(0,1.12,0),(0,1.46,0),.068,5,28)
    shared.rod('AftTerminal',(0,1.44,0),(0,1.53,0),.046,5,24)
    for side in [-1,1]:
        a=.18 if side==1 else math.pi-.18;p,rot,n=shared.frame(-.35,a,.012)
        shared.box('ServiceEquipment',p,(.13,.35,.045),3,.008,rot)
        for j in range(5):
            shared.box('ServiceEquipment',p+rot@Vector((0,-.13+j*.065,.028)),(.115,.018,.018),9,.004,rot)
    for y in [-.80,.25]:
        p,rot,n=shared.frame(y,math.pi/2,.018)
        shared.box('ServiceEquipment',p,(.15,.20,.025),12,.009,rot)
        for x in [-.048,.048]:
            q=p+rot@Vector((x,0,.017));shared.rod('Fasteners',q,q+n*.008,.009,11,8)


def wings():
    for side in [-1,1]:
        shared.crescent_patch('CrescentStructure',side,-.998,.998,0,1,9,0,88,8)
        for lo,hi in [(-.995,-.70),(-.697,-.40),(-.397,-.12),(-.117,.117),(.12,.397),(.40,.697),(.70,.995)]:
            shared.crescent_patch('CrimsonCrescentInsets',side,lo,hi,.12,.70,1,.010,14,5)
            shared.crescent_patch('SilverCrescentRims',side,lo,hi,.72,.985,2,.014,14,4)
            shared.crescent_patch('SilverCrescentRims',side,lo,hi,.015,.09,2,.014,14,3)
        shared.rod('TransverseStructure',(side*.35,.55,0),(side*1.03,.55,0),.100,0,24)
        shared.rod('TransverseStructure',(side*.70,.55,0),(side*.83,.55,0),.145,9,28)
        x=side*1.03
        shared.x_ring('RootServiceCollars',x,.55,0,[(side*-.04,.27),(side*.04,.29),(side*.08,.26),(side*.08,.21),(side*-.04,.21)],2)
        shared.rod('RootServiceCollars',(x,.55,0),(x+side*.09,.55,0),.207,1,40)
        for j in range(8):
            a=math.tau*j/8;y=.55+.242*math.cos(a);z=.242*math.sin(a)
            shared.rod('Fasteners',(x+side*.08,y,z),(x+side*.095,y,z),.011,11,8)
        for t in [-.40,.40]:
            skin=.075*(1-t*t)+.015+.012;p=crescent(side,t,.45,skin)
            rot=Vector((side,0,0)).to_track_quat('Z','Y').to_matrix()
            shared.box('ServiceEquipment',p,(.08,.19,.022),9,.006,rot)
            shared.box('ServiceEquipment',p+Vector((side*.014,0,0)),(.035,.13,.008),3,.002,rot)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.preferences.filepaths.save_version=0
    shared.GROUPS.clear();shared.PROFILE=PROFILE;shared.hull=hull;shared.crescent_point=crescent;shared.ID=ID
    root=bpy.data.objects.new('PlacementRoot',None);bpy.context.collection.objects.link(root)
    root['catalogue_id']=ID;root['forward_axis']='-Y';root['up_axis']='Z'
    root['equipment_slots']=4;root['calibrated_weapon_sockets']=0;root['proposed_world_size']=96
    root['interpretation']='AC1C forward-facing open crescents; hidden fittings authored; no recovered sockets'
    body();wings();objects=shared.finalize(shared.material(),root)
    points=[Vector(p) for o in objects for p in o.bound_box]
    low=Vector(tuple(min(p[a] for p in points) for a in range(3)));high=Vector(tuple(max(p[a] for p in points) for a in range(3)))
    centre=(low+high)/2;factor=18/max(high-low)
    for obj in objects:
        for v in obj.data.vertices:v.co=(v.co-centre)*factor
        obj.data.update()
    helper=bpy.data.objects.new('AlignmentForward',None);bpy.context.collection.objects.link(helper);helper.parent=root
    helper.location=(Vector((0,-2.85,0))-centre)*factor;helper['status']='uncalibrated alignment; not an equipment socket'
    triangles=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects);assert triangles<60000 and len(objects)<=16
    OUT.mkdir(parents=True,exist_ok=True);MEDIA.mkdir(parents=True,exist_ok=True)
    scene=shared.studio();shared.aim(scene,(1,-1,.55),margin=1.20)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects+[root,helper]:obj.select_set(True)
    bpy.context.view_layer.objects.active=root
    bpy.ops.export_scene.gltf(filepath=str(OUT/'model.glb'),export_format='GLB',use_selection=True,export_animations=False,export_extras=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'model.blend'),compress=True,relative_remap=True)
    for name,direction in [('front-quarter',(1,-1,.55)),('rear-quarter',(1,1,.40)),('front',(0,-1,.14)),('side',(1,0,.14)),('top',(0,.001,1)),('underside',(1,-1,-.7))]:
        shared.aim(scene,direction,margin=1.20)
        if name=='underside':
            for lamp in [o for o in scene.objects if o.type=='LIGHT']:
                lamp.location.z=-lamp.location.z;lamp.rotation_euler=(-lamp.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    report=dict(id=ID,issue=236,triangles=triangles,mesh_batches=len(objects),materials=1,packed_maps=2,
        native_dimensions=list((high-low)*factor),normalization_factor=factor,normalization_centre=list(centre),
        blend_sha256=sha(OUT/'model.blend'),glb_sha256=sha(OUT/'model.glb'),generator_sha256=sha(Path(__file__)),
        shared_authoring_helper_sha256=sha(Path(shared.__file__)),shared_material_maps='sources/materials/achaean/dedicated-ore-transporter',
        proposed_world_size=96,current_client_fallback_size=96,scale_status='authored size assumption, not recovered metres',calibrated_sockets=0)
    (OUT/'generation.json').write_text(json.dumps(report,indent=2)+'\n');print('FIGHTER_GENERATED',json.dumps(report))


if __name__=='__main__':main()
