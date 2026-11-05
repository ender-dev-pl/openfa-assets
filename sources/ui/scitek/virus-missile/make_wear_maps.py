"""Authored paint wear for newly reconstructed pods/fins, never reference pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
import random,math,sys
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=True)
def srgb(v):return round(255*(12.92*v if v<=.0031308 else 1.055*v**(1/2.4)-.055))
for index,(name,base) in enumerate([('sensor-violet',(.16,.11,.23))]):
 rng=random.Random(20832+index);im=Image.new('RGB',(256,256));pixels=[]
 for y in range(256):
  for x in range(256):
   shade=.88+rng.random()*.17;shade*=1-.23*math.exp(-((y-248)/15)**2)
   pixels.append(tuple(srgb(min(1,c*shade)) for c in base))
 im.putdata(pixels);draw=ImageDraw.Draw(im)
 for i in range(170):
  x=rng.randrange(256);y=rng.randrange(256);length=rng.randrange(1,9)
  colour=(120,123,113) if i%3==0 else tuple(srgb(c*.45) for c in base)
  draw.line((x,y,x+length,y+rng.choice([-1,0,1])),fill=colour,width=1)
 if name=='fin-green':
  for i in range(70):
   x=rng.randrange(247,256);y=rng.randrange(256);draw.line((x,y,255,y+1),fill=(133,139,127),width=1)
 im.save(out/(name+'.png'))
print('VIRUS_NEW_PART_WEAR_MAPS_CREATED')
