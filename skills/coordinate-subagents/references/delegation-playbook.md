# Delegation playbook

Read this reference when a task needs concrete assignment briefs, batching, shared-state coordination, failure recovery, or an independent audit.

## Build the task graph

For each execution unit, record:

| Field | Decision |
| --- | --- |
| Goal | Observable outcome owned by the unit |
| Dependencies | Prior results required before starting |
| Inputs | Files, facts, tools, and context it may use |
| Writes | Files or external state it alone may change |
| Completion | Conditions that make the unit finished |
| Verification | Evidence the unit must return |
| Risk | Ordinary or high risk, with the reason |

Units are independent only when they can start from available inputs and their ownership, completion, and verification remain separable. Reading the same source does not create a conflict. Concurrent writes to the same file or external record do.

## Prepare a delegation brief

Use this shape and replace every field with task-specific content:

```text
Goal: <one observable outcome>
Ownership: <files, subsystem, records, or decision area>
Do not change: <other agents' areas and out-of-scope work>
Inputs: <required artifacts and facts>
Constraints: <permissions, execution mode, tools, compatibility, style>
Deliverable: <result or artifact to return>
Done when: <completion conditions>
Verify with: <checks and evidence to report>
Coordination: <when to contact the coordinator before crossing scope>
```

When reusing a completed agent, send a complete new brief. Do not assume the old responsibility remains active.

## Batch and synchronize

<!-- policy-contract: allocation.explicit-single-delegation-playbook -->

- After the net-benefit decision approves implementation delegation, keep one useful implementation unit with the coordinator when two or more implementation units exist. If the user explicitly delegates the only implementation unit, give it to the subagent and keep coordination and evidence review with the coordinator.
- Interpret the host's slot contract before allocating work. A reported total team capacity includes the coordinator unless the host says otherwise; a reported subagent count does not.

<!-- policy-contract: audit.reserve-identity-playbook -->

- When a required high-risk audit may not have access to a fresh identity later, reserve a non-implementing subagent and slot before assigning all implementation work.
- Fill only currently available subagent slots after that calculation.
- If more units remain, queue the next independent batch and reuse completed agents.
- Use a single writer for shared files. Other agents return proposed changes or evidence to that writer.
- Start dependent work only after validating the upstream result it consumes.
- Do not ask multiple agents to solve the same unit unless independent comparison or audit is the stated purpose.

## Recover from dispatch problems

<!-- policy-contract: dispatch.inspect-and-recover -->

If a spawn or dispatch fails, inspect agent status before deciding what happened. Then choose the narrowest applicable recovery:

1. Retry a transient dispatch once when the status supports it.
2. Reuse an idle existing agent with a fresh brief.
3. Queue the unit for a later batch.
4. Keep the unit local only when delegation is no longer possible and disclose why.

Do not infer a permanent agent limit from a single failure. Do not switch models repeatedly when the actual blocker is missing data, permissions, tools, or specification.

## Run an independent audit

The auditor must be separate from every implementer whose work is in scope. Provide the request, final artifacts or diff, verification evidence, and the minimum raw context needed to judge the outcome. Do not provide a preferred verdict or hide known failures.

Ask the auditor to check:

- whether the final state satisfies each requirement;
- whether authority and scope stayed within the request;
- whether security, privacy, payment, migration, deployment, or data-loss risks were addressed;
- whether the verification evidence is meaningful and current;
- which failure modes remain and how severe they are.

Resolve every finding. If a fix changes an audited area, send the affected result back for re-audit. For a deployment, audit the final readiness state before execution, then inspect deployment logs, migration results, and post-deployment checks before completion. If no independent auditor is available, state the limitation and do not mark the high-risk task complete.

## Integrate results

The coordinator reviews returned artifacts and evidence without repeating the assigned implementation. Accept or reject a result against requirements and current state. When results conflict, compare their evidence and validation rather than model names.

The final report must distinguish completed work, checks actually run, unresolved findings, and unavailable verification.
