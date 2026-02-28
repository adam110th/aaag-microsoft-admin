When Claude Code creates or updates scripts, all errors MUST be logged with meaningful context. Silent failures are not acceptable.

## Required Behaviour

### Error messages

1. **Describe what failed** — Every error message must state which operation failed, not just that an error occurred. Include relevant details such as file paths, URLs, input values, or step numbers.

2. **Suggest corrective action** — Where possible, include guidance on how the user can resolve the issue (e.g. "Check that the file exists and is not open in another application").

3. **Timestamp all log entries** — Every log entry must include a date and time stamp.

4. **No silent failures** — Never use bare `except` or `catch` blocks that swallow errors without logging. Never discard exception details.

5. **User-friendly output** — Do not expose raw stack traces to end users. Log the full traceback to a log file or stderr, and show the user a clear, actionable message on the terminal.

6. **Step identification** — For scripts with multiple steps, include which step failed so the user knows where the process stopped.

### Logging configuration

7. **Log file output** — Unless otherwise specified, save log files into a `logs/` directory with a date and time stamp in the file name (e.g. `logs/2025-07-15_143022.log`).

8. **Log levels** — All scripts must have a configurable log level that can be set via command-line argument or within the script configuration. Supported levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. The default level must include `WARNING`, `ERROR`, and `CRITICAL` messages.

9. **Dual output** — Log messages must be written to both the log file and the terminal simultaneously. This dual output can be disabled via a command-line argument or script configuration.

10. **Standard logging** — Use standard Python logging modules (`logging` or `loguru`). Do not use `print()` for error or diagnostic output.

## When This Skill Applies

- Every script that Claude Code creates or updates, without exception.
