"""Authored fitted MN2C machinery; user concept detail, legacy-controlled silhouette."""
import bpy
from mathutils import Vector
from build_openfa_assets import box,beam
from mauna_max_combat_craft_type_6_parts import roof_patch,roof_skin,roof_section,closed_grid


def add_details(recipe):
    pairs=[];names=[]
    mats={k:bpy.data.materials[v] for k,v in dict(hull='Type 6 | worn grey layered hull',edge='Type 6 | oxidized service alloy',dark='Type 6 | carbon dark strips',brown='Type 6 | worn brown side details').items()}
    def keep(obj,support):
        names.append(obj.name);pairs.append(dict(part=obj.name,support=support));return obj
    def cube(name,p,size,mat,support,bevel=.003):
        return keep(box('Type 6 detail '+name,p,size,mats[mat],bevel),support)
    # Three framed maintenance banks per side. All straddle actual carriers;
    # the continuous bronze strip remains visible above/between the banks.
    for side in [-1,1]:
        for i,y in enumerate([-1.15,0,1.15]):
            label=f'{side} {i}';carrier=cube('service bay backing '+label,(side*.568,y,-.11),(.042,.46,.17),'dark','Type 6 main hull').name
            for end in [-1,1]:
                cube('service bay jamb '+label+' '+str(end),(side*.592,y+end*.217,-.11),(.04,.027,.19),'hull',carrier)
                cube('service bay ledge '+label+' '+str(end),(side*.592,y,-.11+end*.077),(.04,.46,.026),'edge',carrier)
            for j in range(5):
                cube('service bay rib '+label+' '+str(j),(side*.589,y-.14+j*.07,-.11),(.036,.016,.12),'edge',carrier,.002)
        # Two thicker guard blocks carry the side piping rather than floating.
        for i,y in enumerate([-.59,.59]):
            carrier=cube('pipe saddle '+str(side)+' '+str(i),(side*.565,y,.052),(.04,.17,.10),'hull','Type 6 main hull').name
            rod=beam('Type 6 detail seated conduit '+str(side)+' '+str(i),(side*.586,y-.075,.070),(side*.586,y+.075,.070),.016,mats['edge']);keep(rod,carrier)
    # Lower prow service inset; no emissive/window interpretation is assigned.
    carrier=cube('prow recessed backing',(0,-1.845,-.035),(.70,.035,.12),'dark','Type 6 pale fore panel').name
    for side in [-1,1]:
        cube('prow frame side '+str(side),(side*.35,-1.85,-.035),(.025,.04,.14),'hull',carrier)
        cube('prow frame horizontal '+str(side),(0,-1.85,-.035+side*.055),(.72,.04,.025),'hull',carrier)
    for i,x in enumerate([-.25,-.15,-.05,.05,.15,.25]):cube('prow rib '+str(i),(x,-1.855,-.035),(.018,.03,.10),'edge',carrier,.002)
    # The forward deck remains low; no additional tower is introduced.
    carrier=cube('foredeck recessed backing',(0,-1.46,.165),(.79,.34,.022),'dark','Type 6 main hull').name
    for side in [-1,1]:
        cube('foredeck edge '+str(side),(side*.385,-1.46,.177),(.028,.36,.027),'hull',carrier)
        cube('foredeck transverse edge '+str(side),(0,-1.46+side*.16,.177),(.79,.028,.027),'hull',carrier)
    for i in range(5):cube('foredeck louver '+str(i),(0,-1.57+i*.055,.178),(.69,.017,.029),'edge',carrier,.002)
    # Conformal maintenance banks follow the sloping aft roof exactly.
    for side in [-1,1]:
        x=side*.30;label=str(side)
        carrier=keep(roof_patch('Type 6 detail roof backing '+label,x-.075,x+.075,.22,.66,mats['dark']), 'Type 6 sloped upper roof').name
        for i,y in enumerate([.25,.32,.39,.46,.53,.60]):
            keep(roof_patch('Type 6 detail roof louver '+label+' '+str(i),x-.067,x+.067,y-.011,y+.011,mats['edge'],top=.021,back=.001,support=carrier),carrier)
        for sign in [-1,1]:
            keep(roof_patch('Type 6 detail roof bezel '+label+' '+str(sign),x+sign*.065-.009,x+sign*.065+.009,.22,.66,mats['hull'],top=.018,back=.001,support=carrier),carrier)
    # Four fitted shoulder plates give the raised housing real layered depth.
    # Their width follows the original loft; no generic floating rectangles.
    def shoulder(name,side,y0,y1,low,high,front_offset,back_offset,mat,support):
        front=[];rear=[];columns=17;rows=9
        for row in range(rows):
            f=row/(rows-1)
            for col in range(columns):
                y=y0+(y1-y0)*col/(columns-1);w,_=roof_section(y);z0=.17+(roof_skin(side*w,y)-.17)*low;z1=.17+(roof_skin(side*w,y)-.17)*high;z=z0+(z1-z0)*f
                front.append((side*(w+front_offset),y,z));rear.append((side*(w+back_offset),y,z))
        return keep(closed_grid('Type 6 detail '+name,front,rear,columns,rows,mats[mat]),support)
    for side in [-1,1]:
        for i,(a,b) in enumerate([(.24,.58),(.85,1.20)]):
            label=str(side)+' '+str(i)
            plate=shoulder('roof shoulder armour '+label,side,a,b,.04,.90,.010,-.012,'hull','Type 6 sloped upper roof').name
            inset=shoulder('roof shoulder service inset '+label,side,a+.045,b-.045,.20,.66,.016,.004,'dark',plate).name
            for j,f in enumerate([.28,.43,.58]):shoulder('roof shoulder rib '+label+' '+str(j),side,a+.055,b-.055,f,f+.045,.026,.009,'edge',inset)
            for j,y in enumerate([a+.025,b-.025]):
                w,_=roof_section(y);z=.17+(roof_skin(side*w,y)-.17)*.78
                keep(beam('Type 6 detail shoulder stud '+label+' '+str(j),(side*(w+.004),y,z),(side*(w+.023),y,z),.008,mats['edge']),plate)
    # Small structural bands on the existing red covers; opaque, not bridges.
    for side in [-1,1]:
        for j,yc in enumerate([-.99,-.78]):
            front=[];rear=[]
            for y in [yc-.012,yc+.012]:
                z=.25+(.47-.25)*(y+1.10)/.15 if y<=-.95 else .47+(.40-.47)*(y+.95)/.25
                for x in [side*.28-.085,side*.28+.085]:front.append((x,y,z+.006));rear.append((x,y,z-.006))
            keep(closed_grid('Type 6 detail red cover band '+str(side)+' '+str(j),front,rear,2,2,mats['edge']),'Type 6 red raised piece '+str(side))
    bpy.context.view_layer.update()
    return dict(names=names,attachment_pairs=pairs,interpretation='User artistic concept guides seated service bays, deck/roof louvers and cover bands. Original low layered hull and transverse red covers control shape; added fittings do not establish equipment function.')
