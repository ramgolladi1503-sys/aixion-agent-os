#!/usr/bin/env python3
"""Opt-in GitHub repository reconciler: opens onboarding PRs, never merges.

Requires gh CLI, git and GH_TOKEN. Only repositories explicitly tagged with
the GitHub topic 'aixion-managed' are in scope, regardless of repository name.
Defaults to dry-run; --apply writes remote branches and opens PRs.
"""
import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path

try:
    from onboarding.onboard import onboard_project
except ModuleNotFoundError:
    from onboard import onboard_project

def run(args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True, stderr=subprocess.PIPE).strip()

def eligible_repositories(owner):
    raw = run(["gh", "repo", "list", owner, "--limit", "1000",
               "--json", "nameWithOwner,isArchived,isFork,repositoryTopics"])
    repos = json.loads(raw)
    result = []
    for repo in repos:
        if repo.get("isArchived") or repo.get("isFork"):
            continue
        topics = repo.get("repositoryTopics") or []
        names = {t.get("name") if isinstance(t, dict) else t for t in topics}
        if "aixion-managed" in names:
            result.append(repo["nameWithOwner"])
    return sorted(result)

def reconcile(owner, apply=False):
    if apply and not (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")):
        raise RuntimeError("Authenticated GitHub token required for --apply")
    result = []
    for name in eligible_repositories(owner):
        try:
            # Read-only API check; 404 indicates onboarding is not present.
            probe = subprocess.run(["gh", "api", f"repos/{name}/contents/.aixion/config.json"],
                                   capture_output=True, text=True)
            if probe.returncode == 0:
                result.append({"repo": name, "status": "already_onboarded"})
                continue
            if not apply:
                result.append({"repo": name, "status": "needs_onboarding"})
                continue
            with tempfile.TemporaryDirectory() as tmp:
                checkout = Path(tmp) / "repo"
                run(["gh", "repo", "clone", name, str(checkout), "--", "--quiet"])
                # Never push to main. Only create a branch and a pull request.
                branch = "automation/aixion-agent-os-onboarding"
                existing = subprocess.run(
                    ["gh", "pr", "list", "--repo", name, "--head", branch,
                     "--state", "open", "--json", "number"],
                    capture_output=True, text=True, check=True)
                if json.loads(existing.stdout):
                    result.append({"repo": name, "status": "pr_already_open"})
                    continue
                run(["git", "checkout", "-b", branch], cwd=checkout)
                onboard_project(checkout)
                run(["git", "add", ".aixion", "AGENTS.md", ".github/workflows/aixion-governance.yml"], cwd=checkout)
                if not run(["git", "status", "--porcelain"], cwd=checkout):
                    result.append({"repo": name, "status": "no_changes"})
                    continue
                run(["git", "-c", "user.name=aixion-agent-os",
                     "-c", "user.email=aixion-agent-os@users.noreply.github.com",
                     "commit", "-m", "chore: onboard Aixion Agent OS"], cwd=checkout)
                run(["git", "push", "-u", "origin", branch], cwd=checkout)
                pr = run(["gh", "pr", "create", "--repo", name, "--draft",
                          "--title", "chore: onboard Aixion Agent OS",
                          "--body", "Automated opt-in onboarding PR. Review existing project rules, workflow permissions and CI before merging."],
                         cwd=checkout)
                result.append({"repo": name, "status": "draft_pr_opened", "url": pr})
        except (subprocess.CalledProcessError, ValueError, OSError) as exc:
            result.append({"repo": name, "status": "blocked", "error": str(exc)})
    return result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    print(json.dumps(reconcile(args.owner, apply=args.apply), indent=2))

if __name__ == "__main__":
    main()
