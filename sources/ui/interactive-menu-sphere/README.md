# Interactive menu sphere — #193

Assets only. Derived from the actual legacy-referenced refined menu scene; no client behavior is implemented.

`interactive-sphere.blend` retains editable procedural materials, wear and a 1.2-second demonstration with quaternion rotation and an emissive pulse. `interactive-sphere.glb` contains explicit PBR materials and node rotation animation. glTF material animation is not portable: the client must drive the pulse separately. Exported PBR materials approximate the procedural Blender appearance.

Rotate `SphereRotor` about its origin; keep `SphereBezel` stationary. Core radius is 1.24, pivot is the geometric centre, neutral front faces +Z. Choose a normalized random axis per click and use angle `2*pi*smoothstep(progress)`. Restore the neutral quaternion at completion. Front and rear emblems are closed continuous meshes; the rear reflects the front through the XY plane with corrected winding. This uses the permitted mirrored-logo option, not the bootscreen alternative.

Pulse emblem emission from 0.331 to 3.331 and back with `0.331 + 3*sin(pi*progress)^2`. The client should handle this intent in its presenter/model and preserve its existing dome navigation behavior. Menu-context rail color remains independent.

Source reopen and render, independent GLB import and render, two manifold emblem checks, plus changed-code quality gate passed. Proof frames show front, rear, side and five spin phases. These are Blender runtime proofs, not game integration proofs.

Build: Blender 4.5.15, `blender -b -t 4 --python build_sphere.py -- OUTPUT_DIRECTORY`. The derivation expects the local refined source scene at the sibling issue-176-menu-refinement work path; for standalone reproduction change that input to `sources/ui/legacy-main-menu-refined/main-menu.blend`.
