# Game-rendered construction previews

[Seven playable examples](../gallery/construction-animations.html) show one existing building per culture. Each 15-second clip erects its scaffold, inserts the completed building at full height, then removes the scaffold in reverse order. The building remains visible during removal. Playback controls support seeking and looping; only one clip plays at a time.

These are authored asset-studio sequences, not recordings of live gameplay. Timing is illustrative. The simulation/presenter integration remains separate. A neutral studio plinth is not a test colony.

The host calls the actual `OpenFA.Client.MonoGameSurfaceModelRenderer.RenderStudioProof` implementation, including its PBR materials, studio lighting, shadows and ambient occlusion. Blender only composes and exports the real source GLBs; it does not render these videos. PNG frames come from OpenFA's MonoGame GPU renderer. FFmpeg encodes them as 640×720, 30-fps VP9 WebM, adding phase captions outside the rendered image.

The renderer was loaded from the local game's built assemblies, whose informational version is `1.0.0+528b1f47f9ec26785693b2e4fba2975a6affc46a`. This identifies the binaries actually used, rather than assuming they match the current game checkout. Every clip preserves engine assembly hashes, GPU adapter, input hashes, camera, stage order, frame hashes, encoding parameters and generator/host hashes alongside its video. The authoring host uses the game's existing `OpenFA.ModelRenderProof` friend-assembly API; it changes no game source.

| Culture | Building | Family |
| --- | --- | --- |
| Terran | Living Quarters | PBS2 |
| Rigellian | Filtration Plant | RIS2 |
| Braccatian | Eyes-in-the-Sky | BRS2 |
| Mikotaj | Purity | MKS2 |
| Artemian | Nurseries | ARS2 |
| Mauna | Launch Area | MNS2 |
| Achaean | Habitat | ACS2 |

Source models remain unchanged. Preview composition uniformly fits each building into the clear scaffold footprint, and vertically calibrates the scaffold to enclose that building. Each sequence records these transforms. Temporary crown/shoring meshes listed by the integration contract are hidden when the building is inserted. The common camera is fixed throughout each cycle.

## Reproduction

Requires Blender 4.5 LTS, .NET 8, FFmpeg/ffprobe, Python with Pillow, and an already built sibling `openFA-game` DesktopGL runtime. Build that runtime using the game repository's instructions, in single-node mode with build servers/shared compilation disabled. The preview project defaults to `../openFA-game/src/OpenFA.Client/bin/Debug/net8.0`; override `OpenFaRuntimeRoot` when necessary.

From the assets repository:

```powershell
python tools/asset_workspace.py prepare
python tools/asset_workspace.py blender --blender <blender.exe> -- tools/blender/prepare_construction_previews.py --output <absolute-frames-directory>
dotnet build tools/ConstructionPreview/ConstructionPreview.csproj -c Release -m:1 --disable-build-servers -p:UseSharedCompilation=false
$cultures = 'terran','rigellian','braccatian','mikotaj','artemian','mauna','achaean'
foreach ($culture in $cultures) {
    dotnet tools/ConstructionPreview/bin/Release/net8.0/OpenFA.ModelRenderProof.dll <absolute-frames-directory>/$culture/sequence.json <absolute-frames-directory>/$culture/rendered
}
python tools/build_construction_videos.py <absolute-frames-directory>
python tools/verify_construction_videos.py
```

Finished clips, posters and provenance are preserved in `gallery/media/construction-cycles/`; `index.json` links the seven records. Intermediate GLB archives and uncaptioned PNGs are working artifacts under `artifacts/issue-189/frames/`. The verifier decodes all 3,150 video frames, checks durations/codecs/dimensions, source and tool hashes, ascending/reverse stages and building/scaffold visibility contracts. Actual renderer execution is evidenced separately by each clip's runtime record.
