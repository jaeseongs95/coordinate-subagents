---
name: coordinate-subagents
description: Coordinate Codex subagents by decomposing multi-part work, delegating independent units, assigning ownership, integrating evidence, and requiring separate audits for high-risk changes. Use when the user requests delegation or parallel agents, when work has two or more independently executable units, or when high-risk work needs an independent audit. Do not use for atomic work that does not need independent review.
license: MIT
metadata:
  version: "0.1.0"
---

# Coordinate Subagents

Coordinate work across subagents without expanding the user's scope, permissions, or requested side effects.

## Apply instruction priority

- Follow system, developer, user, repository, and mode constraints before this skill.
- Treat delegation as a way to execute authorized work, never as new authorization.
- Apply the current mode and write restrictions to every delegated task.
- Honor an explicit user choice about whether to delegate, how many agents to use, and which supported model or reasoning effort to select.

## Decide whether to delegate

At the start of a task, identify execution units and their dependencies. A unit is independent when it can begin without another unit's intermediate result and has its own responsibility, completion condition, and verification criterion.

Delegate when any of these conditions holds:

- The user explicitly asks for subagents, delegation, or parallel work.
- Two or more independent units exist.
- A high-risk change requires an independent auditor.

Keep atomic work local. Delegation may also be impossible when every remaining unit depends on prior output, the same file or state requires exclusive access, or collaboration slots, tools, or permissions are unavailable. If an independent unit is not delegated for one of these reasons, state the concrete reason. Task size, coordinator convenience, handoff cost, or token cost alone are not reasons to skip required delegation.

## Assign work

Keep one independent unit with the coordinator and assign the others across available slots. Interpret slot counts from the host contract: when the host reports a total team capacity, the coordinator occupies one slot; when it reports subagent slots, those are all available to delegated work. When independent units exceed the usable slot count, run them in batches and reuse completed subagents with a fresh brief. Do not create artificial units merely to increase parallelism.

Every brief must include:

- the goal and owned responsibility;
- explicit exclusions and write ownership;
- required inputs and relevant context;
- permission, mode, tool, and compatibility constraints;
- the expected output;
- completion and verification criteria.

Give one writer ownership of each shared file or external state. Sequence work when ownership cannot be separated safely. A subagent owns implementation and verification inside its assigned scope and must coordinate before changing another owner's area.

Read [the delegation playbook](references/delegation-playbook.md) when preparing briefs, batching work, resolving ownership conflicts, handling failed dispatch, or running an audit.

## Coordinate and integrate

- Track each assignment and collect its output and verification evidence.
- Use follow-up messages to refine an existing assignment instead of silently duplicating it.
- Wait for delegated work with the collaboration mechanism provided by the host.
- Do not redo delegated work. Review evidence, compare alternatives, resolve conflicts, and integrate the results.
- Resolve disagreements from requirements, current artifacts, and verification results rather than model identity.

## Require independent audits for high-risk work

Treat security, permissions, payments, data loss, schema migrations, deployments, and global configuration changes as high risk. Assign an auditor who did not implement the change. The auditor must inspect the requirements, final change, verification evidence, and plausible failure modes directly.

Do not report high-risk work as complete without an available independent auditor and resolved findings. If the audited area changes afterward, re-audit the affected portion. For deployments, audit readiness before execution and audit the resulting deployment evidence afterward.

## Select models only when useful

Read [the optional model-routing profile](references/model-routing.md) before choosing an explicit model or reasoning override. First inspect the collaboration tool's currently supported combinations. User or host settings override the bundled profile; unsupported profile entries never block delegation when an inherited supported configuration can do the work.

## Complete the task

Before reporting completion:

- account for every assignment;
- verify each requirement against the current state;
- integrate accepted results without overwriting unrelated user work;
- complete required independent audits and resolve their findings;
- report the result, material changes, checks actually run, their outcomes, and remaining constraints.
