After completing all tasks in a repository, Claude Code MUST check whether a `README.md` file exists in the repository root. If none exists, create one with comprehensive repository details including the project purpose, setup instructions, usage examples, and dependencies.

## Required Behaviour

1. **Root README** — If the repository root has no `README.md`, create one that covers:
   - Project name and description
   - Prerequisites and installation steps
   - Usage instructions and examples
   - Configuration details (if applicable)
   - Project structure overview
   - License information (if a licence file exists)

2. **Subdirectory READMEs** — Scan the repository for directories and subdirectories that would benefit from their own `README.md` (e.g. directories containing modules, utilities, or distinct components). Create a `README.md` in each one explaining the directory's purpose, contents, and how it relates to the rest of the project.

3. **Existing READMEs** — If a `README.md` already exists, do not overwrite it. Only update it if the completed task has changed information that the README covers (e.g. new dependencies, changed usage, new directories).

## When This Skill Applies

- After completing all tasks in a session, as a final step.
- When creating a new repository or adding significant new structure to an existing one.
