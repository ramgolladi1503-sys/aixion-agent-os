# Aixion Agent OS — Antigravity Integration Adapter

This adapter connects Google Antigravity workspaces to the centralized Aixion Agent OS.

## How Antigravity Works with Aixion Agent OS:
1. **Dynamic Roster Access**: Skills can be loaded directly from `aixion-agent-os` or installed globally in `~/.gemini/config/skills/`.
2. **Deterministic Task Routing**: The prompt or workflow executes `aixion select "<task>"` to discover the exact minimal agent team needed.
3. **Agile Governance**: All task artifacts follow `aixion-agent-os/governance/agile-lifecycle.yaml`.
4. **Tool/Action Guardrails**: Preserves all project-level rules (such as TradeBot order-action restrictions) while providing access to the 283 Agency Agents.
