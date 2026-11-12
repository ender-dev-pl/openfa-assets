"""Culture-specific engineering proposals from the supplied selected concepts."""
import argparse,math,sys
import bpy
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from engineering_ship_refinement import RefinedShip as Ship



class HiDefRigellianShip(Ship):
    """Keep smooth formed envelopes; spend geometry at functional interfaces."""
    def ellipsoid(self,name,p,size,mat,parent=None):
        bpy.ops.mesh.primitive_uv_sphere_add(segments=40,ring_count=20,radius=1,location=p)
        o=bpy.context.object
        for v in o.data.vertices:v.co=(v.co.x*size[0]/2,v.co.y*size[1]/2,v.co.z*size[2]/2)
        return self.finish(o,name,mat,parent,0,True)

    def cyl(self,name,p,r,depth,mat,axis=(0,0,1),parent=None,vertices=32):
        return super().cyl(name,p,r,depth,mat,axis,parent,vertices)

    def conformal_patch(self,parent,name,width,length,mat,offsets=(-.008,.012)):
        # Sample the actual mesh,not an approximate sphere or a tangent plane.
        nx,ny=7,9;vertices=[];top=max(v.co.z for v in parent.data.vertices)+.3
        for offset in offsets:
            for j in range(ny):
                y=-length/2+length*j/(ny-1)
                for i in range(nx):
                    x=-width/2+width*i/(nx-1)
                    hit,point,normal,index=parent.ray_cast(Vector((x,y,top)),Vector((0,0,-1)))
                    assert hit,('Missing curved housing surface',name,x,y)
                    vertices.append(tuple(point+normal*offset))
        n=nx*ny;faces=[]
        for j in range(ny-1):
            for i in range(nx-1):
                q=j*nx+i;faces.extend([(q,q+1,q+nx+1,q+nx),(n+q+nx,n+q+nx+1,n+q+1,n+q)])
        edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(n-2,n-nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
        faces.extend((a,b,b+n,a+n) for a,b in zip(edge,edge[1:]+edge[:1]))
        return self.local(self.solid(name,vertices,faces,mat),parent,(0,0,0))

    def enrich(self):
        super().enrich()
        body=next(o for o in self.parts if 'smooth oval hull' in o.name)
        alloy=self.materials['silver'];seal=self.materials['recess'];copper=self.materials['copper']
        # Gasket, seated lid and captive fasteners; broad skins stay quiet.
        for side in [-1,1]:
            hatch=self.roof(body,'Rigellian seated service gasket '+str(side),side*.42,.74,(.36,.46),seal,.025)
            self.local_box(hatch,'Rigellian pale alloy service lid '+str(side),(0,0,.016),(.31,.41,.022),alloy,.012)
            for x in [-.115,.115]:
                self.local_cyl(hatch,'Rigellian captive lid bolt '+str(side)+str(x),(x,.14,.032),.018,.018,copper,vertices=8)
            # Actual cooling grille base follows the curved pressure skin.
            grille=self.roof(body,'Rigellian cooling recess '+str(side),side*.46,-.57,(.26,.35),seal,.028)
            for j in range(5):
                self.local_box(grille,'Rigellian cooling louvre '+str(side)+str(j),(0,-.125+j*.062,.022),(.22,.025,.022),alloy,.003)
            # Small copper service hatches on the engine fairings.
            pod=next(o for o in self.parts if 'smooth side nacelle '+str(side) in o.name)
            self.conformal_patch(pod,'Rigellian copper nacelle service collar '+str(side),.26,.43,copper)
            self.conformal_patch(pod,'Rigellian nacelle inspection slot '+str(side),.15,.24,seal,(.007,.024))
        # Broad formed seams and a recessed crew visor echo the hidef fleet,
        # while leaving most pressure skin quiet rather than gridded.
        def skin(name,x0,x1,y0,y1,mat):
            nx,ny=7,7;v=[]
            for depth in [-.018,.016]:
                for j in range(ny):
                    y=y0+(y1-y0)*j/(ny-1)
                    for i in range(nx):
                        x=x0+(x1-x0)*i/(nx-1)
                        z=.35+.50*math.sqrt(max(.01,1-(x/1.10)**2-(y/1.525)**2))
                        v.append((x,y,z-.35+depth))
            n=nx*ny;f=[]
            for j in range(ny-1):
                for i in range(nx-1):
                    q=j*nx+i;f.extend([(q,q+1,q+nx+1,q+nx),(n+q+nx,n+q+nx+1,n+q+1,n+q)])
            edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(n-2,n-nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
            f.extend((a,b,b+n,a+n) for a,b in zip(edge,edge[1:]+edge[:1]))
            return self.local(self.solid(name,v,f,mat),body,(0,0,0))
        skin('Rigellian broad fore formed skin',-.68,.68,-.86,-.27,self.materials['sage'])
        skin('Rigellian broad aft formed skin',-.29,.29,.87,1.20,self.materials['sage'])
        glass=self.mat('crew-visor',(21/255,40/255,46/255),.08,.24)
        skin('Rigellian recessed panoramic crew visor',-.48,.48,-1.12,-.91,glass)
        for x in [-.26,0,.26]:
            self.roof(body,'Rigellian pale visor mullion '+str(x),x,-1.015,(.018,.245),alloy,.018)
        # Elliptical shoulder seal intersects the underlying continuous envelope.
        n=48;v=[(1.1*r*math.cos(i*math.tau/n),1.525*r*math.sin(i*math.tau/n),z-.35) for z in [.225,.265] for r in [.89,1.015] for i in range(n)];f=[]
        for i in range(n):
            j=(i+1)%n;f.extend([(i,j,n+j,n+i),(2*n+i,3*n+i,3*n+j,2*n+j),(i,2*n+i,2*n+j,j),(n+j,3*n+j,3*n+i,n+i)])
        self.local(self.solid('Rigellian formed shoulder gasket',v,f,seal),body,(0,0,0))
        bpy.context.view_layer.update()
        for obj in self.parts:
            if any(t in obj.name for t in ['broad fore formed skin','broad aft formed skin','panoramic crew visor','formed shoulder gasket']):
                assert obj.parent==body,('Skin must inherit the hull transform',obj.name)
                assert all(abs(a-b)<1e-6 for a,b in zip(obj.matrix_world.to_scale(),body.matrix_world.to_scale())),obj.name
                if 'shoulder gasket' not in obj.name:
                    distances=[]
                    for v in obj.data.vertices:
                        hit,point,normal,index=body.closest_point_on_mesh(v.co)
                        assert hit,obj.name
                        distances.append((point-v.co).length)
                    assert max(distances)<.045,('Lifted skin',obj.name,max(distances))
        for o in list(self.parts):
            if 'upper link' in o.name:
                self.local_box(o,'Rigellian protected manipulator service cover '+o.name,(0,-.105,0),(.13,.038,.21),copper,.009)


def cycle(s,j,axis,amount,kind='rotation_euler'):
    start=getattr(j,kind)[axis]
    s.animate(j,axis,[(1,start),(25,start+amount),(49,start),(73,start-amount*.35),(97,start)],kind)

def plate(s,name,polygon,z,depth,mat,parent=None):
    n=len(polygon);v=[(x,y,z+d) for d in [-depth/2,depth/2] for x,y in polygon]
    return s.solid(name,v,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],mat,.025,parent)

def curved_bar(s,name,points,width,depth,mat,parent=None):
    # Solid quadrilateral-section continuous curved tool, rather than loose rods.
    if len(points)>3:
        raw=[Vector(p) for p in points];dense=[]
        for i in range(len(raw)-1):
            a=raw[max(0,i-1)];b=raw[i];c=raw[i+1];d=raw[min(len(raw)-1,i+2)]
            for step in range(5):
                t=step/5;dense.append(tuple(.5*((2*b)+(-a+c)*t+(2*a-5*b+4*c-d)*t*t+(-a+3*b-3*c+d)*t*t*t)))
        points=dense+[tuple(raw[-1])]
    verts=[]
    for i,p in enumerate(points):
        prev=Vector(points[max(0,i-1)]);nxt=Vector(points[min(len(points)-1,i+1)]);t=(nxt-prev).normalized();normal=Vector((-t.y,t.x,0)).normalized()
        verts += [tuple(Vector(p)+normal*w+Vector((0,0,z))) for w,z in [(-width/2,-depth/2),(width/2,-depth/2),(width/2,depth/2),(-width/2,depth/2)]]
    faces=[(3,2,1,0),tuple(range(len(verts)-4,len(verts)))]
    for i in range(len(points)-1):
        for j in range(4):faces.append((4*i+j,4*i+(j+1)%4,4*(i+1)+(j+1)%4,4*(i+1)+j))
    return s.solid(name,verts,faces,mat,.025,parent)

def repair_tool(s,prefix,a,b,c,steel,copper,gold,left=True,parent=None):
    j=s.joint(prefix+'Shoulder',a,parent);s.cyl(prefix+' shoulder bearing',a,.14,.22,copper,(1,0,0),j);s.beam(prefix+' upper link',a,b,.19,.20,steel,j)
    k=s.joint(prefix+'Elbow',b,j);s.cyl(prefix+' elbow bearing',b,.14,.22,steel,(1,0,0),k);s.beam(prefix+' lower link',b,c,.19,.20,steel,k)
    if left:
        s.box(prefix+' clamp bridge',(c[0],c[1]-.08,c[2]),(.48,.20,.20),steel,.06,k)
        for sign in [-1,1]:
            finger=s.joint(prefix+'Jaw'+str(sign),(c[0]+sign*.18,c[1]-.12,c[2]),k)
            s.cyl(prefix+' jaw bearing '+str(sign),(c[0]+sign*.18,c[1]-.12,c[2]),.06,.23,copper,parent=finger,vertices=24)
            s.box(prefix+' copper gripping jaw '+str(sign),(c[0]+sign*.18,c[1]-.28,c[2]),(.14,.38,.20),copper,.025,finger)
            s.animate(finger,2,[(1,0),(25,0),(49,-sign*.22),(73,0),(97,0)],'rotation_euler')
    else:
        s.cyl(prefix+' nozzle housing',(c[0],c[1]-.1,c[2]),.14,.27,steel,(0,1,0),k);s.ring(prefix+' gold nozzle',(c[0],c[1]-.29,c[2]),.12,.06,.22,gold,(0,1,0),k)
    a=.12 if left else -.10;b=-.24 if left else .20
    s.animate(j,0,[(1,0),(25,a),(49,a),(73,0),(97,0)],'rotation_euler');s.animate(k,0,[(1,0),(25,b),(49,b),(73,0),(97,0)],'rotation_euler')

def rigellian(s,role):
    # Same authored palette as the canonical hidef fleet; portable worn maps.
    silver=s.mat('silver',(154/255,172/255,171/255),.62,.62)
    green=s.mat('sage',(100/255,127/255,120/255),.53,.62)
    gold=s.mat('gold',(185/255,155/255,67/255),.62,.62)
    crown=s.mat('crown-gold',(185/255,155/255,67/255),.62,.62)
    copper=s.mat('copper',(168/255,101/255,67/255),.62,.62)
    dark=s.mat('recess',(31/255,42/255,43/255),.40,.78)
    slate=s.mat('slate-shell',(100/255,127/255,120/255),.53,.62)
    lower=s.mat('lower-slate',(54/255,69/255,72/255),.53,.68)
    ventral=s.mat('ventral-copper',(141/255,86/255,59/255),.62,.62)
    s.ellipsoid('Rigellian smooth oval hull',(0,0,.35),(2.20,3.05,1.00),green)
    s.ellipsoid('Rigellian slate ventral skin',(0,.03,.10),(2.12,2.98,.52),lower)
    for side in [-1,1]:s.ellipsoid('Rigellian copper ventral casing '+str(side),(side*.55,.18,-.03),(.60,2.05,.35),ventral)
    # Broad gold fields follow the green hull,as on the canonical assault craft.
    for side in [-1,1]:
        verts=[];nx=3;ny=12
        for layer in [-.018,.012]:
            for j in range(ny):
                y=-.40+j*1.28/(ny-1)
                for i in range(nx):
                    x=side*(.40+i*.17);z=.35+.50*math.sqrt(max(.01,1-(x/1.10)**2-(y/1.525)**2));verts.append((x,y,z+layer))
        n=nx*ny;faces=[]
        for j in range(ny-1):
            for i in range(nx-1):
                q=j*nx+i;faces.extend([(q,q+1,q+1+nx,q+nx),(n+q+nx,n+q+1+nx,n+q+1,n+q)])
        edge=list(range(nx))+[j*nx+nx-1 for j in range(1,ny)]+list(range(n-2,n-nx-1,-1))+[j*nx for j in range(ny-2,0,-1)]
        for i,q in enumerate(edge):t=edge[(i+1)%len(edge)];faces.append((q,t,t+n,q+n))
        s.solid('Rigellian gold upper field '+str(side),verts,faces,gold)
        x=side*1.13;pod=s.ellipsoid('Rigellian smooth side nacelle '+str(side),(x,.27,.35),(.66,1.72,.65),slate)
        y=-.48 if role=='terraform' else 1.0
        s.ring('Rigellian copper engine mouth '+str(side),(x,y,.35),.26,.18,.18,copper,(0,1,0));hole=s.cyl('Temporary nacelle bore',(x,y,.35),.181,.50,dark,(0,1,0));s.cut(pod,hole);s.cyl('Rigellian blind dark engine '+str(side),(x,-.235 if role=='terraform' else .755,.35),.18,.035,dark,(0,1,0))
    if role=='terraform':s.cyl('Rigellian round gold dorsal cap',(0,.32,.86),.39,.16,crown)
    else:s.box('Rigellian oblong gold dorsal cap',(0,.30,.87),(.53,.92,.16),crown,.15)
    if role=='terraform':
        for side in [-1,1]:
            j=s.joint('PrecisionHornPivot'+str(side),(side*.55,-1.03,.18));s.cyl('Rigellian horn root bearing '+str(side),(side*.55,-1.03,.18),.15,.22,silver,(0,0,1),j)
            pts=[(side*x,y,.10) for x,y in [(.55,-1.00),(.76,-1.22),(.80,-1.52),(.72,-1.80)]]
            curved_bar(s,'Rigellian thick precision horn '+str(side),pts,.32,.30,silver,j);s.box('Rigellian copper working pad '+str(side),(side*.72,-1.82,.10),(.30,.20,.30),copper,.055,j);cycle(s,j,2,side*.12)
    else:
        for side in [-1,1]:repair_tool(s,'Rigellian '+('grip' if side<0 else 'weld'),(side*.66,-1.03,.22),(side*.88,-1.43,.08),(side*.72,-1.80,-.05),silver,copper,gold,side<0)
        s.placement.scale=(.83,.83,.83)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--role',choices=['terraform','repair'],required=True);a=p.parse_args(sys.argv[sys.argv.index('--')+1:]);s=HiDefRigellianShip(a.root.resolve(),'rigellian',a.role);rigellian(s,a.role)
    s.export(__file__,['Canonical-style cycle 3:formed pressure-skin sections,panoramic crew visor and shoulder seal complement canonical hidef slate-jade,pale alloy,ochre and copper palette;seated service hatches,cooling louvres and tool covers match functional detail level while preserving quiet formed skins and articulated tools.','Underside,rear engineering and hidden joints are authored extrapolations. ToolOperation is an asset preview;no runtime definition,mechanic,blueprint,production route or package is added.'])
