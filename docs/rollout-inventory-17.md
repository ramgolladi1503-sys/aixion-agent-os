# Aixion Agent OS — 17-repository onboarding inventory

Status as of 2026-10-31. This inventory records **draft PRs**, not deployments
to default branches. No application code or broker behavior was changed.

| Repository | Onboarding PR | Governance check |
| --- | --- | --- |
| tradebot | https://github.com/ramgolladi1503-sys/tradebot/pull/991 | PASS |
| password-manager | https://github.com/ramgolladi1503-sys/password-manager/pull/1 | PASS |
| idea_canvas | https://github.com/ramgolladi1503-sys/idea_canvas/pull/1 | PASS |
| algotradify | https://github.com/ramgolladi1503-sys/algotradify/pull/140 | PASS |
| axiom | https://github.com/ramgolladi1503-sys/axiom/pull/2 | PASS |
| MCP | https://github.com/ramgolladi1503-sys/MCP/pull/57 | PASS |
| Job-Application-Agent | https://github.com/ramgolladi1503-sys/Job-Application-Agent/pull/1 | PASS |
| aixion-control-tower | https://github.com/ramgolladi1503-sys/aixion-control-tower/pull/205 | PASS |
| veriforge | https://github.com/ramgolladi1503-sys/veriforge/pull/2 | PASS |
| tablock | https://github.com/ramgolladi1503-sys/tablock/pull/11 | PASS |
| tradebot_mobile | https://github.com/ramgolladi1503-sys/tradebot_mobile/pull/1 | PASS |
| openai-agents-python | https://github.com/ramgolladi1503-sys/openai-agents-python/pull/1 | PASS |
| tradebot-research-corpus | https://github.com/ramgolladi1503-sys/tradebot-research-corpus/pull/1 | PASS |
| aixion-lab-website | https://github.com/ramgolladi1503-sys/aixion-lab-website/pull/21 | PASS |
| gemini-options-trader | https://github.com/ramgolladi1503-sys/gemini-options-trader/pull/13 | PASS |
| aixion-engineering-observatory | https://github.com/ramgolladi1503-sys/aixion-engineering-observatory/pull/2 | PASS |
| aixion-agent-os | https://github.com/ramgolladi1503-sys/aixion-agent-os/pull/2 | PASS |

## Important caveats

- These are onboarding **metadata checks only**, not full project CI passes.
  Existing website, password-manager, algotradify, MCP and Job-Application-Agent
  pipelines showed unrelated failures during the review window; other
  application workflows may still be running or have additional failures.
- Central reusable governance workflow is pinned to candidate commit
  `3509b5546bd63c18126eede603c1d52fff67cd34` until the central
  implementation is reviewed and merged. Do not silently change that pin.
- Existing AGENTS.md files were preserved in TradeBot, algotradify and
  openai-agents-python. All other pilot PRs add an instructions file.
- Default branches have not been changed by these onboarding PRs.
- Automatic future-repository reconciliation remains disabled pending a
  least-privilege credential, the `AIXION_RECONCILE_ENABLED` repository
  variable, and the `aixion-managed` topic on eligible repositories.
- This inventory does not establish authenticated approvals, operational
  Codex/Antigravity adapters, or a complete Agile execution lifecycle.

## Acceptance criteria before activation on default branches

1. Review central security PR #1 and organization onboarding PR #2.
2. Verify full application CI and investigate failures in each repository.
3. Merge central changes only after review; review each project PR separately.
4. Configure branch protection / required checks, especially for trading repos.
5. Enable the future-repository reconciler with a scoped GitHub App/token and
   mark authorized projects with the `aixion-managed` topic.
6. Confirm the next reconciliation run opens a draft PR for a newly created
   tagged test repository, without merging it.
