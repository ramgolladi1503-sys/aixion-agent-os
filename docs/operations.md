# Aixion Agent OS — Operations Guide

## 1. Daily Operations & CLI Usage

### Check System Health
```bash
aixion doctor
```

### Inspect Available Agent Catalog
```bash
aixion agents list
```

### Dynamic Team Selection
```bash
aixion agents select "Build React modal component"
```

### Onboarding a New Project
```bash
aixion init /path/to/project
```

### Checking Current Project Status
```bash
cd /path/to/project
aixion project status
```

---

## 2. Failure Recovery & Crash Resilience
Task state is continuously persisted in `orchestration/state_store/<TASK-ID>.json`.
If an agent crash, network drop, or execution interruption occurs:
1. Locate `<TASK-ID>` from logs or `aixion project status`.
2. Reload engine with `AgileWorkflowEngine(task_id="<TASK-ID>")`.
3. The exact state, history, and artifacts will be intact, allowing execution to resume from the last completed transition without duplicating past actions.

---

## 3. Human Approval Enforcement
For any safety-critical task:
- Live order actions, live broker connections, or credential edits are blocked by default.
- The state engine requires `human_approved=True` to transition to `IN_DEVELOPMENT` or `RELEASED`.
- Agent consensus cannot override human authorization.
