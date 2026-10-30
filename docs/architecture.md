# Aixion Agent OS — Architecture & Operations Guide

## 1. Executive Summary

**Aixion Agent OS** is a lightweight, local-first agent operating system that provides organization-wide autonomous agent discovery, dynamic routing, Agile governance, and cross-project integration across all current and future Aixion Lab projects.

It indexes the complete **Agency Agents** roster (**283 specialized agents** across 19 divisions), dynamically routes requests to minimal sufficient teams, enforces strict role-separation and evidence gates, and natively supports both **Google Antigravity** and **Codex**.

---

## 2. Directory Structure

```text
aixion-agent-os/
├── bin/
│   └── aixion                        # Unified CLI (doctor, init, agents list/select, status, sync)
├── catalog/
│   ├── manifest.json                 # Unified index of all 283 upstream agents with capabilities & risk
│   ├── sync-policy.yaml              # Pinned commit (b37b5bb33b) and upstream update policies
│   ├── indexer.py                    # Scanner & manifest generator
│   ├── sync.py                       # Upstream change and tampering detector
│   └── upstream/agency-agents/       # Pinned upstream source repository
├── governance/
│   ├── organization-policy.md        # Precedence hierarchy and non-negotiable boundaries
│   ├── agile-lifecycle.yaml          # Formal Agile state machine (Backlog -> Released -> Done)
│   ├── approval-policy.yaml          # Human authorization gate requirements
│   └── evidence-contract.yaml        # Schema for task packets and role handoff receipts
├── routing/
│   └── router.py                     # Deterministic task classifier & dynamic agent selector
├── orchestration/
│   ├── engine.py                     # Agile state machine executor & transition validator
│   └── state_store/                  # Checkpoint persistence for crash recovery & audit
├── adapters/
│   ├── antigravity/                  # Antigravity skill mapping & instructions
│   └── codex/                        # Codex global prompt and custom agent adapter
├── onboarding/
│   └── onboard.py                    # Repository discovery, technology detection, & scaffolding
├── evaluation/
│   └── test_suite.py                 # Automated acceptance test suite (Tests A through J)
└── docs/
    ├── architecture.md               # Architecture documentation
    └── migration-report.md           # Organization project onboarding status
```

---

## 3. Dynamic Routing & Selection Model

Instead of polluting the model context window with hundreds of agent definitions:
1. **Task Arrival**: User or system supplies a prompt.
2. **Domain Classification**: Analyzes domain (`frontend`, `backend`, `trading`, `security`, `general`) and checks if the task is `safety_critical`.
3. **Role-Based Slotting**: Dynamically selects 3 to 4 specialized agents satisfying the core Agile seats:
   - Specification / Product Owner
   - Architecture / Lead
   - Implementation / Developer
   - Independent Verification / QA & Senior QA
4. **Explainable Rationale**: Every agent selection outputs an explicit attribution and score justifying why they were picked.

---

## 4. Agile Governance & Safety Controls

Tasks follow a rigorous 10-state progression:
`BACKLOG` → `REQUIREMENT_READY` → `DESIGN_READY` → `IN_DEVELOPMENT` → `DEV_VERIFIED` → `QA_VERIFIED` → `UAT_APPROVED` → `RELEASE_READY` → `RELEASED` → `DONE`.

### Enforced Constraints:
- **No Self-Approval**: Developers cannot certify QA; architects cannot self-certify implementation.
- **Safety Boundaries**: Tasks with `is_safety_critical=True` (e.g. order execution, live mode, credential changes) cannot transition to `IN_DEVELOPMENT` or `RELEASED` without explicit human authorization.
- **Audit Trails**: Every handoff generates a timestamped receipt in the persistent state store (`orchestration/state_store/`).
