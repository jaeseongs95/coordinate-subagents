#!/usr/bin/env python3
"""Validate the coordinate-subagents skill package without third-party modules."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote


REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPO_ROOT / "skills" / "coordinate-subagents"
EXPECTED_CASE_IDS = {
    "atomic-no-delegation",
    "independent-two-plus-parallel",
    "dependency-order",
    "shared-write-ownership",
    "slot-shortage-reuse",
    "high-risk-independent-audit",
    "plan-readonly",
    "fork-override",
    "unsupported-model-fallback",
}


class ValidationError(Exception):
    """A validation error that should be reported without a traceback."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def read_utf8(path: Path) -> str:
    require(path.is_file(), f"required file is missing: {path.relative_to(REPO_ROOT)}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValidationError(
            f"file is not valid UTF-8: {path.relative_to(REPO_ROOT)}"
        ) from error


def parse_scalar(value: str) -> object:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError as error:
            raise ValidationError(f"invalid double-quoted YAML scalar: {value}") from error
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if lowered in {"null", "~"}:
        return None
    return value


def parse_simple_yaml_map(text: str, source: Path) -> dict[str, object]:
    """Parse the nested mapping subset used by agents/openai.yaml."""
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        require("\t" not in raw_line, f"tabs are not allowed in {source}:{line_number}")
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        content = raw_line.strip()
        require(":" in content, f"invalid YAML mapping at {source}:{line_number}")
        key, value = content.split(":", 1)
        key = key.strip()
        require(bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_-]*", key)),
                f"invalid YAML key at {source}:{line_number}: {key!r}")

        while stack[-1][0] >= indent:
            stack.pop()
        parent = stack[-1][1]
        require(key not in parent, f"duplicate YAML key at {source}:{line_number}: {key}")
        if value.strip():
            parent[key] = parse_scalar(value)
        else:
            child: dict[str, object] = {}
            parent[key] = child
            stack.append((indent, child))
    return root


def parse_frontmatter(skill_md: str) -> dict[str, object]:
    lines = skill_md.splitlines()
    require(lines and lines[0].strip() == "---", "SKILL.md must begin with YAML frontmatter")
    try:
        closing = next(index for index, line in enumerate(lines[1:], start=1)
                       if line.strip() == "---")
    except StopIteration as error:
        raise ValidationError("SKILL.md frontmatter is missing its closing delimiter") from error
    frontmatter_text = "\n".join(lines[1:closing])
    parsed = parse_simple_yaml_map(frontmatter_text, SKILL_ROOT / "SKILL.md")
    return parsed


def validate_frontmatter() -> None:
    metadata = parse_frontmatter(read_utf8(SKILL_ROOT / "SKILL.md"))
    require(metadata.get("name") == "coordinate-subagents",
            "SKILL.md frontmatter name must be 'coordinate-subagents'")
    description = metadata.get("description")
    require(isinstance(description, str) and len(description.strip()) >= 40,
            "SKILL.md frontmatter description must be a meaningful single-line string")
    require(metadata.get("license") == "MIT", "SKILL.md frontmatter license must be 'MIT'")
    version = metadata.get("version")
    nested_metadata = metadata.get("metadata")
    if version is None and isinstance(nested_metadata, dict):
        version = nested_metadata.get("version")
    require(isinstance(version, str) and re.fullmatch(r"0\.1\.0", version) is not None,
            "SKILL.md frontmatter version (version or metadata.version) must be '0.1.0'")
    skill_license = read_utf8(SKILL_ROOT / "LICENSE")
    require(skill_license == read_utf8(REPO_ROOT / "LICENSE"),
            "the installable skill LICENSE must match the repository LICENSE")


def nested_value(mapping: dict[str, object], *keys: str) -> object:
    current: object = mapping
    for key in keys:
        require(isinstance(current, dict) and key in current,
                f"agents/openai.yaml is missing required key: {'.'.join(keys)}")
        current = current[key]
    return current


def validate_openai_yaml() -> None:
    path = SKILL_ROOT / "agents" / "openai.yaml"
    parsed = parse_simple_yaml_map(read_utf8(path), path)
    require(nested_value(parsed, "interface", "display_name") == "Coordinate Subagents",
            "interface.display_name must be 'Coordinate Subagents'")
    short_description = nested_value(parsed, "interface", "short_description")
    require(isinstance(short_description, str) and 12 <= len(short_description.strip()) <= 100,
            "interface.short_description must contain 12-100 characters")
    default_prompt = nested_value(parsed, "interface", "default_prompt")
    require(isinstance(default_prompt, str) and "$coordinate-subagents" in default_prompt,
            "interface.default_prompt must explicitly invoke $coordinate-subagents")
    require(nested_value(parsed, "policy", "allow_implicit_invocation") is True,
            "policy.allow_implicit_invocation must be true")


MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


def extract_link_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and ">" in target:
        return target[1:target.index(">")]
    match = re.match(r"(\S+)(?:\s+[\"'].*[\"'])?$", target)
    return match.group(1) if match else target


def validate_markdown_links() -> None:
    failures: list[str] = []
    for markdown in sorted(REPO_ROOT.rglob("*.md")):
        if ".git" in markdown.parts:
            continue
        for raw_target in MARKDOWN_LINK.findall(read_utf8(markdown)):
            target = unquote(extract_link_target(raw_target))
            if (not target or target.startswith("#") or target.startswith("/")
                    or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target)):
                continue
            path_part = target.split("#", 1)[0].split("?", 1)[0]
            if path_part and not (markdown.parent / path_part).resolve().exists():
                failures.append(
                    f"{markdown.relative_to(REPO_ROOT)} -> {target}"
                )
    require(not failures, "broken relative Markdown links:\n  " + "\n  ".join(failures))


TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".py", ".txt", ".json", ".toml"}


def repository_text_files() -> list[Path]:
    return [
        path for path in REPO_ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts and path.suffix.lower() in TEXT_SUFFIXES
    ]


def validate_no_placeholders() -> None:
    marker = re.compile(
        r"\b(?:TO" + r"DO|FIX" + r"ME|XXX|PLACE" + r"HOLDER|CHANGE" + r"ME|TBD)\b",
        re.IGNORECASE,
    )
    failures: list[str] = []
    for path in repository_text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        for line_number, line in enumerate(read_utf8(path).splitlines(), start=1):
            if marker.search(line):
                failures.append(f"{path.relative_to(REPO_ROOT)}:{line_number}")
    require(not failures, "unfinished placeholder markers found:\n  " + "\n  ".join(failures))


def validate_no_sensitive_data() -> None:
    signatures = {
        "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE" + r" KEY-----"),
        "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b|\bgithub_pat_[A-Za-z0-9_]{40,}\b"),
        "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
        "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
        "Slack token": re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b"),
        "credential assignment": re.compile(
            r"(?i)\b(?:api[_-]?key|access[_-]?token|auth[_-]?token|password|secret)\b"
            r"\s*[:=]\s*[\"']?[A-Za-z0-9_./+=-]{16,}"
        ),
    }
    personal_paths = {
        "Windows user path": re.compile(r"(?i)\b[A-Z]:[\\/]Users[\\/][^\\/\s]+[\\/]"),
        "macOS user path": re.compile(r"/Users/[^/\s]+/"),
        "Linux home path": re.compile(r"/home/[^/\s]+/"),
    }
    failures: list[str] = []
    for path in repository_text_files():
        if path.resolve() == Path(__file__).resolve():
            continue
        text = read_utf8(path)
        for label, pattern in {**signatures, **personal_paths}.items():
            if pattern.search(text):
                failures.append(f"{path.relative_to(REPO_ROOT)}: possible {label}")
    require(not failures, "possible sensitive data or personal paths found:\n  " + "\n  ".join(failures))


def validate_behavior_cases() -> None:
    path = REPO_ROOT / "tests" / "behavior-cases.yaml"
    try:
        document = json.loads(read_utf8(path))
    except json.JSONDecodeError as error:
        raise ValidationError(
            "tests/behavior-cases.yaml must remain valid JSON (and therefore valid YAML 1.2)"
        ) from error
    require(isinstance(document, dict) and document.get("schema_version") == 1,
            "behavior cases must declare schema_version 1")
    cases = document.get("cases")
    require(isinstance(cases, list), "behavior cases must contain a cases list")
    seen: set[str] = set()
    for index, case in enumerate(cases):
        require(isinstance(case, dict), f"behavior case {index} must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id not in seen,
                f"behavior case {index} has a missing or duplicate id")
        seen.add(case_id)
        for key in ("scenario", "input", "expected"):
            require(key in case and isinstance(case[key], (str, dict)),
                    f"behavior case {case_id} requires a structured {key} field")
    require(seen == EXPECTED_CASE_IDS,
            "behavior case IDs differ from the required matrix; "
            f"missing={sorted(EXPECTED_CASE_IDS - seen)}, extra={sorted(seen - EXPECTED_CASE_IDS)}")


def main() -> int:
    checks = [
        validate_frontmatter,
        validate_openai_yaml,
        validate_markdown_links,
        validate_no_placeholders,
        validate_no_sensitive_data,
        validate_behavior_cases,
    ]
    failures: list[str] = []
    for check in checks:
        try:
            check()
            print(f"PASS {check.__name__}")
        except ValidationError as error:
            failures.append(f"FAIL {check.__name__}: {error}")
    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1
    print("All skill package validations passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
