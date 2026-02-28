When Claude Code creates or updates scripts that open files on the local file system for writing, the script MUST handle the case where the file is locked by another process.

## Required Behaviour

1. **Detect the lock** — Before or during the file write operation, catch the appropriate exception (`PermissionError` in Python, `EACCES`/`EBUSY` in Node.js, etc.) that indicates the file is locked.

2. **Notify the user** — Display a clear message stating that the file is locked and cannot be written to. Include the file path in the message so the user knows which file to close.

3. **Prompt to retry** — Ask the user to close the file and press Enter to retry. Example:
   ```
   The file "report.xlsx" is locked by another process.
   Please close the file and press Enter to retry...
   ```

4. **Loop until resolved** — If the file is still locked after the user presses Enter, display the message again and continue looping until the script can proceed.

5. **Allow exit** — The retry loop must respect keyboard interrupts (Ctrl+C) so the user can abort if needed.

## When This Skill Applies

- Any script that writes to local files, especially Excel, Word, PDF, or other document formats that users commonly have open in desktop applications.
