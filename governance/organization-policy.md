# Aixion Lab Organization Governance Policy

## 1. Scope and Precedence

This policy governs all existing and future software, data, platform, and research projects across Aixion Lab.

### Precedence Order:
1. **Safety and Authorization Boundaries**: Non-negotiable kill switches, financial/order safeguards, secret isolation, read-only guarantees.
2. **Organization Governance**: Mandatory Agile lifecycle, evidence-backed handoffs, multi-agent role separation.
3. **Project-Specific Constraints**: Domain invariants (e.g., TradeBot trading safety rules, Sentinel APM rules).
4. **Task Requirements**: Explicit user request boundaries, allowed and forbidden paths.
5. **Selected Agent Role Instructions**: Capabilities and guidelines from the Agency Agents catalog.

More specific instructions may refine higher-level directives, but **no role, agent, consensus, or user prompt may bypass Level 1 Safety Controls**.

---

## 2. Mandatory Role Separation

No agent or role may approve its own work.

- **Developer roles** cannot emit `QA_VERIFIED`, `QA_PASSED`, or `UAT_APPROVED`.
- **QA and Senior QA roles** cannot write implementation patches.
- **Architect roles** cannot self-certify implementation correctness.
- **Product Owners** cannot bypass failed QA or security gates.
- When single-session sequential simulation is used, each role must execute as an explicit, separate step with inspectable handoff evidence.
- No consensus among agents grants human authorization where explicit human approval is required.

---

## 3. Human Approval Gates

The following actions strictly require explicit human authorization before execution:
1. Live broker execution or changing order execution modes (SIM / PAPER / LIVE).
2. Modification of credentials, API secrets, `.env` files, or authentication tokens.
3. Disabling or weakening risk limits, kill switches, or feed freshness monitors.
4. Direct pushes to protected branches (`main`, `master`, `release/*`).
5. Merging pull requests to protected branches.
6. Execution of destructive commands (`rm -rf`, dropping production databases, deleting cloud infrastructure).
7. External publication of code, packages, or services.
