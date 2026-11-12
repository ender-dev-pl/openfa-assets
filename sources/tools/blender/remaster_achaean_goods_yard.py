"""AC24 grounded ochre storage casings, joined coral shoulders and blue-violet tips."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import field
CENTRES=[(-.46,.23),(.46,.23),(0,-.57)]
UPPER=[(.90,.25),(.97,.34),(1.10,.44),(1.26,.47),(1.42,.44),(1.55,.34),(1.66,.19),(1.72,.12),(1.96,.105),(2.00,.09)]

def rounded_upper():
    result=[]
    for i,(a,b) in enumerate(zip(UPPER,UPPER[1:])):
        before=UPPER[max(0,i-1)];after=UPPER[min(len(UPPER)-1,i+2)];h=b[0]-a[0];m0=(b[1]-before[1])/(b[0]-before[0]);m1=(after[1]-a[1])/(after[0]-a[0])
        for j in range(3):
            t=j/3;r=(2*t**3-3*t*t+1)*a[1]+(t**3-2*t*t+t)*h*m0+(-2*t**3+3*t*t)*b[1]+(t**3-t*t)*h*m1;result.append((a[0]+t*h,r))
    return result+[UPPER[-1]]

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='goods-yard'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);gold=material(folder,'Ochre protected lower casings',(.39,.26,.10),.65,.45);blue=material(folder,'Blue violet source tips',(.065,.09,.31),.35,.39);dark=material(folder,'Dark closed recesses',(.015,.020,.025),0,.83);dark.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.10
    worn_coral_pbr(coral,folder)
    for i,(x,y) in enumerate(CENTRES):
        lower=lathe('AC24 grounded ochre casing '+str(i),(x,y),[(0,.28),(.05,.33),(.14,.35),(.88,.35),(.97,.32),(1.02,.29)],gold)
        bpy.context.view_layer.objects.active=lower;t=lower.modifiers.new('Stable pocket base faces','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=t.name)
        upper=lathe('AC24 joined coral shoulder '+str(i),(x,y),rounded_upper(),coral)
        lathe('AC24 short blue violet tip '+str(i),(x,y),[(1.94,.065),(2.27,.065),(2.31,.045)],blue)
        field(lower,'AC24 dark vertical casing recess '+str(i),x,.51,.12,.70,dark,dark)
        pane=bpy.data.objects['AC24 dark vertical casing recess '+str(i)];normal=pane.rotation_quaternion@Vector((0,-1,0))
        for j,z in enumerate([.30,.51,.72]):
            p=pane.location+normal*.035+pane.rotation_quaternion@Vector((0,0,z-.51));rib=box(f'AC24 solid recess cross rib {i} {j}',p,(.17,.08,.035),gold,.008);rib.rotation_mode='QUATERNION';rib.rotation_quaternion=pane.rotation_quaternion
        px=x+(-.06 if i==0 else .06 if i==1 else 0);field(upper,'AC24 dark upper port '+str(i),px,1.43,.09,.09,dark,dark)
        bpy.context.view_layer.objects.active=lower;t=lower.modifiers.new('Stable recessed casing triangles','TRIANGULATE');t.ngon_method='CLIP';bpy.ops.object.modifier_apply(modifier=t.name);cleanup(lower);cleanup(upper)
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','remaster_achaean_manoeuvring_device.py','remaster_achaean_missile_launcher.py','checks_achaean_shipyard.py']
    finish(folder,dict(issue=256,id='openfa:building/legacy/174',key='AC24',name='Goods Yard',culture='achaean',footprint=[2,2],definition_class=255,construction_updates=40,triangle_budget=30000,materials=4,structure_checks='checks_achaean_goods_yard',state_contract='Static highly protected storage for non-ore goods. Actual source has three grounded ochre lower casings,joined rounded coral shoulders/dark ports,short blue-violet tips and vertical recessed/ribbed lower details. No exposed cargo,door motion or capacity-fill stages evidenced by all41 fixed-view catalogue phases. Grooves/ribs are closed-casing engineering interpretation,not open cargo bays. Shared ACS2 and client storage/activity/damage mapping separate;hidden depth/engineering interpreted.',scale_contract='PlacementRoot identity groundZ0;Blender-Yfront/+Zup;2x2footprint. Source colour boundary/three-unit asymmetry retained;exact tile/world/camera calibration and Android frame time separate.'),__file__,[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac24/model.blend'])
if __name__=='__main__':main()
