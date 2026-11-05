import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation, RotationSpline
from scipy.interpolate import PchipInterpolator
p=Path(__file__).resolve().parent
d=json.loads((p/'camera-model.json').read_text())
# Manually interpreted nozzle centres and midpoint of forward fins, in native pixels.
marks=[(24,[(39,257),(92,285),(209.5,180)],.52),(36,[(80,244),(156,267),(222.5,175.5)],.58),(48,[(129,236),(200,251),(242,176.5)],.65),(60,[(172,226),(238,240),(255,175.5)],.72),(72,[(214,216),(272,220),(267,175.5)],.85),(84,[(236,216),(294,219),(277,177.5)],.92),(95,[(241,218),(295,219),(289,179)],.95)]
pts=np.array([[-1.35,-2.78,0],[1.35,-2.78,0],[0,3.65,1.481]])*.78
angles=np.linspace(0,2*np.pi,40,endpoint=False)
circle=np.array([.67*np.cos(angles),angles*0,.67*np.sin(angles)]).T*.78+pts[0]
def project(q):return np.c_[160+400*q[:,0]/-q[:,2],140-400*q[:,1]/-q[:,2]]
def pred(x,points=pts):return project(Rotation.from_rotvec(x[:3]).apply(points)+x[3:])
def residual(x,target,aspect,prior):
    uv=pred(x); cp=pred(x,circle); sv=np.linalg.svd(cp-cp.mean(0),compute_uv=False)
    return np.r_[((uv-target)*np.array([[1,1],[1,1],[.3,.3]])).ravel(),(sv[1]/sv[0]-aspect)*25,(x[:3]-prior)*2]
rows=[]
for n,uv,a in marks:
    old=next(z for z in d['poses'] if z['source_frame']==n)
    m=np.array(old['camera_matrix']);r=Rotation.from_matrix(m[:3,:3]/.78).as_rotvec()
    if rows: r=np.array(rows[-1]['pose'][:3])
    x=np.r_[r,m[:3,3]]
    fit=least_squares(residual,x,args=(np.array(uv),a,r),max_nfev=1500)
    rows.append(dict(source_frame=n,pose=fit.x.tolist(),target=uv,projected=pred(fit.x).tolist(),nozzle_rmse=float(np.sqrt(np.mean((pred(fit.x)[:2]-uv[:2])**2)))))
# Extend the observed path to the off-screen opening, preserving the original fin midpoint.
x0=np.array(rows[0]['pose']); x1=np.array(rows[1]['pose'])
early=x0-(x1-x0)*2
# Opening nozzles are outside the frame; constrain visible forward-fin midpoint only.
early[:3]=x0[:3]; early[3:]=x0[3:]+(x0[3:]-x1[3:])*2
q=Rotation.from_rotvec(early[:3]).apply(pts[2])+early[3:]
uv=project(q[None])[0];early[3]+=(151-uv[0])*(-q[2])/400;early[4]-=(181-uv[1])*(-q[2])/400
rows.insert(0,dict(source_frame=0,pose=early.tolist(),note='Opening extrapolated: nozzles outside frame; visible fin midpoint constrained.'))
t=np.array([r['source_frame'] for r in rows]);xs=np.array([r['pose'] for r in rows]);times=np.arange(192)/2
rot=RotationSpline(t,Rotation.from_rotvec(xs[:,:3]))(times)
trans=PchipInterpolator(t,xs[:,3:],extrapolate=True)(times)
(p/'pose-fit.json').write_text(json.dumps(dict(provenance='Manual interpretation of low-resolution reference; approximate model geometry; offscreen points inferred.',landmarks=rows,camera_world=d['camera_world'],poses=[dict(frame=i+1,rotation=q.tolist(),translation=v.tolist()) for i,(q,v) in enumerate(zip(rot.as_quat(),trans))]),indent=2))
print([(r['source_frame'],round(r.get('nozzle_rmse',0),2)) for r in rows])
