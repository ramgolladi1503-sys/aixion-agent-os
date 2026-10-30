# Aixion Agent OS

> Organization-wide autonomous agent discovery, dynamic routing, Agile governance, and project integration.

[![Build & Acceptance Tests](https://img.shields.io/badge/tests-10%2F10%20passing-brightgreen)](#acceptance-tests)
[![Adversarial Audit](https://img.shields.io/badge/security-10%2F10%20blocked%20(100%25)-blue)](#adversarial-panel-verification)
[![Agency Agents Catalog](https://img.shields.io/badge/catalog-283%20agents-purple)](#catalog-and-dynamic-routing)

---

## 1. Overview

**Aixion Agent OS** (`aixion-agent-os`) provides an organization-wide operating system that governs all existing and future Aixion Lab projects. It bridges the complete [Agency Agents](https://github.com/msitarzewski/agency-agents) catalog (283 agents across 19 divisions) with deterministic capability routing, strict Agile state machine governance, fail-closed human approval boundaries, and unified developer environment adapters for **Google Antigravity** and **Codex**.

---

## 2. Architecture

```text
aixion-agent-os/
├── bin/
│   └── aixion                        # Unified CLI (doctor, init, agents list/select, status, sync)
├── catalog/
│   ├── upstream/agency-agents/       # Pinned upstream source repository (commit b37b5bb33b)
│   ├── extracted/                    # Converted tool-specific definitions:
│   │   ├── antigravity/ (283 skills) # Antigravity SKILL.md files
│   │   └── codex/ (283 TOMLs)        # Codex .toml custom agent files
│   ├── manifest.json                 # Complete index of all 283 agents with capabilities & risk
│   ├── sync-policy.yaml              # Update policy & quarantine rules
│   ├── indexer.py                    # Scanner & manifest generator
│   └── sync.py                       # Upstream change & tampering detector
├── governance/
│   ├── organization-policy.md        # Precedence hierarchy and non-negotiable boundaries
│   ├── agile-lifecycle.yaml          # Formal Agile state machine (Backlog -> Released -> Done)
│   ├── approval-policy.yaml          # Human authorization gate requirements
│   ├── risk-classification.yaml      # 3-tier risk model (HIGH, MEDIUM, LOW)
│   └── evidence-contract.yaml        # Schema for task packets and role handoff receipts
├── routing/
│   └── router.py                     # Deterministic task classifier & dynamic agent selector
├── orchestration/
│   ├── engine.py                     # Agile state machine executor & transition validator
│   ├── state_store/                  # Checkpoint persistence for crash recovery & audit
│   └── control_tower_telemetry.jsonl # Telemetry event log for Control Tower bridge
├── adapters/
│   ├── antigravity/                  # Antigravity skill mapping & instructions
│   ├── codex/                        # Codex global instructions & TOML adapter
│   ├── github/                       # GitHub branch protection, PR readiness & release gates
│   └── control_tower_bridge.py       # Live event streaming into Aixion Control Tower
├── onboarding/
│   └── onboard.py                    # Repository discovery, technology detection, & scaffolding
├── evaluation/
│   └── test_suite.py                 # Automated acceptance test suite (Tests A through J)
├── adversarial_audit/
│   ├── harnesses/attack_vector_runner.py  # 10-vector automated adversarial attack harness
│   └── reports/                           # Complete 20-agent adversarial panel sign-off report
└── docs/
    ├── architecture.md               # Architecture documentation
    ├── installation.md               # Prerequisites & installation instructions
    ├── operations.md                 # Daily operations, recovery, and CLI guide
    └── migration-report.md           # Organization project onboarding status
```

---

## 3. Quick Start & CLI Usage

### System Diagnostics
```bash
./bin/aixion doctor
```

### Dynamic Team Selection
```bash
./bin/aixion agents select "Build React modal component with dark mode"
```

### Onboarding an Existing or New Project
```bash
./bin/aixion init /path/to/project
```

### Upstream Catalog Synchronization & Tamper Check
```bash
./bin/aixion catalog sync
```

---

## 4. Acceptance Tests

Run the test suite covering Tests A through J:

```bash
PYTHONPATH=. python3 evaluation/test_suite.py
```

Results:
- **TEST A**: Complete catalog (283 agents indexed, SHA-256 verified)
- **TEST B**: Dynamic selection (Frontend task picks frontend/design/QA)
- **TEST C**: Specialized routing (Trading task picks quant/runtime/risk)
- **TEST D**: Existing project (TradeBot retains rules under Aixion governance)
- **TEST E**: New project scaffolding (Onboards and generates config)
- **TEST F**: Cross-environment consistency (Antigravity & Codex shared policies)
- **TEST G**: Approval enforcement (Blocked transitions without authorization)
- **TEST H**: Failure recovery (State store checkpoint reloads intact)
- **TEST I**: Catalog updates (Sync detector flags differences)
- **TEST J**: Noninterference (Does not alter repo runtime files)

---

## 5. Adversarial Panel Verification

Tested against a 20-agent adversarial panel (10 Attackers + 10 Reviewers) covering prompt injection, developer self-approval bypass, silent live trading promotion, manifest poisoning, DoS context flooding, state store path traversal, privilege escalation, and state re-entry:

```bash
PYTHONPATH=. python3 adversarial_audit/harnesses/attack_vector_runner.py
```
**Outcome**: 10 / 10 attacks blocked with zero bypasses.
