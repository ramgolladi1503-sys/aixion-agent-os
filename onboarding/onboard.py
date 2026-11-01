#!/usr/bin/env python3
"""Safe, repeatable onboarding for any existing or newly created Git repository.

The generated files are portable: no absolute developer-machine paths. Onboarding
is an explicit local step; GitHub does not automatically apply it to new repos.
"""
import argparse
import datetime
import json
from pathlib import Path

POLICY_REPO = "ramgolladi1503-sys/aixion-agent-os"
WORKFLOW_REF = "3509b5546bd63c18126eede603c1d52fff67cd34"

def _technology(path):
    indicators = {
        "python": ["pyproject.toml", "requirements.txt", "setup.py"],
        "node": ["package.json"],
        "go": ["go.mod"],
        "rust": ["Cargo.toml"],
        "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
        "flutter": ["pubspec.yaml"],
    }
    return [name for name, markers in indicators.items() if any((path / marker).is_file() for marker in markers)]

def _create_once(path, content):
    if path.exists() or path.is_symlink():
        return "preserved"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as stream:
        stream.write(content)
    return "created"

def onboard_project(target_repo_path, project_name=None, project_type="general", require_git=True):
    path = Path(target_repo_path).expanduser().resolve()
    if not path.is_dir():
        raise FileNotFoundError(f"Repository directory not found: {path}")
    if require_git and not (path / ".git").exists():
        raise ValueError("Not a Git repository; initialize Git first or use --allow-non-git")
    if project_type not in {"general", "trading", "research", "web", "backend", "mobile", "platform"}:
        raise ValueError("Unsupported project type")
    aixion = path / ".aixion"
    existing = aixion / "config.json"
    if existing.is_symlink():
        raise PermissionError("Refusing symlinked project configuration")
    if existing.exists():
        try:
            old = json.loads(existing.read_text(encoding="utf-8"))
        except (ValueError, UnicodeError) as exc:
            raise ValueError("Existing config invalid; refusing overwrite") from exc
        if not isinstance(old, dict):
            raise ValueError("Existing config must be an object")
        return {"status": "already_onboarded", "project_name": old.get("project_name", path.name),
                "files": {}, "config": old}

    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    config = {
        "schema_version": 1, "project_name": project_name or path.name,
        "project_type": project_type, "tech_stack": _technology(path),
        "agent_os_repository": POLICY_REPO,
        "lifecycle_profile": "research" if project_type == "research" else "production_software",
        "governance_mode": "strict", "evidence_dir": ".aixion/evidence",
        "onboarded_at": now
    }
    instructions = """# Aixion Lab project instructions

This repository uses the Aixion Agent OS catalog and governance:
https://github.com/ramgolladi1503-sys/aixion-agent-os

Before implementation: inspect this repository's own instructions and safety
constraints, classify the task, and select a minimal suitable agent team.
Do not assume a role prompt grants permissions. Record requirements, design,
implementation and independent QA evidence. Never bypass protected branches,
human approval, production or broker safety controls.

For local agent selection use the centrally installed Aixion CLI; do not
assume it is installed on all machines. If unavailable, report the missing
integration rather than fabricating execution.
"""
    workflow = """name: Aixion Agent OS governance
on:
  pull_request:
  workflow_dispatch:
permissions:
  contents: read
jobs:
  governance:
    uses: ramgolladi1503-sys/aixion-agent-os/.github/workflows/reusable-governance.yml@3509b5546bd63c18126eede603c1d52fff67cd34
"""
    governance = """# Organization governance

Source of truth: https://github.com/ramgolladi1503-sys/aixion-agent-os
This file is a pointer, not evidence of an installed runtime adapter.
Project-specific safety rules remain in force. Never merge without approved
review and passing CI. The reusable workflow checks configuration structure;
it does not authenticate release approvals.
"""
    files = {}
    files["AGENTS.md"] = _create_once(path / "AGENTS.md", instructions)
    files[".aixion/GOVERNANCE.md"] = _create_once(aixion / "GOVERNANCE.md", governance)
    files[".github/workflows/aixion-governance.yml"] = _create_once(
        path / ".github/workflows" / "aixion-governance.yml", workflow)
    files[".aixion/config.json"] = _create_once(
        existing, json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    return {"status": "onboarded", "project_name": config["project_name"],
            "files": files, "config": config}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--name")
    parser.add_argument("--type", default="general", dest="project_type")
    parser.add_argument("--allow-non-git", action="store_true")
    args = parser.parse_args()
    print(json.dumps(onboard_project(args.path, args.name, args.project_type,
                                     require_git=not args.allow_non_git), indent=2))

if __name__ == "__main__":
    main()
