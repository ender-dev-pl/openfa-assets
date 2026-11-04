# Historical migration records

- `files.json`: frozen import provenance, original paths, then-current destinations and SHA-256 values.
- `issues.json` / `issues.md`: verified original/new GitHub issue identities and dependencies.
- `import_from_game.py`: the one-time recipe used for the initial import. It describes that historical layout, not the current project organization. It is not called by authoring preparation.
- `validation/`: evidence of the completed initial migration, not a moving report of future work.

Use `project/layout.json` for current destinations, semantic roles and explicit retirements. `python tools/asset_workspace.py audit-import` compares retained current files with the original import while reporting retired inputs separately. Intentional future source changes need current verification; they must not be concealed by changing historical import hashes.

Historical bare issue numbers in preserved metadata refer to `ender-dev-pl/ed-openfa-game`; resolve them through the issue crosswalk. Old GitHub URLs redirect to transferred issues. Historical bodies, comments and milestone history are retained, and no model is automatically marked complete by migration or reorganization.
