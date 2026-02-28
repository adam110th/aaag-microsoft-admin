#!/usr/bin/env python3
"""
Skill Evaluation Engine v1.0

Intelligent skill activation based on:
- Keywords and patterns in prompts
- File paths mentioned or being edited
- Directory mappings
- Intent detection
- Content pattern matching

Outputs a structured reminder with matched skills and reasons.
"""

import json
import re
import sys
from pathlib import Path

RULES_PATH = Path(__file__).parent / "skill-rules.json"


def load_rules() -> dict:
    """Load skill rules from JSON file."""
    try:
        with open(RULES_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Failed to load skill rules: {exc}", file=sys.stderr)
        sys.exit(0)


def extract_file_paths(prompt: str) -> list[str]:
    """Extract file paths mentioned in the prompt."""
    paths: set[str] = set()

    # Match explicit paths with common extensions
    ext_pattern = r'(?:^|\s|["\x27`])([\w\-./\\]+\.(?:py|pyi|txt|json|ya?ml|md|sh|ps1|toml|cfg|ini|sql|html|css|js|ts|jsx|tsx|ipynb|xlsx|csv))\b'
    for m in re.finditer(ext_pattern, prompt, re.IGNORECASE):
        paths.add(m.group(1).replace("\\", "/"))

    # Match paths starting with common directories
    dir_pattern = r'(?:^|\s|["\x27`])((?:src|app|lib|tests|test|scripts|utils|models|views|templates|static|\.claude|\.github|docs|config)/[\w\-./\\]+)'
    for m in re.finditer(dir_pattern, prompt, re.IGNORECASE):
        paths.add(m.group(1).replace("\\", "/"))

    # Match quoted paths
    quoted_pattern = r'["\x27`]([\w\-./\\]+/[\w\-./\\]+)["\x27`]'
    for m in re.finditer(quoted_pattern, prompt):
        paths.add(m.group(1).replace("\\", "/"))

    return list(paths)


def matches_pattern(text: str, pattern: str, flags: int = re.IGNORECASE) -> bool:
    """Check if a regex pattern matches the text."""
    try:
        return bool(re.search(pattern, text, flags))
    except re.error:
        return False


def matches_glob(file_path: str, glob_pattern: str) -> bool:
    """Check if a simplified glob pattern matches a file path."""
    regex = (
        glob_pattern.replace(".", r"\.")
        .replace("**/", "<<<DS>>>")
        .replace("**", "<<<DD>>>")
        .replace("*", "[^/]*")
        .replace("<<<DS>>>", "(.*/)?")
        .replace("<<<DD>>>", ".*")
        .replace("?", ".")
    )
    try:
        return bool(re.match(f"^{regex}$", file_path, re.IGNORECASE))
    except re.error:
        return False


def match_directory_mapping(file_path: str, mappings: dict) -> str | None:
    """Check if file path matches any directory mapping."""
    for directory, skill_name in mappings.items():
        if file_path == directory or file_path.startswith(directory + "/"):
            return skill_name
    return None


def evaluate_skill(
    skill_name: str,
    skill: dict,
    prompt: str,
    prompt_lower: str,
    file_paths: list[str],
    rules: dict,
) -> dict | None:
    """Evaluate a single skill against the prompt and context."""
    triggers = skill.get("triggers", {})
    exclude_patterns = skill.get("excludePatterns", [])
    priority = skill.get("priority", 5)
    scoring = rules["scoring"]

    score = 0
    reasons: list[str] = []

    # Check exclude patterns first
    for pattern in exclude_patterns:
        if matches_pattern(prompt_lower, pattern):
            return None

    # 1. Keywords
    for keyword in triggers.get("keywords", []):
        if keyword.lower() in prompt_lower:
            score += scoring["keyword"]
            reasons.append(f'keyword "{keyword}"')

    # 2. Keyword patterns (regex)
    for pattern in triggers.get("keywordPatterns", []):
        if matches_pattern(prompt_lower, pattern):
            score += scoring["keywordPattern"]
            reasons.append(f"pattern /{pattern}/")

    # 3. Intent patterns
    for pattern in triggers.get("intentPatterns", []):
        if matches_pattern(prompt_lower, pattern):
            score += scoring["intentPattern"]
            reasons.append("intent detected")
            break

    # 4. Context patterns
    for pattern in triggers.get("contextPatterns", []):
        if pattern.lower() in prompt_lower:
            score += scoring["contextPattern"]
            reasons.append(f'context "{pattern}"')

    # 5. Path patterns
    if triggers.get("pathPatterns") and file_paths:
        for fp in file_paths:
            for pattern in triggers["pathPatterns"]:
                if matches_glob(fp, pattern):
                    score += scoring["pathPattern"]
                    reasons.append(f'path "{fp}"')
                    break

    # 6. Directory mappings
    if rules.get("directoryMappings") and file_paths:
        for fp in file_paths:
            mapped = match_directory_mapping(fp, rules["directoryMappings"])
            if mapped == skill_name:
                score += scoring["directoryMatch"]
                reasons.append("directory mapping")
                break

    # 7. Content patterns
    for pattern in triggers.get("contentPatterns", []):
        if matches_pattern(prompt, pattern):
            score += scoring["contentPattern"]
            reasons.append("code pattern detected")
            break

    if score > 0:
        return {
            "name": skill_name,
            "score": score,
            "reasons": list(dict.fromkeys(reasons)),
            "priority": priority,
        }
    return None


def get_related_skills(matches: list[dict], skills: dict) -> list[str]:
    """Get related skills that should also be suggested."""
    matched_names = {m["name"] for m in matches}
    related: set[str] = set()
    for match in matches:
        skill = skills.get(match["name"], {})
        for name in skill.get("relatedSkills", []):
            if name not in matched_names:
                related.add(name)
    return list(related)


def format_confidence(score: int, min_score: int) -> str:
    """Format confidence level based on score."""
    if score >= min_score * 3:
        return "HIGH"
    if score >= min_score * 2:
        return "MEDIUM"
    return "LOW"


def evaluate(prompt: str) -> str:
    """Main evaluation function."""
    rules = load_rules()
    config = rules["config"]
    skills = rules["skills"]

    prompt_lower = prompt.lower()
    file_paths = extract_file_paths(prompt)

    matches = []
    for name, skill in skills.items():
        match = evaluate_skill(name, skill, prompt, prompt_lower, file_paths, rules)
        if match and match["score"] >= config["minConfidenceScore"]:
            matches.append(match)

    if not matches:
        return ""

    # Sort by score desc, then priority desc
    matches.sort(key=lambda m: (m["score"], m["priority"]), reverse=True)
    top = matches[: config["maxSkillsToShow"]]

    related = get_related_skills(top, skills)

    lines = ["<user-prompt-submit-hook>", "SKILL ACTIVATION REQUIRED", ""]

    if file_paths:
        lines.append(f"Detected file paths: {', '.join(file_paths)}")
        lines.append("")

    lines.append("Matched skills (ranked by relevance):")

    for i, match in enumerate(top, 1):
        confidence = format_confidence(match["score"], config["minConfidenceScore"])
        lines.append(f"{i}. {match['name']} ({confidence} confidence)")
        if config.get("showMatchReasons") and match["reasons"]:
            lines.append(f"   Matched: {', '.join(match['reasons'][:3])}")

    if related:
        lines.append(f"\nRelated skills to consider: {', '.join(related)}")

    lines.extend([
        "",
        "Before implementing, you MUST:",
        "1. EVALUATE: State YES/NO for each skill with brief reasoning",
        "2. ACTIVATE: Invoke the Skill tool for each YES skill",
        "3. IMPLEMENT: Only proceed after skill activation",
        "",
        "Example evaluation:",
        f"- {top[0]['name']}: YES - [your reasoning]",
    ])
    if len(top) > 1:
        lines.append(f"- {top[1]['name']}: NO - [your reasoning]")

    lines.extend([
        "",
        "DO NOT skip this step. Invoke relevant skills NOW.",
        "</user-prompt-submit-hook>",
    ])

    return "\n".join(lines)


def main() -> None:
    """Read prompt from stdin and evaluate."""
    raw = sys.stdin.read()
    prompt = ""
    try:
        data = json.loads(raw)
        prompt = data.get("prompt", "")
    except (json.JSONDecodeError, TypeError):
        prompt = raw

    if not prompt.strip():
        sys.exit(0)

    try:
        output = evaluate(prompt)
        if output:
            print(output)
    except Exception as exc:
        print(f"Skill evaluation failed: {exc}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
