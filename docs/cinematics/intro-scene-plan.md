# Remaining intro: sequential basic reconstruction

Original frames **413–1873**, after the completed first sequence. Full film: 1874 original frames, 3748 output frames at 24fps (156.1667s).

The first pass establishes editable scene geometry, camera cuts, silhouettes, main props and motion. Refining facial likeness, detailed surfaces, exact typography and effects is deferred. Original pixels are evidence, never replacement background textures.

| ID | Original frames | Scene | Milestone |
|---|---:|---|---|
| E1 | 413–447 | Interrupted transmission | transmissions |
| F | 448–606 | Officer broadcast | transmissions |
| E2 | 607–641 | Interference before portraits | transmissions |
| H1 | 642–678 | Parrilo Salaria rotating bust | portraits |
| H2 | 679–738 | Marcissus Salaria framed portrait | portraits |
| H3 | 739–761 | Lynn Salaria cameo | portraits |
| H4 | 762–791 | Dramon Salaria admiral | portraits |
| I | 792–958 | Warship under attack | battle |
| J | 959–978 | Escape through explosions | battle |
| K | 979–1072 | Council audience | council |
| L | 1073–1147 | Document signing | council |
| E3 | 1148–1194 | Interrupted council transmission | alien |
| M | 1195–1301 | Alien broadcast front | alien |
| N | 1302–1384 | Alien broadcast profile | alien |
| O | 1385–1443 | Alien broadcast closeup | alien |
| E4 | 1444–1492 | Interrupted alien transmission | alien |
| P | 1493–1664 | Laboratory pan | laboratory |
| Q | 1665–1731 | Handheld display | laboratory |
| R | 1732–1764 | Overhead machine approach | ending |
| S | 1765–1873 | Final emblem and flare | ending |

Ranges are inclusive and zero-based. One-frame black samples occur at several decoded cuts; the plan retains them as observed, without asserting playback intent. The officer broadcast has an internal closer-camera cut at 555; the battle includes a foreground pass near 916.

Each major milestone is rendered/inspected in actual Blender, committed and pushed before the next. Native scenes remain separate. Static GLB imports are geometric interchange checks only; material baking and real-time game integration are outside this pass.

[Source plan](../../sources/docs/assets/cinematics/intro/remaining-basic/shot-plan.json) · [Previous source checkpoint](intro-reconstruction.md)

## Basic pass completed

All twenty planned remaining shots are built as independent editable Blender scenes, with static GLB geometry checks and inspected three-frame previews. The full assembly contains 24 scene strips including the preserved first sequence, spans native frames 1–3748 at 24 fps, and retains the first sequence's three cross-dissolves. The new shots use their observed cut boundaries; later matching of transitions and distortion is deferred.

See [complete source and rebuild instructions](../../sources/docs/assets/cinematics/intro/remaining-basic/README.md), [full editable assembly](../../sources/docs/assets/cinematics/intro/remaining-basic/full-intro-basic.blend), and [per-shot source plan](../../sources/docs/assets/cinematics/intro/remaining-basic/shot-plan.json). The review proxy is silent and sampled at 6 fps; native scene animation remains 24 fps.
