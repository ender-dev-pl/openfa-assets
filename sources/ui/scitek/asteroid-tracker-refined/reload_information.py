import bpy,sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index('--')+1]).resolve()
bpy.ops.wm.open_mainfile(filepath=str(out/'asteroid-tracker-information.blend'))
s=bpy.context.scene;s.frame_set(88);s.render.filepath=str(out/'reload-087.png');bpy.ops.render.render(write_still=True)
print('TRACKER_INFORMATION_RELOADED')
