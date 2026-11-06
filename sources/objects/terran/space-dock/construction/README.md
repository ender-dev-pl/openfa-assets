# PS7C construction state (#216)

Contains the exact shared core from `../refined/model.blend` plus the resized
existing scaffold, temporary shields and local `ConstructionActivity` carriage.
See the [shared model contract](../refined/README.md) and both source-bound runtime
reports. The six-second clip retains authored timing; no legacy operating cycle
is claimed. The source files preserve the earlier #192 construction study.

Use this state for actual construction, with the finished model's placement root
and common core scale. The scaffold overhang is not a reason to renormalize the
station's size independently. The main game thread must verify actual client
placement, GPU appearance, construction transitions and equipment attachments.
