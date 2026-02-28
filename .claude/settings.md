# Claude Code Settings Documentation

## Environment Variables

- `INSIDE_CLAUDE_CODE`: `"1"` — Indicates code is running inside Claude Code. Scripts can check this to adjust behavior.
- `BASH_DEFAULT_TIMEOUT_MS`: Default timeout for bash commands (7 minutes / 420000ms).
- `BASH_MAX_TIMEOUT_MS`: Maximum timeout for bash commands.

## Hooks

### UserPromptSubmit

- **Skill Evaluation**: Analyzes prompts and suggests relevant skills.
  - **Script**: `.claude/hooks/skill-eval.sh` → `.claude/hooks/skill-eval.py`
  - **Config**: `.claude/hooks/skill-rules.json`
  - **Behavior**: Matches keywords, file paths, intent patterns, and directory mappings to suggest which default skills are relevant to the current prompt. Outputs a structured reminder with matched skills ranked by confidence.
  - **Timeout**: 5 seconds

### PreToolUse

- **Main Branch Protection**: Prevents file edits on main/master branch.
  - **Matcher**: `Edit|MultiEdit|Write` tools
  - **Behavior**: Blocks file edits when on `main` or `master` branch. Suggests creating a feature branch first.
  - **Timeout**: 5 seconds
  - **Exit code 2**: Blocks the tool execution

### PostToolUse

1. **Python Auto-Format**: Auto-format Python files with ruff (30s timeout)
   - **Matcher**: `Edit|MultiEdit|Write` tools
   - **Triggers**: After editing `.py` files
   - **Command**: `ruff format <file>` then `ruff check --fix <file>`
   - **Behavior**: Formats code and auto-fixes lint issues. Shows feedback if errors found.

2. **Auto-Install Dependencies**: Auto-install after requirements.txt changes (60s timeout)
   - **Matcher**: `Edit|MultiEdit|Write` tools
   - **Triggers**: After editing `requirements.txt` or `requirements*.txt` files
   - **Command**: `pip install -r requirements.txt`
   - **Behavior**: Installs dependencies automatically.

3. **Auto-Run Tests**: Run tests after test file changes (120s timeout)
   - **Matcher**: `Edit|MultiEdit|Write` tools
   - **Triggers**: After editing `test_*.py`, `*_test.py`, or `conftest.py` files
   - **Command**: `pytest <file> --tb=short -q`
   - **Behavior**: Runs related tests, shows results. Non-blocking.

4. **Python Type Check**: Type-check Python files with pyright (30s timeout)
   - **Matcher**: `Edit|MultiEdit|Write` tools
   - **Triggers**: After editing `.py` files
   - **Command**: `pyright <file>`
   - **Behavior**: Shows type errors if found. Non-blocking.

## Hook Response Format

```json
{
  "feedback": "Message shown to user",
  "suppressOutput": true,
  "block": true,
  "continue": false
}
```

## Environment Variables Available in Hooks

| Variable | Description |
|----------|-------------|
| `$CLAUDE_TOOL_INPUT_FILE_PATH` | File being edited |
| `$CLAUDE_TOOL_NAME` | Tool being used |
| `$CLAUDE_PROJECT_DIR` | Project root directory |

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Non-blocking error (shows feedback) |
| `2` | Blocking error (PreToolUse only — blocks the action) |
