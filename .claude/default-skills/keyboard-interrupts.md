When Claude Code creates or updates scripts, every script MUST handle keyboard interrupts (Ctrl+C) gracefully.

## Required Behaviour

1. **Catch the interrupt** — Wrap long-running operations, main loops, and entry points with a handler for `KeyboardInterrupt` (Python), `SIGINT` (Node.js/Go/C), or the equivalent signal for the language being used.

2. **Clean up resources** — On interrupt, close any open file handles, database connections, network sockets, or temporary files before exiting. Do not leave partial output files or locked resources behind.

3. **Exit cleanly** — Print a brief message (e.g. `"Interrupted by user. Exiting."`) and exit with a non-zero exit code to indicate abnormal termination.

4. **Do not suppress** — Never catch `KeyboardInterrupt` inside a bare `except Exception` block. Always handle it separately or let it propagate after cleanup.

## Example (Python)

```python
import sys

def main():
    # ... script logic ...
    pass

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting.")
        sys.exit(130)
```

## When This Skill Applies

- Every script that Claude Code creates or updates, without exception.
