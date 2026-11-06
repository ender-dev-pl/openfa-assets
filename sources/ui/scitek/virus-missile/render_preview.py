"""Render the actual authored Long Range Transmitter turntable, preserving source identity."""
import bpy,sys,json,hashlib
from pathlib import Path
source=Path(sys.argv[sys.argv.index('--')+1]).resolve();out=Path(sys.argv[sys.argv.index('--')+2]).resolve();out.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(source));s=bpy.context.scene;s.cycles.samples=8;s.render.resolution_x=320;s.render.resolution_y=360;s.render.film_transparent=False
# Keep studio illumination on the object but match legacy's black film canvas.
nt=s.world.node_tree;output=next(n for n in nt.nodes if n.type=='OUTPUT_WORLD');previous=output.inputs['Surface'].links[0].from_socket
black=nt.nodes.new('ShaderNodeBackground');black.inputs['Color'].default_value=(0,0,0,1);black.inputs['Strength'].default_value=1
path=nt.nodes.new('ShaderNodeLightPath');mix=nt.nodes.new('ShaderNodeMixShader');nt.links.new(path.outputs['Is Camera Ray'],mix.inputs[0]);nt.links.new(previous,mix.inputs[1]);nt.links.new(black.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],output.inputs['Surface'])
for frame in range(1,61):
    s.frame_set(frame);s.render.filepath=str(out/f'{frame-1:03}.png');bpy.ops.render.render(write_still=True)
(out/'proof.json').write_text(json.dumps(dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),renderer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),frames=60,fps=15),indent=2)+'\n')
print('TRACKER_PREVIEW_RENDERED')
