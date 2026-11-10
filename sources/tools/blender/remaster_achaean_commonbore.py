"""AC21 clustered cast chambers with actual source-visible staggered lower lobes."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import field
PODS=[(-1.0,-.10,.40,.78),(-.35,-.64,.42,.76),(.35,.04,.40,.90),(.45,-.62,.40,.74),(1.0,-.22,.35,.70)]

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='commonbore'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate source conduits',(.13,.21,.26),.65,.43);gold=material(folder,'Ochre source couplings',(.39,.26,.10),.65,.45);dark=material(folder,'Dark source recesses',(.015,.020,.025),0,.83);red=material(folder,'Red slit backs',(.22,.008,.003),.1,.45);amber=material(folder,'Pale amber source fields',(.78,.40,.12),.10,.30,.17)
    worn_coral_pbr(coral,folder)
    lower=lathe('AC21 grounded broad lower chamber',(-.55,.28),[(0,.46),(.07,.57),(.25,.64),(.55,.68),(.92,.72),(1.20,.74),(1.43,.65),(1.62,.48),(1.70,.36)],coral)
    upper=lathe('AC21 upper onion chamber',(-.55,.28),[(1.48,.42),(1.57,.56),(1.78,.65),(2.03,.63),(2.26,.53),(2.49,.38),(2.66,.23),(2.78,.13),(2.82,.09)],coral)
    lathe('AC21 slate tip socket',(-.55,.28),[(2.75,.10),(2.85,.12),(2.91,.09)],slate)
    lathe('AC21 short ochre tip',(-.55,.28),[(2.86,.065),(3.05,.065),(3.10,.035)],gold)
    pods=[]
    for i,(x,y,r,h) in enumerate(PODS):pods.append(lathe('AC21 grounded small chamber '+str(i),(x,y),[(0,r*.72),(.07,r*.90),(h*.35,r),(h*.65,r*.95),(h*.87,r*.64),(h*.97,r*.30),(h,r*.05)],coral))
    for i,(x,y,z0,z1,zc) in enumerate([(-.48,-.44,.42,1.93,1.08),(.15,.04,.72,2.22,1.40)]):
        lathe('AC21 slate vertical fitting '+str(i),(x,y),[(z0,.070),(z0+.05,.095),(z1-.09,.095),(z1-.03,.075),(z1,.035)],slate)
        lathe('AC21 ochre middle coupling '+str(i),(x,y),[(zc-.09,.09),(zc-.07,.12),(zc+.07,.12),(zc+.09,.09)],gold)
    box('AC21 supported right slate connector',(.67,-.08,.61),(.60,.12,.10),slate,.025)
    for i,(x,z) in enumerate([(-.55,2.47),(-.62,2.33),(-.48,2.33),(-.55,2.19)]):field(upper,'AC21 upper amber field '+str(i),x,z,.050,.075,amber,dark)
    slots=[(lower,'main',-.84,.98,.16),(pods[1],'front left',-.35,.16,.14),(pods[3],'front right',.45,.14,.14)]
    for body,label,x,z,w in slots:
        field(body,'AC21 red slit back '+label,x,z,w,.085,red,dark);pane=bpy.data.objects['AC21 red slit back '+label];o=box('AC21 amber slit '+label,pane.location,(w*.43,.015,.028),amber,.004);o.rotation_mode='QUATERNION';o.rotation_quaternion=pane.rotation_quaternion;o.location+=pane.rotation_quaternion@Vector((0,-.012,0))
    for o in [lower,upper,*pods]:cleanup(o)
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','remaster_achaean_manoeuvring_device.py','remaster_achaean_missile_launcher.py','checks_achaean_shipyard.py']
    finish(folder,dict(issue=256,id='openfa:building/legacy/171',key='AC21',name='Commonbore',culture='achaean',footprint=[3,3],definition_class=8,construction_updates=44,triangle_budget=30000,materials=6,structure_checks='checks_achaean_commonbore',state_contract='Static legacy-led common-ore facility:two joined large chambers,five source-visible staggered ground lobes,two attached slate fittings/ochre couplings,four upper amber fields and three red/amber lower slits. All41 catalogue frames are fixed-view reveal/highlight,not evidence of pump/drill motion. No invented bore mechanism or foundation slab. Shared ACS3 construction and client extraction/activity/damage mapping separate. Hidden depth and exact internal engineering interpreted.',scale_contract='PlacementRoot identity groundZ0;Blender-Yfront/+Zup;3x3footprint. Staggered asymmetry retained;exact tile/world/camera calibration and Android frame time separate.'),__file__,[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac21/model.blend'])
if __name__=='__main__':main()


