# Migration records

- `files.json`: exact original paths, destination paths, ownership and SHA-256 baseline.
- `issues.json` / `issues.md`: verified original-to-destination GitHub issue mapping and dependency references.
- `import_from_game.py`: one-time import recipe. It refuses to overwrite an existing source import.

Historical bare issue numbers in preserved metadata and documentation refer to `ender-dev-pl/ed-openfa-game`. Use the issue crosswalk instead of interpreting those numbers as current local issue IDs. Old GitHub issue URLs redirect to transferred issues. Historical body text and milestone history are retained; migrated work is not automatically marked complete.

Mixed game-integration issues #940 and #195 remain in the game repository and link to this project's migration tracker. The pure 3D authoring/reference/model-verification issues have been semantically reviewed for transfer. Runtime missile/combat/rendering issues remain game-owned.
