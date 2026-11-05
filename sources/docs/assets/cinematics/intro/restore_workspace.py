"""Verify and copy this cinematic's sources into an isolated, ignored authoring workspace."""
from pathlib import Path
import argparse,hashlib,shutil
root=Path(__file__).resolve().parent
repo=next(p for p in root.parents if (p/'.git').exists())
ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,default=repo/'artifacts/intro-authoring');args=ap.parse_args();out=args.output.resolve()
assert out.is_relative_to(repo/'artifacts') or out.is_relative_to(repo/'.workspace'),'Use this repository artifacts/ or .workspace/.'
assert not out.exists(),'Refusing to overwrite an existing workspace.'
for line in (root/'SOURCES.sha256').read_text().splitlines():
 digest,name=line.split('  ',1);f=(root/name).resolve();assert f.is_relative_to(root);assert hashlib.sha256(f.read_bytes()).hexdigest()==digest,name
shutil.copytree(root,out,ignore=shutil.ignore_patterns('__pycache__','*.blend1'));print('INTRO_WORKSPACE_READY',out)
