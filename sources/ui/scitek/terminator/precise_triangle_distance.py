"""Double precision nearest point for thin bevel triangles; no float32 BVH query."""
import math
def sub(a,b):return tuple(float(x)-float(y) for x,y in zip(a,b))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def weights(p,a,b,c):
 u=sub(b,a);v=sub(c,a);w=sub(p,a);aa=dot(u,u);bb=dot(u,v);cc=dot(v,v);den=aa*cc-bb*bb
 if abs(den)<1e-30:return None
 x=(cc*dot(w,u)-bb*dot(w,v))/den;y=(aa*dot(w,v)-bb*dot(w,u))/den;return 1-x-y,x,y
def nearest(p,vertices,triangles):
 best=float('inf');which=None
 for index,triangle in enumerate(triangles):
  a,b,c=[vertices[i] for i in triangle];w=weights(p,a,b,c)
  if w is not None and min(w)>=-1e-10:
   q=tuple(sum(float(v[i])*t for v,t in zip((a,b,c),w)) for i in range(3));d=dot(sub(p,q),sub(p,q))
  else:
   d=float('inf')
   for x,y in [(a,b),(b,c),(c,a)]:
    edge=sub(y,x);den=dot(edge,edge);t=max(0,min(1,dot(sub(p,x),edge)/den)) if den else 0;q=tuple(float(x[i])+t*edge[i] for i in range(3));d=min(d,dot(sub(p,q),sub(p,q)))
  if d<best:best=d;which=index
 return which,math.sqrt(best)
def interpolate(p,a,b,c,ta,tb,tc):
 w=weights(p,a,b,c);assert w is not None
 return tuple(sum(float(v[i])*t for v,t in zip((ta,tb,tc),w)) for i in range(2))
