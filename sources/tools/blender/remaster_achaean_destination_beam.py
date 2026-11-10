"""Legacy-led AC17 rounded casing, stepped flank plate and supported front fittings."""
import sys,math
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import patch,field

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='destination-beam'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51)
    slate=material(folder,'Slate source fittings',(.13,.21,.26),.63,.43)
    dark=material(folder,'Dark recessed fields',(.015,.021,.024),0,.83)
    brass=material(folder,'Ochre source fittings',(.39,.26,.10),.65,.45)
    red=material(folder,'Red lower inset',(.23,.012,.008),.2,.35)
    blue=material(folder,'Pale blue source fields',(.26,.43,.53),.12,.30,.10)
    worn_coral_pbr(coral,folder)
    body=lathe('AC17 main rounded casing',(0,0),[(0,.55),(.05,.66),(.18,.74),(.40,.84),(.70,.91),(1.00,.94),(1.30,.93),(1.60,.88),(1.85,.79),(2.04,.67),(2.22,.49),(2.40,.36),(2.58,.25),(2.73,.19),(2.78,.17)],coral)
    lathe('AC17 short stepped ochre tip',(0,0),[(2.72,.15),(2.80,.15),(2.83,.10),(3.00,.10),(3.02,.065),(3.24,.065)],brass)
    # A raised circular source field is part of the casting, not an invented glass dome.
    circle=[(.46*math.cos(a*math.tau/16),.46*math.sin(a*math.tau/16)) for a in range(16)]
    patch('AC17 broad circular coral field',body,(.24,1.57),circle,coral)
    flank=[(-.22,-.58),(-.27,-.22),(-.24,.19),(-.18,.49),(-.04,.60),(.13,.54),(.20,.36),(.32,.31),(.32,.21),(.12,.19),(.10,-.10),(.02,-.20),(.04,-.45)]
    patch('AC17 left stepped slate plate',body,(-.52,1.35),flank,slate)
    field(body,'AC17 pale blue circular instrument',-.29,1.03,.15,.15,blue,dark)
    for i,x in enumerate([.16,.36]):field(body,'AC17 paired lower dark slot '+str(i),x,1.04,.085,.18,dark,dark)
    field(body,'AC17 upper dark aperture',0,2.50,.10,.13,dark,dark)
    # Ground fittings match the actual visible front cluster; rear is deliberately plain.
    for i,x in enumerate([-.64,.64]):
        pod=lathe('AC17 grounded coral side foot '+str(i),(x,-.54),[(0,.16),(.04,.19),(.36,.18),(.43,.15)],coral)
        lathe('AC17 slate side cap '+str(i),(x,-.54),[(.39,.16),(.46,.16),(.55,.09),(.60,.055)],slate)
        for j,dx in enumerate([-.065,.065]):field(pod,'AC17 side blue inset '+str(i)+' '+str(j),x+dx,.24,.045,.13,blue,dark)
        cleanup(pod)
    gold=lathe('AC17 ochre ground axial fitting',(0,-.95),[(0,.16),(.04,.23),(.12,.25),(.49,.25),(.56,.20)],brass)
    field(gold,'AC17 red axial inset',0,.28,.16,.16,red,dark)
    lathe('AC17 grounded axial shoe',(0,-1.16),[(0,.11),(.08,.14),(.15,.13)],brass)
    lathe('AC17 tall slate front fitting',(0,-.92),[(.48,.19),(.55,.20),(.69,.15),(.94,.10),(1.17,.045),(1.20,.04)],slate)
    cleanup(body);cleanup(gold)
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','remaster_achaean_manoeuvring_device.py','remaster_achaean_missile_launcher.py','checks_achaean_shipyard.py']
    finish(folder,dict(issue=256,id='openfa:building/legacy/167',key='AC17',name='Destination Beam',culture='achaean',footprint=[2,2],definition_class=255,construction_updates=100,triangle_budget=30000,materials=6,structure_checks='checks_achaean_destination_beam',state_contract='Static source-led warp building from actual shadow/body and all41 fixed-view catalogue phases. Main round cast field,left stepped slate plate,two lower dark slots,small pale blue field,upper dark aperture,short ochre tip and supported ground fittings. Catalogue reveal/highlight does not establish mechanical operation. No beam or jump animation inferred; shared ACS2 construction and client warp/power/state mapping separate. Hidden rear and exact fitting function interpreted.',scale_contract='Identity PlacementRoot at groundZ0; Blender-Y front/+Zup. Two-by-two placement; exact client tile/world and source camera calibration separate.'),__file__,[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac17/model.blend'])
if __name__=='__main__':main()


