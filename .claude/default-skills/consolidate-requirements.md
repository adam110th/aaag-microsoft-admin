# Consolidate Requirements Files

After completing any task that adds, removes, or updates dependencies in any subfolder's `requirements.txt` (or equivalent dependency file), Claude Code MUST merge all subfolder dependencies into the root-level `requirements.txt`.

## Required Behaviour

1. **Single source of truth** — The root `requirements.txt` is the authoritative list of all project dependencies.

2. **Merge on change** — After modifying any `requirements.txt` in a subfolder (e.g. `data_prep/requirements.txt`), merge its contents into the root `requirements.txt`.

3. **Section comments** — Preserve section comments indicating which subfolder each group of dependencies originated from:
   ```
   # --- From: data_prep/requirements.txt ---
   ```

4. **De-duplicate** — If the same package appears in multiple subfolders, keep the highest pinned version in the root file.

5. **Consistent formatting:**
   - Pin direct dependencies with `==`.
   - Keep optional or commented-out dependencies as comments.
   - Group dependencies by category with blank lines between groups.

6. **New subfolders** — When a new subfolder is created that contains its own `requirements.txt`, add a new section to the root file.

7. **Removed dependencies** — When a dependency is removed from a subfolder, also remove it from the corresponding section in the root file (unless another subfolder still requires it).

## When This Skill Applies

- Any time a `requirements.txt` in a subfolder is created, modified, or deleted.
- When scanning the project after completing a task (per the auto-update common files skill).
