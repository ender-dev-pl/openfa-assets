# Rigellian building source review

Tracked in [#970](https://github.com/ender-dev-pl/ed-openfa-game/issues/970), relates to #948, #946 and the RI01 study #969.

`prepare_rigellian_building_references.py` decodes the actual archived RI01..RI23 `.256` payloads and their embedded VGA palettes. The committed `rigellian-building-references.json` preserves every ID, definition class, footprint, source/index/palette hash, nonempty layer PNG hash, empty-layer descriptor and selected catalogue phase hash. All original pixels, derived reference sheets and temporary payloads remain under ignored `artifacts/rigellian-building-reference-study/`.

Coverage is 23 definitions, 126 surface descriptors (123 nonempty), and 23 catalogue videos with 41 frames each. The video decoder exports all 943 frames; phases 0, 10, 20, 30 and 40 are indexed for comparison. Three empty descriptors are retained explicitly: RI10 layers 15 and 16, and RI22 layer 1. Empty descriptors are not missing models or zero-sized images to invent replacements for.

## Visual findings and mechanisms

The complete surface/catalogue sheet was inspected. Separate phase and layer sheets were inspected for RI02, RI10, RI18, RI22 and RI23. RI02's video shows a blank presentation, a coarse reveal, the readable body, a red outline and highlighted features at the same spatial view. This is consistent with the previously reviewed RI01 sequence; it does not provide five camera angles. Review of all remaining phase sequences is still required before per-model acceptance.

The five 18-descriptor sheets require different mechanisms:

| Source | Definition / class | Observed source progression | Current runtime evidence |
| --- | --- | --- | --- |
| RI10 | Ground Deck / 26 | Paired doors open over a deep hangar-access shaft with vertical wall features; two empty pause descriptors; final image includes purple ground pixels | Not in directional-body allowlist; activity selector is a separate path |
| RI18 | Missile Launcher / 14 | Upper shell opens into a visible circular mouth; final image includes purple ground pixels | Not in directional-body allowlist; silo launch selector is separate from heading selection |
| RI19 | Thermal Lance / 17 | Separate extra layers require review as an assembly, rather than substituting the largest layer for the body | Explicitly in directional-body allowlist |
| RI22 | Ex-Fang / 40 | Changing orientation of dish/support assembly; static layer 1 is empty | Explicitly in directional-body allowlist |
| RI23 | Ultrathermal Lance / 18 | Twin gold emitters change projected direction over a green body and gold foundation | Explicitly in directional-body allowlist |

The code evidence is `LegacyBuildingSpriteFrameSelector.cs` and `legacy-gameplay.json` (hashes recorded). The selector documents recovered `UpdateBuildingTurretSpriteFrame` at FRAGILE.LE:0x44B80, distinguishes static descriptor 1 from heading descriptors 2..17, and has independent activity/launch selectors. Matching class numbers and visible progression guide further investigation; cross-culture launch timing and attachment mapping are not proven solely by these sheets.

Diagnostic composites use decoded offsets, layer 1 followed by one extra layer, and index-zero transparency. They are explicitly labelled diagnostic overlays. They do not claim to reproduce the original runtime's shadow ramps, purple mixed-colour composition, layer ordering in every state or activity selection. The 16 additional layers must not automatically be labelled 16 rotations for all five buildings. The generic inventory `rotation-video` source-kind label likewise does not establish that alien hologram videos are turntables.

## Next reconstruction: RI02 Filtration Plant

Identity is `openfa:building/legacy/041`, Rigellian, footprint 2x2, definition class 38. Source evidence shows a broad rounded lower body, tapered shoulder, narrower capped upper tower, six gold front ports in two columns, a smaller gold upper feature, lower vertical slots and a taller side channel. These features are visible in both the surface body and readable/hilighted catalogue phases. Hidden back surfaces, pipe routing, internal mechanism and exact dimensions remain inferred.

The new model must include material-appropriate wear under the instruction dated 2026-10-29: localized joint dirt, stains, abrasion and small dents, while preserving silhouette and equipment legibility. Original pixels remain reference-only. No RI02 high-detail model, animation, artistic acceptance or runtime integration is delivered by this reference milestone.

Reproduce/check using the existing legacy Python/Pillow/Unicorn runtime:

```powershell
& ../legacy/system/python/python.exe tools/blender/prepare_rigellian_building_references.py
& ../legacy/system/python/python.exe tools/blender/prepare_rigellian_building_references.py --check
```

This is an analytical source milestone; no application or model runtime changed.
