"""Read-only Blender inspection of the seven description-driven corrections."""
import argparse,hashlib,json,sys
from pathlib import Path
import bpy
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--repo',type=Path,required=True)
a=ap.parse_args(sys.argv[sys.argv.index('--')+1:])
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for n in [16,18,19,20,21,45,53]:
    ident=f'TI{n:03d}';native=a.repo/f'sources/docs/assets/reconstruction/trading-goods-refined/{ident}/lore/{ident}.blend'
    before=sha(native);bpy.ops.wm.open_mainfile(filepath=str(native));objects=[o for o in bpy.context.scene.objects if o.type in {'MESH','CURVE','FONT'}]
    names=[o.name for o in objects];used={m for o in objects for m in o.data.materials};materials=sorted(m.name for m in used)
    row=dict(legacy_stem=ident,native=native.relative_to(a.repo).as_posix(),native_sha256=before,material_names=materials)
    if n==16:
        assert sum('unfaceted raw opal' in name for name in names)==2
        assert all('metachrome' in m.name or 'raw opal' in m.name for m in used)
        row.update(raw_opals=2,introduced_diamonds=0)
    elif n==18:
        gem=next(o for o in objects if 'square emerald' in o.name);coords=[v.co for v in gem.data.vertices]
        dx=max(v.x for v in coords)-min(v.x for v in coords);dy=max(v.y for v in coords)-min(v.y for v in coords)
        assert abs(dx-dy)<1e-6 and len({round(v.z,5) for v in coords})==7
        assert all('white gold' in m.name or 'emerald' in m.name for m in used)
        row.update(square_xy_extents=[dx,dy],step_cut_rings=7)
    elif n==19:
        gem=next(o for o in objects if 'rounded unfaceted cabochon' in o.name)
        assert all(p.use_smooth for p in gem.data.polygons) and len(gem.data.vertices)>2000
        assert any('red gold' in m.name for m in used) and any('copper' in m.name for m in used)
        row.update(cabochon_smooth_shading=True,cabochon_vertices=len(gem.data.vertices))
    elif n==20:
        assert sum('individual astramarine ' in name for name in names)==23
        assert sum('white gold bezel' in name for name in names)==23
        assert sum('necklace link' in name for name in names)==22
        for o in objects:
            if 'necklace link' in o.name:assert all('titanium' in m.name for m in o.data.materials)
        row.update(astramarines=23,white_gold_bezels=23,titanium_links=22)
    elif n==21:
        assert sum('inset ultropaz' in name for name in names)==4 and sum('inset alexandrite' in name for name in names)==4
        assert not any('pearl' in m.name or 'astramarine' in m.name for m in used)
        row.update(ultropaz=4,alexandrite=4,colour_change_verified=False)
    elif n==45:
        assert not any('undissolved pearl' in name for name in names)
        liquid=next(o for o in objects if 'brandy fill /' in o.name)
        assert abs(liquid.data.materials[0].node_tree.nodes['Principled BSDF'].inputs['IOR'].default_value-1.36)<1e-5
        assert any('hollow glass /' in name for name in names)
        row.update(intact_pearl_objects=0,separate_liquid_mesh=True,hollow_glass_mesh=True)
    else:
        mansions=[o for o in objects if 'mansion_kind' in o]
        truth=sum(o['mansion_kind']=='truth' for o in mansions);deceit=sum(o['mansion_kind']=='deceit' for o in mansions)
        goals=[o for o in mansions if o.get('ultimate_truth')]
        assert len(mansions)==20 and truth==deceit==10 and len(goals)==1
        assert goals[0]['mansion_kind']=='truth' and goals[0]['board_tier']==max(o['board_tier'] for o in mansions)==5
        tokens=[o for o in bpy.context.scene.objects if 'illustrative_role' in o]
        assert len(tokens)==4 and sum('board support column' in name for name in names)==4
        row.update(mansion_locations=20,truth=truth,deceit=deceit,board_tiers=6,highest_goal='ultimate truth',illustrative_character_roles=[o['illustrative_role'] for o in tokens])
    assert sha(native)==before;rows.append(row)
report=dict(count=7,inspector='sources/tools/trading-goods/refining/verify_lore_geometry.py',inspector_sha256=sha(Path(__file__)),scope='Actual read-only Blender geometry/material inspection; semantic and visual judgements remain manual.',items=rows)
(a.repo/'docs/trading-goods/lore-corrections-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('LORE_GEOMETRY_VERIFIED',len(rows),'native files; independent GLB/render checks are recorded separately',flush=True)
