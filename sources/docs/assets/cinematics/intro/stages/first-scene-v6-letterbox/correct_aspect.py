"""Undo the reconstructed vertical stretch globally, then frame the image in 4:3 letterbox."""
import bpy,json
from pathlib import Path
p=Path(__file__).resolve().parent;s=bpy.context.scene;s.use_nodes=True;n=s.node_tree.nodes;l=s.node_tree.links
out=next(x for x in n if x.type=='COMPOSITE');source=out.inputs['Image'].links[0].from_socket
for link in list(out.inputs['Image'].links):l.remove(link)
frame=n.new('NodeFrame');frame.label='Display correction — square sun, 4:3 letterbox';frame.name='v6 — Global display aspect correction'
scale=n.new('CompositorNodeScale');scale.name='Undo vertical stretch';scale.space='RELATIVE';scale.inputs['X'].default_value=7/6;scale.inputs['Y'].default_value=(262/560)*(7/6);scale.parent=frame;l.new(source,scale.inputs['Image'])
black=n.new('CompositorNodeMixRGB');black.name='Full original canvas / opaque black';black.blend_type='MULTIPLY';black.inputs[0].default_value=1;black.inputs[2].default_value=(0,0,0,1);l.new(source,black.inputs[1]);black.parent=frame
alpha=n.new('CompositorNodeAlphaOver');alpha.inputs[0].default_value=1;l.new(black.outputs[0],alpha.inputs[1]);l.new(scale.outputs[0],alpha.inputs[2]);alpha.parent=frame
l.new(alpha.outputs[0],out.inputs['Image'])
# Preserve the old vertical field of view in the new 4:3 render canvas.
# The compositor restores original X framing while applying only the desired Y correction.
s.camera.data.sensor_fit='HORIZONTAL';s.camera.data.lens*=6/7
s.render.resolution_x=960;s.render.resolution_y=720
s.render.pixel_aspect_x=1;s.render.pixel_aspect_y=1;s['display_correction']='Global Y 262/560; retain framing; output 960x720 with approximately 393px active picture and black bars.';s['reference_display']='User reports 320x240 letterbox presentation. Calibrated against round photosphere; source decoded dimensions remain separate.'
s.frame_set(121);bpy.ops.wm.save_as_mainfile(filepath=str(p/'opening-letterbox.blend'))
s.render.resolution_x=640;s.render.resolution_y=480;s.cycles.samples=8;s.render.filepath=str(p/'blender-check.png');bpy.ops.render.render(write_still=True)
print('COMPOSITOR_RESULT',bpy.data.images['Render Result'].size[:])
