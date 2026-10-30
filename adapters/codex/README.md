# Aixion Agent OS — Codex Integration Adapter

This adapter connects Codex CLI and Codex Desktop environments to the centralized Aixion Agent OS.

## How Codex Works with Aixion Agent OS:
1. **Global Instructions**: Codex reads instructions from `~/.codex/AGENTS.md`. Aixion Lab governance is incorporated into the instructions hierarchy.
2. **Custom Agent TOMLs**: Upstream agency agents can be converted to Codex `.toml` definitions located in `~/.codex/agents/` using `catalog/upstream/agency-agents/scripts/convert.sh --tool codex`.
3. **Execution Mode**: Codex executes custom agents with consistent Agile handoff requirements.
4. **Safety Enforcement**: High-risk paths fail closed, ensuring that model simulation does not bypass approval gates.
