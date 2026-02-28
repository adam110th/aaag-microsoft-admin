When Claude Code creates or updates scripts that open files, database connections, network sockets, subprocess handles, or other system resources, those resources MUST be properly closed and released after use.

## Required Behaviour

1. **Use language-appropriate patterns:**
   - **Python** — Context managers (`with` statements)
   - **Java** — `try-with-resources`
   - **C#** — `using` statements
   - **Go** — `defer`
   - **JavaScript/TypeScript** — `try/finally` or `using` (with explicit resource disposal)
   - **Other languages** — `try/finally` as a fallback

2. **Do not rely on garbage collection** — Garbage collection timing is unpredictable and language-dependent. Always close resources explicitly.

3. **Handle cleanup on errors** — Resources must be released even when an exception occurs during processing. This is why context managers and `try/finally` blocks are required rather than manual `.close()` calls after processing.

## Why

Unclosed resources cause file descriptor exhaustion, connection pool depletion, data corruption from unflushed buffers, and file lock issues on Windows.

## When This Skill Applies

- Every script that opens files, database connections, network sockets, subprocess handles, HTTP sessions, or any other closeable resource.
