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
EXPECTED_VERSION = "0.1.2"
OFFICIAL_FRONTMATTER_KEYS = {
    "name",
    "description",
    "license",
    "allowed-tools",
    "metadata",
}
EXPECTED_CASE_IDS = {
    "atomic-no-delegation",
    "audit-slot-reservation",
    "completion-integration",
    "delegation-exception-boundary",
    "independent-two-plus-parallel",
    "dependency-order",
    "dispatch-recovery",
    "explicit-atomic-allocation",
    "shared-write-ownership",
    "slot-shortage-reuse",
    "high-risk-independent-audit",
    "plan-readonly",
    "preference-resolution",
    "fork-override",
    "unsupported-model-fallback",
}
POLICY_REQUIRED_CLAUSES = {
    "authority.inherit-mode": (
        "Apply the current mode and write restrictions to every delegated task.",
    ),
    "delegation.atomic-local": (
        "Keep ordinary atomic work local unless the user explicitly requests delegation or independent review.",
    ),
    "delegation.explicit-request": (
        "The user explicitly asks for subagents, delegation, or parallel work.",
    ),
    "delegation.independent-parallel": (
        "Two or more independent units exist.",
    ),
    "delegation.allowed-exceptions": (
        "When delegation is otherwise required, the only exceptions are that every remaining unit depends on prior output, the same file or state requires exclusive access, or collaboration slots, tools, or permissions are unavailable.",
        "Task size, coordinator convenience, handoff cost, or token cost alone are not valid exceptions, and no exception waives a required high-risk audit.",
    ),
    "preferences.ask-once": (
        "At the first point in each task when delegation will occur, check whether the user or host already supplied a delegation preference.",
        "If no preference exists and choosing among the bundled profiles would materially affect agent count, batching, model selection, or reasoning effort, ask one short optional question offering `balanced` (recommended), `economy`, and `quality`.",
        "Ask at most once per task.",
        "If no answer is available before dispatch or the host cannot ask, use `balanced` and proceed.",
        "Never infer a subscription plan from model availability or usage observations; use plan details only when the user or host provides them.",
        "A preference may tune allocation and supported runtime settings, but it never expands authority or waives required independent audits.",
    ),
    "allocation.keep-one-and-fill-slots": (
        "When two or more implementation units exist, keep one independent unit with the coordinator and assign the others across available slots.",
        "If the user explicitly asks to delegate the only implementation unit, assign that unit to a subagent and keep coordination and evidence review with the coordinator.",
    ),
    "allocation.batch-reuse": (
        "When independent units exceed the usable slot count, run them in batches and reuse completed subagents with a fresh brief.",
    ),
    "allocation.explicit-single-delegation-playbook": (
        "If the user explicitly delegates the only implementation unit, give it to the subagent and keep coordination and evidence review with the coordinator.",
    ),
    "ownership.single-writer": (
        "Give one writer ownership of each shared file or external state.",
        "A subagent owns investigation, implementation, deliverable preparation, and verification inside its assigned scope and must coordinate before changing another owner's area.",
    ),
    "integration.no-redo": (
        "Do not redo delegated work.",
        "Resolve disagreements from requirements, current artifacts, and verification results rather than model identity.",
    ),
    "audit.independent-required": (
        "Assign an auditor who did not implement the change.",
        "The auditor must inspect the requirements, final change, verification evidence, and plausible failure modes directly.",
    ),
    "audit.reserve-identity": (
        "When high-risk work requires an independent auditor and later access to a fresh agent identity is uncertain, reserve a non-implementing subagent and its slot before filling implementation assignments.",
    ),
    "audit.reserve-identity-playbook": (
        "When a required high-risk audit may not have access to a fresh identity later, reserve a non-implementing subagent and slot before assigning all implementation work.",
    ),
    "audit.no-completion-without-auditor": (
        "Do not report high-risk work as complete without an available independent auditor and resolved findings.",
        "If no auditor is available, state the limitation and do not claim that an independent audit occurred.",
    ),
    "audit.reaudit-after-change": (
        "If the audited area changes afterward, re-audit the affected portion.",
        "For deployments, audit readiness before execution and audit the resulting deployment evidence afterward.",
    ),
    "audit.finding-disposition": (
        "Resolve each audit finding by fixing it, disproving it with evidence, or recording risk acceptance from an authorized decision-maker when higher-priority policy permits that outcome.",
        "Deferral alone does not resolve a finding.",
    ),
    "completion.current-evidence": (
        "confirm that each subagent's scoped verification actually passed",
        "verify each requirement against current evidence with checks proportional to its failure impact",
        "avoid checks that merely repeat the implementation, and reverify only the affected scope when a later change invalidates earlier evidence",
    ),
    "completion.report-facts": (
        "report the result, material changes, checks actually run, their outcomes, and remaining constraints",
        "never present an unrun check or unverified setting as completed",
    ),
    "dispatch.inspect-and-recover": (
        "If a spawn or dispatch fails, inspect agent status before deciding what happened.",
        "Keep the unit local only when delegation is no longer possible and disclose why.",
    ),
    "routing.settings-supported": (
        "Inspect the current collaboration tool schema before setting an override.",
        "Confirm the meaning and support of modes or aliases such as `Fast` and `Pro`, and reasoning levels such as `ultra`, from the current tool schema and, when needed, official host documentation.",
        "Never report an unsupported setting as applied.",
    ),
    "routing.luna-high-minimum": (
        "Use `gpt-5.6-luna` only at `high` reasoning or above.",
        "If that combination is unsupported, choose another supported model instead of lowering Luna's reasoning.",
    ),
    "routing.full-history-inherits": (
        "With `fork_turns=\"all\"`, inherit the parent model and reasoning effort; do not set model or reasoning overrides.",
    ),
    "routing.unsupported-fallback": (
        "If overrides are unavailable but inherited execution is supported, delegate with the inherited configuration.",
    ),
    "routing.no-mechanical-retry": (
        "Do not retry through progressively different models when the failure comes from missing information, permissions, tools, an unsupported setting, or an incomplete specification.",
    ),
}
POLICY_FORBIDDEN_CLAUSES = {
    "allocation.explicit-single-delegation-playbook": (
        "The coordinator must keep the only implementation unit even when the user explicitly delegates it.",
    ),
    "audit.reserve-identity-playbook": (
        "Fill all implementation slots before considering a later auditor.",
    ),
    "delegation.independent-parallel": (
        "Delegation is optional when two or more independent units exist.",
    ),
    "audit.independent-required": (
        "An implementer may audit their own work.",
    ),
    "audit.no-completion-without-auditor": (
        "Report high-risk work as complete without an auditor.",
    ),
    "completion.report-facts": (
        "Present unrun checks or unverified settings as completed.",
    ),
    "routing.luna-high-minimum": (
        "Lower Luna's reasoning when the requested combination is unavailable.",
    ),
}
POLICY_FORBIDDEN_PATTERNS = {
    "allocation.explicit-single-delegation-playbook": (
        r"(?i)(?:^|[.!?]\s+|-\s+)(?:the\s+)?coordinator\s+(?:must\s+)?(?:keep|retain|own)\b[^.]{0,120}\b(?:only|sole)\s+implementation\s+unit\b[^.]{0,160}\bexplicit(?:ly)?\b[^.]{0,80}\bdelegat\w*\b",
        r"(?i)(?:^|[.!?]\s+|-\s+)(?:keep|retain|assign)\b[^.]{0,40}\b(?:only|sole)\s+implementation\s+unit\b[^.]{0,60}\b(?:with|to)\s+the\s+coordinator\b[^.]{0,160}\bexplicit\w*\b[^.]{0,80}\bdelegat\w*\b",
    ),
    "audit.reserve-identity-playbook": (
        r"(?i)(?:^|[.!?]\s+|-\s+)(?:fill|assign|use)\b[^.]{0,80}\ball\s+implementation\s+slots\b[^.]{0,80}\bbefore\b[^.]{0,80}\bauditor\b",
    ),
}
POLICY_ALLOWED_PROBES = {
    "allocation.explicit-single-delegation-playbook": (
        "The coordinator must not keep the only implementation unit when the user explicitly delegates it.",
        "Never let the coordinator keep the only implementation unit when the user explicitly delegates it.",
    ),
    "audit.reserve-identity-playbook": (
        "Do not fill all implementation slots before reserving an auditor.",
        "Do not ever fill all implementation slots before reserving an auditor.",
    ),
}
POLICY_FORBIDDEN_PROBES = {
    "allocation.explicit-single-delegation-playbook": (
        "Keep the only implementation unit with the coordinator even after an explicit delegation request.",
        "The coordinator must retain the sole implementation unit when the user explicitly delegates it.",
    ),
    "audit.reserve-identity-playbook": (
        "Fill all implementation slots before considering a later auditor.",
    ),
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
    unexpected = set(metadata) - OFFICIAL_FRONTMATTER_KEYS
    require(not unexpected,
            f"SKILL.md frontmatter contains unsupported keys: {sorted(unexpected)}")
    require(metadata.get("name") == "coordinate-subagents",
            "SKILL.md frontmatter name must be 'coordinate-subagents'")
    name = metadata.get("name")
    require(isinstance(name, str) and len(name) <= 64
            and re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) is not None,
            "SKILL.md frontmatter name must be lowercase hyphen-case and <= 64 characters")
    description = metadata.get("description")
    require(isinstance(description, str) and len(description.strip()) >= 40,
            "SKILL.md frontmatter description must be a meaningful single-line string")
    require(len(description) <= 1024 and "<" not in description and ">" not in description,
            "SKILL.md frontmatter description must be <= 1024 characters and contain no angle brackets")
    require(metadata.get("license") == "MIT", "SKILL.md frontmatter license must be 'MIT'")
    nested_metadata = metadata.get("metadata")
    require(isinstance(nested_metadata, dict),
            "SKILL.md frontmatter metadata must be a mapping")
    version = nested_metadata.get("version")
    require(version == EXPECTED_VERSION,
            f"SKILL.md frontmatter metadata.version must be {EXPECTED_VERSION!r}")
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


def validate_version_references() -> None:
    expected_tag = f"v{EXPECTED_VERSION}"
    pinned_pattern = re.compile(
        r"github\.com/jaeseongs95/coordinate-subagents/tree/"
        r"(v\d+\.\d+\.\d+)/skills/coordinate-subagents"
    )
    for name in ("README.md", "README.ko.md"):
        text = read_utf8(REPO_ROOT / name)
        tags = pinned_pattern.findall(text)
        require(tags == [expected_tag],
                f"{name} must contain exactly one pinned install URL for {expected_tag}; "
                f"found={tags}")


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
        "macOS user path": re.compile(r"/" + r"Users/[^/\s]+/"),
        "Linux home path": re.compile(r"/" + r"home/[^/\s]+/"),
    }
    patterns = {**signatures, **personal_paths}
    probes = {
        "private key": "-----BEGIN " + "PRIVATE KEY-----",
        "GitHub token": "gh" + "p_" + "A" * 36,
        "OpenAI-style secret": "sk-" + "A" * 24,
        "AWS access key": "AK" + "IA" + "A" * 16,
        "Slack token": "xo" + "xb-" + "A" * 24,
        "credential assignment": "api_key=" + "A" * 20,
        "Windows user path": "C:" + "\\Users\\sample\\project",
        "macOS user path": "/" + "Users/sample/project",
        "Linux home path": "/" + "home/sample/project",
    }
    for label, probe in probes.items():
        require(patterns[label].search(probe) is not None,
                f"sensitive-data detector regression for {label}")

    failures: list[str] = []
    scanned_paths: set[Path] = set()
    for path in repository_text_files():
        scanned_paths.add(path.resolve())
        text = read_utf8(path)
        for label, pattern in patterns.items():
            if pattern.search(text):
                failures.append(f"{path.relative_to(REPO_ROOT)}: possible {label}")
    require(Path(__file__).resolve() in scanned_paths,
            "the sensitive-data scan must include its validator source")
    require(not failures, "possible sensitive data or personal paths found:\n  " + "\n  ".join(failures))


POLICY_MARKER = re.compile(r"<!--\s*policy-contract:\s*([a-z0-9.-]+)\s*-->")
MARKDOWN_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")


def discover_policy_contracts() -> dict[str, dict[str, str]]:
    discovered: dict[str, dict[str, str]] = {}
    for path in sorted(SKILL_ROOT.rglob("*.md")):
        current_heading = ""
        for line_number, line in enumerate(read_utf8(path).splitlines(), start=1):
            heading = MARKDOWN_HEADING.match(line)
            if heading:
                current_heading = heading.group(1)
            for marker in POLICY_MARKER.findall(line):
                require(marker not in discovered,
                        f"duplicate policy contract marker {marker!r} at "
                        f"{path.relative_to(REPO_ROOT)}:{line_number}")
                discovered[marker] = {
                    "source": path.relative_to(REPO_ROOT).as_posix(),
                    "section": current_heading,
                }
    return discovered


def read_markdown_section(path: Path, section: str) -> str:
    lines: list[str] = []
    active = False
    for line in read_utf8(path).splitlines():
        heading = MARKDOWN_HEADING.match(line)
        if heading:
            if active:
                break
            active = heading.group(1) == section
            continue
        if active:
            lines.append(line)
    require(active or lines, f"missing Markdown section {section!r} in {path.relative_to(REPO_ROOT)}")
    return " ".join("\n".join(lines).split())


def evaluate_delegation_trigger(inputs: dict[str, object]) -> dict[str, object]:
    if inputs.get("explicit_request") is True:
        return {"delegate": True, "trigger": "explicit-user-request"}
    if int(inputs.get("independent_units", 0)) >= 2:
        return {"delegate": True, "trigger": "independent-units"}
    if inputs.get("high_risk") is True:
        return {"delegate": True, "trigger": "high-risk-audit"}
    return {"delegate": False, "trigger": "none"}


def evaluate_parallel_allocation(inputs: dict[str, object]) -> dict[str, object]:
    independent_units = int(inputs["independent_units"])
    slot_count = max(int(inputs["slot_count"]), 0)
    usable_subagents = max(slot_count - 1, 0) if inputs["slot_kind"] == "team-capacity" else slot_count
    coordinator_units = 1 if independent_units else 0
    remaining = max(independent_units - coordinator_units, 0)
    active_subagents = min(remaining, usable_subagents)
    queued_units = remaining - active_subagents
    return {
        "delegate": independent_units >= 2,
        "coordinator_units": coordinator_units,
        "active_subagents": active_subagents,
        "queued_units": queued_units,
        "reuse_completed_agent": queued_units > 0,
    }


def evaluate_explicit_atomic_allocation(inputs: dict[str, object]) -> dict[str, object]:
    explicit_request = inputs.get("explicit_request") is True
    atomic_units = int(inputs.get("atomic_units", 0))
    available_subagent_slots = int(inputs.get("available_subagent_slots", 0))
    delegate = explicit_request and atomic_units == 1 and available_subagent_slots >= 1
    return {
        "delegate": delegate,
        "coordinator_units": 0 if delegate else atomic_units,
        "active_subagents": 1 if delegate else 0,
        "coordinator_role": "coordination-and-evidence-review" if delegate else "implementation",
    }


def evaluate_audit_slot_reservation(inputs: dict[str, object]) -> dict[str, object]:
    slot_count = max(int(inputs.get("available_subagent_slots", 0)), 0)
    audit_required = inputs.get("audit_required") is True
    identity_uncertain = inputs.get("fresh_identity_later_uncertain") is True
    reserved = 1 if audit_required and identity_uncertain and slot_count > 0 else 0
    implementation_units = max(int(inputs.get("subagent_implementation_units", 0)), 0)
    active_implementers = min(implementation_units, slot_count - reserved)
    return {
        "reserved_auditor_slots": reserved,
        "active_implementation_subagents": active_implementers,
        "queued_implementation_units": implementation_units - active_implementers,
    }


def evaluate_dependency_schedule(inputs: dict[str, object]) -> dict[str, object]:
    has_dependency = inputs.get("has_dependency") is True
    independent_sibling = inputs.get("independent_sibling") is True
    return {
        "dependent_parallel": not has_dependency,
        "independent_sibling_parallel": independent_sibling,
        "execution": "mixed" if has_dependency and independent_sibling else "sequential",
    }


def evaluate_shared_state(inputs: dict[str, object]) -> dict[str, object]:
    write_conflict = inputs.get("same_target") is True and inputs.get("access") == "write"
    return {
        "concurrent_access": not write_conflict,
        "single_writer_required": write_conflict,
    }


def evaluate_delegation_exception(inputs: dict[str, object]) -> dict[str, object]:
    allowed_reasons = {"dependency", "exclusive-state", "slots", "tools", "permissions"}
    exception_allowed = (
        inputs.get("reason") in allowed_reasons
        and inputs.get("all_remaining_blocked") is True
    )
    return {
        "exception_allowed": exception_allowed,
        "disclose_reason": exception_allowed,
        "high_risk_audit_waived": False,
    }


def evaluate_dispatch_recovery(inputs: dict[str, object]) -> dict[str, object]:
    actions = {
        "transient": "retry-once",
        "idle-agent-available": "reuse-with-fresh-brief",
        "capacity-full": "queue-next-batch",
        "no-delegation-possible": "keep-local-and-disclose",
    }
    status = inputs.get("status")
    require(status in actions, f"unsupported dispatch status in behavior vector: {status!r}")
    return {"inspect_status_first": True, "action": actions[str(status)]}


def evaluate_audit_gate(inputs: dict[str, object]) -> dict[str, object]:
    high_risk_domains = {
        "security",
        "permissions",
        "payments",
        "data-loss",
        "schema-migration",
        "deployment",
        "global-configuration",
    }
    domains = set(inputs.get("risk_domains", []))
    requires_audit = bool(domains & high_risk_domains)
    implementers = inputs.get("implementers", [])
    require(isinstance(implementers, list) and all(isinstance(item, str) for item in implementers),
            "audit behavior vectors require an implementers list")
    auditor_independent = (
        inputs.get("auditor_available") is True
        and inputs.get("auditor") is not None
        and inputs.get("auditor") not in implementers
    )
    reaudit_required = requires_audit and inputs.get("changed_after_audit") is True
    findings = inputs.get("findings", [])
    require(isinstance(findings, list) and all(isinstance(item, dict) for item in findings),
            "audit behavior vectors require a findings list")

    def finding_is_resolved(finding: dict[str, object]) -> bool:
        disposition = finding.get("disposition")
        if disposition in {"fixed", "disproved-with-evidence"}:
            return True
        if disposition == "authorized-risk-acceptance":
            return (
                finding.get("authorization_present") is True
                and finding.get("higher_priority_policy_permits") is True
            )
        return False

    findings_resolved = all(finding_is_resolved(finding) for finding in findings)
    audit_ready = auditor_independent and findings_resolved and not reaudit_required
    deployment = "deployment" in domains
    pre_audit_passed = inputs.get("pre_audit_passed") is True
    ready_to_deploy = deployment and audit_ready and pre_audit_passed
    if not requires_audit:
        complete = True
    elif deployment:
        complete = (
            ready_to_deploy
            and inputs.get("deployment_executed") is True
            and inputs.get("deployment_evidence_available") is True
            and inputs.get("post_audit_passed") is True
        )
    else:
        complete = audit_ready
    return {
        "independent_audit_required": requires_audit,
        "auditor_independent": auditor_independent,
        "findings_resolved": findings_resolved,
        "ready_to_deploy": ready_to_deploy,
        "complete": complete,
        "reaudit_required": reaudit_required,
        "pre_and_post_deployment_audit": deployment,
        "claim_independent_audit": requires_audit and auditor_independent,
    }


def evaluate_mutation_boundary(inputs: dict[str, object]) -> dict[str, object]:
    return {
        "mutation_allowed": (
            inputs.get("mode") != "plan"
            and inputs.get("authorization") == "write"
        )
    }


def evaluate_fork_override(inputs: dict[str, object]) -> dict[str, object]:
    fork_turns = str(inputs.get("fork_turns"))
    has_override = (
        inputs.get("model_override") is True
        or inputs.get("reasoning_override") is True
    )
    inherit_parent = fork_turns == "all"
    recent_count = fork_turns.isdigit() and int(fork_turns) > 0
    valid = not (inherit_parent and has_override)
    if has_override and not inherit_parent:
        valid = fork_turns == "none" or recent_count
    return {
        "valid_combination": valid,
        "inherit_parent_settings": inherit_parent,
    }


def evaluate_preference_resolution(inputs: dict[str, object]) -> dict[str, object]:
    supplied = inputs.get("supplied_preference")
    valid_profiles = {"balanced", "economy", "quality"}
    supplied_valid = supplied in valid_profiles
    material = inputs.get("material_effect") is True
    host_can_ask = inputs.get("host_can_ask") is True
    already_asked = inputs.get("already_asked") is True
    ask = not supplied_valid and material and host_can_ask and not already_asked
    response = inputs.get("response")
    profile = str(response) if ask and response in valid_profiles else None
    if supplied_valid:
        profile = str(supplied)
    if profile is None:
        profile = "balanced"
    return {
        "ask_optional_question": ask,
        "profile": profile,
        "proceed_to_dispatch": True,
        "infer_subscription_plan": False,
        "waive_required_audit": False,
    }


def evaluate_model_policy(inputs: dict[str, object]) -> dict[str, object]:
    action = inputs.get("action")
    if action == "fallback":
        preferred_supported = inputs.get("preferred_supported") is True
        inherited_supported = inputs.get("inherited_supported") is True
        return {
            "delegate": preferred_supported or inherited_supported,
            "set_explicit_override": preferred_supported,
            "invent_support": False,
        }
    if action == "luna-reasoning":
        effort_order = {"low": 0, "medium": 1, "high": 2, "xhigh": 3, "max": 4, "ultra": 5}
        valid = effort_order.get(str(inputs.get("reasoning")), -1) >= effort_order["high"]
        return {
            "valid_combination": valid,
            "lower_luna_reasoning": False,
            "fallback": "none" if valid else "another-supported-model",
        }
    if action == "fast-mode":
        valid = inputs.get("explicit_request") is True and inputs.get("supported") is True
        return {"valid_combination": valid, "claim_applied": valid}
    if action == "setting-support":
        return {
            "verify_tool_schema": True,
            "verify_official_docs_when_needed": True,
            "claim_applied": inputs.get("supported") is True,
        }
    if action == "retry-diagnosis":
        blockers = {"information", "permissions", "tools", "unsupported-setting", "specification"}
        actual_blocker = inputs.get("failure_reason") in blockers
        return {
            "retry_with_other_models": not actual_blocker,
            "resolve_actual_blocker": actual_blocker,
        }
    raise ValidationError(f"unsupported model-policy action: {action!r}")


def evaluate_completion_gate(inputs: dict[str, object]) -> dict[str, object]:
    evidence_invalidated = inputs.get("evidence_invalidated") is True
    evidence_current = (
        not evidence_invalidated
        or inputs.get("affected_scope_reverified") is True
    )
    required_truths = (
        "assignments_accounted",
        "current_requirement_evidence",
        "subagent_checks_passed",
        "checks_proportional",
        "avoids_redundant_replay",
        "audit_findings_resolved",
    )
    complete = (
        all(inputs.get(key) is True for key in required_truths)
        and evidence_current
        and inputs.get("unrun_check_claimed_complete") is not True
    )
    return {
        "complete": complete,
        "reverify_scope": "affected-only" if evidence_invalidated else "none",
        "conflict_basis": "requirements-and-evidence",
    }


BEHAVIOR_EVALUATORS = {
    "delegation-trigger": evaluate_delegation_trigger,
    "parallel-allocation": evaluate_parallel_allocation,
    "explicit-atomic-allocation": evaluate_explicit_atomic_allocation,
    "audit-slot-reservation": evaluate_audit_slot_reservation,
    "dependency-schedule": evaluate_dependency_schedule,
    "shared-state": evaluate_shared_state,
    "delegation-exception": evaluate_delegation_exception,
    "dispatch-recovery": evaluate_dispatch_recovery,
    "audit-gate": evaluate_audit_gate,
    "mutation-boundary": evaluate_mutation_boundary,
    "preference-resolution": evaluate_preference_resolution,
    "fork-override": evaluate_fork_override,
    "model-policy": evaluate_model_policy,
    "completion-gate": evaluate_completion_gate,
}


def reject_duplicate_json_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON key in behavior cases: {key!r}")
        result[key] = value
    return result


def validate_behavior_cases() -> None:
    path = REPO_ROOT / "tests" / "behavior-cases.yaml"
    try:
        document = json.loads(
            read_utf8(path),
            object_pairs_hook=reject_duplicate_json_pairs,
        )
    except json.JSONDecodeError as error:
        raise ValidationError(
            "tests/behavior-cases.yaml must remain valid JSON (and therefore valid YAML 1.2)"
        ) from error
    require(isinstance(document, dict) and document.get("schema_version") == 2,
            "behavior cases must declare schema_version 2")

    declared_contracts = document.get("policy_contracts")
    require(isinstance(declared_contracts, dict) and declared_contracts,
            "behavior cases must declare policy_contracts")
    discovered_contracts = discover_policy_contracts()
    require(set(POLICY_REQUIRED_CLAUSES) == set(discovered_contracts),
            "validator policy clauses and discovered markers differ")
    for contract_id, probes in POLICY_FORBIDDEN_PROBES.items():
        patterns = POLICY_FORBIDDEN_PATTERNS[contract_id]
        for probe in probes:
            require(any(re.search(pattern, probe) for pattern in patterns),
                    f"semantic reversal probe was not detected for {contract_id}: {probe!r}")
    for contract_id, probes in POLICY_ALLOWED_PROBES.items():
        patterns = POLICY_FORBIDDEN_PATTERNS[contract_id]
        for probe in probes:
            require(not any(re.search(pattern, probe) for pattern in patterns),
                    f"allowed policy probe was rejected for {contract_id}: {probe!r}")
    require(set(declared_contracts) == set(discovered_contracts),
            "declared and discovered policy contracts differ; "
            f"missing={sorted(set(discovered_contracts) - set(declared_contracts))}, "
            f"extra={sorted(set(declared_contracts) - set(discovered_contracts))}")
    for contract_id, declaration in declared_contracts.items():
        require(isinstance(declaration, dict),
                f"policy contract {contract_id} must be an object")
        require(declaration == discovered_contracts[contract_id],
                f"policy contract {contract_id} points to {declaration!r}, "
                f"but its marker is at {discovered_contracts[contract_id]!r}")
        source = REPO_ROOT / str(declaration["source"])
        section_text = read_markdown_section(source, str(declaration["section"]))
        for clause in POLICY_REQUIRED_CLAUSES[contract_id]:
            require(" ".join(clause.split()) in section_text,
                    f"policy contract {contract_id} is missing required clause: {clause!r}")
        for clause in POLICY_FORBIDDEN_CLAUSES.get(contract_id, ()):
            require(" ".join(clause.split()) not in section_text,
                    f"policy contract {contract_id} contains forbidden reversal: {clause!r}")
        for pattern in POLICY_FORBIDDEN_PATTERNS.get(contract_id, ()):
            require(re.search(pattern, section_text) is None,
                    f"policy contract {contract_id} contains a semantic reversal matching: {pattern!r}")

    cases = document.get("cases")
    require(isinstance(cases, list), "behavior cases must contain a cases list")
    seen_cases: set[str] = set()
    referenced_contracts: set[str] = set()
    for index, case in enumerate(cases):
        require(isinstance(case, dict), f"behavior case {index} must be an object")
        case_id = case.get("id")
        require(isinstance(case_id, str) and case_id not in seen_cases,
                f"behavior case {index} has a missing or duplicate id")
        seen_cases.add(case_id)
        require(isinstance(case.get("scenario"), str) and case["scenario"].strip(),
                f"behavior case {case_id} requires a scenario")
        contracts = case.get("contracts")
        require(isinstance(contracts, list) and contracts
                and all(isinstance(item, str) for item in contracts),
                f"behavior case {case_id} requires contract IDs")
        require(len(contracts) == len(set(contracts)),
                f"behavior case {case_id} contains duplicate contract IDs")
        unknown_contracts = set(contracts) - set(declared_contracts)
        require(not unknown_contracts,
                f"behavior case {case_id} references unknown contracts: {sorted(unknown_contracts)}")
        referenced_contracts.update(contracts)

        rule = case.get("rule")
        require(rule in BEHAVIOR_EVALUATORS,
                f"behavior case {case_id} uses unsupported rule {rule!r}")
        vectors = case.get("vectors")
        require(isinstance(vectors, list) and vectors,
                f"behavior case {case_id} requires test vectors")
        seen_vectors: set[str] = set()
        for vector in vectors:
            require(isinstance(vector, dict),
                    f"behavior case {case_id} contains a non-object vector")
            vector_id = vector.get("id")
            require(isinstance(vector_id, str) and vector_id not in seen_vectors,
                    f"behavior case {case_id} has a missing or duplicate vector id")
            seen_vectors.add(vector_id)
            inputs = vector.get("input")
            expected = vector.get("expected")
            require(isinstance(inputs, dict) and isinstance(expected, dict),
                    f"behavior vector {case_id}/{vector_id} requires input and expected objects")
            actual = BEHAVIOR_EVALUATORS[str(rule)](inputs)
            require(actual == expected,
                    f"behavior vector {case_id}/{vector_id} failed; "
                    f"expected={expected!r}, actual={actual!r}")

    require(seen_cases == EXPECTED_CASE_IDS,
            "behavior case IDs differ from the required matrix; "
            f"missing={sorted(EXPECTED_CASE_IDS - seen_cases)}, "
            f"extra={sorted(seen_cases - EXPECTED_CASE_IDS)}")
    require(referenced_contracts == set(declared_contracts),
            "policy contracts must all be exercised by behavior vectors; "
            f"unreferenced={sorted(set(declared_contracts) - referenced_contracts)}")


def main() -> int:
    checks = [
        validate_frontmatter,
        validate_version_references,
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
