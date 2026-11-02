"""Independent PB21 source/GLB geometry, materials, silhouette and render checks."""
import hashlib
import json
import sys
from pathlib import Path

import bpy
from mathutils import Vector
from mathutils.kdtree import KDTree
from mathutils.bvhtree import BVHTree

sys.path.insert(0,str(Path(__file__).resolve().parent))
from refine_seismic_penetrator import ROOT, OUTPUT, MEDIA, VIEWS, configure_camera, roof_z


def snapshot():
    result={}
    deps=bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH':continue
        evaluated=obj.evaluated_get(deps);mesh=evaluated.to_mesh()
        points=sorted(set(tuple(round(v,5) for v in evaluated.matrix_world@vertex.co) for vertex in mesh.vertices))
        result[obj.name]=dict(points=points,materials=[m.name for m in mesh.materials],bounds=[min(p[i] for p in points) for i in range(3)]+[max(p[i] for p in points) for i in range(3)])
        evaluated.to_mesh_clear()
    return result


def verify_form(state):
    assert 'Rounded compound roof and nose' in state
    bell=state['Rounded internal survey machine bell']
    assert all(p[2]<=roof_z(p[0],p[1])-.155 for p in bell['points']), 'Machine bell penetrates the roof'
    braces=[item for name,item in state.items() if 'diamond brace' in name]
    assert len(braces)>=30, 'Missing open rear/side structure'
    assert all(.08<=item['bounds'][2] and item['bounds'][5]<=.60 for item in braces), 'Lattice escaped its frame'
    small=state['Hatch 0 shallow domed lid']['bounds'];large=state['Hatch 1 shallow domed lid']['bounds']
    assert (large[3]-large[0])/(small[3]-small[0])>1.25, 'Unequal hatch silhouette lost'
    all_points=[p for item in state.values() for p in item['points']]
    bounds=[min(p[i] for p in all_points) for i in range(3)]+[max(p[i] for p in all_points) for i in range(3)]
    assert bounds[2]>=-.001 and bounds[5]<1.43, ('Unexpected tall silhouette',bounds)
    assert bounds[4]-bounds[1]>bounds[3]-bounds[0], 'Rounded fore/aft footprint lost'
    # Test the evaluated skin itself. Three collinear longitudinal samples on
    # the former flat ramp would have almost zero deviation from their chord.
    roof=bpy.data.objects['Rounded compound roof and nose']
    evaluated=roof.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh()
    tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in data.vertices],[list(p.vertices) for p in data.polygons],all_triangles=False)
    sections=[]
    for x in [-.50,0,.50]:
        heights=[]
        for y in [-.30,-.80,-1.30]:
            hit,_,_,_=tree.ray_cast(Vector((x,y,3)),Vector((0,0,-1)),5)
            assert hit is not None,('Missing nose skin',x,y)
            heights.append(hit.z)
        deviation=heights[1]-(heights[0]+heights[2])/2
        assert deviation>.055,('Nose has regressed to a planar slope',x,heights,deviation)
        sections.append(dict(x=x,ys=[-.30,-.80,-1.30],surface_heights=heights,chord_deviation=deviation))
    evaluated.to_mesh_clear()
    axis=bpy.data.objects.get('Shared drill axis')
    assert axis is not None,'Missing common drill assembly axis'
    assert not any(name.startswith('Nose shell standoff') for name in state),'Separate nose supports create a false offset drill axis'
    origin=axis.matrix_world.translation
    parts=['Front geophysical probe shaft','Probe guide collar','Internal precision drill head','Probe fork bridge']
    errors=[]
    for name in parts:
        bound=state[name]['bounds'];centre=Vector(((bound[0]+bound[3])/2,(bound[1]+bound[4])/2,0))
        errors.append((centre-Vector((origin.x,origin.y,0))).length)
        assert bpy.data.objects[name].parent==axis,(name,'Detached from the common drill axis')
    tines=[name for name in state if name.startswith('Pale probe fork tine')]
    assert len(tines)==2 and all(bpy.data.objects[name].parent==axis for name in tines)
    tine_centres=[Vector(((state[name]['bounds'][0]+state[name]['bounds'][3])/2,(state[name]['bounds'][1]+state[name]['bounds'][4])/2,0)) for name in tines]
    errors.append(((tine_centres[0]+tine_centres[1])/2-Vector((origin.x,origin.y,0))).length)
    assert max(errors)<.0001,('Drill parts do not share a centreline',errors)
    shaft=state['Front geophysical probe shaft']['bounds'];collar=state['Probe guide collar']['bounds'];head=state['Internal precision drill head']['bounds']
    assert shaft[2]<head[5] and shaft[5]>collar[5], 'Drill shaft is not continuous from head through the roof collar'
    # Probe the actual lower drum's front wall: the centreline must pass through
    # its open sector, with solid material immediately beside that opening.
    drum=bpy.data.objects['Exposed grey violet drilling drum']
    evaluated=drum.evaluated_get(bpy.context.evaluated_depsgraph_get());data=evaluated.to_mesh()
    tree=BVHTree.FromPolygons([evaluated.matrix_world@v.co for v in data.vertices],[list(p.vertices) for p in data.polygons],all_triangles=False)
    front_hits=[]
    for offset in [-.20,0,.20]:
        hit,_,_,_=tree.ray_cast(Vector((origin.x+offset,-3,.26)),Vector((0,1,0)),5)
        assert hit is not None,('Missing lower drum surface',offset)
        front_hits.append(hit.y)
    evaluated.to_mesh_clear()
    assert front_hits[1]>max(front_hits[0],front_hits[2])+.5,('Drill axis does not align with drum opening',front_hits)
    return dict(bounds=bounds,diamond_braces=len(braces),hatch_diameter_ratio=(large[3]-large[0])/(small[3]-small[0]),bell_below_roof=True,convex_nose_sections=sections,
        common_drill_axis=dict(origin=list(origin),maximum_part_centre_error=max(errors),drum_front_ray_hits=front_hits,shared_parent=True,continuous_shaft=True,no_separate_nose_supports=True))


def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUTPUT/'model.blend'))
    scene=bpy.context.scene;native=snapshot();form=verify_form(native)
    textures={image.name for image in bpy.data.images if image.packed_file}
    assert len(textures)==3, ('Missing packed authored wear textures',textures)
    assert not any(o.animation_data for o in scene.objects),'Unrequested/inferred loop present'
    configure_camera(VIEWS['front-quarter'])
    for obj in list(scene.objects):
        if obj.type not in ['CAMERA','LIGHT']:bpy.data.objects.remove(obj,do_unlink=True)
    for data in list(bpy.data.meshes):
        if data.users==0:bpy.data.meshes.remove(data)
    for mat in list(bpy.data.materials):
        if mat.users==0:bpy.data.materials.remove(mat)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT/'model.glb'))
    imported=snapshot();verify_form(imported)
    assert native.keys()==imported.keys(),'GLB mesh names/populations differ'
    error=0
    for name in native:
        a=native[name];b=imported[name]
        assert len(a['points'])==len(b['points']),(name,'Evaluated positions differ')
        # Seam splitting and float32 transforms can reorder equal rounded X/Y
        # coordinates. Match actual positions, not an exporter-dependent order.
        for source,target in [(a['points'],b['points']),(b['points'],a['points'])]:
            tree=KDTree(len(target))
            for i,p in enumerate(target):tree.insert(p,i)
            tree.balance()
            error=max(error,max(tree.find(p)[2] for p in source))
        assert a['materials']==b['materials'],(name,'Material binding changed',a['materials'],b['materials'])
    assert error<.0001,('GLB geometry drift',error)
    for name,direction in [('imported-front-quarter',VIEWS['front-quarter']),('imported-rear-quarter',VIEWS['rear-quarter']),('imported-nose-profile',VIEWS['nose-profile'])]:
        configure_camera(direction);scene.render.filepath=str(MEDIA/(name+'.png'));bpy.ops.render.render(write_still=True)
    # A separate technical cutaway shows the probe and machine bell, not a
    # gameplay destruction state. The normal exported source remains complete.
    for obj in scene.objects:
        if obj.type=='MESH' and (obj.name.startswith(('Rounded compound roof','Upper shell edge skirt','Faded red roof','Pale nose roof','Roof fine','Edge abrasion'))):obj.hide_render=True
    configure_camera(VIEWS['front-quarter']);scene.render.filepath=str(MEDIA/'technical-cutaway.png');bpy.ops.render.render(write_still=True)
    report=dict(issue=181,id='terran:seismic-penetrator',blender=bpy.app.version_string,
        blend_sha256=hashlib.sha256((OUTPUT/'model.blend').read_bytes()).hexdigest(),
        glb_sha256=hashlib.sha256((OUTPUT/'model.glb').read_bytes()).hexdigest(),
        verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        source_mesh_count=len(native),imported_mesh_count=len(imported),maximum_position_error=error,
        matched_named_materials=True,packed_wear_textures=sorted(textures),form=form,
        reference='sources/docs/reconstruction/models/seismic-penetrator-reference.json',
        acceptance='Technical geometry/material checks and actual Blender renders; final artistic acceptance remains with the user')
    (MEDIA/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PB21_NATIVE_GLB_VALIDATED',len(native),error,flush=True)


if __name__=='__main__':main()
