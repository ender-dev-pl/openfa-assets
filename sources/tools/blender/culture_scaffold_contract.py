"""Source-derived ranges and explicit user-requested scaffold presentation order."""
import math


def chain(stage,capacity):
    if stage<1 or capacity<1:raise ValueError('Positive stage and capacity required')
    return [capacity]*(stage//capacity)+([stage%capacity] if stage%capacity else [])


def recipe(family,references):
    reference=next(f for f in references['families'] if f['key']==family['family'])
    capacity=reference['descriptor_count']-1
    size=reference['footprint_class']
    width=reference['descriptors'][-1]['size'][0]
    pitch=capacity*4/width*(size*.9*math.sqrt(2))/math.sqrt(2/3)
    return reference,capacity,size,pitch


def phases():
    return [dict(id='erection',building_visible=False),dict(id='reveal',building_visible=True),
            dict(id='dismantling',building_visible=True),dict(id='complete',building_visible=True,scaffold_visible=False)]


def definitions_for(family,limits):
    result=[]
    for record in limits['records']:
        if record['family']!=family:continue
        ceiling=record['max_stage_while_constructing']
        result.append(dict(id=record['id'],name=record['name'],ceiling=ceiling,
                           erection_stages=list(range(1,ceiling+1)),dismantling_stages=list(range(ceiling,0,-1))))
    return result
