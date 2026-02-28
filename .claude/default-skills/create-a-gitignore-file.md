When Claude Code works on a repository, if no `.gitignore` file is present, one MUST be created before any other work begins.

## Required Behaviour

1. **Tailored to the project** — The `.gitignore` must include rules appropriate for the languages, frameworks, and tools used in the repository (e.g. Python, Node.js, Go, Java). Use standard community `.gitignore` templates as a baseline.

2. **IDE and OS files** — Include rules for common IDE directories (`.vscode/`, `.idea/`, `*.suo`, `*.user`) and OS-generated files (`.DS_Store`, `Thumbs.db`, `desktop.ini`).

3. **Secrets and environment files** — Always include `.env`, `.env.*`, `*.pem`, `*.key`, and other common secrets file patterns.

4. **Custom ignores section** — Add a clearly marked section at the bottom of the file for custom project-specific ignore rules:
   ```
   # ===== Custom Ignores =====
   # Add project-specific rules below this line.
   ```
   If the `.gitignore` is updated in the future, this section MUST be retained.

5. **Existing `.gitignore`** — If a `.gitignore` already exists, do not overwrite it. Only add missing rules and ensure the custom ignores section is present.

## When This Skill Applies

- At the start of any task in a repository that does not have a `.gitignore` file.
- When checking common files after completing a task (per the auto-update common files skill).
