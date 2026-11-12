"""Fitted MN3C machinery from the user concept, constrained by the legacy envelope."""
import bpy
from build_openfa_assets import box,beam
from mauna_elite_command_craft_parts import skin


def add_details(recipe):
    pairs=[];names=[]
    mats={key:bpy.data.materials[label] for key,label in dict(hull='Elite | worn grey armour',blue='Elite | worn pale blue bands',edge='Elite | oxidized service alloy',dark='Elite | dark recesses').items()}
    def keep(obj,support):
        names.append(obj.name);pairs.append(dict(part=obj.name,support=support));return obj
    def cube(label,p,size,mat,support,bevel=.003):
        return keep(box('Elite detail '+label,p,size,mats[mat],bevel),support)
    for index,cy in [(-1,-.62),(1,.62)]:
        pod='Elite pod '+str(index)
        for side in [-1,1]:
            label=str(index)+' '+str(side);band='Elite blue side band '+label
            # Keep the blue material field readable inside a real fitted bezel.
            for end in [-1,1]:
                cube('blue field long rim '+label+' '+str(end),(side*.535,cy-.225+end*.090,0),(.035,.024,.60),'hull',band)
                cube('blue field end rim '+label+' '+str(end),(side*.535,cy-.225,end*.290),(.035,.205,.026),'edge',band)
                cube('blue field clasp '+label+' '+str(end),(side*.541,cy-.225,end*.215),(.040,.10,.025),'edge',band)
            frame='Elite service frame '+label;inset='Elite service inset '+label
            # The existing fasteners remain visible just inside the hood edges.
            for end in [-1,1]:
                cube('service hood horizontal '+label+' '+str(end),(side*.536,cy+.12,end*.266),(.036,.42,.027),'hull',frame)
                cube('service hood jamb '+label+' '+str(end),(side*.536,cy+.12+end*.195,0),(.036,.018,.54),'hull',frame)
            for j,z in enumerate([-.065,.065]):
                rod=beam('Elite detail service inset rib '+label+' '+str(j),(side*.540,cy+.005,z),(side*.540,cy+.235,z),.009,mats['edge']);keep(rod,inset)
        # Paired low deck maintenance covers; no tall command tower is inferred.
        carrier=cube('deck recess '+str(index),(0,cy+.15,.425),(.50,.29,.028),'dark',pod).name
        for side in [-1,1]:
            cube('deck longitudinal rim '+str(index)+' '+str(side),(side*.24,cy+.15,.440),(.025,.31,.025),'hull',carrier)
            cube('deck transverse rim '+str(index)+' '+str(side),(0,cy+.15+side*.14,.440),(.50,.025,.025),'hull',carrier)
        for j,y in enumerate([.06,.12,.18,.24]):cube('deck louver '+str(index)+' '+str(j),(0,cy+y,.444),(.40,.019,.025),'edge',carrier)
        # Two framed end panels flank, rather than replace, the original axial root.
        end=index*1.12
        for side in [-1,1]:
            label=str(index)+' '+str(side);carrier=cube('end field backing '+label,(side*.30,end+index*.005,0),(.20,.026,.58),'dark',pod).name
            cube('end blue armour '+label,(side*.30,end+index*.020,0),(.13,.025,.48),'blue',carrier)
            for sign in [-1,1]:
                cube('end field upright '+label+' '+str(sign),(side*.30+sign*.085,end+index*.020,0),(.022,.032,.58),'hull',carrier)
                cube('end field cap '+label+' '+str(sign),(side*.30,end+index*.020,sign*.275),(.20,.032,.026),'edge',carrier)
        # The enlarged legacy end views show a broad upper opaque-blue field.
        blue=cube('end upper blue field '+str(index),(0,end+index*.006,.22),(.80,.028,.14),'blue',pod).name
        for side in [-1,1]:
            cube('end upper field endcap '+str(index)+' '+str(side),(side*.39,end+index*.019,.22),(.025,.032,.16),'hull',blue)
            cube('end upper field edge '+str(index)+' '+str(side),(0,end+index*.019,.22+side*.065),(.80,.032,.020),'edge',blue)
        # Small stepped structural collars retain the thin opposed projections.
        projection='Elite axial projection '+str(index)
        for j,y in enumerate([1.36,1.60]):
            collar=cube('axial collar '+str(index)+' '+str(j),(0,index*y,0),(.155 if j==0 else .13,.105,.16 if j==0 else .14),'hull',projection).name
            for side in [-1,1]:cube('axial collar pin '+str(index)+' '+str(j)+' '+str(side),(side*.065,index*y,0),(.032,.045,.055),'edge',collar)
    # The connector has fitted routing, but its two side voids stay genuinely open.
    tray=cube('connector tray',(0,0,.168),(.50,.40,.040),'dark','Elite central connection').name
    for side in [-1,1]:cube('connector tray rim '+str(side),(side*.235,0,.192),(.025,.40,.027),'hull',tray)
    for i,x in enumerate([-.10,.10]):
        conduit=beam('Elite detail connector conduit '+str(i),(x,-.15,.214),(x,.15,.214),.035,mats['edge']);keep(conduit,tray)
        for side in [-1,1]:cube('connector strap '+str(i)+' '+str(side),(x,side*.10,.235),(.085,.027,.035),'hull',conduit.name)
    # Low side trusses give the short connector physical construction depth.
    # Their outer edge stays well inside the documented x=+/-0.43 void columns.
    for side in [-1,1]:
        x=side*.328
        for i,(a,b) in enumerate([((x,-.10,-.18),(x,.10,.10)),((x,-.10,.10),(x,.10,-.18)),((x,-.10,-.18),(x,-.10,.10)),((x,.10,-.18),(x,.10,.10))]):
            keep(beam('Elite detail connector side truss '+str(side)+' '+str(i),a,b,.012,mats['hull']),'Elite central connection')
    bpy.context.view_layer.update()
    return dict(names=names,attachment_pairs=pairs,interpretation='User reference guides framed material fields, low deck machinery, end panels, stepped collars and supported connector routes. Their precise engineering is authored; no glazing, emission, tall bridge or calibrated equipment socket is inferred.')
