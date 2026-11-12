"""Verify user-requested mirrored repair wings in native and imported geometry."""
import hashlib,json
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[4]
FOLDER=ROOT/'sources/proposals/engineering-ships/achaean/repair'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def pairs():
    result=[]
    for stem in ['silver wing','wing boss','red boss inset','wing root']:
        result.append(('Achaean repair '+stem+' -1','Achaean repair '+stem+' 1'))
    for face in [-1,1]:
        result.append(('Achaean repair red wing field -1 '+str(face),'Achaean repair red wing field 1 '+str(-face)))
    return result

def mirrored_error(*,split_vertices=False):
    error=0
    for left,right in pairs():
        a=bpy.data.objects[left];b=bpy.data.objects[right]
        assert a.type==b.type=='MESH' and len(a.data.polygons)==len(b.data.polygons)
        # glTF can split coincident corners differently for UVs/normals. The actual
        # mirrored surface and triangle count must still match;native counts remain strict.
        if not split_vertices:assert len(a.data.vertices)==len(b.data.vertices)
        av=[a.matrix_world@v.co for v in a.data.vertices];bv=[b.matrix_world@v.co for v in b.data.vertices]
        ta=BVHTree.FromPolygons(av,[list(f.vertices) for f in a.data.polygons]);tb=BVHTree.FromPolygons(bv,[list(f.vertices) for f in b.data.polygons])
        error=max(error,max(tb.find_nearest(Vector((-v.x,v.y,v.z)))[3] for v in av),max(ta.find_nearest(Vector((-v.x,v.y,v.z)))[3] for v in bv))
    assert error<1e-5,('Repair wing mirror error',error)
    return error

def main():
    meta=json.loads((FOLDER/'model.json').read_text());results={};counts={}
    for kind in ['native','imported']:
        if kind=='native':bpy.ops.wm.open_mainfile(filepath=str(FOLDER/'model.blend'),load_ui=False,use_scripts=False)
        else:
            bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(FOLDER/'model.glb'))
        results[kind]={}
        for frame in [1,25,49,73,97]:
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();results[kind][str(frame)]=mirrored_error(split_vertices=kind=='imported')
        counts[kind]={left:[len(bpy.data.objects[left].data.vertices),len(bpy.data.objects[right].data.vertices)] for left,right in pairs()}
        # Negative control on actual loaded geometry: a displaced wing vertex must fail.
        obj=bpy.data.objects['Achaean repair silver wing -1'];obj.data.vertices[0].co.x-=.20;bpy.context.view_layer.update()
        rejected=False
        try:mirrored_error(split_vertices=kind=='imported')
        except AssertionError:rejected=True
        assert rejected,'Symmetry verifier accepted a distorted wing'
    report=dict(issue=265,binaries=meta['binaries'],verifier_sha256=sha(Path(__file__)),mirrored_pairs=pairs(),maximum_surface_errors=results,corner_vertex_counts=counts,import_vertex_split_policy='Allow differing glTF corner splits only;equal triangle counts and bidirectional mirrored surfaces remain required. Native vertex counts stay equal.',distorted_wing_rejected=True,scope='Fixed wings,roots and bosses only;ventral articulated service tool is intentionally asymmetric. User correction overrides the selected concept asymmetric arches.')
    (FOLDER/'wing-symmetry-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print('ACHAEAN_WING_SYMMETRY_OK',json.dumps(results))

if __name__=='__main__':main()
