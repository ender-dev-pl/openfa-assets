"""Bind manually authored lore judgements to the current verified models/images.

This does not perform semantic review. Edit the pipe-separated review notes only
after reading the descriptions and actually inspecting changed assets/renders.
"""
import argparse,hashlib,json,subprocess
from collections import Counter
from pathlib import Path

ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--game-repo',type=Path,required=True)
a=ap.parse_args();root=Path(__file__).resolve().parents[1]
sha=lambda b:hashlib.sha256(b).hexdigest()
source_path='content/standard/localization/en.json'
raw=(a.game_repo/source_path).read_bytes();localization=json.loads(raw);strings=localization['strings']
revision=subprocess.check_output(['git','-C',str(a.game_repo),'rev-parse','HEAD'],text=True).strip()
committed=json.loads(subprocess.check_output(['git','-C',str(a.game_repo),'show','HEAD:'+source_path]))
coverage=json.loads((root/'docs/trading-goods/coverage.json').read_text())
mp=root/'docs/trading-goods/refinement-validation.json';manifest=json.loads(mp.read_text())
images={e['legacy_stem']:e for e in manifest['items']}
notes_path=root/'docs/trading-goods/lore-review-notes.tsv'
notes=notes_path.read_text().splitlines();assert len(notes)==101
audit_path=root/'docs/trading-goods/lore-audit.json'
previous=json.loads(audit_path.read_text())
old={e['legacy_stem']:e for e in previous['entries']}
corrections=json.loads((root/'docs/trading-goods/lore-corrections-validation.json').read_text())
inspections={e['legacy_stem']:e for e in corrections['items']}
entries=[]
for item,line in zip(coverage['items'],notes):
    number,status,priority,requirement,finding,action=line.split('|');ident=item['legacy_stem']
    assert int(number)==item['id']+1 and ident==f'TI{int(number):03d}'
    image=images[ident]
    assert sha((root/image['native']).read_bytes())==image['native_sha256']
    assert sha((root/image['image']).read_bytes())==image['image_sha256']
    e=dict(legacy_stem=ident,item_id=item['id'],name=item['name'],assessment=status,priority=priority,lore_requirement=requirement,current_finding=finding,next_action=action,description_key=item['description_key'],description_sha256=sha(strings[item['description_key']].encode()),native=image['native'],native_sha256=image['native_sha256'],image=image['image'],image_sha256=image['image_sha256'])
    if 'previous_review' in old[ident]:e['previous_review']=old[ident]['previous_review']
    elif old[ident]['assessment']!=status:
        e['previous_review']={k:old[ident][k] for k in ['assessment','current_finding','native','native_sha256','image_sha256']}
        e['previous_review']['milestone']='c3b17b4'
    if ident in inspections:
        x=inspections[ident];assert x['native_sha256']==e['native_sha256']
        e['blender_inspection']={k:v for k,v in x.items() if k not in ['legacy_stem','native','native_sha256']}
    elif old[ident].get('blender_inspection') and old[ident]['native_sha256']==e['native_sha256']:
        e['blender_inspection']=old[ident]['blender_inspection']
    entries.append(e)
counts=dict(Counter(e['assessment'] for e in entries))
report=dict(schema_version=2,count=101,scope=previous['scope'],lore_source=dict(repository='ender-dev-pl/ed-openfa-game',revision=revision,path=source_path,file_sha256=sha(raw),semantic_content_matches_revision=committed==localization),image_manifest_sha256=sha(mp.read_bytes()),manual_notes_sha256=sha(notes_path.read_bytes()),correction_inspections_sha256=sha((root/'docs/trading-goods/lore-corrections-validation.json').read_bytes()),counts=counts,assessment_meanings=previous['assessment_meanings'],limits=['All 101 English descriptions were manually read and compared with rendered studies. The seven corrected natives also have read-only Blender geometry/material inspection.','Technical validation does not certify artistic quality, chemical composition, physical scale, carat mass, biological effects or payload behaviour.','The shared catalogue does not imply a common cultural origin. Authored motifs and ambiguous icon/text relationships remain explicit.','Full procedural materials are native-only; GLB shader graphs remain unbaked.'],entries=entries)
audit_path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
lines=['# Trading goods — lore and representation audit','','All **101 item descriptions** were manually read and compared with rendered models. This is a semantic/art-direction assessment, separate from technical render acceptance.','','[Machine-readable audit](lore-audit.json) · [Current gallery](../../gallery/trading-goods-shared.md) · [Reproduction](REFINEMENT.md)','','Source: [English item lore at '+revision[:7]+'](https://github.com/ender-dev-pl/ed-openfa-game/blob/'+revision+'/'+source_path+'). Description, native and image hashes bind each review to its evidence.','','## Result','']
for status,count in counts.items():lines.append('- **'+status+'**: '+str(count)+' — '+report['assessment_meanings'][status])
lines+=['','## Corrected explicit conflicts','','The initial audit at `c3b17b4` found seven specific contradictions. Separate `lore/` revisions now correct:','','- TI016: raw opal and metachrome, with no introduced diamonds.', '- TI018: deliberate square step-cut emerald in white gold.', '- TI019: smooth domed ruby cabochon, with red gold and copper.', '- TI020: 23 astramarines, white-gold bezels and titanium links.', '- TI021: ultropaz and alexandrite in yellow gold; one studio-light colour state.', '- TI045: actual brandy fill in hollow glass, with subtle dissolved-nacre scattering and no whole pearl beads.', '- TI053: ten mansions of truth plus ten of deceit, the highest truth goal and illustrative arcana-like character pieces. The more elaborate staircase/craft of the icon remains a refinement target.','','[Read-only Blender inspection](lore-corrections-validation.json) records actual geometry/material checks. Each corrected entry retains its previous finding and source hash. These fixes do not close the remaining partial or ambiguous artistic findings.','','## Cultural and evidence cautions','','- TI064 is a rare, revered Artemian axe associated with Cyreni. Recessed lunar/border channels, forged bronze and carved wood are authored interpretations, not recovered canonical writing. Do not copy Braccatian Celtic/Saxon styling indiscriminately onto Artemian objects.', '- TI007: the description lists drinking glasses, but the original icon has a carafe-like centrepiece. Keep that tension explicit.', '- TI063: the commodity is Kraagil oil, while the icon depicts the creature. Preserve that metonymy and improve its whale/dragon/crustacean anatomy rather than automatically substituting a bottle.', '- TI053 describes 20 locations, not 20 floors. The corrected set retains six tiers.', '- A “cabochon” material name is not evidence of an unfaceted shape; the revised ruby geometry was actually opened and rendered.', '- Static renders do not establish colour-change behaviour, temporal effects, biological efficacy, payload function or racial scale.','','## Full catalogue','','| Item/current image | Fit | Priority | Lore requirement | Assessment and next action |','|---|---|---|---|---|']
for e in entries:
    cells=['['+e['legacy_stem']+' '+e['name']+'](../../'+e['image']+')',e['assessment'],e['priority'],e['lore_requirement'],e['current_finding']+' **Next:** '+e['next_action']]
    lines.append('| '+' | '.join(c.replace('|','/') for c in cells)+' |')
lines+=['','## Recheck after edits','','Manual notes are maintained in `lore-review-notes.tsv` (six pipe-separated fields per item). Regenerate only after actual review:','','```sh','blender -b --python-exit-code 1 --python sources/tools/trading-goods/refining/verify_lore_geometry.py -- --repo .','python tools/build_trading_lore_audit.py --game-repo ../ed-openfa-game','python tools/verify_trading_lore_audit.py --game-repo ../ed-openfa-game','```','','The final check verifies evidence freshness and coverage, not semantic judgement. Replacing hashes alone is not a new review.','']
(root/'docs/trading-goods/LORE-AUDIT.md').write_text('\n'.join(lines))
print('LORE_AUDIT_GENERATED',counts)
