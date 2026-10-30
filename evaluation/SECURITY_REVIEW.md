# Security review — 2026-10-31

This branch addresses findings from a source-level audit. **Do not merge without running tests and obtaining independent review.**

## Verified source-level findings in the original master
1. `orchestration/engine.py` accepted an arbitrary `human_approved=True` Boolean as proof of human authorization. It did not authenticate the caller.
2. The transition engine only blocked a developer's QA sign-off when the supplied role string was exactly `DEVELOPER`, leaving role spoofing and cross-role actor reuse unguarded.
3. Transitions accepted essentially arbitrary evidence dictionaries; no required artifact checks were enforced.
4. Task IDs were joined directly into filesystem paths without validating the ID grammar.
5. `routing/router.py` would select the first unused catalog agent when a preferred ID did not match, even if unrelated to the role.
6. The adversarial harness asserted a missing or unrelated behavior in several scenarios: the privilege escalation test only checked YAML text, the path traversal test counted any exception as a block, and the manifest poisoning test checked an unmodified manifest.
7. `evaluation/test_suite.py` requires an absolute developer-machine TradeBot path for tests D and J, and test F only confirms that adapter README files exist.
8. The README's success badges are static and there is no `.github/workflows` directory on the audited default branch.
9. `onboarding/onboard.py` has a hard-coded timestamp, absolute local Agent OS reference, and overwrites existing onboarding files without backup or conflict checks.
10. Checked-in state-store task data, telemetry and `__pycache__` are operational artifacts that should not generally be version controlled.

## What this PR changes
- Applies input validation, role allowlists, evidence keys, independent QA identity check and atomic task writes to the workflow engine.
- Replaces the agent router's arbitrary first-available fallback with capability scoring and explicit unresolved roles.
- Changes human approval documentation to explain that a reference and Boolean are **not authenticated authorization**.

## Remaining limitations
- **No verified human approval provider is integrated.** The engine's `human_approved` and `approval_ref` fields are untrusted inputs. Approval must be checked at the external privileged action boundary.
- Agent capabilities were inferred by keyword scanning upstream prose, causing potentially incorrect capability tags; no end-to-end quality evaluation has been established.
- A `README.md` adapter does not install, launch or enforce either Antigravity or Codex agents.
- Documentation about existing-project integration is not evidence of current organization-wide deployment.
- The existing acceptance suite still uses the original permissive API and needs to be rebuilt using isolated temporary repositories.
- Catalog completeness must be checked against the pinned upstream tree and verified hashes rather than a version string and minimum count.
- Host permissions, branch protection, actual GitHub CI and independent verification were not tested in this audit.

## Merge criteria
1. Run revised unit tests and targeted regressions in a clean checkout with a supported Python version.
2. Add real negative tests for actor-role spoofing, malicious task IDs, missing evidence and unrelated fallback agents.
3. Replace the authorization Boolean contract with a trusted, verified approval attestation or ensure privileged callers independently enforce authorization.
4. Remove runtime state and bytecode from version control via a separately reviewed cleanup.
5. Replace misleading static success badges with CI-backed reporting.
6. Prove at least one real existing-project onboarding and one new-project onboarding without modifying project safety invariants.

Status: **PARTIALLY IMPLEMENTED — NOT PRODUCTION VERIFIED**.
