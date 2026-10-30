#!/usr/bin/env python3
"""
sync.py — Synchronization mechanism to detect new, modified, renamed, and removed upstream agents.
Verifies changes against catalog/manifest.json. Ignores documentation/playbook markdown files.
"""

import sys
import json
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_FILE = BASE_DIR / "catalog" / "manifest.json"
UPSTREAM_DIR = BASE_DIR / "catalog" / "upstream" / "agency-agents"

EXCLUDED_PARTS = {"playbooks", "runbooks", "coordination"}
EXCLUDED_NAMES = {
    "README.md", "CONTRIBUTING.md", "LICENSE.md", "SECURITY.md",
    "CONTRIBUTING_zh-CN.md", "handoff-templates.md", "agent-activation-prompts.md",
    "QUICKSTART.md", "EXECUTIVE-BRIEF.md", "nexus-strategy.md"
}

def check_sync():
    if not MANIFEST_FILE.exists():
        print("Error: Manifest file does not exist. Run indexer.py first.")
        sys.exit(1)
        
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    indexed_agents = {a["source_file"]: a for a in manifest["agents"]}
    
    current_files = {}
    for md_file in UPSTREAM_DIR.rglob("*.md"):
        if md_file.name in EXCLUDED_NAMES:
            continue
        if any(p in md_file.parts for p in EXCLUDED_PARTS):
            continue
            
        rel = str(md_file.relative_to(BASE_DIR))
        parts = md_file.relative_to(UPSTREAM_DIR).parts
        if len(parts) >= 2 and parts[0] in manifest["divisions"]:
            current_files[rel] = md_file
            
    added = []
    modified = []
    removed = []
    unchanged = []
    
    for rel_path, file_path in current_files.items():
        content = file_path.read_text(encoding="utf-8")
        current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
        
        if rel_path not in indexed_agents:
            added.append(rel_path)
        else:
            prev_hash = indexed_agents[rel_path].get("sha256")
            if current_hash != prev_hash:
                modified.append({"path": rel_path, "prev_hash": prev_hash, "new_hash": current_hash})
            else:
                unchanged.append(rel_path)
                
    for rel_path in indexed_agents:
        if rel_path not in current_files:
            removed.append(rel_path)
            
    status = {
        "status": "IN_SYNC" if not (added or modified or removed) else "CHANGES_DETECTED",
        "total_current_agents": len(current_files),
        "total_indexed_agents": len(indexed_agents),
        "unchanged": len(unchanged),
        "added": added,
        "modified": modified,
        "removed": removed
    }
    
    print(json.dumps(status, indent=2))
    return 0 if status["status"] == "IN_SYNC" else 2

if __name__ == "__main__":
    sys.exit(check_sync())
