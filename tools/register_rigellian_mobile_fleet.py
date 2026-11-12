"""Register one canonical model per mobile Rigellian type and preserve history.

Only exact superseded tracked payloads whose committed original bytes have been
verified are retired. Editable variants remain recoverable from an immutable Git
commit; their metadata/media remain in the checkout. No directory is removed.
"""
from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
PRESERVED_COMMIT='489d518a4363254a92b6538e4d7ced44aebf9efc'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def preserve(item):
    """Fail closed: no edited/uncommitted model may be retired as a duplicate."""
    spec=PRESERVED_COMMIT+':'+item['path']
    original=subprocess.check_output(['git','show',spec],cwd=ROOT)
    assert hashlib.sha256(original).hexdigest()==item['sha256'],('Historical bytes differ; preserve variant before retirement',item['path'])
    assert len(original)==item['bytes']
    blob=subprocess.check_output(['git','rev-parse',spec],cwd=ROOT).decode().strip()
    item['preserved_commit']=PRESERVED_COMMIT
    item['preserved_blob']=blob
    item['recovery_url']='https://github.com/ender-dev-pl/openfa-assets/blob/'+PRESERVED_COMMIT+'/'+item['path']
    item['committed_bytes_verified_before_retirement']=True
    return item


def write_json(path,data):
    old=path.read_bytes() if path.exists() else b''
    text=json.dumps(data,indent=2,ensure_ascii=False)+'\n'
    path.write_bytes(text.replace('\n','\r\n').encode() if b'\r\n' in old else text.encode())


def board(style):
    image=Image.new('RGB',(1400,1130),(15,22,27));draw=ImageDraw.Draw(image)
    font=ImageFont.load_default(size=21);small=ImageFont.load_default(size=16)
    for i,ship in enumerate(style['ships']):
        x=(i%2)*700;y=(i//2)*550
        source=Image.open(ROOT/'gallery/media/objects/rigellian'/ship['slug']/'verified-native.png').convert('RGBA')
        source.thumbnail((680,500));image.paste(source,(x+(700-source.width)//2,y+35),source)
        draw.text((x+20,y+8),ship['name']+' | '+str(ship['proposed_world_size'])+' proposed world units',font=font,fill='#DCE7E4')
    draw.text((20,1100),'Individual views fit separately. Use shared-scale-top / shared-scale-oblique for relative sizes.',font=small,fill='#AFBFBE')
    image.save(ROOT/'gallery/media/objects/rigellian/fleet/review.jpg',quality=92)


def main():
    style=json.loads((ROOT/'sources/objects/rigellian/fleet-style.json').read_text(encoding='utf-8'))
    path=ROOT/'sources/docs/reconstruction/models/inventory.json';inventory=json.loads(path.read_text(encoding='utf-8'))
    layout_path=ROOT/'project/layout.json';layout=json.loads(layout_path.read_text(encoding='utf-8'))
    migration_path=ROOT/'sources/objects/rigellian/canonical-assets.json'
    migration=json.loads(migration_path.read_text(encoding='utf-8')) if migration_path.exists() else {'issue':232,'models':[]}
    removed={item['path'] for row in migration['models'] for item in row['removed_models']}
    tracked=set(subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0'))
    for ship in style['ships']:
        record=next(row for row in inventory['records'] if row['id']==ship['id'])
        out=ROOT/ship['canonical_directory'];report=json.loads((out/'runtime-verification.json').read_text(encoding='utf-8'))
        generation=json.loads((out/'generation.json').read_text(encoding='utf-8'))
        for ext in ['blend','glb']:assert report[ext+'_sha256']==sha(out/f'model.{ext}')
        new_blend=ship['canonical_directory'].removeprefix('sources/')+'/model.blend'
        existing=next((row for row in migration['models'] if row['id']==ship['id']),None)
        history=[] if existing is None else existing['removed_models']
        for study in record['available_studies']:
            if study['blend']==new_blend:continue
            historical=dict(study,present=False,superseded_by=new_blend,retirement_issue=232)
            record.setdefault('superseded_studies',[]).append(historical)
            for ext in ['blend','glb']:
                relative='sources/'+str(Path(study['blend']).with_suffix('.'+ext)).replace('\\','/')
                target=(ROOT/relative).resolve()
                assert target.is_relative_to(ROOT/'sources/docs/assets/reconstruction')
                assert relative in tracked,('Only tracked superseded payloads may be retired',relative)
                if target.exists():
                    history.append(preserve({'path':relative,'sha256':sha(target),'bytes':target.stat().st_size}))
                    target.unlink();removed.add(relative)
        for original in history:preserve(original)
        media='gallery/media/objects/rigellian/'+ship['slug']
        views=[{'label':label,'image':media+'/'+name+'.png'} for name,label in [
            ('front-quarter','Front quarter'),('rear-quarter','Rear quarter'),('top','Top'),('underside','Underside'),
            ('verified-native','Saved native reopen'),('verified-imported','Independent GLB import')]]
        views.extend({'label':label,'image':'gallery/media/objects/rigellian/fleet/'+name+'.png'} for name,label in [
            ('shared-scale-top','Fleet: proposed sizes, common top camera'),('shared-scale-oblique','Fleet: proposed sizes, common oblique camera')])
        record['available_studies']=[{'stage':'hi-def-broad-skin-refinement','blend':new_blend,'present':True,
            'sha256':report['blend_sha256'],'media':media,'views':views,
            'final_visual_acceptance':'Agent-reviewed authored reconstruction; user and game acceptance pending'}]
        record['selected_refinement']={'stage':'hi-def-broad-skin-refinement','blend':new_blend,
            'glb':new_blend.removesuffix('.blend')+'.glb','issue':232,
            'integration':'Single canonical hull for flight, build previews and SciTek. Apply proposed scale explicitly; no calibrated sockets or game acceptance supplied.'}
        record['acceptance'].update({'reference_views_reviewed':True,'silhouette_and_proportions':True,
            'high_detail_structure':True,'materials':True,'native_and_glb_runtime':True,
            'attachment_transforms':False,'final_visual_acceptance':False})
        row={'id':ship['id'],'blend':ship['canonical_directory']+'/model.blend',
             'glb':ship['canonical_directory']+'/model.glb','blend_sha256':report['blend_sha256'],
             'glb_sha256':report['glb_sha256'],'removed_models':history,'media':media}
        if existing:migration['models'][migration['models'].index(existing)]=row
        else:migration['models'].append(row)
        model={'id':ship['id'],'name':ship['name'],'issue':232,'legacy_entry':ship['legacy_entry'],
               'role_class':ship['legacy_role_class'],'proposed_world_size':ship['proposed_world_size'],
               'size_status':'Authored recommendation, not recovered metres or an applied client override',
               'forward_axis':'-Y','up_axis':'Z','root':'PlacementRoot','triangles':report['triangles'],
               'mesh_batches':report['mesh_batches'],'materials':1,'measured_dimensions':generation['measured_dimensions'],
               'blend_sha256':report['blend_sha256'],'glb_sha256':report['glb_sha256'],
               'calibrated_weapon_sockets':False,'game_runtime_acceptance':False,
               'references':'../fleet-style.json','views':[v['image'] for v in views]}
        write_json(out/'model.json',model)
        import sys
        sys.path.insert(0,str(ROOT/'sources/tools/blender'))
        from rigellian_mobile_runtime_evidence import bind
        bind(ROOT,record,ship)
        (out/'README.md').write_text('# '+ship['name']+'\n\nCanonical mobile Rigellian hull, issue #232. '+
            'Use model.glb for all game presentations; model.blend is the editable source.\n\n'+
            'The supplied hi-def reference and original paletted '+ship['legacy_entry']+
            ' constrain the visible form. Hidden service structures, panel layouts and wear are authored. '+
            'Broad formed skins replace the rejected dense regular panel grid. IS0C is the craft-quality benchmark, not a Rigellian design template.\n\n'+
            f"Proposed size: {ship['proposed_world_size']} world units, native maximum extent {ship['authoring_length_units']}. "+
            'The client currently falls back to 96 for this id; integration must apply and verify the intended override. '+
            'Root scale is identity, forward -Y, up Z in Blender; standard glTF axis conversion is applied. '+
            'Windows/service details use the same authoring scale across the fleet.\n\n'+
            'One shared 2048-square worn PBR atlas, embedded in each portable GLB. '+
            'runtime-verification.json binds native reopening, independent import, geometry and rendered evidence to hashes. '+
            'No calibrated weapon sockets, flight behaviour or client GPU acceptance is claimed. '+
            'The shared fleet comparison uses actual relative model sizes and a single camera.\n',encoding='utf-8')
    write_json(path,inventory)
    migration['policy']='Exactly one current editable Blend and runtime GLB per mobile Rigellian id. Completed superseded editable variants are preserved in verified immutable Git history; historical metadata/media remain in the checkout.'
    migration['preservation_commit']=PRESERVED_COMMIT
    write_json(migration_path,migration)
    retained=[]
    for item in layout['files']:
        if item['destination'] in removed:
            if not any(row['original']==item['original'] for row in layout.setdefault('retired_imports',[])):
                layout['retired_imports'].append({'original':item['original'],'reason':'Superseded by canonical mobile Rigellian hull in issue #232; historical media and metadata retained.'})
        else:retained.append(item)
    layout['files']=retained
    board(style)
    registered={item['destination'] for item in retained}
    roots=[ROOT/'sources/objects/rigellian'/s['slug'] for s in style['ships']]
    roots.extend([ROOT/'sources/materials/rigellian-mobile-fleet',ROOT/'gallery/media/objects/rigellian/fleet'])
    roots.extend(ROOT/'gallery/media/objects/rigellian'/s['slug'] for s in style['ships'])
    files=[p for folder in roots for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files.extend(ROOT/p for p in ['sources/objects/rigellian/fleet-comparison.json','sources/objects/rigellian/canonical-assets.json',
        'sources/tools/rigellian_fleet_surface_maps.py','sources/tools/blender/build_rigellian_mobile_fleet.py',
        'sources/tools/blender/verify_rigellian_mobile_fleet.py','sources/tools/blender/rigellian_mobile_runtime_evidence.py'])
    if (ROOT/'sources/objects/rigellian/delivery-review.json').exists():files.append(ROOT/'sources/objects/rigellian/delivery-review.json')
    for file in files:
        destination=file.relative_to(ROOT).as_posix()
        if destination in registered:continue
        role='material-texture' if destination.startswith('sources/materials/') else 'media' if destination.startswith('gallery/') else 'source'
        layout['files'].append({'original':destination.removeprefix('sources/'),'destination':destination,'role':role,'ownership':'authored'})
        registered.add(destination)
    write_json(layout_path,layout)
    print('RIGELLIAN_CANONICAL_REGISTERED',len(style['ships']),'models;',len(removed),'superseded payloads retired')


if __name__=='__main__':main()
