"""RI06 retained roof wells, supports, maps and refined crown contract."""
import math
import bpy
import bmesh
from mathutils import Vector
from verify_rigellian_bunker import ray, LEVELS, DENTS, WELL, MAST_OFFSET, disc_profile, radius, audit, geometry_bounds, texture_evidence
from verify_rigellian_crowns import form

def retained_body_structure(meshes):
    bpy.context.view_layer.update();root=bpy.data.objects['PlacementRoot']
    assert all(obj.parent==root for obj in meshes)
    assert root.location.length<1e-6 and root.rotation_euler.to_matrix().is_identity and all(abs(v-1)<1e-6 for v in root.scale)
    for index,start in enumerate(LEVELS):
        disc=bpy.data.objects[f'RI06 broad saucer level {index}']
        floor=ray(disc,(*WELL,6),(0,0,-1));surround=ray(disc,(WELL[0]+.32,WELL[1],6),(0,0,-1))
        assert floor is not None and surround is not None and surround.z-floor.z>.20,'Well must cut actual roof'
        sleeve=bpy.data.objects[f'RI06 level {index} embedded well sleeve'];insert=bpy.data.objects[f'RI06 level {index} recessed well floor']
        assert ray(sleeve,(*WELL,6),(0,0,-1)) is None
        bottom=ray(insert,(*WELL,-1),(0,0,1));top=ray(insert,(*WELL,6),(0,0,-1))
        assert bottom.z<floor.z<top.z,'Floor must embed into roof well bottom'
        wall=ray(disc,(*WELL,start+.30),(1,0,0));outside=ray(sleeve,(1,WELL[1],start+.30),(-1,0,0))
        assert outside.x>wall.x,'Sleeve must meet actual bore wall'
        inside=ray(sleeve,(*WELL,start+.18),(1,0,0));edge=ray(insert,(1,WELL[1],start+.18),(-1,0,0))
        assert edge.x>inside.x,'Floor must meet sleeve'
        fins=[obj for obj in meshes if obj.name.startswith(f'RI06 level {index} well cooling fin')];assert len(fins)==2
        for fin in fins:
            x,y,_=fin.matrix_world.translation
            assert ray(fin,(x,y,-1),(0,0,1)).z<ray(insert,(x,y,6),(0,0,-1)).z
        phi,z,depth=DENTS[index];normal=Vector((math.cos(phi),math.sin(phi),0));point=ray(disc,normal*2+Vector((0,0,z)),-normal)
        assert depth*.75<radius(disc_profile(start),z)-math.hypot(point.x,point.y)<depth*1.3
        for n,phi in enumerate([-math.pi/2,-.30]):
            suffix='' if n==0 else '.001';normal=Vector((math.cos(phi),math.sin(phi),0));axis=Vector((0,0,start+.23))
            bezel=bpy.data.objects[f'RI06 level {index} rim fitting bezel'+suffix]
            face=bpy.data.objects[f'RI06 level {index} square brass rim face'+suffix]
            back=ray(bezel,axis,normal);front=ray(bezel,axis+normal*2,-normal);skin=ray(disc,axis+normal*2,-normal)
            gold_back=ray(face,axis,normal);gold_front=ray(face,axis+normal*2,-normal)
            assert back.dot(normal)<skin.dot(normal)<front.dot(normal)
            assert gold_back.dot(normal)<front.dot(normal)<gold_front.dot(normal)
    column=bpy.data.objects['RI06 solid interlevel structural column']
    for index in range(3):
        disc=bpy.data.objects[f'RI06 broad saucer level {index}']
        assert ray(column,(0,0,-1),(0,0,1)).z<ray(disc,(0,0,6),(0,0,-1)).z
        assert ray(column,(0,0,6),(0,0,-1)).z>ray(disc,(0,0,-1),(0,0,1)).z
    neck=bpy.data.objects['RI06 solid exposed brass mast neck'];mast=bpy.data.objects['RI06 tapered upper mast'];roof=bpy.data.objects['RI06 broad saucer level 2']
    assert ray(neck,(0,0,-1),(0,0,1)).z<ray(roof,(0,0,6),(0,0,-1)).z
    assert ray(neck,(0,0,6),(0,0,-1)).z>ray(mast,(0,0,-1),(0,0,1)).z
    for i,strut in enumerate(sorted([obj for obj in meshes if obj.name.startswith('RI06 pale neck retaining strut')],key=lambda obj:obj.name)):
        phi=math.pi/4+i*math.pi/2;normal=Vector((math.cos(phi),math.sin(phi),0));axis=Vector((0,0,2.66+MAST_OFFSET))
        back=ray(strut,axis,normal);front=ray(strut,axis+normal,-normal);skin=ray(mast,axis+normal,-normal)
        assert back.dot(normal)<skin.dot(normal)<front.dot(normal)
    stem=bpy.data.objects['RI06 crown solid mounting stem'];bowl=bpy.data.objects['RI06 crown compact fork bowl']
    assert ray(stem,(0,0,-1),(0,0,1)).z<ray(mast,(0,0,6),(0,0,-1)).z
    assert ray(bowl,(0,0,-1),(0,0,1)).z<ray(stem,(0,0,6),(0,0,-1)).z
    assert ray(bpy.data.objects['RI06 crown central terminal'],(0,0,6),(0,0,-1)).z>4.75+MAST_OFFSET
    contact=audit();assert len(contact['components'])==1,contact['isolated']
    bounds=geometry_bounds(meshes);assert min(bounds[:2])>=-1.5 and max(bounds[3:5])<=1.5 and abs(bounds[2])<.001
    assert not any(obj.animation_data for obj in meshes)
    return bounds,contact


def structure():
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    for obj in meshes:
        bm = bmesh.new()
        try:
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-6)
            assert all(edge.is_manifold for edge in bm.edges), obj.name
            assert bm.calc_volume(signed=True) > 0, obj.name
        finally:
            bm.free()
    bounds, contacts = retained_body_structure(meshes)
    crown = form('ri06')
    textures = texture_evidence(meshes)
    return dict(positive_closed_meshes=len(meshes), body_bounds=bounds,
                one_sampled_contact_component=len(contacts['components']) == 1,
                three_roof_wells_and_seated_sleeves_floors_fins=True, three_dents_and_six_rim_fittings=True,
                crown=crown, texture_pixels_and_uvs=textures,
                contact_scope='Existing sampled nearest-surface contact graph; not exhaustive structural intersection proof.')
