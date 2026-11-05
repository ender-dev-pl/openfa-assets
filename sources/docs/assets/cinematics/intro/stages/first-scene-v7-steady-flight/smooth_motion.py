"""Smooth rotational motion on SO(3), damp secondary rocking, preserve rear-engine screen anchor."""
from pathlib import Path
import json,numpy as np
from scipy.spatial.transform import Rotation
from scipy.interpolate import make_smoothing_spline
p=Path(__file__).resolve().parent;source=json.loads((p/'input-poses.json').read_text());a={'camera_world':source['camera_world']};rows=source['poses'];t=np.arange(302)/24;u=t/t[-1];r=Rotation.from_quat([x['rotation'] for x in rows]);rv=(r[0].inv()*r).as_rotvec();axis=rv[-1]/np.linalg.norm(rv[-1]);main=rv@axis;secondary=rv-main[:,None]*axis
trend=make_smoothing_spline(t,main,lam=10)(t);trend-=(1-u)*(trend[0]-main[0])+u*(trend[-1]-main[-1])
side=np.column_stack([make_smoothing_spline(t,secondary[:,i],lam=10)(t) for i in range(3)])*.3;side-=(1-u[:,None])*side[0]+u[:,None]*side[-1]
new=r[0]*Rotation.from_rotvec(trend[:,None]*axis+side);oldT=np.array([x['translation'] for x in rows]);newT=oldT.copy();points=np.array([[-1.35,-2.78,0],[1.35,-2.78,0]])*.78
anchors=[]
for i in range(302):
 q=r[i].apply(points)+oldT[i];target=np.mean(q[:,:2]/-q[:,2,None],axis=0);rot=new[i].apply(points);z=rot[:,2]+oldT[i,2];inv=1/-z
 newT[i,:2]=(target-np.mean(rot[:,:2]*inv[:,None],axis=0))/np.mean(inv)
 q2=new[i].apply(points)+newT[i];anchors.append(float(np.max(np.abs(np.mean(q2[:,:2]/-q2[:,2,None],axis=0)-target)))*400)
def dynamics(R):
 v=(R[:-1].inv()*R[1:]).as_rotvec()*24;acc=np.diff(v,axis=0)*24
 return dict(max_angular_speed_degrees_per_second=float(np.linalg.norm(v,axis=1).max()*180/np.pi),max_angular_acceleration_degrees_per_second_squared=float(np.linalg.norm(acc,axis=1).max()*180/np.pi),rms_angular_acceleration=float(np.sqrt(np.mean(np.sum(acc*acc,axis=1)))*180/np.pi))
report=dict(method='SO(3) logarithm smoothing, acceleration regularization lambda 10, secondary-axis amplitude 0.3, endpoint correction; kinematic animation, not force/torque simulation.',before=dynamics(r),after=dynamics(new),secondary_axis_peak_before_degrees=float(np.linalg.norm(secondary,axis=1).max()*180/np.pi),secondary_axis_peak_after_degrees=float(np.linalg.norm(side,axis=1).max()*180/np.pi),max_nozzle_midpoint_screen_error_original_pixels=max(anchors),max_pose_difference_degrees=float((r.inv()*new).magnitude().max()*180/np.pi),original_translation_depth_unchanged=True,endpoint_orientation_error_degrees=[float((r[i].inv()*new[i]).magnitude()*180/np.pi) for i in [0,-1]])
assert max(anchors)<1e-8 and report['after']['max_angular_acceleration_degrees_per_second_squared']<5
(p/'motion-verification.json').write_text(json.dumps(report,indent=2)+'\n');(p/'steady-poses.json').write_text(json.dumps(dict(camera_world=a['camera_world'],poses=[dict(frame=i+1,rotation=q.tolist(),translation=v.tolist()) for i,(q,v) in enumerate(zip(new.as_quat(),newT))]),indent=2)+'\n');print(json.dumps(report,indent=2))
