"""Scene definitions are added in chronological, committed milestones. Basic pass only."""
import blockout_tools as T
from mathutils import Vector
import math

def transmissions(info):
 if info['id'].startswith('E'):T.signal(info);return
 s=T.SCENE;c=T.camera((3,-11,2.9),(0,0,4.5),42);T.background('red');T.light('cool face key',(-4,-4,8),700,(.38,.45,.64));T.light('red rim',(4,2,7),950,(.6,.12,.16));a=T.human('broadcast officer',uniform=(.045,.065,.063),skin=(.23,.22,.28));T.talk(a,448,604)
 for n,z in [(448,-.20),(510,.10),(555,-.09),(604,.08)]:T.key(a['head'],'rotation_euler',n,(0,.03,z))
 for n,loc,target in [(448,(3,-11,2.9),(0,0,4.5)),(554,(3,-11,2.9),(0,0,4.5)),(555,(2,-7.3,4.0),(0,0,5.15)),(604,(2,-7.3,4.0),(0,0,5.15))]:
  T.key(c,'location',n,loc);T.key(c,'rotation_euler',n,(Vector(target)-Vector(loc)).to_track_quat('-Z','Y').to_euler())
 for fc in c.animation_data.action.fcurves:
  for k in fc.keyframe_points:k.interpolation='CONSTANT'

BUILDERS={'transmissions':transmissions}
