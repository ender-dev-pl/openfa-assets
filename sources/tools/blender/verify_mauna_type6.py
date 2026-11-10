"""Native/imported MN2C runtime checks using its dedicated detail author."""
from pathlib import Path
import argparse,json,sys
sys.path.insert(0,str(Path(__file__).parent))
import remaster_mauna_type6 as author
import verify_mauna_mobile_ship as common

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--ship',required=True);key=p.parse_args(sys.argv[sys.argv.index('--')+1:]).ship
    assert key=='max-combat-craft-type-6'
    inputs=[Path(__file__),Path(author.__file__),Path(common.__file__),Path(author.detail_parts.__file__),Path(author.detail_parts.roof_patch.__code__.co_filename),Path(author.detail_parts.box.__code__.co_filename)]
    before={item:author.sha(item) for item in inputs}
    common.author=author
    common.main(key)
    out,_=author.folders(key);report_path=out/'runtime-verification.json'
    assert report_path.resolve().parent==out.resolve() and report_path.name=='runtime-verification.json'
    report=json.loads(report_path.read_bytes());meta=json.loads((out/'model.json').read_bytes())
    assert meta['detail_parts_sha256']==author.sha(Path(author.detail_parts.__file__))
    report['shared_mauna_verifier_sha256']=report['verifier_sha256'];report['verifier_sha256']=author.sha(Path(__file__))
    report['detail_parts_sha256']=meta['detail_parts_sha256']
    for field,helper_path in [('detail_baseline_helpers_sha256',Path(author.detail_parts.roof_patch.__code__.co_filename)),('detail_primitives_sha256',Path(author.detail_parts.box.__code__.co_filename))]:
        assert meta[field]==author.sha(helper_path);report[field]=meta[field]
    assert before=={item:author.sha(item) for item in inputs},'Verifier changed a source input'
    report['verifier_inputs_unchanged']=True
    report_path.write_text(json.dumps(report,indent=2)+'\n')
    assert before=={item:author.sha(item) for item in inputs},'Report write changed a source input'
