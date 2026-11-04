"""Run original assertions on byte-identical working copies; never rebuild model sources."""
import hashlib
import importlib
import json
from pathlib import Path
import shutil
import sys
import traceback
import uuid
import argparse
import bpy

sys.path.insert(0,str(Path(__file__).resolve().parent))
REPO=Path(__file__).resolve().parents[2]
OUTPUT=REPO/'docs/assets/reconstruction/evidence/rigellian-runtime-revalidation'
EARLY=['cpu','filtration','nourishment','community','health','bunker','science','databanks','construction','ground_deck']


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--changed-only',action='store_true',help='Reuse exact unchanged source/verifier/report evidence; rerun changed models')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    OUTPUT.mkdir(parents=True,exist_ok=True)
    previous=json.loads((OUTPUT/'summary.json').read_text()) if args.changed_only else None
    prior={r['id']:r for r in previous['records']} if previous else {}
    session=REPO/'artifacts/issue-1106-rigellian-runtime'/uuid.uuid4().hex
    inventory_path=REPO/'docs/reconstruction/models/inventory.json'
    records=[r for r in json.loads(inventory_path.read_text())['records'] if r['category']=='buildings' and r['culture']=='rigellian']
    assert len(records)==23
    script_root=Path(__file__).resolve().parent
    scripts={sha(p):p.stem for p in script_root.glob('verify_*.py')}
    results=[]
    for index,record in enumerate(records):
        study=[s for s in record['available_studies'] if s['present']][-1]
        source=(REPO/study['blend']).parent
        hashes={str(p.relative_to(source)).replace('\\','/'):sha(p) for p in source.rglob('*') if p.is_file()}
        assert hashes['model.blend']==study['sha256']
        report=json.loads((source/'technical-review.json').read_text())
        verifier='verify_rigellian_'+EARLY[index] if index<10 else scripts[report['verifier_sha256']]
        module=importlib.import_module(verifier)
        assert module.ROOT.resolve()==source.resolve(),('Verifier target differs',verifier)
        old=prior.get(record['id'])
        if old and old['passed'] and old['source_assets_unchanged'] and old['source_files']==hashes and old['verifier_sha256']==sha(script_root/(verifier+'.py')):
            assert old['new_technical_report_sha256']==sha(OUTPUT/source.name/'technical-review.json')
            assert (REPO/old['working_copy']/'imported-glb-front-quarter.png').is_file()
            results.append(dict(old,execution_reused=True))
            print('RIGELLIAN_REVALIDATION_UNCHANGED_REUSED',record['id'],flush=True)
            continue
        target=session/source.name
        shutil.copytree(source,target)
        assert all(sha(target/name)==digest for name,digest in hashes.items())
        # Redirect matching root globals in already-imported support modules as
        # well; scene/contact helper assertions themselves remain unchanged.
        changed=[]
        for loaded in list(sys.modules.values()):
            if loaded is None: continue
            root=getattr(loaded,'ROOT',None)
            if isinstance(root,Path) and root.resolve()==source.resolve():
                changed.append((loaded,root));loaded.ROOT=target
        outcome=dict(id=record['id'],blend=study['blend'],verifier=verifier+'.py',
            verifier_sha256=sha(script_root/(verifier+'.py')),source_files=hashes,
            source_assets_unchanged=False,passed=False,execution_reused=False)
        try:
            module.main()
            outcome['passed']=True
        except Exception:
            outcome['failure']=traceback.format_exc()
            print(outcome['failure'],flush=True)
        finally:
            for loaded,root in changed: loaded.ROOT=root
        assert hashes=={str(p.relative_to(source)).replace('\\','/'):sha(p) for p in source.rglob('*') if p.is_file()},'Original evidence changed'
        outcome['source_assets_unchanged']=True
        destination=OUTPUT/source.name;destination.mkdir(parents=True,exist_ok=True)
        for name in ['technical-review.json']:
            shutil.copy2(target/name,destination/name)
        outcome['new_technical_report_sha256']=sha(destination/'technical-review.json')
        outcome['working_copy']=str(target.relative_to(REPO)).replace('\\','/')
        results.append(outcome)
        print('RIGELLIAN_REVALIDATION_RESULT',record['id'],outcome['passed'],flush=True)
    summary=dict(issue=1106,blender=bpy.app.version_string,runner_sha256=sha(Path(__file__)),
        inventory_sha256=sha(inventory_path),models=len(results),passed=sum(r['passed'] for r in results),
        records=results,final_visual_acceptance=False,
        executions_reused=sum(r['execution_reused'] for r in results),
        executions_rerun=sum(not r['execution_reused'] for r in results),
        scope='Existing source-specific native/import assertions on verified byte-identical copies; generated working renders remain in artifacts. Original files/evidence unchanged; no final art/state/integration acceptance.')
    (OUTPUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    assert summary['passed']==23,'Some source-specific verifiers failed; inspect summary'
    print('RIGELLIAN_REVALIDATION_OK',len(results),flush=True)


if __name__=='__main__': main()
