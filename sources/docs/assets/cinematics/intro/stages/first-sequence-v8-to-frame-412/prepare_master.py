import bpy
from pathlib import Path
p=Path(__file__).resolve().parent;m=bpy.data.scenes['MASTER — First sequence through original frame 412'];bpy.context.window.scene=m;ed=m.sequence_editor;seq=ed.strips if hasattr(ed,'strips') else ed.sequences
sound=seq.new_sound('Original intro soundtrack / packed',str(p/'opening-audio.m4a'),8,1);sound.frame_final_duration=826;sound.sound.pack();m.frame_set(353)
if bpy.context.screen:
 for area in bpy.context.screen.areas:
  if area.type=='VIEW_3D':area.type='SEQUENCE_EDITOR';area.spaces.active.view_type='SEQUENCER_PREVIEW';break
bpy.ops.wm.save_as_mainfile(filepath=str(p/'first-sequence-to-412.blend'));print('MASTER_AUDIO_PACKED',bool(sound.sound.packed_file))
