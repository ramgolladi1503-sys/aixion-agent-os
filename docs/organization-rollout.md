# Organization-wide adoption: existing AND future repositories

## What is enforced now
The central repo provides a reusable GitHub Actions workflow. A repository that
runs `aixion init /path/to/repo` receives a portable config, AGENTS.md pointer
(if no existing file), and a workflow calling the central policy check.

The bootstrap preserves existing AGENTS.md and config files. The generated
workflow validates onboarding metadata; it does NOT prove real agent execution,
authenticate approvals, or replace project-specific CI and branch protection.

## Existing repositories
For each authorized local checkout: create a feature branch, run
`python3 /path/to/aixion-agent-os/onboarding/onboard.py /path/to/repo`,
inspect the generated changes, test the project, and open a PR. Do not run
bulk writes against repositories without checking permissions and safety rules.

## Every future repository
Use a repository template containing the bootstrap artifacts, OR run the
bootstrap immediately after `git init` / `gh repo create`. These are
repeatable onboarding paths, not automatic account-level enforcement.

**Important**: GitHub does not automatically inherit workflows across all
repositories owned by a personal account. An organization-wide policy for
every newly created repository requires an organization-managed GitHub App
receiving repository-created webhooks, or another authorized inventory/
automation service with access to those repositories. A scheduled scan is
not instantaneous. GitHub organization rulesets and required workflows may
depend on plan and ownership. Do not claim coverage without validating it.

## Completion criteria
- Enumerate actual accessible repositories from GitHub, not local folders alone.
- Create a migration PR in every eligible existing repository.
- Configure a GitHub App or approved service for repository-created events.
- On every new repo event: verify scope, open a bootstrap PR (never push main),
  and record onboarding outcome.
- Reconcile inventory periodically to catch missed events.
- Track unonboarded repositories as noncompliant in Control Tower.
- Protect merge paths with branch/ruleset policies and verified approvals.
- Test real Codex and Antigravity execution adapters separately.

## Current status
Central reusable workflow and local bootstrap: implemented on feature branch,
subject to CI. Cross-repository rollout and automatic repo-created events:
NOT IMPLEMENTED. No existing application repository was changed in this PR.
