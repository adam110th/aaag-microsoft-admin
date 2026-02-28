#!/bin/bash
# Skill Evaluation Hook v1.0
# Wrapper script that delegates to the Python evaluation engine
#
# This hook runs on UserPromptSubmit and analyzes the prompt for:
# - Keywords and patterns indicating skill relevance
# - File paths mentioned in the prompt
# - Intent patterns (what the user wants to do)
# - Directory mappings (what directories map to which skills)
#
# Configuration is in skill-rules.json

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY_SCRIPT="$SCRIPT_DIR/skill-eval.py"

# Try python3 first, fall back to python, then py
if command -v python3 &>/dev/null; then
  PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
  PYTHON_CMD="python"
elif command -v py &>/dev/null; then
  PYTHON_CMD="py"
else
  # Fallback: exit silently if Python not found
  exit 0
fi

# Check if the Python script exists
if [[ ! -f "$PY_SCRIPT" ]]; then
  exit 0
fi

# Pipe stdin to the Python script
cat | "$PYTHON_CMD" "$PY_SCRIPT" 2>/dev/null

# Always exit 0 to allow the prompt through
exit 0
