After completing any task in a repository, Claude Code MUST check whether the repository's common files need updating.

## Required Checks

1. **`.gitignore`** — Verify the `.gitignore` is tailored to the languages and frameworks used in the repository. If new languages, tools, or output directories have been introduced by the task, add the appropriate ignore rules. Retain any custom ignore rules in a clearly marked section at the bottom of the file.

2. **`README.md`** — Check whether the root `README.md` accurately reflects the current state of the repository. If the task changed entry points, dependencies, usage instructions, or architecture, update the README accordingly. Also check any `README.md` files in subdirectories and update them if they are affected by the changes.

3. **Dependency files** — For Python projects, check whether `requirements.txt` needs updating (new imports, removed packages, version changes). For other languages, check the equivalent dependency file (`package.json`, `Gemfile`, `go.mod`, `Cargo.toml`, etc.).

4. **CI/CD configs** — If the task introduced new test files, changed the project structure, or added dependencies that require build steps, verify that CI/CD workflow files (e.g. `.github/workflows/`) still reflect the project accurately.

5. If the github repository is public, it is mandatory that the GPL license is applied, not MIT.

## When This Skill Applies

- After completing any task that modifies code, adds files, or changes project structure.
- This is a post-task check — perform it after the primary work is done, not before.