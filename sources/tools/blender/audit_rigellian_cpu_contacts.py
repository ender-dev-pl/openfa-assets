"""Audit RI01 component contacts with evaluated world-space surface samples.

Nearest-surface signed distances are a diagnostic, not a proof of complete
solid intersection: edge-only intersections can escape vertex/face sampling.
"""
import json
import sys
from pathlib import Path

import bpy
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from verify_rigellian_cpu import ROOT


def audit():
    graph=bpy.context.evaluated_depsgraph_get();records={}
    bpy.context.view_layer.update()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH': continue
        evaluated=obj.evaluated_get(graph);mesh=evaluated.to_mesh()
        try:
            vertices=[evaluated.matrix_world @ v.co for v in mesh.vertices]
            faces=[tuple(p.vertices) for p in mesh.polygons]
            samples=vertices+[evaluated.matrix_world @ p.center for p in mesh.polygons]
            records[obj.name]=(BVHTree.FromPolygons(vertices,faces),samples,
                [min(v[a] for v in vertices) for a in range(3)]+[max(v[a] for v in vertices) for a in range(3)])
        finally: evaluated.to_mesh_clear()
    links=[];adjacency={name:set() for name in records}
    for i,a in enumerate(records):
        tree_a,samples_a,bounds_a=records[a]
        for b in list(records)[i+1:]:
            tree_b,samples_b,bounds_b=records[b]
            if any(bounds_a[k]>bounds_b[k+3]+.0001 or bounds_b[k]>bounds_a[k+3]+.0001 for k in range(3)): continue
            distance=None
            for tree,samples in [(tree_a,samples_b),(tree_b,samples_a)]:
                for sample in samples:
                    point,normal,_,separation=tree.find_nearest(sample)
                    if point is None: continue
                    if separation<=.0001 or (sample-point).dot(normal)<-.00001:
                        distance=separation;break
                if distance is not None: break
            if distance is not None:
                adjacency[a].add(b);adjacency[b].add(a);links.append([a,b])
    remaining=set(records);components=[]
    while remaining:
        stack=[min(remaining)];component=set()
        while stack:
            name=stack.pop()
            if name in component: continue
            component.add(name);stack.extend(adjacency[name]-component)
        remaining-=component;components.append(sorted(component))
    return dict(method='Evaluated vertex/face-centre nearest-surface signed-distance diagnostic; not exhaustive solid intersection proof',
        tolerance=.0001,links=links,components=sorted(components,key=len,reverse=True),
        isolated=[name for name,neighbors in adjacency.items() if not neighbors])


def main():
    reports={}
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'model.blend'));reports['native']=audit()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/'model.glb'));reports['glb']=audit()
    meta=json.loads((ROOT/'model.json').read_text())
    published=dict(revision=meta['revision'],blend_sha256=meta['blend_sha256'],glb_sha256=meta['glb_sha256'],
        diagnostic=reports,exhaustive_solid_contact_proof=False,final_visual_acceptance=False)
    (ROOT/'contact-review.json').write_text(json.dumps(published,indent=2)+'\n')
    out=ROOT.parents[5]/'artifacts/rigellian-cpu-reference-study/contact-audit.json'
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(reports,indent=2)+'\n')
    for kind,report in reports.items():
        print('CPU_CONTACT_AUDIT',kind,'component sizes',[len(c) for c in report['components']],
              'isolated',report['isolated'],flush=True)
    assert all(len(report['components'])==1 for report in reports.values()),'Disconnected structural assembly'


if __name__=='__main__': main()
