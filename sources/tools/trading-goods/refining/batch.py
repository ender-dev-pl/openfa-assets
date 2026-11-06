"""Build and independently validate refined sources, then render them with bounded workers.

Run with ordinary Python inside an environment providing Blender. Existing results are
reused only when their source/tool hashes and requested render settings still match.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import subprocess


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--items', default=','.join(map(str, range(1, 102))))
    ap.add_argument('--jobs', type=int, default=4)
    ap.add_argument('--renders', type=Path, help='Alternate local work/output directory')
    ap.add_argument('--verify-only', action='store_true', help='Build and check native/GLB files without rendering')
    ap.add_argument('--width', type=int, default=1024)
    ap.add_argument('--samples', type=int, default=64)
    a = ap.parse_args()
    root = a.repo.resolve()
    tools = Path(__file__).resolve().parent
    natives = root/'sources/docs/assets/reconstruction/trading-goods-refined'
    work = a.renders.resolve() if a.renders else root/'artifacts/trading-goods-refining/production'
    work.mkdir(parents=True, exist_ok=True)
    numbers = list(map(int, a.items.split(',')))
    selections_path = root/'docs/trading-goods/refinement-selections.json'
    selection_data = json.loads(selections_path.read_text()) if selections_path.exists() else {}
    selections = selection_data.get('overrides', {})
    renderers = selection_data.get('renderer_overrides', {})

    def folder_for(number):
        ident = f'TI{number:03d}'
        return root/selections[ident]['folder'] if ident in selections else natives/ident
    missing = []
    for number in numbers:
        folder = folder_for(number)
        record = folder/'refinement.json'
        if not record.exists():
            missing.append(number)
            continue
        journal = json.loads(record.read_text())
        assert journal['builder_sha256'] == sha(tools/'refine.py'), folder
        for prefix in ['geometry','revision']:
            if prefix+'_builder' in journal:
                assert journal[prefix+'_builder_sha256'] == sha(root/journal[prefix+'_builder']), folder
        assert journal['refined_native_sha256'] == sha(folder/(f'TI{number:03d}.blend')), folder
    if missing:
        base_missing = [n for n in missing if f'TI{n:03d}' not in selections
                        or not (natives/f'TI{n:03d}'/'refinement.json').is_file()]
        if base_missing:
            with (work/'build.log').open('w') as log:
                subprocess.run(['blender', '-b', '--python-exit-code', '1', '-t', '1', '--python', str(tools/'refine.py'), '--',
                                '--repo', str(root), '--items', ','.join(map(str, base_missing)), '--out', str(natives)],
                               stdout=log, stderr=subprocess.STDOUT, check=True)
        for number in missing:
            ident = f'TI{number:03d}'
            if ident in selections:
                with (work/(ident+'-geometry-build.log')).open('w') as log:
                    subprocess.run(['blender', '-b', '--python-exit-code', '1', '-t', '1', '--python', str(root/selections[ident]['builder']), '--',
                                    '--repo', str(root), '--out', str(folder_for(number))],
                                   stdout=log, stderr=subprocess.STDOUT, check=True)
        print('REFINEMENT_BUILD_COMPLETE', len(missing), flush=True)

    def process(number):
        ident = f'TI{number:03d}'
        folder = folder_for(number)
        native, glb = folder/(ident+'.blend'), folder/(ident+'.glb')
        report = folder/'runtime-validation.json'
        renderer = root/renderers[ident] if ident in renderers else tools/'render.py'
        roles = {m['role'] for m in json.loads((folder/'refinement.json').read_text())['materials']}
        samples = a.samples if roles.intersection({'glass', 'gem'}) else min(32, a.samples)
        with (work/(ident+'.log')).open('w') as log:
            subprocess.run(['blender', '-b', '--python-exit-code', '1', '-t', '1', '--python', str(tools/'verify.py'), '--',
                            '--native', str(native), '--glb', str(glb), '--report', str(report)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
            if a.verify_only:
                return ident+' independently verified'
            png = work/(ident+'.png')
            journal = png.with_suffix('.json')
            if png.exists() and journal.exists():
                old = json.loads(journal.read_text())
                if (old['native_sha256'] == sha(native) and old['renderer_sha256'] == sha(renderer)
                        and old['image_sha256'] == sha(png) and old['resolution'] == [a.width, a.width*3//4]
                        and old['samples'] == samples):
                    return ident+' verified; render reused'
            receipt = work/(ident+'.published.json')
            if not png.exists() and journal.exists() and receipt.exists():
                old = json.loads(journal.read_text())
                installed = json.loads(receipt.read_text())
                published = root/installed['image']
                if (old['native_sha256'] == sha(native) == installed['native_sha256']
                        and old['renderer_sha256'] == sha(renderer)
                        and old['image_sha256'] == installed['render_output_sha256']
                        and published.exists() and sha(published) == installed['image_sha256']
                        and old['resolution'] == [a.width, a.width*3//4] and old['samples'] == samples):
                    return ident+' verified; published render reused'
            subprocess.run(['blender', '-b', '--python-exit-code', '1', '-t', '1', '--python', str(renderer), '--',
                            '--native', str(native), '--out', str(png), '--width', str(a.width),
                            '--samples', str(samples)], stdout=log, stderr=subprocess.STDOUT, check=True)
        return ident+' verified and rendered'

    with ThreadPoolExecutor(max_workers=a.jobs) as executor:
        for task in as_completed([executor.submit(process, n) for n in numbers]):
            print(task.result(), flush=True)


if __name__ == '__main__':
    main()
