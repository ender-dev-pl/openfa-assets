"""Independently authored stepped Mauna casing; legacy pixels are reference-only."""
import math
import bpy,bmesh
from mathutils import Vector
from build_openfa_assets import material,box,cylinder
PROFILES={};LOCATIONS={};ROTATIONS={};PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.15,0),(0,-1,0))}
PREFIX='Mauna Burns Unit '
DENTS=[('central casing',-.36,.05,.18,.012),('forward terminal',-.18,-.82,.14,.008)]
def dent(obj,x,y,top,depth):
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.subdivide_edges(bm,edges=list(bm.edges),cuts=23,use_grid_fill=True)
    for v in bm.verts:
        if abs(v.co.z-top)<1e-5:v.co.z-=depth*math.exp(-2*(((v.co.x-x)/.10)**2+((v.co.y-y)/.10)**2))
    bm.to_mesh(obj.data);bm.free();obj.data.update()
def solid(name,p,size,m,bevel=.012):
    obj=box(PREFIX+name,p,size,m,bevel)
    # Bake placement for stable local UV and imported geometry comparisons.
    for v in obj.data.vertices:v.co+=obj.location
    obj.location=(0,0,0)
    return obj
def build():
    m=dict(gold=material('Mauna Burns Unit | worn grey casing',(.10,.14,.17),.65,.72),red=material('Mauna Burns Unit | worn terminal alloy',(.12,.17,.21),.65,.72),accent=material('Mauna Burns Unit | worn pale side alloy',(.30,.42,.46),.68,.72),dark=material('Mauna Burns Unit | dark recessed alloy',(.025,.035,.04),.5,.80),edge=material('Mauna Burns Unit | fastener alloy',(.19,.24,.26),.72,.70))
    body=solid('central casing',(0,0,0),(1.2,1.24,.36),m['gold'],.025);dent(body,-.36,.05,.18,.012)
    for y,name in [(-.78,'forward terminal'),(.78,'rear terminal')]:
        obj=solid(name,(0,y,0),(.80,.44,.28),m['red'],.016)
        if y<0:dent(obj,-.18,-.82,.14,.008)
        solid(name+' seam',(0,y*.80,.141),(.64,.028,.018),m['dark'],.004)
    solid('pale side spine',(.08,0,.205),(.12,1.02,.09),m['accent'],.009)
    solid('pale outer rail',(.51,0,.205),(.18,1.02,.09),m['accent'],.009)
    solid('dark inset floor 0',(.29,0,.185),(.26,1.02,.02),m['dark'],.004)
    solid('dark longitudinal field',(-.50,0,.183),(.10,1.20,.025),m['dark'],.004)
    for i,y in enumerate([-.32,.32]):
        solid('service cover '+str(i),(-.32,y,.19),(.30,.30,.05),m['gold'],.01)
        for j,x in enumerate([-.42,-.22]):
            for k,by in enumerate([y-.10,y+.10]):cylinder(PREFIX+'fastener '+str(i)+' '+str(j)+' '+str(k),(x,by,.22),.018,.04,m['edge'],16)
        solid('underside joint '+str(i),(0,y,-.18),(.85,.05,.025),m['dark'],.004)
    return m
