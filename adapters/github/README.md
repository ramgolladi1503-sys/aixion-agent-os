# Aixion Agent OS — GitHub Governance & Release Adapter

This adapter enforces GitHub-side release controls, branch protections, and PR gating.

## Invariant Policies:
1. **Never Push Directly to Protected Branches**:
   - Pushes to `main`, `master`, and `release/*` are strictly blocked for agents.
   - All changes must be delivered on isolated feature branches (e.g. `feat/...` or `fix/...`).
2. **Pull Request Readiness**:
   - A PR can only be created when the task reaches `RELEASE_READY`.
   - The PR description must link to the task's evidence artifact.
3. **Merge Authorization**:
   - An agent cannot execute `gh pr merge` without explicit human authorization.
   - CI status must be green before merge approval.
