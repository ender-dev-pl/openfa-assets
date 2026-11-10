"""AC22 tall rare-ore tower with source-visible sleeve, reliefs and grounded cluster."""
import sys,math
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import field,patch
PODS=[(-1.0,-.10,.37,.72),(-.35,-.64,.42,.76),(.25,.02,.40,.90),(.45,-.62,.40,.74),(.95,-.22,.35,.70)]

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='deepbore'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate source conduits',(.13,.21,.26),.65,.43);gold=material(folder,'Ochre source sleeve and collars',(.39,.26,.10),.65,.45);dark=material(folder,'Dark source recesses',(.015,.020,.025),0,.83);red=material(folder,'Red source fields',(.22,.008,.003),.1,.45);amber=material(folder,'Pale amber source fields',(.78,.40,.12),.10,.30,.17)
    worn_coral_pbr(coral,folder)
    lower=lathe('AC22 tall grounded lower chamber',(-.60,.25),[(0,.47),(.07,.54),(.30,.59),(.80,.60),(1.30,.60),(1.80,.60),(2.25,.60),(2.48,.55),(2.56,.40)],coral)
    upper=lathe('AC22 compact upper shoulder chamber',(-.60,.25),[(2.36,.43),(2.48,.55),(2.69,.62),(2.94,.60),(3.16,.48),(3.37,.32),(3.52,.18),(3.60,.11)],coral)
    lathe('AC22 narrow coral neck',(-.60,.25),[(3.53,.085),(3.75,.085)],coral)
    lathe('AC22 small coral top cap',(-.60,.25),[(3.67,.08),(3.71,.17),(3.81,.21),(3.94,.18),(4.03,.09)],coral)
    lathe('AC22 tall ochre sleeve',(-.60,.25),[(3.98,.08),(4.04,.095),(4.68,.095),(4.73,.07)],gold)
    lathe('AC22 thin slate upper tip',(-.60,.25),[(4.67,.035),(4.96,.035)],slate)
    outline=[(.16*math.cos(i*math.tau/12),.115*math.sin(i*math.tau/12)) for i in range(12)]
    for i,z in enumerate([1.18,1.61,2.04]):patch('AC22 lower cast relief '+str(i),lower,(-.27,z),outline,coral)
    pods=[]
    for i,(x,y,r,h) in enumerate(PODS):pods.append(lathe('AC22 grounded small chamber '+str(i),(x,y),[(0,r*.72),(.07,r*.90),(h*.35,r),(h*.65,r*.95),(h*.87,r*.64),(h*.97,r*.30),(h,r*.05)],coral))
    for i,(x,y,z0,z1,zc) in enumerate([(-.48,-.34,.42,2.10,1.20),(-.05,.03,.72,2.42,1.55)]):
        lathe('AC22 slate vertical fitting '+str(i),(x,y),[(z0,.070),(z0+.05,.095),(z1-.09,.095),(z1-.03,.075),(z1,.035)],slate)
        lathe('AC22 ochre middle coupling '+str(i),(x,y),[(zc-.09,.09),(zc-.07,.12),(zc+.07,.12),(zc+.09,.09)],gold)
    box('AC22 supported right slate connector',(.62,-.08,.61),(.60,.12,.10),slate,.025)
    for i,(x,z) in enumerate([(x,z) for x in [-.83,-.71] for z in [2.86,3.14]]):field(upper,'AC22 upper amber segment '+str(i),x,z,.055,.095,amber,dark)
    for i,x in enumerate([-.83,-.71]):field(upper,'AC22 upper red middle band '+str(i),x,3.00,.055,.075,red,dark)
    slots=[(lower,'main',-.93,.98,.16),(pods[1],'front left',-.35,.16,.14),(pods[3],'front right',.45,.14,.14),(pods[4],'outer right',.95,.14,.14)]
    for body,label,x,z,w in slots:
        field(body,'AC22 red slit back '+label,x,z,w,.085,red,dark);pane=bpy.data.objects['AC22 red slit back '+label];o=box('AC22 amber slit '+label,pane.location,(w*.43,.015,.028),amber,.004);o.rotation_mode='QUATERNION';o.rotation_quaternion=pane.rotation_quaternion;o.location+=pane.rotation_quaternion@Vector((0,-.012,0))
    for o in [lower,upper,*pods]:cleanup(o)
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','remaster_achaean_manoeuvring_device.py','remaster_achaean_missile_launcher.py','checks_achaean_shipyard.py']
    finish(folder,dict(issue=256,id='openfa:building/legacy/172',key='AC22',name='Deepbore',culture='achaean',footprint=[3,3],definition_class=21,construction_updates=42,triangle_budget=30000,materials=6,structure_checks='checks_achaean_deepbore',state_contract='Static source-led rare-ore facility:tall closed coral tower/shoulder,three rounded cast reliefs,short neck/cap,long ochre sleeve/slate tip,five grounded clustered lobes,two supported slate fittings/ochre collars,warm upper segments/red middle band and four lower red/amber slits. All41 catalogue phases are fixed-view reveal/highlight,no operating motion evidenced. Surface descriptor0 is used as shadow-mask pass despite containing coloured artwork;descriptor1 is visible body. Do not infer an inactive-blue material state from descriptor0. Shared ACS3 and client rare-ore extraction/activity/damage mapping separate;hidden depth/engineering interpreted.',scale_contract='PlacementRoot identity groundZ0;Blender-Yfront/+Zup;3x3footprint. Tall relative proportions retained;exact tile/world/camera calibration and Android frame time separate.'),__file__,[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac22/model.blend'])
if __name__=='__main__':main()
