**MANDATORY — EXECUTE BEFORE ANY OTHER OUTPUT**

When Claude Code starts a new session, the following checks MUST be
performed automatically **before** responding to the user's first message
or doing any other work. Do NOT skip these steps. Do NOT address the user's
task first. Complete all checks, report the summary, and only then proceed
to the user's request.

## Step 1. Git Repository Sync

If the current working directory is a Git repository, synchronise it with the remote:

1. **Fetch latest** — Run `git fetch --all --prune` to download all remote changes and clean up deleted remote branches.

2. **Check for divergence** — Compare the current branch with its upstream tracking branch. Determine whether the local branch is:
   - **Up to date** — No action needed. Inform the user briefly.
   - **Behind** — Remote has commits not in the local branch. Ask the user: *"Your local branch is X commits behind the remote. Would you like to pull the latest changes?"* If yes, run `git pull`.
   - **Ahead** — Local has commits not pushed to the remote. Warn the user: *"Your local branch is X commits ahead of the remote. You have unpushed changes."* Do not push automatically.
   - **Diverged** — Both local and remote have new commits. Warn the user: *"Your local branch has diverged from the remote (X local, Y remote commits). You may need to merge or rebase."* Ask the user how they would like to proceed.

3. **Uncommitted changes** — If there are uncommitted changes (staged or unstaged), warn the user: *"You have uncommitted changes in the working directory."* List the modified files briefly. Do not commit or stash automatically.

4. **Stale branches** — If there are local branches whose upstream tracking branch has been deleted (marked `[gone]`), inform the user: *"You have X local branches with deleted remote tracking branches. Would you like to clean them up?"*

5. **Claude configuration changes** — After fetching (and pulling if applicable), check whether the incoming remote changes include modifications to any file inside the `.claude/` directory (e.g. `CLAUDE.md`, `settings.json`, files in `default-skills/`, files in `project-skills/`). Use `git diff` against the previous local HEAD to detect these changes.

   If `.claude/` changes are detected:

   a. **Notify the user** — List the specific `.claude/` files that were added, modified, or deleted:
      *"The following Claude Code configuration files were updated from the remote: [file list]. These may include new or changed skills, settings, or project instructions."*

   b. **Offer a review** — Ask the user: *"Would you like me to review these Claude configuration changes and check whether any existing repository files need to be revised to comply with the updated skills or settings?"*

   c. **Review process** (if the user agrees) — Read each changed `.claude/` file, identify what behaviour changed (new rules, modified rules, removed rules), then scan the repository codebase for files that may be affected. Report findings to the user with specific file paths and descriptions of what needs to change.

   d. **Offer automatic updates** — After presenting the review findings, ask the user: *"Would you like me to automatically update and refactor the affected files to comply with the new Claude configuration?"*
      - If yes, make all necessary changes, showing each file modification to the user as it is made.
      - If no, leave the files unchanged but keep the review findings visible so the user can address them manually.

   e. **No changes detected** — If no `.claude/` files were modified in the incoming changes, skip this check silently.

## Step 2. Python Virtual Environment Activation

If the repository contains a Python virtual environment, activate it automatically:

1. **Detect venv** — Check for a virtual environment directory in the following locations (in order):
   - `venv/`
   - `.venv/`
   - `env/`
   - `.env/` (only if it contains `pyvenv.cfg`, to avoid confusing it with a dotenv file)

2. **Activate** — Once found, activate the virtual environment by sourcing the appropriate activation script:
   - **Linux/macOS:** `source <venv>/bin/activate`
   - **Windows:** `<venv>\Scripts\activate`

3. **No venv found** — If no virtual environment is detected, inform the user: *"No Python virtual environment found. Would you like to create one?"* If yes, create it using `python -m venv venv` and activate it.

4. **Verify activation** — After activation, confirm the Python interpreter is the one inside the venv by checking `which python` (Linux/macOS) or `where python` (Windows).

## Step 3. Pip Upgrade Check

After the virtual environment is activated (or if Python is available without a venv):

1. **Check pip version** — Run `pip --version` and compare the installed version against the latest available version.

2. **Upgrade if needed** — If pip is outdated, upgrade it automatically by running:
   ```
   python -m pip install --upgrade pip
   ```

3. **Report** — Inform the user of the pip version after the check (whether it was already current or was upgraded).

## Reporting

After completing all checks, provide the user with a brief summary. Example:

```
Session startup checks complete:
  Git: Fetched latest. Local branch is up to date with origin/main.
  Venv: Activated (venv/). Python 3.14.1.
  Pip: Upgraded from 25.0 to 25.1.
```

Keep the summary concise. Only expand on items that need user attention or action.

## When This Skill Applies

- Every time Claude Code begins a new session in any directory.
- The checks run once at session start, not on every tool call.
