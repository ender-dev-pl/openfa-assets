"""First independent PH09 profile/connector assembly; reference-only originals."""
import math
import bpy,bmesh
from mathutils import Vector,Matrix
from build_openfa_assets import material,box,cylinder,beam,finish
from manufactured_vessels import vessel,profile_radius
from manufactured_annuli import annulus
NOSE='Warp Generator flared dome'
CORE='Warp Generator middle cylinder'
TUBE='Warp Generator rounded module'
Y_AXIS=Matrix(((1,0,0),(0,0,1),(0,-1,0)))
PROFILES={NOSE:[(-1.10,.025),(-1.08,.12),(-1.0,.28),(-.90,.40),(-.75,.52),(-.60,.60),(-.50,.64),(-.4375,.64)],CORE:[(-.48,.30),(.3125,.30)],TUBE:[(.20,.27),(.35,.37),(.55,.41),(.75,.37),(.90,.26),(1.0,.16),(1.0625,.09)]}
LOCATIONS={n:Vector((0,0,0)) for n in PROFILES}
ROTATIONS={n:Y_AXIS for n in PROFILES}
DENTS={NOSE:(math.pi,-.75,.006),CORE:(math.pi,-.10,.004),TUBE:(math.pi,.55,.005)}
PANELS=[(CORE,-.32,-.03,0),(CORE,-.32,-.03,math.pi)]
BANDS=[(.80,.84),(.94,.98)]
PATCHES=[]
SOCKETS={'AlignmentForward':((0,-1.25,0),(0,-1,0))}

def surface(owner,phi,z,offset=0):
    r=profile_radius(PROFILES[owner],z);angle,height,depth=DENTS[owner];delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle));r-=depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2));r+=offset
    return LOCATIONS[owner]+ROTATIONS[owner] @ Vector((r*math.cos(phi),r*math.sin(phi),z))


def hull_frame(owner,phi,z):
    obj=bpy.data.objects[owner];p=surface(owner,phi,z);n=ROTATIONS[owner] @ Vector((math.cos(phi),math.sin(phi),0));inv=obj.matrix_world.inverted();hit,p,normal,_=obj.ray_cast(inv @ (p+n*3),(inv.to_3x3() @ -n).normalized());assert hit
    return obj.matrix_world @ p,(inv.to_3x3().transposed() @ normal).normalized()


def orient(obj,rotation,origin=(0,0,0)):
    for v in obj.data.vertices:v.co=Vector(origin)+rotation @ v.co
    obj.data.update();return obj


def patch(name,owner,z0,z1,phi,width,surface_material,top=.008,back=-.018,support=None):
    spec=dict(name=name,owner=owner,z0=z0,z1=z1,phi=phi,width=width,top=top,back=back,support=support or owner)
    columns=65 if 'dome sector' in name else 17;steps=max(8,math.ceil((z1-z0)/.022));heights=[z0+(z1-z0)*i/steps for i in range(steps+1)]
    for z,_ in PROFILES[owner]:
        if z0<z<z1:heights=[h for h in heights if abs(h-z)>1e-8]+[z]
    heights.sort();height=len(heights);size=columns*height;vertices=[]
    for offset in [top,back]:vertices.extend(surface(owner,phi+width*(-1+2*i/(columns-1)),z,offset) for z in heights for i in range(columns))
    faces=[]
    for row in range(height-1):
        for col in range(columns-1):
            a=row*columns+col;f=(a,a+1,a+columns+1,a+columns);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(columns))+[row*columns+columns-1 for row in range(1,height)]+list(reversed(range((height-1)*columns,(height-1)*columns+columns-1)))+[row*columns for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]))
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);finish(obj,name,surface_material,0);PATCHES.append(spec)
    skin_faces=2*(height-1)*(columns-1)
    for face in data.polygons:face.use_smooth=face.index<skin_faces
    # Preserve the finite edge wall as a sharp boundary of each curved skin.
    uses={}
    for face in data.polygons:
        for edge in face.edge_keys:uses.setdefault(tuple(sorted(edge)),[]).append(face.use_smooth)
    for edge in data.edges:edge.use_edge_sharp=len(set(uses[tuple(sorted(edge.vertices))]))>1
    return obj





def axial(name,y,radius,depth,mat,x=0,z=0,vertices=48):
    return cylinder(name,(x,y,z),radius,depth,mat,vertices,rotation=Vector((0,1,0)).to_track_quat('Z','Y').to_euler())


def build():
    PATCHES.clear()
    m=dict(hull=material('Warp Generator | worn pale shell alloy',(.28,.29,.26),.72,.70),yellow=material('Warp Generator | worn yellow bands',(.44,.32,.025),.52,.73),copper=material('Warp Generator | worn copper connectors',(.34,.18,.10),.76,.70),edge=material('Warp Generator | oxidized service alloy',(.16,.20,.22),.78,.65),dark=material('Warp Generator | dark terminal inlays',(.012,.016,.018),.40,.80))
    for owner,profile in PROFILES.items():orient(vessel(owner,profile,m['hull'],[DENTS[owner]]),Y_AXIS)
    for i in range(4):
        phi=i*math.tau/4;x=.32*math.cos(phi);z=.32*math.sin(phi)
        axial('Warp Generator copper connector '+str(i),.225,.060,.45,m['copper'],x,z)
        axial('Warp Generator connector sleeve '+str(i),.10,.075,.07,m['edge'],x,z)
    for i,(y0,y1) in enumerate(BANDS):
        rows=[(y,profile_radius(PROFILES[TUBE],y)+.006,profile_radius(PROFILES[TUBE],y)-.014) for y in [y0,(y0+y1)/2,y1]]
        orient(annulus('Warp Generator yellow band '+str(i),(0,0),rows,m['yellow'],(0,y0,0)),Y_AXIS)
    # Finite fitted dome sectors leave narrow exposed-shell seams between them.
    for i in range(4):patch('Warp Generator dome sector '+str(i),NOSE,-1.02,-.48,i*math.pi/2,.74,m['hull'],.009,-.016)
    axial('Warp Generator front inlay',-1.11,.075,.025,m['dark'])
    orient(annulus('Warp Generator front bezel',(0,0),[(-1.125,.10,.055),(-1.109375,.10,.055)],m['hull'],(0,-1.12,0)),Y_AXIS)
    axial('Warp Generator rear inlay',1.068,.10,.040,m['dark'])
    orient(annulus('Warp Generator rear bezel',(0,0),[(1.0,.145,.065),(1.0859375,.13,.065)],m['hull'],(0,1.03,0)),Y_AXIS)
    for end,y in [('front',-1.126),('rear',1.091)]:
        for i in range(3):
            phi=i*math.tau/3;axial('Warp Generator '+end+' terminal stud '+str(i),y,.009,.018,m['edge'],.032*math.cos(phi),.032*math.sin(phi),24)
    bpy.context.view_layer.update()
    for i,(owner,z0,z1,phi) in enumerate(PANELS):
        panel='Warp Generator service cover '+str(i);patch(panel,owner,z0,z1,phi,.20,m['hull'])
        for j,f in enumerate([.32,.68]):
            z=z0+(z1-z0)*f;patch('Warp Generator service slot '+str(i)+' '+str(j),owner,z-.004,z+.004,phi,.13,m['dark'],.016,.003,panel)
        for j,f in enumerate([.15,.85]):
            z=z0+(z1-z0)*f
            for k,off in enumerate([-.15,.15]):
                p,n=hull_frame(owner,phi+off,z);cylinder('Warp Generator fastener '+str(i)+' '+str(j)+' '+str(k),p+n*.009,.003,.022,m['edge'],16,rotation=n.to_track_quat('Z','Y').to_euler())
    return m
