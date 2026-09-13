---
name: coordinate-subagents
description: Coordinate Codex subagents by delegating work only when the user requests it or a documented net-benefit check justifies it, assigning ownership, integrating evidence, and separating required high-risk audits. Do not activate solely because multiple work units exist, a task is complex, or orchestration is enabled.
license: MIT
metadata:
  version: "1.0.0"
---

# Coordinate Subagents

Coordinate work across subagents without expanding the user's scope, permissions, or requested side effects.

## Apply instruction priority

<!-- policy-contract: authority.inherit-mode -->

- Follow system, developer, user, repository, and mode constraints before this skill.
- Treat delegation as a way to execute authorized work, never as new authorization.
- Apply the current mode and write restrictions to every delegated task.
- Honor an explicit user choice about whether to delegate, how many agents to use, and which supported model or reasoning effort to select.

## Decide whether to delegate

At the start of a task, identify execution units and their dependencies. A unit is independent when it can begin without another unit's intermediate result and has its own responsibility, completion condition, and verification criterion.

Implementation delegation is allowed only when the user explicitly requests it or every net-benefit condition below is satisfied:

<!-- policy-contract: delegation.explicit-request -->
<!-- policy-contract: delegation.independent-parallel -->

- The unit has an independently verifiable result and completion condition.
- Concurrent execution reduces a real dependency or time bottleneck.
- A limited brief can provide enough context for accurate work.
- File and external-state ownership can remain disjoint and single-writer.
- Handoff, waiting, review, integration, and likely rework still cost less than direct execution.

A required high-risk audit justifies a separate auditor, not implementation delegation. Record the positive delegation reason before dispatch; the number of work units, task size, complexity, or `orchestration.requested` alone is not a positive reason.

<!-- policy-contract: delegation.atomic-local -->
<!-- policy-contract: delegation.allowed-exceptions -->

Keep work local when the net-benefit conditions are not all confirmed, including multi-unit work that is sequential, shares a writer, needs the coordinator's full context, or would cost more to hand off and integrate. When approved delegation cannot run because dependencies, exclusive state, slots, tools, or permissions make it impossible, keep the work local and disclose the concrete reason. Task size and coordinator convenience do not override the net-benefit check. No implementation-delegation decision waives a required high-risk audit.

## Resolve the delegation preference

<!-- policy-contract: preferences.ask-once -->

At the first point in each task when delegation will occur, check whether the user or host already supplied a delegation preference. If no preference exists and choosing among the bundled profiles would materially affect agent count, batching, model selection, or reasoning effort, ask one short optional question offering `balanced` (recommended), `economy`, and `quality`. Ask at most once per task. Do not ask when a preference is already available or the choice would not materially affect execution.

Continue safe preparation while an answer is pending. If no answer is available before dispatch or the host cannot ask, use `balanced` and proceed. Never infer a subscription plan from model availability or usage observations; use plan details only when the user or host provides them. A preference may tune allocation and supported runtime settings, but it never expands authority or waives required independent audits.

Read [the optional model-routing profile](references/model-routing.md) for the profile definitions.

## Assign work

<!-- policy-contract: allocation.keep-one-and-fill-slots -->
<!-- policy-contract: allocation.batch-reuse -->

When implementation delegation has been approved and two or more implementation units exist, keep one independent unit with the coordinator and assign the others across available slots. If the user explicitly asks to delegate the only implementation unit, assign that unit to a subagent and keep coordination and evidence review with the coordinator. Interpret slot counts from the host contract: when the host reports a total team capacity, the coordinator occupies one slot; when it reports subagent slots, those are all available to delegated work. When independent units exceed the usable slot count, run them in batches and reuse completed subagents with a fresh brief. Do not create artificial units merely to increase parallelism.

<!-- policy-contract: audit.reserve-identity -->

When high-risk work requires an independent auditor and later access to a fresh agent identity is uncertain, reserve a non-implementing subagent and its slot before filling implementation assignments.

Every brief must include:

- the goal and owned responsibility;
- explicit exclusions and write ownership;
- required inputs and relevant context;
- permission, mode, tool, and compatibility constraints;
- the expected output;
- completion and verification criteria.

<!-- policy-contract: context.limited-default -->

Use a limited-history or no-history fork by default. Supply the brief, source locations and artifact digests instead of the full conversation. Use full history only when omitting it would make the unit inaccurate or unverifiable, and record that concrete reason before dispatch. Do not paste large logs or completed work products into the coordinator context; return their artifact locations, conclusions, verification evidence, and unresolved items.

<!-- policy-contract: ownership.single-writer -->

Give one writer ownership of each shared file or external state. Sequence work when ownership cannot be separated safely. A subagent owns investigation, implementation, deliverable preparation, and verification inside its assigned scope and must coordinate before changing another owner's area.

Read [the delegation playbook](references/delegation-playbook.md) when preparing briefs, batching work, resolving ownership conflicts, handling failed dispatch, or running an audit.

## Coordinate and integrate

<!-- policy-contract: integration.no-redo -->

- Track each assignment and collect its output and verification evidence.
- Use follow-up messages to refine an existing assignment instead of silently duplicating it.
<!-- policy-contract: integration.no-duplicate-retry -->
- Do not dispatch another assignment with the same objective, input or candidate digest, and failure evidence unless a new discriminator or explicitly requested independent comparison changes the work.
- Wait for delegated work with the collaboration mechanism provided by the host.
- Do not redo delegated work. Review evidence, compare alternatives, resolve conflicts, and integrate the results.
- Resolve disagreements from requirements, current artifacts, and verification results rather than model identity.

## Require independent audits for high-risk work

<!-- policy-contract: audit.independent-required -->

Treat security, permissions, payments, data loss, schema migrations, deployments, and global configuration changes as high risk. Assign an auditor who did not implement the change. The auditor must inspect the requirements, final change, verification evidence, and plausible failure modes directly.

<!-- policy-contract: audit.no-completion-without-auditor -->
<!-- policy-contract: audit.reaudit-after-change -->

Do not report high-risk work as complete without an available independent auditor and resolved findings. If no auditor is available, state the limitation and do not claim that an independent audit occurred. If the audited area changes afterward, re-audit the affected portion. For deployments, audit readiness before execution and audit the resulting deployment evidence afterward.

<!-- policy-contract: audit.finding-disposition -->

Resolve each audit finding by fixing it, disproving it with evidence, or recording risk acceptance from an authorized decision-maker when higher-priority policy permits that outcome. Deferral alone does not resolve a finding.

## Select models only when useful

Read [the optional model-routing profile](references/model-routing.md) before choosing an explicit model or reasoning override. First inspect the collaboration tool's currently supported combinations. User or host settings override the bundled profile; unsupported profile entries never block delegation when an inherited supported configuration can do the work.

## Complete the task

Before reporting completion:

<!-- policy-contract: completion.current-evidence -->
<!-- policy-contract: completion.report-facts -->

- account for every assignment;
- confirm that each subagent's scoped verification actually passed;
- verify each requirement against current evidence with checks proportional to its failure impact;
- avoid checks that merely repeat the implementation, and reverify only the affected scope when a later change invalidates earlier evidence;
- integrate accepted results without overwriting unrelated user work;
- complete required independent audits and resolve their findings;
- report the result, material changes, checks actually run, their outcomes, and remaining constraints;
- never present an unrun check or unverified setting as completed.
