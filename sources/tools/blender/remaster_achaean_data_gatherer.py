"""AC14 source-led satellite silo with a tall ochre mast and open rear well."""
import math,sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cut,cleanup,worn_coral_pbr
from remaster_achaean_missile_launcher import cylinder,surface_y
PORTS=[(-.18,.80),(.18,.80),(-.31,.55),(0,.55),(.31,.55),(-.18,.30),(.18,.30)]


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='data-gatherer'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate mast fittings',(.16,.24,.29),.7,.40);dark=material(folder,'Dark recessed fields',(.015,.020,.025),0,.87);brass=material(folder,'Ochre mast',(.35,.25,.11),.65,.46);amber=material(folder,'Amber source window',(.70,.27,.04),.12,.30,.25)
    dark.node_tree.nodes['Principled BSDF'].inputs['Specular IOR Level'].default_value=.1;worn_coral_pbr(coral,folder)
    left=lathe('AC14 left rear mast chamber',(-.65,.40),[(0,.48),(.07,.63),(.46,.70),(.83,.63),(1.15,.45),(1.36,.22),(1.43,.10)],coral)
    fore=lathe('AC14 left foreground chamber',(-.65,-.65),[(0,.44),(.06,.58),(.25,.62),(.48,.54),(.67,.35),(.76,.08)],coral)
    rear=lathe('AC14 open rear launch chamber',(.65,.40),[(0,.50),(.08,.64),(.50,.70),(.93,.65),(1.20,.51),(1.38,.35),(1.47,.33),(1.56,.33)],coral)
    right=lathe('AC14 right foreground field chamber',(.65,-.65),[(0,.53),(.07,.69),(.36,.74),(.71,.68),(.97,.50),(1.16,.25),(1.22,.08)],coral)
    for i,(dx,z) in enumerate(PORTS):
        x=.65+dx;y=surface_y(right,x,z)
        cut(right,cylinder('temporary dark front bore',(x,y-.025,z),.075,.27,dark,'Y'),'Actual front field '+str(i))
        cylinder('AC14 dark field floor '+str(i),(x,y+.095,z),.073,.018,dark,'Y')
    # Preserve a permanently exposed emitter, widening the old .17 radius to .28
    # because the actual AC14 raster shows a broader mouth than AC13.
    cut(rear,cylinder('temporary permanent vertical bore',(.65,.40,.95),.28,1.8,dark),'Permanently exposed satellite well')
    cylinder('AC14 recessed launch well floor',(.65,.40,.052),.279,.008,dark)
    profile=[(1.20,.14),(1.43,.14)]
    for i in range(6):
        z=1.45+i*.19;profile.extend([(z,.14),(z+.025,.16),(z+.07,.16),(z+.095,.14)])
    profile.append((2.68,.14));lathe('AC14 ochre lower mast',(-.65,.40),profile,brass)
    lathe('AC14 slate mast collar',(-.65,.40),[(2.62,.16),(2.67,.23),(2.78,.23),(2.81,.20),(2.84,.23),(2.95,.23),(3.01,.16),(3.05,.16)],slate)
    lathe('AC14 ochre upper mast',(-.65,.40),[(2.98,.075),(4.55,.075)],brass)
    lathe('AC14 short ochre fore fitting',(-.65,-.44),[(.57,.07),(1.23,.07),(1.27,.04)],brass)
    box('AC14 connected interstitial casting',(0,-.22,.49),(.90,.44,.50),coral,.06)
    lathe('AC14 short slate pedestal',(0,-.22),[(.33,.14),(.90,.14),(1.00,.10)],coral)
    lathe('AC14 short slate bulb',(0,-.22),[(.92,.12),(.98,.20),(1.12,.22),(1.24,.14),(1.29,.08)],slate)
    lathe('AC14 short slate post',(0,-.22),[(1.22,.065),(1.80,.065)],slate)
    lathe('AC14 short right probe',(.65,-.48),[(1.04,.035),(1.45,.035)],slate)
    y=surface_y(fore,-.65,.20)
    cut(fore,box('temporary amber recess',(-.65,y-.02,.20),(.27,.20,.16),dark,.014),'Single source amber field')
    box('AC14 low amber window',(-.65,y+.065,.20),(.25,.014,.14),amber,.012)
    for o in [left,fore,rear,right]:cleanup(o)
    finish(folder,dict(issue=256,id='openfa:building/legacy/164',key='AC14',name='Data Gatherer',culture='achaean',footprint=[3,3],definition_class=9,construction_updates=28,triangle_budget=30000,materials=5,structure_checks='checks_achaean_data_gatherer',state_contract='Static exposed satellite silo from actual two-layer surface/fixed-view catalogue. Four connected coral lobes resolve the source foreground/rear shoulders; tall ochre mast with slate collar,short blue-gray fitting,seven dark right fields and one amber front window. Preserves useful prior permanent open-emitter treatment and .05 floor datum; mouth widened from prior .17 to .28 radius to follow the broader AC14 source. No lid cycle inferred. Hidden rear,dark-field purpose,exact dimensions and tiny fitting interpretation remain separate. Shared ACS3 construction and client satellite/state/mode mapping remain separate.',scale_contract='PlacementRoot at groundZ0; Blender-Y front/+Zup. Client tile scale,satellite fit and authored well dimensions need integration review.'),__file__,[Path(__file__).with_name('achaean_remaster_geometry.py'),Path(__file__).with_name('remaster_achaean_shipyard.py'),Path(__file__).with_name('remaster_achaean_missile_launcher.py'),Path(__file__).with_name('checks_achaean_shipyard.py'),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/reconstruction/launch-facilities/achaean/ac14/model.blend'])
if __name__=='__main__':main()
