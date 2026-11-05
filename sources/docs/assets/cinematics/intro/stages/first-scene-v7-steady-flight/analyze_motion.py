from pathlib import Path
import json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.interpolate import make_smoothing_spline
p=Path(__file__).resolve().parent;root=p.parent;a=json.loads((root/'first-scene-v4-ship-fit/pose-fit.json').read_text());b=json.loads((root/'first-scene-v5-to-frame-150/extension-poses.json').read_text());rows=a['poses']+b['poses'];t=np.arange(302)/24;r=Rotation.from_quat([x['rotation'] for x in rows]);rv=(r[0].inv()*r).as_rotvec();axis=rv[-1]/np.linalg.norm(rv[-1]);main=rv@axis;secondary=rv-main[:,None]*axis
for lam in [1,10,50,200]:
 trend=make_smoothing_spline(t,main,lam=lam)(t)
 side=np.column_stack([make_smoothing_spline(t,secondary[:,i],lam=lam)(t) for i in range(3)])*.3
 new=trend[:,None]*axis+side
 R=r[0]*Rotation.from_rotvec(new);v=(R[:-1].inv()*R[1:]).as_rotvec()*24;acc=np.diff(v,axis=0)*24;deviation=(r.inv()*R).magnitude()*180/np.pi
 print(lam,'speed',np.linalg.norm(v,axis=1).max()*180/np.pi,'accel',np.linalg.norm(acc,axis=1).max()*180/np.pi,'dev',deviation.max(), 'progress',np.round(trend[[0,48,96,144,192,240,300]]*180/np.pi,2))
