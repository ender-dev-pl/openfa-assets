"""AC23 three connected four-lobed storage columns with two grounded slate braces."""
import sys
from pathlib import Path
import bpy
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import worn_coral_pbr
CENTRES=[(-.48,.22),(.48,.22),(0,-.58)]
PROFILE=[(0,.34),(.07,.44),(.21,.50),(.36,.48),(.47,.38),(.53,.38),(.70,.50),(.87,.48),(1.00,.38),(1.06,.38),(1.23,.50),(1.40,.48),(1.53,.38),(1.59,.38),(1.76,.50),(1.96,.46),(2.12,.31),(2.20,.06)]

def rounded_profile():
    # Cubic radius interpolation uses actual axial spacing; control sections stay exact.
    result=[]
    for i,(a,b) in enumerate(zip(PROFILE,PROFILE[1:])):
        before=PROFILE[max(0,i-1)];after=PROFILE[min(len(PROFILE)-1,i+2)];h=b[0]-a[0];m0=(b[1]-before[1])/(b[0]-before[0]);m1=(after[1]-a[1])/(after[0]-a[0])
        for j in range(3):
            t=j/3;r=(2*t**3-3*t*t+1)*a[1]+(t**3-2*t*t+t)*h*m0+(-2*t**3+3*t*t)*b[1]+(t**3-t*t)*h*m1;result.append((a[0]+t*h,r))
    return result+[PROFILE[-1]]

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='ore-yard'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate structural braces',(.13,.21,.26),.65,.43);red=material(folder,'Red source top tips',(.24,.009,.003),.16,.45);red.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.15
    worn_coral_pbr(coral,folder)
    for i,xy in enumerate(CENTRES):
        lathe('AC23 four-lobed storage column '+str(i),xy,rounded_profile(),coral)
        lathe('AC23 short red top tip '+str(i),xy,[(2.15,.055),(2.20,.065),(2.29,.055),(2.31,.03)],red)
    for i,(x,y) in enumerate([(0,-1.05),(.61,-.26)]):
        box('AC23 grounded slate brace '+str(i),(x,y,.94),(.13,.18,1.88),slate,.025)
        for j,z in enumerate([.51,1.04,1.57]):
            cy=y+.01;box(f'AC23 brace strap {i} {j}',(x,cy,z),(.21,.25,.055),slate,.009)
            for k,dx in enumerate([-.078,.078]):box(f'AC23 strap fastener {i} {j} {k}',(x+dx,cy-.13,z),(.025,.018,.025),slate,.006)
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','checks_achaean_shipyard.py']
    finish(folder,dict(issue=256,id='openfa:building/legacy/173',key='AC23',name='Ore Yard',culture='achaean',footprint=[2,2],definition_class=30,construction_updates=44,triangle_budget=30000,materials=3,structure_checks='checks_achaean_ore_yard',state_contract='Static protected ore storage from actual body/shadow and all41 fixed-view catalogue phases. Three attached four-lobed closed coral columns with three short red tips;two grounded slate braces on front and right-rear columns. Left-rear column remains without added brace. Source gives no exposed ore,capacity-fill stages,door motion or transfer mechanism. Small brace straps/fasteners and hidden depth interpreted engineering;shared ACS2/client storage/activity/damage mapping separate.',scale_contract='PlacementRoot identity groundZ0;Blender-Yfront/+Zup;2x2footprint. Triangular three-column arrangement and source-visible asymmetry retained;exact tile/world/camera calibration and Android frame time separate.'),__file__,[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac23/model.blend'])
if __name__=='__main__':main()
