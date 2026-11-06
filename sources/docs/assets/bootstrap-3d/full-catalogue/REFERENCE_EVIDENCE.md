# Full building catalogue reference inventory

Tracked in #943. The installed package has 177 definitions: Terran 40, Rigellian
23, Braccatian 23, Mikotaj 21, Artemian 23, Mauna 21 and Achaean 26.
`recipes.json` preserves every package ID, global type, culture and footprint.

Terran PB previews are rotation videos from `_MA`. Other cultures use `_ZOOM`
holographic presentation videos whose interface and false-colour effects must
not be mistaken for the actual building materials. Their `_B` surface sheets
provide the material/shape evidence. Directional weapons can require both the
static base and a separate heading frame; inspecting frame one alone can show
an incomplete or blank structure (notably RI22 and the Achaean weapon towers).
The reference inventory records the composed frames, hashes and source roles.

Reference contact sheets for all seven cultures were inspected. Each explicit
recipe table row records the observed silhouette and authored parameters; hidden
interiors and ambiguous small details remain modelling choices. Parts are expanded
into editable solids, not pixel extrusion or a texture-painted proxy. Shared
assembly vocabulary represents related building families. The five detailed
studies from #942 are preserved and reused rather than replaced by coarse copies.

All original reference images/decoded videos stay in the ignored
`artifacts/issue-943-catalogue/references/` directory. Only their provenance and
newly authored shape recipes are tracked here. No original images or meshes are
distributed in these model sources.

Reference preparation (requires the existing legacy Python/Pillow/Unicorn runtime):

```powershell
& ../legacy/system/python/python.exe tools/blender/prepare_catalogue_references.py `
  --legacy-root ../legacy
python tools/blender/author_catalogue_recipes.py
```

## Directional source assemblies (#944)

`LegacyBuildingSpriteFrameSelector` and `legacy-gameplay.json` identify the
runtime heading path and its 16 body frames (2–17), independently composed over
the static descriptor. All nine IDs in the current runtime allowlist are covered
by the authored rigs. The export also covers all authored barrel weapons and
catalogue classes 3, 17, 18, 27 and 40 across cultures; this broader source-model
capability does not enable them in the runtime by itself.

The reference sheet shows a defensive gun cap on PB31 and PB33. The original
recipes had represented this only with an aerial; the rig pass adds independently
authored cupola/barrel solids, while preserving the fixed panels/storage body.
RI22 separates its rotor panels from the support. MK21 rotates the authored
crystal emitter assembly over its foundation, rather than inventing a barrel.
Exact pivots and hidden mechanical details are modelling choices inferred from
the visible assemblies; the files are not recovered original rig data.
