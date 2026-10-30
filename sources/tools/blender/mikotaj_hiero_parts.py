"""First MK0A scout: compact opaque faceted metal, radial fins and an axial spike."""
import math
import bpy
from mathutils import Vector
from build_openfa_assets import material,cylinder,beam,finish
from manufactured_vessels import profile_radius

PROFILES={'Hiero faceted hull':[(-.1875,.22),(-.125,.55),(0,.68),(.15625,.50),(.21875,.24)],
 'Hiero upper spike':[(.125,.22),(.25,.14),(.6875,.045),(.96875,.014)],
 'Hiero lower keel':[(-.484375,.015),(-.35,.06),(-.125,.14)]}
BODY_DENT=(-math.pi/2,.07,.005)
FIN_DENT=(.85,.04,.003)
SOCKETS={'AlignmentForward':((0,-1.18,-.005),(0,-1,0))}
PATCHES=[]
CROSS=[]
for i in range(8):
    a=Vector((math.cos(math.pi/8+i*math.tau/8),math.sin(math.pi/8+i*math.tau/8)))
    b=Vector((math.cos(math.pi/8+(i+1)*math.tau/8),math.sin(math.pi/8+(i+1)*math.tau/8)))
    CROSS.extend(a.lerp(b,j/8) for j in range(8))


def body_dent(phi,z):
    angle,height,depth=BODY_DENT;delta=math.atan2(math.sin(phi-angle),math.cos(phi-angle))
    return depth*math.exp(-2*((delta/.11)**2+((z-height)/.09)**2))


def mesh(name,vertices,faces,surface):
    data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],faces);data.update();obj=bpy.data.objects.new(name,data)
    bpy.context.collection.objects.link(obj);finish(obj,name,surface,0);return obj


def faceted_shell(name,surface):
    profile=PROFILES[name];heights=[]
    for a,b in zip(profile,profile[1:]):
        count=math.ceil((b[0]-a[0])/.018);heights.extend(a[0]+(b[0]-a[0])*i/count for i in range(count))
    heights.append(profile[-1][0]);vertices=[];count=len(CROSS)
    for z in heights:
        radius=profile_radius(profile,min(profile[-1][0],max(profile[0][0],z)))
        for p in CROSS:
            d=body_dent(math.atan2(p.y,p.x),z) if name=='Hiero faceted hull' else 0;q=p*radius-p.normalized()*d;vertices.append((q.x,q.y,z))
    first=len(vertices);last=first+1;vertices.extend([(0,0,heights[0]),(0,0,heights[-1])]);end=(len(heights)-1)*count
    faces=[(first,(i+1)%count,i) for i in range(count)]+[(last,end+i,end+(i+1)%count) for i in range(count)]
    faces.extend((row*count+i,row*count+(i+1)%count,(row+1)*count+(i+1)%count,(row+1)*count+i) for row in range(len(heights)-1) for i in range(count))
    return mesh(name,vertices,faces,surface)


def closed_surfaces(name,top,back,width,height,surface):
    size=len(top);vertices=top+back;faces=[]
    for row in range(height-1):
        for col in range(width-1):
            a=row*width+col;f=(a,a+1,a+width+1,a+width);faces.extend([f,tuple(size+i for i in reversed(f))])
    edge=list(range(width))+[row*width+width-1 for row in range(1,height)]+list(reversed(range((height-1)*width,(height-1)*width+width-1)))+[row*width for row in reversed(range(1,height-1))]
    faces.extend((a,a+size,b+size,b) for a,b in zip(edge,edge[1:]+edge[:1]));return mesh(name,vertices,faces,surface)


def fin_width(r):return .24+(.20-.24)*(r-.36)/(.78-.36) if r<=.78 else .20+(.035-.20)*(r-.78)/(1.16-.78)


def fin_top(r,t):
    centre,side,depth=FIN_DENT
    return .075-.10*(r-.36)-depth*math.exp(-2*(((r-centre)/.09)**2+((t-side)/.07)**2))


def fin_point(i,r,t,offset=0):
    phi=i*math.pi/2;n=Vector((math.cos(phi),math.sin(phi),0));a=Vector((-math.sin(phi),math.cos(phi),0))
    return n*r+a*t+Vector((0,0,fin_top(r,t)+offset))


def fin(i,surface,inlay=False):
    width=17;rows=33 if inlay else 49;low,high=(.65,1.03) if inlay else (.36,1.16)
    heights=[low+(high-low)*j/(rows-1) for j in range(rows)]
    if not inlay:heights=sorted([r for r in heights if abs(r-.78)>1e-8]+[.78])
    top=[];back=[]
    for r in heights:
        half=.020 if inlay else fin_width(r)
        for j in range(width):
            t=half*(-1+2*j/(width-1));top.append(fin_point(i,r,t,.004 if inlay else 0));back.append(fin_point(i,r,t,-.012 if inlay else -(.10-.04*(r-.36)/.80)))
    return closed_surfaces(('Hiero fin inset ' if inlay else 'Hiero radial fin ')+str(i),top,back,width,len(heights),surface)


def gold_collar(surface):
    heights=[.24,.25,.275];count=len(CROSS);size=count*len(heights);vertices=[]
    for offset in [.010,-.018]:
        for z in heights:
            radius=profile_radius(PROFILES['Hiero upper spike'],z)+offset;vertices.extend((p.x*radius,p.y*radius,z) for p in CROSS)
    faces=[]
    for row in range(len(heights)-1):
        for i in range(count):
            a=row*count+i;b=row*count+(i+1)%count;faces.extend([(a,b,b+count,a+count),(a+size,a+count+size,b+count+size,b+size)])
    for row in [0,len(heights)-1]:
        for i in range(count):a=row*count+i;b=row*count+(i+1)%count;faces.append((a,a+size,b+size,b))
    return mesh('Hiero octagonal gold collar',vertices,faces,surface)


def gold_stripe(surface):
    width=17;height=21;top=[];back=[]
    for row in range(height):
        z=.285+(.49-.285)*row/(height-1);radius=profile_radius(PROFILES['Hiero upper spike'],z)
        for col in range(width):
            x=radius*math.sin(math.pi/8)*.75*(-1+2*col/(width-1));y=-radius*math.cos(math.pi/8)
            top.append((x,y-.006,z));back.append((x,y+.012,z))
    return closed_surfaces('Hiero gold spike stripe',top,back,width,height,surface)


def roof(phi,r,t):
    n=Vector((math.cos(phi),math.sin(phi),0));a=Vector((-math.sin(phi),math.cos(phi),0));origin=n*r+a*t+Vector((0,0,3))
    body=bpy.data.objects['Hiero faceted hull'];inverse=body.matrix_world.inverted();hit,p,normal,_=body.ray_cast(inverse @ origin,(inverse.to_3x3() @ Vector((0,0,-1))).normalized());assert hit
    p=body.matrix_world @ p;normal=(inverse.to_3x3().transposed() @ normal).normalized()
    if normal.z<0:normal=-normal
    return p,normal


def roof_patch(name,phi,radial,width,depth,surface,top=.006,back=-.014,support='Hiero faceted hull'):
    columns=13;rows=13;front=[];rear=[]
    for row in range(rows):
        r=radial+width*(-.5+row/(rows-1))
        for col in range(columns):
            t=depth*(-.5+col/(columns-1));p,_=roof(phi,r,t);front.append(p+Vector((0,0,top)));rear.append(p+Vector((0,0,back)))
    obj=closed_surfaces(name,front,rear,columns,rows,surface);PATCHES.append(dict(name=name,phi=phi,radial=radial,width=width,depth=depth,top=top,back=back,support=support));return obj


def build():
    PATCHES.clear()
    m=dict(hull=material('Hiero | worn slate blue metal',(.10,.15,.24),.70,.61),gold=material('Hiero | dulled gold accents',(.32,.28,.08),.72,.63),
        edge=material('Hiero | oxidized service alloy',(.19,.23,.27),.78,.62),dark=material('Hiero | carbon dark seams',(.012,.015,.021),.40,.80))
    for name in PROFILES:faceted_shell(name,m['hull'])
    for i in range(4):fin(i,m['hull']);fin(i,m['dark'],inlay=True)
    gold_collar(m['gold']);gold_stripe(m['gold']);bpy.context.view_layer.update()
    for i in range(4):
        phi=math.pi/4+i*math.pi/2;cover='Hiero roof service cover '+str(i)
        roof_patch(cover,phi,.34,.13,.11,m['hull'])
        for j,distance in enumerate([-.025,.025]):roof_patch('Hiero roof service slot '+str(i)+' '+str(j),phi,.34+distance,.010,.074,m['dark'],top=.012,back=.003,support=cover)
        for j,t in enumerate([-.040,.040]):
            p,normal=roof(phi,.34,t);cylinder('Hiero roof fastener '+str(i)+' '+str(j),p+normal*.008,.007,.015,m['edge'],vertices=16,rotation=normal.to_track_quat('Z','Y').to_euler())
    beam('Hiero upper needle',(0,0,.95),(0,0,1.10),.004,m['edge'])
    return m
