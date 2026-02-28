When Claude Code reviews or works on a repository, create or update an internal knowledge map file at `.claude/codebase-knowledge.md` to store structured information about the repository. This file enables Claude Code to understand and navigate the codebase more quickly in future sessions.

## When to Create or Update

- On the **first session** in a repository that does not yet have a `.claude/codebase-knowledge.md` file, perform an initial scan and create it.
- On **subsequent sessions**, review the file at the start and update it after completing tasks if the codebase has changed (new files, renamed modules, updated dependencies, architectural changes).
- After **major refactors, new feature additions, or dependency changes**, update the relevant sections.

## What to Include

The `.claude/codebase-knowledge.md` file should contain the following sections:

### 1. Repository Overview
- Repository name, purpose, and a one-line description.
- Primary languages and frameworks used.
- License type (if present).

### 2. Architecture and Structure
- Top-level directory layout with brief descriptions of each folder's purpose.
- Key architectural patterns (e.g. MVC, microservices, monorepo, plugin-based).
- Module or package boundaries and how they relate to each other.

### 3. Entry Points
- Main entry points for the application (e.g. `main.py`, `index.ts`, `cmd/server/main.go`).
- CLI commands or scripts used to run, build, or test the project.
- Key configuration files and their roles (e.g. `webpack.config.js`, `pyproject.toml`, `Makefile`).

### 4. Key Components
- Core classes, modules, or packages and their responsibilities.
- Important interfaces, abstract classes, or traits that define contracts.
- Data models and database schema locations (if applicable).

### 5. Dependencies and Tooling
- Dependency management file(s) and their location (e.g. `requirements.txt`, `package.json`, `go.mod`).
- Notable third-party libraries and what they are used for.
- Build tools, linters, formatters, and test frameworks in use.

### 6. Development Patterns and Conventions
- Naming conventions (file naming, variable naming, branch naming).
- Code organization patterns (where new features go, test file placement).
- Error handling patterns used across the codebase.
- Logging approach and configuration.

### 7. Testing
- Test framework(s) used and how to run tests.
- Test directory structure and naming conventions.
- Notable test utilities or fixtures.

### 8. CI/CD and Deployment
- CI/CD platform and workflow files (e.g. `.github/workflows/`, `.gitlab-ci.yml`).
- Deployment targets and processes (if evident from configuration).
- Environment-specific configuration handling.

### 9. Known Quirks and Gotchas
- Non-obvious behaviors, workarounds, or legacy patterns.
- Areas of technical debt or planned refactors (if documented).
- Platform-specific considerations.

## Formatting Rules

- Use Markdown with clear headings for each section.
- Keep entries concise — one to two sentences per item.
- Use bullet points or short tables, not long prose.
- Include file paths relative to the repository root.
- Omit sections that do not apply to the repository rather than leaving them empty.
- Do not include sensitive data such as API keys, tokens, or credentials.

## File Location and Git Behavior

- Store the file at `.claude/codebase-knowledge.md` so it lives alongside other Claude Code configuration.
- This file **should be committed** to the repository so that all Claude Code users and sessions benefit from the shared knowledge.
- If the repository's `.gitignore` excludes `.claude/`, note this in the file header and inform the user that the knowledge map will be session-local only.
