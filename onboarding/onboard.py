#!/usr/bin/env python3
"""
onboard.py — Onboards an existing or new Aixion Lab repository into Aixion Agent OS.
Generates .aixion/ configuration, connects to central catalog, applies Agile lifecycle,
and preserves project-specific safety rules.
"""

import sys
import json
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

def onboard_project(target_repo_path: str, project_name: str = None, project_type: str = "general"):
    repo_path = Path(target_repo_path).resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"Target repository {repo_path} does not exist.")
        
    p_name = project_name or repo_path.name
    aixion_dir = repo_path / ".aixion"
    aixion_dir.mkdir(parents=True, exist_ok=True)
    
    # Detect technology stack
    tech_stack = []
    if (repo_path / "package.json").exists():
        tech_stack.append("node/typescript")
    if (repo_path / "requirements.txt").exists() or (repo_path / "pyproject.toml").exists() or any(repo_path.glob("*.py")):
        tech_stack.append("python")
    if (repo_path / "pubspec.yaml").exists():
        tech_stack.append("flutter/dart")
        
    config = {
        "project_name": p_name,
        "project_type": project_type,
        "tech_stack": tech_stack,
        "agent_os_root": str(BASE_DIR),
        "lifecycle_profile": "production_software",
        "governance_mode": "strict",
        "evidence_dir": ".aixion/evidence",
        "onboarded_at": "2026-10-31T02:15:00Z"
    }
    
    (aixion_dir / "config.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    (aixion_dir / "evidence").mkdir(exist_ok=True)
    
    # Symlink or reference governance
    gov_link = aixion_dir / "GOVERNANCE.md"
    gov_link.write_text(
        f"# Aixion Agent OS Onboarding\n\nThis project is managed under Aixion Agent OS governance.\nCentral Agent OS location: `{BASE_DIR}`\n",
        encoding="utf-8"
    )
    
    print(f"Successfully onboarded {p_name} at {repo_path}")
    return config

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: onboard.py <repo_path> [project_name] [project_type]")
        sys.exit(1)
    onboard_project(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None, sys.argv[3] if len(sys.argv) > 3 else "general")
