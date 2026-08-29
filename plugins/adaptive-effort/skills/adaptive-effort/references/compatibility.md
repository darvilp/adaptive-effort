# Compatibility snapshot

Snapshot date: 2026-08-28

## Required capabilities

- Codex subagents enabled
- `spawn_agent` with an explicit reasoning-effort override
- a fresh-context spawn option (`fork_turns="none"` or older equivalent)
- Superpowers skills equivalent to:
  - `subagent-driven-development`
  - `test-driven-development`
  - `verification-before-completion`
  - `requesting-code-review` or another review workflow

## Supported distribution surface

The package is a native skills-only Codex plugin and community marketplace.

The Codex app and CLI support plugins. Codex IDE extensions do not currently support plugins. Use the Codex app or CLI for Adaptive Effort.

## Custom-agent packaging

Current plugin manifests do not support installing standalone `.codex/agents/*.toml` definitions. Adaptive Effort therefore uses explicit `reasoning_effort`, inherited model, fresh context, and role instructions in each spawn message without requiring an agent-type field.

## Superpowers target

Compatibility is capability-based rather than version-only. Installed-cache inspection on 2026-08-28 found the OpenAI-curated Superpowers plugin version 6.3.0 and its required named workflow skills.

Unknown Superpowers versions may run when required skills are present, but diagnostics should warn until tested.

## Evidence boundaries

- Current OpenAI documentation establishes Codex app, CLI, and IDE support claims.
- Installed-cache inspection establishes that Superpowers 6.3.0 and Adaptive Effort 0.1.0 were present. It does not prove runtime routing.
- The exact live smoke returned `ADAPTIVE_EFFORT_SMOKE_OK` after a child was requested with inherited model, low effort, and fresh context. The token proves the child spawn/tool path completed with the requested settings. It does not independently observe or prove the child's model, effort, or context metadata.
- A fresh task exposed Adaptive Effort from the installed plugin. That separately proves new-task pickup.

## Known limits

- A skill cannot guarantee the host exposes model, effort, or context metadata for post-spawn inspection. Record host or UI metadata separately when it is available.
- Explicit spawn effort can be unavailable in some product surfaces or model configurations.
- The doctor script can inspect local installation and configuration but cannot prove runtime routing without a live smoke spawn.
- The parent sandbox and approval mode are inherited by subagents.


## Snapshot sources

- OpenAI Plugins overview: https://developers.openai.com/codex/plugins
- OpenAI Codex changelog, March 25, 2026 plugin entry: https://developers.openai.com/codex/changelog
- OpenAI Build plugins: https://developers.openai.com/codex/build-plugins
- OpenAI Codex developer commands: https://developers.openai.com/codex/developer-commands
- OpenAI Codex source, multi-agent spawn specification: https://github.com/openai/codex/blob/main/codex-rs/core/src/tools/handlers/multi_agents_spec.rs
- OpenAI-curated Superpowers plugin: https://github.com/openai/plugins/tree/main/plugins/superpowers
