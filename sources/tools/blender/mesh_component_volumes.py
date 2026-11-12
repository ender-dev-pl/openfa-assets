"""Check closed, consistently wound, positive-volume mesh components."""
import bmesh


def component_volumes(obj):
    bm=bmesh.new();bm.from_mesh(obj.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=1e-6)
    assert all(e.is_manifold and e.is_contiguous for e in bm.edges),(obj.name,'Open/inconsistent physical surface')
    remaining=set(bm.verts);volumes=[]
    while remaining:
        seed=next(iter(remaining));region=set();queue=[seed]
        while queue:
            v=queue.pop()
            if v in region:continue
            region.add(v);queue += [e.other_vert(v) for e in v.link_edges if e.other_vert(v) not in region]
        remaining-=region;faces={f for v in region for f in v.link_faces};volume=0
        for f in faces:
            verts=[v.co for v in f.verts]
            volume+=sum(verts[0].dot(verts[i].cross(verts[i+1]))/6 for i in range(1,len(verts)-1))
        assert volume>1e-11,(obj.name,'Nonpositive component',volume);volumes.append(volume)
    bm.free();return volumes

