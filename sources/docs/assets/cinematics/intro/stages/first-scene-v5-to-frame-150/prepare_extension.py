"""Continue manually fitted ship motion; synthesize an editable procedural galaxy field."""
import json, shutil
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation,RotationSpline
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import gaussian_filter,zoom,map_coordinates
p=Path(__file__).resolve().parent;old=p.parent/'first-scene-v4-ship-fit';base=json.loads((p/'base-ship-fit.json').read_text())
pts=np.array([[-1.35,-2.78,0],[1.35,-2.78,0],[0,3.65,1.481]])*.78
a=np.linspace(0,2*np.pi,40,endpoint=False);circle=np.array([.67*np.cos(a),a*0,.67*np.sin(a)]).T*.78+pts[0]
def pred(x,points=pts):
 q=Rotation.from_rotvec(x[:3]).apply(points)+x[3:];return np.c_[160+400*q[:,0]/-q[:,2],140-400*q[:,1]/-q[:,2]]
def residual(x,target,prior):
 c=pred(x,circle);sv=np.linalg.svd(c-c.mean(0),compute_uv=False)
 return np.r_[((pred(x)-target)*np.array([[1,1],[1,1],[.3,.3]])).ravel(),(sv[1]/sv[0]-.95)*20,(x[:3]-prior[:3])*3]
# Approximate screen landmarks interpreted from the extracted original frames.
marks=[(100,[(248,210),(299,213),(296,176)]),(105,[(253,209),(302,211),(301,176)]),(110,[(257,208),(305,210),(304,176)]),(120,[(267,207),(308,209),(309,177)]),(130,[(272,200),(310,202),(309,173)]),(140,[(273,197),(310,199),(308,171)]),(150,[(273,195),(309,197),(308,169)])]
rows=base['landmarks'][-3:];prior=np.array(rows[-1]['pose'])
for n,target in marks:
 result=least_squares(residual,prior,args=(np.array(target),prior),max_nfev=1200);prior=result.x
 rows.append(dict(source_frame=n,pose=prior.tolist(),target=target,projected=pred(prior).tolist(),nozzle_rmse=float(np.sqrt(np.mean((pred(prior)[:2]-target[:2])**2)))))
t=np.array([r['source_frame'] for r in rows]);x=np.array([r['pose'] for r in rows]);times=np.minimum(np.arange(192,302)/2,150)
rs=RotationSpline(t,Rotation.from_rotvec(x[:,:3]))(times);tr=PchipInterpolator(t,x[:,3:])(times)
out=dict(camera_world=base['camera_world'],provenance='Approximate manual landmarks; same simplified ship mesh as v4. Original frames 0..150 inclusive; final half-frame held.',landmarks=rows,poses=[dict(frame=i+193,rotation=q.tolist(),translation=v.tolist()) for i,(q,v) in enumerate(zip(rs.as_quat(),tr))])
(p/'extension-poses.json').write_text(json.dumps(out,indent=2)+'\n')
# Procedural field: no source pixels are sampled. Native pixel coordinates aid reproducibility.
h,w=896,1024; yy,xx=np.mgrid[0:h,0:w];px=(xx+.5)/w*320;py=280-(yy+.5)/h*280;rng=np.random.default_rng(8732)
def noise(scale):
 small=rng.normal(size=(scale,scale));big=zoom(small,(h/scale,w/scale),order=3)[:h,:w];return big/(big.std()+1e-9)
n1=noise(12);n2=noise(40);n3=noise(140);n4=noise(280)
dx=px-153;dy=py-129;c=np.cos(.32);s=np.sin(.32);X=(c*dx+s*dy)/145;Y=(-s*dx+c*dy)/88
r=np.sqrt(X*X+Y*Y);theta=np.arctan2(Y,X);rw=r+.026*n1+.012*n2
phase=theta+3.1*np.log(np.maximum(rw,.06))+.16*n1+.07*n2
arms=np.exp(-((np.sin(phase*1.0))/.38)**2)
threads=np.exp(-((np.sin(phase*2+.9))/.37)**2)*.20
outer=np.exp(-((rw-.92)/.045)**2)*(.4+.6*np.clip(n1*.25+.5,0,1))
envelope=np.exp(-(r/1.04)**10)*(1-np.exp(-(r/.15)**2))
density=(arms*.70+threads+outer*.30)*envelope*np.clip(.72+.22*n2+.12*n3+.05*n4,0,1.5)
# Dust lanes break up the arms instead of producing a regular luminous pinwheel.
dust=np.clip(.6+.3*n1+.12*n2,.04,1);density*=dust
rgb=density[...,None]*np.array([.24,.18,.17])
inner=np.exp(-((px-146)/47)**2-((py-113)/43)**2)*np.clip(.65+.20*n2+.08*n3,0,1)
rgb+=inner[...,None]*np.array([.065,.135,.135])
core=np.exp(-((px-146)/13)**2-((py-113)/16)**2)
rgb+=core[...,None]*np.array([.38,.52,.48])
# Golden horizontal and diagonal diffraction streaks visible in the reference.
for cx,cy,length,angle,width,gain in [(146,113,140,0,.48,.24),(161,131,137,.77,.6,.25),(174,169,63,0,.5,.16)]:
 u=(px-cx)*np.cos(angle)+(py-cy)*np.sin(angle);v=-(px-cx)*np.sin(angle)+(py-cy)*np.cos(angle)
 streak=np.exp(-(v/width)**2)*np.maximum(0,1-(u/length)**8)*np.exp(-(u/length)**4)
 rgb+=streak[...,None]*np.array([gain,gain*.57,gain*.25])
rgba=np.ones((h,w,4),np.float32);rgba[:,:,:3]=rgb;np.save(p/'procedural-galaxy.npy',rgba)
# Faint blue/green filaments beginning the following dissolve at frame 150.
fil=np.exp(-(np.sin((px/45+py/61)+n1*.4)*7)**2)*np.clip(n2*.3+.3,0,1)
fil*=np.exp(-((px-165)/150)**4-((py-150)/135)**4)
rgba[:,:,:3]=fil[...,None]*np.array([.025,.13,.13]);np.save(p/'procedural-next-cloud.npy',rgba)
print('Prepared poses and independent procedural cloud fields')
