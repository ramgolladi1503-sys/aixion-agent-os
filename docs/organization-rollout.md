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
subject to CI. Application rollout: 16 draft onboarding PRs opened in the owner's 16 other repositories;
none merged. Scheduled future-repository reconciliation is implemented but disabled.
Instantaneous repo-created webhook onboarding is NOT IMPLEMENTED.
Aixion Agent OS is the 17th repository and the central policy source.

## Scheduled GitHub reconciliation (implemented, disabled by default)

The central workflow `.github/workflows/reconcile-repositories.yml` runs every
six hours **only when enabled**. It enumerates repositories under the configured
GitHub owner, scopes to those tagged `aixion-managed`, checks whether each has
`.aixion/config.json`, and opens a **draft onboarding PR** for missing repos.
It never merges. It does not run unless all of these are configured:

1. Set the repository variable `AIXION_RECONCILE_ENABLED=true`.
2. Add a dedicated, least-privilege token as secret `AIXION_ROLLOUT_TOKEN`.
   The token must be able to list the owner's repositories and create branches
   and PRs in specifically authorized repositories. Do not use a broad
   personal token when a fine-grained token or GitHub App will work.
3. Add the `aixion-managed` GitHub topic to each existing and newly created
   Aixion project, regardless of its repository name.
4. Review the first dry run locally:
   `PYTHONPATH=. python3 onboarding/github_reconcile.py --owner ramgolladi1503-sys`.
5. Verify the initial workflow run, generated PRs and project-specific rules.

The first scan of a new tagged repository may take up to six hours plus
GitHub Actions scheduling delay. **This is eventual onboarding, not an
instantaneous repository-created webhook**. Repositories without the topic
are intentionally out of scope, including legacy repos until explicitly tagged.
The workflow is NOT enabled by this PR, and no rollout token was configured.

## Pilot and authorization gate

The website pilot (`aixion-lab-website` PR #21) passed its central
`governance / validate-onboarding` job. Its separate browser/visual suite
failed, so overall website CI is not green. The central policy implementation
remains in draft PR #1 (security) and stacked PR #2 (onboarding); application
PRs are also drafts. No claim of complete deployment is justified yet.

**Authorization needed from repository owner:** approve central PR review and
merges, then application PR review/merges after checks; configure the GitHub
secret `AIXION_ROLLOUT_TOKEN` and variable `AIXION_RECONCILE_ENABLED` only
after reviewing token scope. Do not paste tokens into PRs or chat. Grant
`Contents: Read and write` and `Pull requests: Read and write` on explicitly
selected repos; use a GitHub App for long-lived automation if possible.

This onboarding does not execute Codex/Antigravity, authenticate human
approvals, enforce branch protection, or connect Control Tower telemetry.
Those are separate release blockers for a full autonomous Agent OS.
