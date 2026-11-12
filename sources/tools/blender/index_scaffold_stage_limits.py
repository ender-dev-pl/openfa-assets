"""Read actual scaffold stage ceilings from the reconstructed original LE image."""
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from extract_fragile_le import reconstruct,parse_le
from analyse_scaffold_stacking import scaffold_chain
REPO=Path(__file__).resolve().parents[2]
TARGET=REPO/'docs/reconstruction/models/scaffold-stage-limits.json'


def sha(path):
    return hashlib.sha256(path.read_text(encoding='utf-8-sig').encode() if path.suffix in ['.py','.json','.c'] else path.read_bytes()).hexdigest()


def build_index(root=REPO,legacy=None):
    legacy=legacy or root.parent/'legacy';out=root/'artifacts/issue-983-scaffold-stacking';out.mkdir(parents=True,exist_ok=True)
    reconstruct(legacy/'FRAGILE.LE',out/'memory.bin');memory=(out/'memory.bin').read_bytes()
    objects=parse_le((legacy/'FRAGILE.LE').read_bytes())[-1];assert objects[2].base_address==0xb0000
    instructions={0x44a0a:('0fb63c8576620300','movzx edi, byte [eax*4 + data-object-relative 0x36276]'),0x44a27:('0fbe490a','movsx ecx, byte [ecx + 0xA]'),0x44a53:('8a0c8574620300','mov cl, byte [eax*4 + data-object-relative 0x36274]')}
    for address,(raw,_) in instructions.items():
        assert memory[address:address+len(bytes.fromhex(raw))]==bytes.fromhex(raw),'Unexpected original instruction bytes'
    buildings=json.loads((root/'content/standard/catalogues/legacy-buildings.json').read_text())['buildings']
    references=json.loads((root/'docs/reconstruction/models/shared-construction-references.json').read_text())
    dependencies={item['id']:item for item in references['building_dependencies']}
    records=[]
    for definition in buildings:
        identity=definition['legacy'];global_type=identity['globalType'];offset=0xe6274+global_type*20
        assert list(memory[offset:offset+2])==[definition['footprintWidth'],definition['footprintHeight']]
        assert memory[offset+3]==identity['definitionClass']
        duration=memory[0xb9fd1+global_type*6];assert duration==identity['constructionUpdates'] and duration>0
        ceiling=memory[offset+2];assert 1<=ceiling<=255
        capacity=32>>memory[offset] if global_type<40 else 2
        maximum=min(ceiling,duration)
        chain=scaffold_chain(duration,1,ceiling,capacity)
        assert sum(r['frame'] for r in chain)==maximum
        records.append(dict(id=definition['id'],name=identity['name'],global_type=global_type,family=dependencies[definition['id']]['family'],
            definition_address=hex(offset),stage_ceiling_address=hex(offset+2),stage_ceiling_raw=ceiling,construction_updates=duration,
            frames_per_tier=capacity,max_stage_while_constructing=maximum,max_tiers=len(chain),max_stage_chain=chain,
            raw_definition_sha256=hashlib.sha256(memory[offset:offset+20]).hexdigest()))
    assert len(records)==177 and len({r['global_type'] for r in records})==177
    families=[]
    for family in references['families']:
        used=[r for r in records if r['family']==family['key']]
        families.append(dict(family=family['key'],building_count=len(used),max_required_stage=max((r['max_stage_while_constructing'] for r in used),default=0),
            max_required_tiers=max((r['max_tiers'] for r in used),default=0),
            tallest_building_ids=[r['id'] for r in used if r['max_tiers']==max(v['max_tiers'] for v in used)] if used else [],
            status='Observed required range; prototype/final 3D coverage must be checked separately' if used else 'Installed family without current catalogue dependency'))
    paths=['content/standard/catalogues/legacy-buildings.json','docs/reconstruction/models/shared-construction-references.json',
           'tools/extract_fragile_le.py','tools/blender/analyse_scaffold_stacking.py','artifacts/fragile-le-decompilation/FRAGILE.LE.decompiled.c']
    return dict(issue=983,generator_sha256=sha(Path(__file__)),executable_sha256=sha(legacy/'FRAGILE.LE'),memory_sha256=hashlib.sha256(memory).hexdigest(),
        text_hash_policy='UTF-8/LF-normalized text; binary exact',source_sha256={p:sha(root/p) for p in paths},
        instruction_evidence={hex(address):dict(bytes=raw,interpretation=text) for address,(raw,text) in instructions.items()},data_object_base='0xB0000',
        field='Building definition +2 is consumed as the construction stage ceiling at 0x449F0; broader physical-height meaning is not assigned',
        assumptions=['Normal active construction remainingUpdates range is 1..constructionUpdates; completion remainingUpdates=0 takes the completed-building branch',
                     'Current definition-culture scaffold mapping retained; original owner-based resource choice remains separate'],
        records=records,families=families,building_count=177,max_required_tiers=max(r['max_tiers'] for r in records),
        buildings_requiring_stacking=sum(r['max_tiers']>1 for r in records),final_visual_acceptance=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    result=build_index()
    if args.check: assert json.loads(TARGET.read_text())==result,'Stale scaffold stage limits'
    else: TARGET.write_text(json.dumps(result,indent=2)+'\n')
    print('SCAFFOLD_STAGE_LIMITS_OK',result['building_count'],'buildings',result['buildings_requiring_stacking'],'require stacking; max tiers',result['max_required_tiers'])


if __name__=='__main__': main()
