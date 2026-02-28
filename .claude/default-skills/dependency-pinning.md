When Claude Code creates or updates dependency files (`requirements.txt`, `package.json`, `Gemfile`, `go.mod`, `Cargo.toml`, etc.), all dependencies MUST be pinned to specific versions or use compatible-release specifiers.

## Required Behaviour

1. **Python `requirements.txt`** — Use `==` for all direct dependencies (e.g. `requests==2.32.3`).

2. **Node.js `package.json`** — Use `^` (caret) ranges (e.g. `"express": "^4.18.2"`).

3. **Other languages** — Use the language's equivalent of compatible-release specifiers (e.g. `~=` in Python's `pyproject.toml`, `~>` in Ruby's `Gemfile`).

4. **Never leave unpinned** — Do not use `>=` without an upper bound, bare package names without versions, or `*` wildcards.

5. **Check current versions** — When adding a new dependency, check the current latest stable version and pin to that version. Do not guess or use outdated versions.

## Why

Unpinned dependencies cause non-reproducible builds. A dependency update can silently break a project days or weeks after the code was last working.

## When This Skill Applies

- Every time Claude Code adds, removes, or modifies entries in a dependency file.
