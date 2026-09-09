# Optional model-routing profile

This profile supplies portable defaults for hosts that expose the listed models. It is a preference profile, not a compatibility requirement. Explicit user choices, higher-priority instructions, current tool schemas, and host availability take precedence.

Read this file only when selecting a model or reasoning override for a delegated unit. Delegation itself must continue with a supported inherited configuration when the preferred override is unavailable.

## Choose from task characteristics

| Preferred model | Consider first for |
| --- | --- |
| `gpt-5.6-luna` | Well-scoped discovery, structured processing, and implementation with fixed acceptance criteria |
| `gpt-5.6-terra` | General code analysis, feature work, review, bounded refactoring, and moderate design |
| `gpt-5.6-sol` | Complex analysis, multi-module changes, difficult diagnosis, and conflicting requirements |
| `gpt-6-astra` | Project-wide design, task decomposition, conflict resolution, complex tool workflows, and important integration audits |

Choose the model, reasoning effort, execution mode, and decision to delegate independently. Consider complexity, failure impact, ease of verification, required context and tools, change breadth, and total cost together.

## Apply runtime constraints

<!-- policy-contract: routing.settings-supported -->
<!-- policy-contract: routing.luna-high-minimum -->
<!-- policy-contract: routing.full-history-inherits -->
<!-- policy-contract: routing.unsupported-fallback -->

- Inspect the current collaboration tool schema before setting an override.
- Use `gpt-5.6-luna` only at `high` reasoning or above. If that combination is unsupported, choose another supported model instead of lowering Luna's reasoning.
- For other models, choose reasoning effort from the task's needs. Use `xhigh`, `max`, or `ultra` only when the added review value is concrete.
- Use Fast mode only when the user explicitly requests it and the current host exposes a supported control.
- Confirm the meaning and support of modes or aliases such as `Fast` and `Pro`, and reasoning levels such as `ultra`, from the current tool schema and, when needed, official host documentation. Never report an unsupported setting as applied.
- With `fork_turns="all"`, inherit the parent model and reasoning effort; do not set model or reasoning overrides.
- For a specific override, use `fork_turns="none"` or a positive recent-turn count and include all missing context in the brief.
- If overrides are unavailable but inherited execution is supported, delegate with the inherited configuration.

## Diagnose before retrying

<!-- policy-contract: routing.no-mechanical-retry -->

Do not retry through progressively different models when the failure comes from missing information, permissions, tools, an unsupported setting, or an incomplete specification. Resolve the actual blocker or report it.

Repository maintainers may update this profile independently from the core delegation policy as model availability changes. Keep the core usable when every listed model name becomes unavailable.
