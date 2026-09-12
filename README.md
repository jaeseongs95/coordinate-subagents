# Coordinate Subagents

[한국어](README.ko.md)

`coordinate-subagents` is a Codex skill for deciding when to delegate work, assigning independent work to subagents, coordinating shared state, and requiring a separate review for high-risk changes.

The repository is organized as a multi-skill package from the start. It currently contains one installable skill at [`skills/coordinate-subagents`](skills/coordinate-subagents). More focused skills and an orchestrator can be added without merging their instructions into one large skill.

> **Community project:** This repository is not an official OpenAI project and is not affiliated with or endorsed by OpenAI.

## What it does

- Separates independent work from sequential or atomic work before delegating.
- Assigns clear ownership, inputs, constraints, outputs, and verification criteria.
- Keeps shared-file and shared-state writes coordinated.
- Uses an independent reviewer for security, permissions, payments, data loss, migrations, deployment, and global configuration changes.
- Leaves final integration and accountability with the coordinating agent.
- Offers an optional model-routing profile for Luna, Terra, Sol, and Astra while respecting the models and reasoning levels available in the current host.

The model-routing profile is a maintainer-recommended default, not a requirement. User instructions, repository rules, host capabilities, and runtime restrictions take precedence. See [`model-routing.md`](skills/coordinate-subagents/references/model-routing.md).

## Install

Use the built-in `$skill-installer` and give it the GitHub folder URL:

```text
$skill-installer install https://github.com/jaeseongs95/coordinate-subagents/tree/main/skills/coordinate-subagents
```

Enter this as a Codex prompt, not as a shell command.

To pin the current `v1.0.0` release:

```text
$skill-installer install https://github.com/jaeseongs95/coordinate-subagents/tree/v1.0.0/skills/coordinate-subagents
```

Codex normally detects newly installed skills automatically. Restart Codex if the skill does not appear. The [official OpenAI skill guide](https://learn.chatgpt.com/docs/build-skills) describes local skill installation and discovery.

You can install and use this skill on its own as described above. To use it in an integrated workflow with other governance skills, install the [Agent Governance Suite](https://github.com/jaeseongs95/agent-governance-suite), which includes this skill.

## Use

Invoke the skill explicitly when you want delegation to be part of the task:

```text
$coordinate-subagents split this work into independent units, run the safe units in parallel, and integrate the verified results.
```

The skill also allows implicit invocation. Codex may select it when a request clearly involves parallel delegation, ownership coordination, or an independent high-risk review. Implicit matching depends on the skill description and the host's current skill configuration.

Installing or invoking this skill does not grant permissions, bypass approvals, expand the user's request, or make unavailable tools and models available. Every subagent remains subject to the same applicable user instructions, repository rules, execution mode, sandbox, permissions, and tool access.

## Validation

Run `python tests/validate_skill.py` before publishing. CI runs the same check on Ubuntu and Windows. It validates package metadata, links, licenses, UI metadata, unfinished scaffold markers and secret hygiene, policy-contract markers, and structured policy decision vectors. These deterministic checks verify the documented policy contract; they do not claim to make language-model behavior deterministic. Use an independent forward test and audit as release evidence for material behavior changes.

## Repository layout

```text
coordinate-subagents/
├── skills/
│   └── coordinate-subagents/
│       ├── SKILL.md
│       ├── agents/openai.yaml
│       └── references/
├── tests/
├── README.md
├── README.ko.md
└── LICENSE
```

Each future workflow should remain a focused skill under `skills/<skill-name>/`. If several workflows need one entry point, add a separate orchestrator skill that classifies the request, selects the required skills, orders their inputs and outputs, checks intermediate results, and integrates the final result.

## Planned plugin packaging

The repository is ready to grow into this structure:

```text
coordinate-subagents/
├── plugin.json                  # added when plugin packaging begins
├── skills/
│   ├── workflow-orchestrator/   # routing and integration
│   ├── coordinate-subagents/    # delegation and review policy
│   ├── requirements/            # future focused skill
│   ├── design/                  # future focused skill
│   ├── validation/              # future focused skill
│   └── packaging/               # future focused skill
└── ...
```

The current package intentionally does not include `plugin.json`; it distributes only the standalone `coordinate-subagents` skill. When multiple skills are ready, add the canonical portable `plugin.json` at the repository root and package the existing `skills/` tree without moving this skill. Do not treat the compatibility `.codex-plugin/plugin.json` format as the canonical portable manifest. See the official OpenAI guides for [building skills](https://learn.chatgpt.com/docs/build-skills) and [packaging plugins](https://developers.openai.com/plugins/build/plugins).

## License

[MIT](LICENSE)
