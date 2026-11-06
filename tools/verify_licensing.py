# SPDX-License-Identifier: MIT
"""Audit repository license scopes and explain an individual file's assignment."""
import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tooling'))
from openfa_tools.licensing import audit, classify, load_policy


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--explain')
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    if args.explain:
        print(json.dumps(dict(path=args.explain, **classify(args.explain, load_policy(ROOT))), indent=2))
        return
    raw = subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'], cwd=ROOT)
    report = audit(ROOT, [path for path in raw.decode('utf-8').split('\0') if path])
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print('LICENSING_SCOPES_VERIFIED',report['files'],json.dumps(report['counts'],sort_keys=True))


if __name__ == '__main__':
    main()
