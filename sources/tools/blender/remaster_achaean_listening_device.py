"""AC15 narrow stepped receiver, parallel ribbed column and connected coral elbow."""
import math,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cut,cleanup,worn_coral_pbr,tube_path
from remaster_achaean_missile_launcher import cylinder,surface_y


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='listening-device'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate receiver belts',(.16,.24,.29),.7,.40);dark=material(folder,'Dark receiver recess',(.015,.020,.025),0,.87);brass=material(folder,'Ochre ribbed column',(.35,.25,.11),.65,.46);amber=material(folder,'Amber source panes',(.70,.27,.04),.12,.30,.25);red=material(folder,'Muted red aerial',(.18,.025,.015),.45,.50)
    dark.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.1;worn_coral_pbr(coral,folder)
    base=lathe('AC15 main ground chamber',(-.15,.10),[(0,.40),(.07,.53),(.45,.64),(.90,.62),(1.20,.49),(1.43,.28),(1.55,.11)],coral)
    foot=lathe('AC15 right ground foot',(.75,-.10),[(0,.24),(.06,.33),(.24,.35),(.40,.30),(.50,.18),(.54,.08)],coral)
    lathe('AC15 lower slate support',(-.15,.10),[(1.35,.14),(2.82,.14)],slate)
    for i,z in enumerate([1.60,1.94,2.28]):lathe('AC15 lower slate collar '+str(i),(-.15,.10),[(z,.14),(z+.025,.18),(z+.12,.18),(z+.145,.14)],slate)
    profile=[(2.70,.20),(2.78,.31),(2.90,.32),(2.96,.39),(3.17,.40),(3.26,.38),(3.40,.40),(4.08,.40),(4.42,.40),(4.46,.36),(4.50,.32),(4.82,.32),(4.88,.26),(4.92,.23),(5.10,.23),(5.16,.14),(5.45,.14),(5.52,.06)]
    lathe('AC15 stepped coral receiver',(-.15,.10),profile,coral)
    lathe('AC15 broad slate receiver belt',(-.15,.10),[(3.43,.402),(4.05,.402)],slate)
    for i,z in enumerate([3.45,3.80]):lathe('AC15 upper slate band '+str(i),(-.15,.10),[(z,.402),(z+.02,.43),(z+.16,.43),(z+.18,.402)],slate)
    lathe('AC15 muted red needle',(-.15,.10),[(5.42,.06),(6.60,.06)],red)
    profile=[(.30,.13)]
    for i in range(9):
        z=.37+i*.205;profile.extend([(z,.13),(z+.025,.15),(z+.11,.15),(z+.135,.13)])
    profile.append((2.30,.13));lathe('AC15 ribbed ochre side column',(.75,.10),profile,brass)
    path=[(-.05,.10,2.85),(.50,.10,2.85)]
    for i in range(1,13):a=math.pi/2*(1-i/12);path.append((.50+.25*math.cos(a),.10,2.60+.25*math.sin(a)))
    path.append((.75,.10,2.20));tube_path('AC15 supported coral return elbow',path,.12,coral)
    cut(base,box('temporary tall amber pocket',(-.15,-.51,.80),(.24,.40,.66),dark,.025),'Actual vertical amber recess')
    box('AC15 amber recess dark back',(-.15,-.32,.80),(.22,.014,.64),dark,.018)
    for i,z in enumerate([.65,.95]):box('AC15 amber source pane '+str(i),(-.15,-.34,z),(.16,.014,.14),amber,.012)
    y=surface_y(foot,.75,.22)
    cut(foot,cylinder('temporary forward foot recess',(.75,y-.015,.22),.145,.24,dark,'Y'),'Actual forward round recess')
    cylinder('AC15 forward dark red field',(.75,y+.09,.22),.143,.018,red,'Y')
    for o in [base,foot]:cleanup(o)
    finish(folder,dict(issue=256,id='openfa:building/legacy/165',key='AC15',name='Listening Device',culture='achaean',footprint=[2,2],definition_class=16,construction_updates=40,triangle_budget=30000,materials=6,structure_checks='checks_achaean_listening_device',state_contract='Static sensor-array equivalent from actual shadow/body and fixed-view catalogue reveal. Narrow stepped coral receiver with broad slate belt,two banded lower supports,connected coral return elbow,parallel ribbed ochre column,two stacked amber source fields and forward dark-red foot field. Muted red needle has no invented blinking or coloured band markings. Hidden rear,fitting purposes and exact dimensions interpreted; no operational motion established. Shared ACS2 construction and client state/mode mapping remain separate.',scale_contract='PlacementRoot at groundZ0; Blender-Y front/+Zup. Authored narrow proportions follow source silhouette; client tile/world and neighbouring-building scale need integration review.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),Path(__file__).with_name('remaster_achaean_shipyard.py'),Path(__file__).with_name('remaster_achaean_missile_launcher.py'),Path(__file__).with_name('checks_achaean_shipyard.py'),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac15/model.blend'])
if __name__=='__main__':main()
