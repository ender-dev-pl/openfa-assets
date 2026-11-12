"""Build every required state of distinct, editable culture/footprint scaffold kits."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_openfa_assets import setup_scene
from build_refined_terran import save_blend_to,render_to
from build_refined_rigellian_scaffold import export_glb_to
from catalogue_rendering import evaluated_points,fit_camera
from culture_scaffold_parts import Kit,STYLES,empty,surface
from culture_scaffold_contract import chain,recipe,phases,definitions_for

REPO=Path(__file__).resolve().parents[2]
ROOT=REPO/'docs/assets/reconstruction/scaffolds/culture-kits'
LIMITS_PATH=REPO/'docs/reconstruction/models/scaffold-stage-limits.json'
REFERENCE_PATH=REPO/'docs/reconstruction/models/shared-construction-references.json'
CULTURE_PATH=REPO/'docs/reconstruction/models/cultural-architecture-index.json'
LIMITS=json.loads(LIMITS_PATH.read_text())
REFERENCES=json.loads(REFERENCE_PATH.read_text())
FAMILIES=[f for f in LIMITS['families'] if f['max_required_stage'] and f['family']!='RIS2']


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def family_recipe(family):
    return recipe(family,REFERENCES)


def build_family(family,preview=False):
    reference,capacity,size,pitch=family_recipe(family)
    width=reference['descriptors'][-1]['size'][0]
    culture=reference['culture'];key=family['family']
    stages=[min(capacity,family['max_required_stage'])] if preview else range(1,family['max_required_stage']+1)
    destination=ROOT/('previews' if preview else 'families')/key
    destination.mkdir(parents=True,exist_ok=True)
    cases=[]
    for stage in stages:
        print('CULTURE_BUILD',key,stage,'/',family['max_required_stage'],flush=True)
        scene=setup_scene(512,24)
        scene.render.threads_mode='FIXED';scene.render.threads=8
        root=empty('PlacementRoot')
        root['family']=key;root['culture']=culture
        root['footprint_width']=root['footprint_height']=size
        root['construction_stage']=stage;root['physical_pitch_calibrated']=False
        root['construction_sequence']='erection-reveal-dismantling-complete'
        kit=Kit(culture,size,pitch,capacity,surface(culture,'main',ROOT/'textures'),surface(culture,'trim',ROOT/'textures'))
        kit.footing(root)
        frames=chain(stage,capacity)
        for level,frame in enumerate(frames): kit.tier(root,level,frame)
        kit.crown(root,stage)
        unique=kit.finish()
        bpy.context.view_layer.update()
        folder=destination/f'stage-{stage:02}';folder.mkdir(parents=True,exist_ok=True)
        points=evaluated_points(kit.objects)
        fit_camera(scene,points,(10,-10,10))
        render_to(scene,folder/'front-quarter.png')
        boundaries={1,capacity,capacity+1,family['max_required_stage']-1,family['max_required_stage']}
        rear=stage in boundaries or preview
        if rear:
            fit_camera(scene,points,(-10,10,10));render_to(scene,folder/'rear-quarter.png')
        fit_camera(scene,points,(10,-10,10))
        bpy.ops.object.select_all(action='DESELECT')
        for obj in scene.objects:
            if obj.type in ['MESH','EMPTY']:obj.select_set(True)
        bpy.context.view_layer.objects.active=root
        export_glb_to(folder/'model.glb');save_blend_to(folder/'model.blend')
        cases.append(dict(stage=stage,frames=frames,mesh_objects=len(kit.objects),unique_meshes=unique,
                          blend_sha256=sha(folder/'model.blend'),glb_sha256=sha(folder/'model.glb'),rear_view=rear,
                          hide_on_reveal=[o.name for o in kit.objects if not o['reveal_visible']]))
    definitions=definitions_for(key,LIMITS)
    culture_evidence=json.loads(CULTURE_PATH.read_text())
    article=next((c for c in culture_evidence['cultures'] if c['culture']==culture),None)
    manifest=dict(issue=188,family=key,culture=culture,footprint=size,capacity=capacity,pitch=pitch,
                  pitch_status='Provisional source-repeat projection; not calibrated game-world height',
                  pitch_derivation=f'{capacity}*4/{width}*({size}*.9*sqrt(2))/sqrt(2/3)',
                  required_max_stage=family['max_required_stage'],required_max_tiers=family['max_required_tiers'],
                  style=STYLES[culture],cdb_evidence=article or culture_evidence['not_located'][0],
                  authored_interpretation='OpenFA3D removable perimeter kit; mechanisms, joints, hidden structure and materials are authored interpretations, not recovered CDB technology',
                  source_reference=key,reference_descriptor_sha256=[d['png_sha256'] for d in reference['descriptors']] if 'png_sha256' in reference['descriptors'][0] else reference['source_sha256'],
                  clear_volume=dict(half_extent_xy=size*.45-.10,temporary_crown_removed_on_reveal=True,interior_shoring=False),
                  phases=phases(),
                  sequence_provenance='User requirement: full height, insert building, reverse dismantling revealing from top; not a newly recovered legacy timing rule',
                  definitions=definitions,cases=cases,
                  inputs={str(p.relative_to(REPO)).replace('\\','/'):sha(p) for p in [LIMITS_PATH,REFERENCE_PATH,CULTURE_PATH,ROOT/'authored-wear.json',Path(__file__),Path(__file__).with_name('culture_scaffold_parts.py'),Path(__file__).with_name('culture_scaffold_contract.py')]},
                  preview_only=preview,exact_legacy_fidelity_accepted=False,game_integration_verified=False)
    (destination/'model.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return dict(family=key,culture=culture,manifest=str((destination/'model.json').relative_to(ROOT)),sha256=sha(destination/'model.json'),stages=len(cases))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--preview',action='store_true');parser.add_argument('--families',nargs='*')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    families=[f for f in FAMILIES if not args.families or f['family'] in args.families]
    records=[build_family(f,args.preview) for f in families]
    if not args.preview and not args.families:
        (ROOT/'index.json').write_text(json.dumps(dict(issue=188,families=records,existing_ris2='../rigellian/size-2-refined/model.json',definition_count=sum(1 for r in LIMITS['records'] if r['family']!='RIS2'),required_new_states=sum(r['stages'] for r in records)),indent=2)+'\n')
    print('CULTURE_SCAFFOLDS_BUILT',len(records),sum(r['stages'] for r in records),flush=True)


if __name__=='__main__':main()
