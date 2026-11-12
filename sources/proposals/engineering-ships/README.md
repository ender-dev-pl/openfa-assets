# Engineering ship proposals — issue #265

Fourteen new authored OpenFA asset proposals: Terraforming Ship and Repair / Construction Assist Ship for seven cultures. These are not recovered legacy units. The selected supplied concepts and their identities are in `concepts.json`.

This directory is deliberately separate from canonical legacy unit catalogues. No unit, blueprint, production route, client package or game mechanic is registered by these files. Model dimensions use provisional proposal units; production and hangar clearance need a separate future integration decision.

Each completed model has editable named tool pivots, authored material maps, a looping four-second `ToolOperation` animation, a Blend source and GLB export. Normal flight can keep the tools in their first-frame pose; the clip demonstrates articulation only. No behaviour is automatically enabled in OpenFA.

The runtime verifier opens the saved Blend and independently imports GLB, checks closed geometry and a physical support graph at six animation poses, compares animated surfaces and texture pixels, verifies a single exported clip, and renders both playback paths. This does not certify swept collision avoidance between every pair of intermediate frames or establish gameplay acceptance.

Run author scripts with Blender and `--root` pointing to this asset repository. Run `verify_engineering_proposal.py -- --culture <culture> --role terraform|repair`. Publish encoded previews with `publish_engineering_proposals.py`; it requires FFmpeg and FFprobe. These asset-specific scripts and resulting assets have the asset license specified by the repository licensing policy.

The dedicated [proposal gallery](../../../gallery/engineering-proposals.html) shows only models with current runtime evidence. Concepts without a finished model remain proposals, not completed assets. Older concept iterations remain in the private evidence workspace.
