"""Analytical fresh-chain model of 0x449F0; not an application state implementation."""


def scaffold_chain(completed_updates,remaining_updates,resource_limit,frames_per_tier,scale_byte=0):
    if frames_per_tier not in [2,4,8,16]:
        raise ValueError('Expected observed construction tier capacity')
    if not 1<=resource_limit<=255 or not 0<=scale_byte<=255:
        raise ValueError('Expected byte resource limit and scale')
    if not 0<=completed_updates<=255 or not -128<=remaining_updates<=127:
        raise ValueError('Construction definition is unsigned; remaining counter is signed')
    stage=min(resource_limit,max(1,completed_updates-remaining_updates+1))
    scale=((scale_byte-1)&255)+1
    full,partial=divmod(stage,frames_per_tier)
    frames=[frames_per_tier]*full+([partial] if partial else [])
    # Decompile writes signed 16.16 screen Y; smaller Y is higher on screen.
    step_fixed=(frames_per_tier*8//2)*256*scale
    return [dict(frame=frame,screen_y_offset_fixed=-level*step_fixed,
                 screen_y_offset_pixels=-level*step_fixed/65536) for level,frame in enumerate(frames)]
