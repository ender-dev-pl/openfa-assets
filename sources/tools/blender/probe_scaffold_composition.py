"""Execute original scaffold child, priority-copy, sorter and dispatch instructions in fixtures."""
import argparse,hashlib,json,struct,sys
from pathlib import Path
from unicorn import Uc,UC_ARCH_X86,UC_MODE_32,UC_HOOK_CODE
from unicorn.x86_const import UC_X86_REG_EAX,UC_X86_REG_EDX,UC_X86_REG_ESI,UC_X86_REG_ESP,UC_X86_REG_EIP
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from extract_fragile_le import reconstruct
REPO=Path(__file__).resolve().parents[2]
TARGET=REPO/'docs/reconstruction/models/scaffold-composition-evidence.json'
RETURN=0x4fff00
CALLBACK=0x4ffe00
SENTINEL=0x742f0


def write(uc,address,value): uc.mem_write(address,struct.pack('<I',value&0xffffffff))


def read(uc,address): return struct.unpack('<I',uc.mem_read(address,4))[0]


def machine(memory):
    uc=Uc(UC_ARCH_X86,UC_MODE_32);uc.mem_map(0,0x500000);uc.mem_write(0,memory);return uc


def return_from_stub(uc):
    stack=uc.reg_read(UC_X86_REG_ESP);target=read(uc,stack)
    uc.reg_write(UC_X86_REG_ESP,stack+4);uc.reg_write(UC_X86_REG_EIP,target)


def call(uc,address):
    write(uc,0x4efffc,RETURN);uc.reg_write(UC_X86_REG_ESP,0x4efffc)
    uc.emu_start(address,RETURN,count=100000)
    assert uc.reg_read(UC_X86_REG_EIP)==RETURN,'Original snippet did not return within instruction budget'


def child_keys(memory,count,base=100):
    assert 1<=count<=32 and base+count<0xffffffff
    uc=machine(memory);root=0x300000;allocated=[];write(uc,root+0x18,0x330000);write(uc,root+0x14,base)
    def allocator(uc,address,size,data):
        if address==0x72393:
            child=root+(len(allocated)+1)*0x100;allocated.append(child)
            uc.reg_write(UC_X86_REG_EAX,child);return_from_stub(uc)
    uc.hook_add(UC_HOOK_CODE,allocator);nodes=[root]
    for _ in range(count-1):
        uc.reg_write(UC_X86_REG_EAX,nodes[-1]);call(uc,0x44990);child=uc.reg_read(UC_X86_REG_EAX)
        assert read(uc,nodes[-1]+0x20)==child and read(uc,child+0x18)==0x330000 and read(uc,child+0x1c)&0xffff==1
        nodes.append(child)
    # A same-resource existing child is reused, not allocated again.
    if count>1:
        uc.reg_write(UC_X86_REG_EAX,root);call(uc,0x44990);assert uc.reg_read(UC_X86_REG_EAX)==nodes[1]
    keys=[]
    for node in nodes:
        uc.reg_write(UC_X86_REG_ESI,node)
        uc.emu_start(0x7ff91,0x7ff97,count=2)  # Actual priority +0x14 -> prepared key +0x38.
        keys.append(read(uc,node+0x38))
    assert len(allocated)==count-1
    assert bytes(uc.mem_read(0x44990,0x449e7-0x44990))==memory[0x44990:0x449e7]
    return dict(levels=count,keys=keys,allocator_calls=len(allocated),existing_child_reused=count>1,executed_child_code_unchanged=True)


def ordered_dispatch(memory,keys):
    assert keys and all(0<key<0xffffffff for key in keys)
    uc=machine(memory);nodes=[0x300000+i*0x100 for i in range(len(keys))]
    uc.mem_write(SENTINEL,bytes(128));write(uc,SENTINEL+4,nodes[0]);write(uc,SENTINEL+8,nodes[-1]);write(uc,SENTINEL+0x28,SENTINEL);write(uc,SENTINEL+0x2c,SENTINEL)
    uc.mem_write(0x74039,b'\0')
    for i,(node,key) in enumerate(zip(nodes,keys)):
        uc.mem_write(node,bytes(128));write(uc,node+4,nodes[i+1] if i+1<len(nodes) else SENTINEL);write(uc,node+8,nodes[i-1] if i else SENTINEL)
        write(uc,node+0x24,0x1000);write(uc,node+0x38,key);write(uc,node+0x14,key)
    callbacks=[];stubs=[]
    def hook(uc,address,size,data):
        if address in [0x6a7fd,0x7fc5a]: stubs.append(hex(address));return_from_stub(uc)
        elif address==CALLBACK:
            callbacks.append(read(uc,uc.reg_read(UC_X86_REG_EAX)+0x38));return_from_stub(uc)
    uc.hook_add(UC_HOOK_CODE,hook);call(uc,0x7fe2e)
    prepared=[];node=read(uc,SENTINEL+0x28)
    while node!=SENTINEL:
        prepared.append(read(uc,node+0x38));node=read(uc,node+0x28);assert len(prepared)<=len(keys)
    assert prepared==sorted(keys)
    write(uc,0x7454c,min(keys));write(uc,0x74018,0xffffffff);write(uc,0x7401c,0xffffffff);write(uc,0x9b544,100);write(uc,0x9b540,100);uc.mem_write(0x75404,b'\0')
    for node in nodes:
        for offset,value in [(0x24,0x1001),(0x30,0),(0x34,0),(0x44,1),(0x48,1),(0x54,CALLBACK),(0x58,0),(0x70,0)]: write(uc,node+offset,value)
    call(uc,0x804a5);assert callbacks==prepared
    # Fixture globals occupy raw data-relative locations outside executed code.
    # No executed instruction was patched, including the two stubbed helpers.
    for start,end in [(0x44990,0x449e7),(0x7fe2e,0x803cf),(0x804a5,0x80680)]:
        assert bytes(uc.mem_read(start,end-start))==memory[start:end]
    return dict(input_keys=keys,prepared_keys=prepared,callback_keys=callbacks,stubbed_helpers=sorted(set(stubs)),executed_code_unchanged=True)


def build_evidence(root=REPO,legacy=None):
    legacy=legacy or root.parent/'legacy'
    output=root/'artifacts/issue-983-scaffold-stacking';output.mkdir(parents=True,exist_ok=True)
    source=legacy/'FRAGILE.LE';reconstruct(source,output/'memory.bin');memory=(output/'memory.bin').read_bytes()
    cases=[]
    for levels in [1,2,3,9,11]:
        chain=child_keys(memory,levels);dispatch=ordered_dispatch(memory,list(reversed(chain['keys'])))
        cases.append(dict(child_chain=chain,dispatch=dispatch))
    cases.append(dict(dispatch=ordered_dispatch(memory,[103,100,102,101])))
    return dict(issue=983,executable_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),memory_sha256=hashlib.sha256(memory).hexdigest(),
        generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),cases=cases,
        result='Within nonwrapping positive priorities, scaffold parents precede their higher-level children in body callback dispatch: bottom-to-top/lower-first',
        scope='Original unpatched instruction execution in isolated synthetic descriptor/global fixtures; not a running game or full sprite compositor',
        substitutions={'0x72393':'Allocator returns controlled empty descriptor; original child helper still writes fields', '0x6A7FD':'Cache release stub if called','0x7FC5A':'Clipping/dirty-region helper returns without drawing',hex(CALLBACK):'Fixture sprite callback records prepared key; no original sprite rasterizer or palette effects executed'},
        limitations=['Raw unrelocated data-relative globals deliberately bound to fixture memory; no full LE relocation/runtime claim',
                     'Positive distinct priorities without 32-bit wrap; ownership, visibility and arbitrary descriptor flags not covered',
                     'No pixel blending, shadow/palette ramps, source sprite ordering beyond these body descriptors, or game integration proof'],
        body_order_verified=True,full_pixel_composition_verified=False,final_visual_acceptance=False)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args();result=build_evidence()
    if args.check: assert json.loads(TARGET.read_text())==result,'Stale scaffold composition evidence'
    else: TARGET.write_text(json.dumps(result,indent=2)+'\n')
    print('SCAFFOLD_BODY_ORDER_OK',len(result['cases']),'original-instruction fixtures')


if __name__=='__main__': main()
