# Provider-neutral model-routing presets

This policy supplies portable model and reasoning-effort recommendations for hosts that expose compatible subagent controls. The machine-readable source is [`model-routing-presets.json`](model-routing-presets.json).

Explicit user choices, higher-priority instructions, repository rules, current host capabilities, and runtime restrictions take precedence over every preset.

## Keep presets separate from delegation

<!-- policy-contract: routing.preset-does-not-delegate -->
<!-- policy-contract: routing.user-override-precedence -->

Apply a preset only after implementation delegation or an independent audit has already been approved. A preset selects a model and reasoning effort for an assigned role; it never triggers delegation, increases agent count, changes batching, broadens authority, or waives a required audit.

Use `balanced` when no preference is available. Ask about `economy`, `balanced`, or `quality` at most once and only when the model or effort choice would materially affect execution. A user-supplied model or effort overrides the preset when the host supports it.

## Map roles before providers

<!-- policy-contract: routing.role-provider-matrix -->

Classify each approved assignment as one of these roles before consulting a provider mapping:

- `discovery`: bounded search, inventory, extraction, or structured processing with a clear check;
- `general-implementation`: ordinary code analysis, feature work, review, and bounded refactoring;
- `complex-reasoning`: difficult diagnosis, multi-module design, conflicting requirements, or costly integration;
- `independent-audit`: a fresh review of high-risk requirements, final changes, evidence, and failure modes.

Select the profile and role first, then resolve the current host's provider entry in `model-routing-presets.json`. Provider model names and effort labels are adapter values, not cross-provider quality equivalences.

## Apply the OpenAI Codex adapter

<!-- policy-contract: routing.codex-adapter -->
<!-- policy-contract: routing.luna-high-minimum -->
<!-- policy-contract: routing.full-history-inherits -->

For Codex collaboration tools, pass the selected `model` and `reasoning_effort` as spawn arguments only when the current schema supports that exact combination. With `fork_turns="all"`, inherit the parent model and reasoning effort; do not set model or reasoning overrides. For an explicit override, use `fork_turns="none"` or a positive recent-turn count and include missing context in the brief.

Use `gpt-5.6-luna` only at `high` reasoning or above. If that combination is unsupported, choose another supported model instead of lowering Luna's reasoning. For other models, use `xhigh`, `max`, or `ultra` only when the added review value is concrete.

Consult the current collaboration tool schema first and use the [official OpenAI model-selection guide](https://developers.openai.com/api/docs/guides/latest-model) when current product guidance is needed.

## Apply the Anthropic Claude Code adapter

<!-- policy-contract: routing.claude-code-adapter -->

For Claude Code, prefer stable aliases such as `haiku`, `sonnet`, `opus`, and `fable` instead of pinning dated model IDs. Apply `model` and `effort` in a custom subagent definition or CLI agent definition; a per-invocation model argument may override the definition when the current host supports it. Keep effort in the subagent definition or inherit the active effort when per-invocation effort is unavailable.

Before dispatch, check the installed Claude Code version, organization allowlist, provider availability, and any environment variable that forces a model. After dispatch, use the task view to confirm the actual model and effort when verification matters. Claude Code effort levels are calibrated within each model, so do not treat the same label as an exact match to a Codex reasoning level.

Use the official Claude Code documentation for [model configuration](https://code.claude.com/docs/en/model-config) and [custom subagents](https://code.claude.com/docs/en/sub-agents) when current support or precedence is uncertain.

## Apply runtime constraints

<!-- policy-contract: routing.settings-supported -->
<!-- policy-contract: routing.unsupported-fallback -->

Inspect the current host schema and capabilities before setting an override. Never report an unsupported or unverified setting as applied. Treat subscription details as context, not proof that a model, usage allowance, or runtime control is available.

For high-risk work, do not use a model class below `general` or effort below `high`. If a preset falls below that floor, promote the role to the same profile's `general-implementation` selection and then raise effort to `high` if needed.

Use modes such as `Fast` and `Pro`, or effort levels such as `ultra` and `ultracode`, only when the user explicitly requests them and the current host documents and exposes the control. If a preferred override is unavailable but inherited execution is supported, delegate with the inherited configuration. If neither is supported, report the capability limit without changing the approved work's scope.

## Diagnose before retrying

<!-- policy-contract: routing.no-mechanical-retry -->

Do not retry through progressively different models when the failure comes from missing information, permissions, tools, an unsupported setting, or an incomplete specification. Resolve the actual blocker or report it.

The preset matrix is a versioned maintainer recommendation. Update provider mappings and deterministic fixtures when host capabilities change; keep the core delegation policy usable when every listed model name becomes unavailable.
