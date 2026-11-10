"""AC19 enclosed dome column, grounded side facings and source-visible front conduit."""
import sys
from pathlib import Path
import bpy
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from achaean_remaster_geometry import ROOT,lathe,box,material,finish
from remaster_achaean_shipyard import cleanup,worn_coral_pbr
from remaster_achaean_manoeuvring_device import field

def main():
    bpy.ops.wm.read_factory_settings(use_empty=True);folder='asteroid-shield'
    coral=material(folder,'Coral alloy',(.43,.19,.13),.48,.51);slate=material(folder,'Slate front conduit',(.13,.21,.26),.65,.43);gold=material(folder,'Ochre flank facing',(.39,.26,.10),.65,.45);dark=material(folder,'Dark instrument backs',(.015,.020,.025),0,.83);red=material(folder,'Red instrument casing',(.24,.009,.003),.16,.35);blue=material(folder,'Pale blue source fields',(.24,.40,.53),.12,.30,.10);amber=material(folder,'Amber lower source slit',(.85,.39,.075),.12,.30,.25);lens=material(folder,'Red source lens',(.38,.015,.008),.15,.27,.15)
    red.node_tree.nodes.get('Principled BSDF').inputs['Specular IOR Level'].default_value=.12
    worn_coral_pbr(coral,folder)
    body=lathe('AC19 enclosed main casing',(0,0),[(0,.55),(.06,.61),(.18,.63),(.50,.63),(1.10,.63),(1.70,.63),(2.20,.63),(2.35,.65),(2.52,.64),(2.70,.57),(2.88,.44),(3.02,.27),(3.14,.21),(3.30,.18),(3.36,.15)],coral)
    lathe('AC19 short slate upper tip',(0,0),[(3.29,.085),(3.40,.085),(3.78,.065)],slate)
    box('AC19 grounded ochre left facing',(-.60,-.13,1.15),(.18,.42,2.30),gold,.035)
    box('AC19 grounded long coral right facing',(.49,-.39,1.20),(.19,.22,2.40),coral,.045)
    shoe=lathe('AC19 grounded front shoe',(0,-.63),[(0,.13),(.05,.18),(.28,.18),(.36,.13),(.40,.08)],coral)
    conduit=lathe('AC19 supported front conduit',(0,-.66),[(.32,.07),(.40,.085),(.79,.085),(1.14,.085),(1.44,.085),(1.84,.085),(2.12,.085),(2.43,.07)],slate)
    bpy.context.view_layer.objects.active=conduit;tri=conduit.modifiers.new('Conduit base faces','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
    for i,z in enumerate([.60,.95,1.28,2.10,2.30]):field(conduit,'AC19 pale conduit field '+str(i),0,z,.06,.12,blue,dark)
    bpy.context.view_layer.objects.active=conduit;tri=conduit.modifiers.new('Conduit pocket faces','TRIANGULATE');tri.ngon_method='CLIP';bpy.ops.object.modifier_apply(modifier=tri.name);cleanup(conduit)
    collar=lathe('AC19 red conduit instrument',(0,-.66),[(1.43,.08),(1.48,.13),(1.56,.165),(1.70,.165),(1.78,.13),(1.82,.08)],red)
    field(collar,'AC19 red instrument lens',0,1.63,.10,.10,lens,dark)
    for i,z in enumerate([.72,1.12]):field(body,'AC19 small left pale field '+str(i),-.22,z,.065,.10,blue,dark)
    field(body,'AC19 upper red recessed port',-.29,2.65,.10,.13,red,dark)
    field(shoe,'AC19 lower red inset',0,.16,.16,.07,red,dark)
    pane=bpy.data.objects['AC19 lower red inset'];o=box('AC19 amber lower slit',pane.location,(.065,.015,.025),amber,.003);o.rotation_mode='QUATERNION';o.rotation_quaternion=pane.rotation_quaternion;o.location+=pane.rotation_quaternion@Vector((0,-.012,0))
    for o in [body,shoe,collar]:cleanup(o)
    helpers=['achaean_remaster_geometry.py','remaster_achaean_shipyard.py','remaster_achaean_manoeuvring_device.py','remaster_achaean_missile_launcher.py','checks_achaean_shipyard.py']
    finish(folder,dict(issue=256,id='openfa:building/legacy/169',key='AC19',name='Asteroid Shield',culture='achaean',footprint=[2,2],definition_class=10,construction_updates=46,triangle_budget=30000,materials=8,structure_checks='checks_achaean_asteroid_shield',state_contract='Static source-led power-intensive screen device with enclosed domed column,asymmetric long side facings,front slate conduit,red instrument collar,two small left pale fields,upper red port,grounded red/amber shoe and short slate tip. All41 catalogue phases are fixed-view reveal/highlight,not evidenced operating motion or shield-bubble effect. Low constant source-field emission is authored per material; client activity/power/shield mapping and shared ACS2 construction separate. Hidden rear/depth engineering interpreted.',scale_contract='PlacementRoot identity at groundZ0;Blender-Yfront/+Zup;2x2footprint. Exact tile/world,camera calibration and Android frame time separate.'),__file__,[*(Path(__file__).with_name(n) for n in helpers),ROOT/'tools/publication_support.py',ROOT/'sources/docs/assets/bootstrap-3d/full-catalogue/achaean/ac19/model.blend'])
if __name__=='__main__':main()

