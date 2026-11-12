"""Run the shared RI17 verifier with enough whole-object framing margin."""
import argparse
from pathlib import Path
import sys
import bpy

sys.path.insert(0, str(Path(__file__).parent))
import verify_remastered_rigellian_static as shared


def main(recipe):
    original = shared.fit_camera

    def framed(direction, meshes):
        original(direction, meshes)
        bpy.context.scene.camera.data.ortho_scale *= 1.08

    # Scope the framing adjustment to this case without changing any shared
    # author/verifier source already bound by previous building reports.
    shared.fit_camera = framed
    try:
        shared.main(recipe)
    finally:
        shared.fit_camera = original


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--recipe', type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    main(args.recipe)
