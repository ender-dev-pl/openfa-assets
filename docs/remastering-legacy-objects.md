# Remastering legacy 3D objects

This policy applies to remastered 3D buildings, ships, and trading goods, together with their associated blueprints, construction or operational animations, and other object-specific visual elements. It governs new remasters and explicitly requested revisions; it does not require retroactive changes to completed models.

## Source hierarchy

1. **Primary visual reference:** the correctly paletted legacy sprite depicting the specific object at the highest resolution available in the original assets. Inspect all available representations, including surface presentation, overview presentation, and detail views. Choose the representation that carries the most object-specific visual information as the primary reference; record other useful variants as supporting evidence. The largest pixel dimensions alone do not decide between variants when a smaller view reveals more structure. Preserve visible silhouette, proportions, colour placement, distinctive components, and known animation states. Record unresolved or contradictory details rather than inventing them as fact.
2. **Additional source evidence:** the game's language package and `.cdb` databases. Use object descriptions, function, cultural context, materials, and any stated physical dimensions to explain and constrain the design. Record the exact file, record or identifier, and relevant text for claims used in the remaster. General culture lore informs interpretation but does not override an object-specific sprite or description.
3. **Authored interpretation:** details absent from the source evidence may be designed to make the object coherent in 3D. Identify these choices as interpretations. Do not present ImageGen output or an earlier model as recovered legacy evidence.

Original pixels remain reference material; follow [provenance and media rules](provenance.md) when recording or publishing evidence.

## Required production sequence

1. **High-resolution concept image.** Supply ImageGen with the selected legacy sprite as an image reference and the relevant language-package and `.cdb` lore. Generate a high-resolution image of the same object before beginning its new 3D model. Review it against the source sprite and lore, revise conflicts, and retain the selected result with its prompt, source identifiers, and notes on interpreted details. The concept develops the reference; it does not replace it.
2. **Editable 3D source.** Create a `.blend` model of the object from the reviewed concept and original evidence. Use physical dimensions stated by the sources. When dimensions are absent or incomplete, document the scale assumption and its basis; do not claim an invented measurement as canonical. Keep meaningful parts, materials, pivots, attachments, and animated components editable. Add material- and function-appropriate wear to newly created objects while retaining a readable silhouette and markings.
3. **Export and related elements.** Export the approved model as `.glb`. Create associated blueprints and animations from the same geometry, scale, identity, and source interpretation. Retain the editable source and any authored inputs needed to reproduce the exports. Preserve earlier accepted iterations when refining an object.

## Review and acceptance

- Compare the concept, actual Blender renders, and independently imported GLB against the selected legacy sprite and supporting variants. Check silhouette, distinctive details, colours, material roles, scale, and any known animation states.
- Open the editable `.blend` and import the `.glb` in Blender's actual runtime. Inspect the rendered result; file presence, polygon counts, and a successful export alone do not establish visual acceptance.
- Record the selected sprite variant and why it was preferred, lore citations, known dimensions or scale assumptions, concept image and prompt, authored deviations, source and export paths, and verification results. Keep original-game media outside published authored sources as required by [provenance](provenance.md).
- Follow the [authoring workflow](workflow.md) for workspace preparation, publication locations, and project checks. A finished model does not by itself establish gameplay integration acceptance.

## Reference examples

The [Rigellian ships](../gallery/ships-rigellian.md) and [Federal Transporter IS0C](../gallery/ships-shared.md#federal-transporter-is0c) are accepted examples of remaster quality and presentation. Their individual source evidence still determines each new object's design; the examples are not universal geometry or material templates.
