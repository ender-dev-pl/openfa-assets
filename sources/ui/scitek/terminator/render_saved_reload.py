"""Render a saved solid source with its retained camera and studio state."""
import bpy,sys
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];source,target=map(lambda p:Path(p).resolve(),args);bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.frame_set(1);s.cycles.samples=16;s.render.filepath=str(target);bpy.ops.render.render(write_still=True);print('TERMINATOR_SAVED_RELOAD_RENDERED')
