# Project Skills

This folder contains **project-specific** skill definitions as plain `.md`
files. Unlike `default-skills/`, which holds organization-wide rules applied
to every repository, this folder is for skills that are unique to the
particular project this `.claude/` configuration lives in.

## How It Works

Claude Code automatically loads `.claude/CLAUDE.md` at the start of every
session. The `CLAUDE.md` file includes instructions to scan this
`project-skills/` folder for any `.md` files (excluding this `README.md`)
and follow the skill instructions contained within them. This means you can
add new project-specific skills simply by dropping a `.md` file into this
folder — no other configuration changes are required.

## When to Use This Folder

Use `project-skills/` for skills that:

- Are specific to this project and would not apply to other repositories
- Define project-specific coding conventions, patterns, or workflows
- Describe domain-specific rules (e.g., API naming conventions, database
  migration patterns, deployment procedures)
- Provide context about the project's architecture that Claude should
  always consider

## When NOT to Use This Folder

Do **not** place skills here if they:

- Should apply to all repositories in the organization — use
  `default-skills/` instead and register them in the central skills registry
- Contain sensitive data such as credentials or secrets
- Duplicate rules already covered by `default-skills/`

## Adding a New Project Skill

1. Create a `.md` file in this directory with the skill instructions.
   Use a descriptive filename (e.g., `api-naming-conventions.md`,
   `database-migration-rules.md`).
2. Write clear, concise behavioral rules in the file — the same format
   used by `default-skills/` files.
3. Commit and push. The skill will be active for all Claude Code sessions
   in this project from the next session onward.

## Example Skill File

```markdown
# API Naming Conventions

When creating or modifying API endpoints in this project:

- Use kebab-case for URL paths (e.g., `/user-profiles`, not `/userProfiles`)
- Use camelCase for JSON request/response body fields
- Prefix all internal API routes with `/internal/`
- Include API version in the URL path (e.g., `/v1/users`)
```

## File Format

- Files must use the `.md` extension
- `README.md` in this folder is excluded from skill loading
- Each file should focus on a single skill or closely related set of rules
- Keep files concise and actionable

## Relationship to Default Skills

| Folder | Scope | Managed By | Synced Centrally |
|--------|-------|------------|------------------|
| `default-skills/` | Organization-wide | Platform engineering team | Yes (via skills registry) |
| `project-skills/` | This project only | Project team | No |

Project skills are loaded **in addition to** default skills. If a project
skill conflicts with a default skill, the project skill takes precedence
for this repository.
