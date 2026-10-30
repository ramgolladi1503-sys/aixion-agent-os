#!/usr/bin/env python3
"""
indexer.py — Build the unified Aixion Agent OS manifest from upstream agency-agents.
Parses frontmatter, metadata, capabilities, risk levels, and generates catalog/manifest.json.
Scans both top-level and nested category directories (e.g. game-development subengines).
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPSTREAM_DIR = BASE_DIR / "catalog" / "upstream" / "agency-agents"
MANIFEST_FILE = BASE_DIR / "catalog" / "manifest.json"

CATEGORIES = [
    "academic", "design", "engineering", "finance", "game-development",
    "gis", "healthcare", "marketing", "paid-media", "product",
    "project-management", "research", "sales", "security",
    "spatial-computing", "specialized", "strategy", "support", "testing"
]

EXCLUDED_NAMES = {
    "README.md", "CONTRIBUTING.md", "LICENSE.md", "SECURITY.md",
    "CONTRIBUTING_zh-CN.md", "handoff-templates.md", "agent-activation-prompts.md"
}

def parse_frontmatter(content: str):
    if not content.startswith("---"):
        return {}, content
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content
    fm_text = parts[1]
    body = parts[2].strip()
    meta = {}
    for line in fm_text.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta, body

def infer_capabilities(name: str, desc: str, body: str, division: str):
    text = (name + " " + desc + " " + body[:1000]).lower()
    caps = set()
    
    caps.add(f"division:{division}")
    
    keywords = {
        "frontend": ["frontend", "ui", "ux", "react", "vue", "css", "html", "javascript", "tailwind", "web"],
        "backend": ["backend", "api", "database", "sql", "server", "microservices", "python", "golang", "node"],
        "architecture": ["architect", "system design", "scale", "infrastructure", "invariants", "distributed"],
        "security": ["security", "vulnerability", "auth", "owasp", "encryption", "audit", "pentest"],
        "testing": ["qa", "test", "verification", "e2e", "jest", "pytest", "adversarial", "retest", "regression"],
        "data": ["data", "etl", "analytics", "pipeline", "pandas", "ml", "machine learning", "dataset"],
        "finance": ["finance", "trading", "quant", "risk", "portfolio", "accounting", "valuation"],
        "devops": ["devops", "ci/cd", "docker", "kubernetes", "cloud", "aws", "gcp", "deploy"],
        "mobile": ["ios", "android", "flutter", "swift", "react native", "mobile"],
        "product": ["product", "roadmap", "backlog", "user story", "requirements", "acceptance criteria"],
        "review": ["review", "critique", "code review", "audit", "challenge"]
    }
    
    for tag, words in keywords.items():
        if any(w in text for w in words):
            caps.add(tag)
            
    return sorted(list(caps))

def infer_risk_classification(division: str, name: str, desc: str):
    high_risk_words = ["security", "pentest", "vulnerability", "financial", "trading", "execution", "deploy", "infrastructure", "root", "database"]
    text = (division + " " + name + " " + desc).lower()
    if division in ["security", "finance"]:
        return "HIGH"
    if any(w in text for w in high_risk_words):
        return "MEDIUM"
    return "LOW"

def build_manifest():
    print(f"Indexing Agency Agents from {UPSTREAM_DIR}...")
    agents = []
    
    for cat in CATEGORIES:
        cat_dir = UPSTREAM_DIR / cat
        if not cat_dir.exists():
            continue
        for file in sorted(cat_dir.rglob("*.md")):
            if file.name in EXCLUDED_NAMES:
                continue
            if "playbooks" in file.parts or "runbooks" in file.parts or "coordination" in file.parts:
                continue
                
            rel_path = file.relative_to(BASE_DIR)
            content = file.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)
            
            if not meta.get("name") and not meta.get("description"):
                continue
                
            agent_id = file.stem
            display_name = meta.get("name", agent_id.replace("-", " ").title())
            description = meta.get("description", "")
            
            sha256 = hashlib.sha256(content.encode("utf-8")).hexdigest()
            caps = infer_capabilities(display_name, description, body, cat)
            risk = infer_risk_classification(cat, display_name, description)
            
            agent_entry = {
                "id": agent_id,
                "display_name": display_name,
                "division": cat,
                "description": description,
                "capabilities": caps,
                "supported_task_types": [
                    "engineering" if cat in ["engineering", "testing", "security", "game-development"] else
                    "product" if cat in ["product", "project-management"] else
                    "strategy" if cat in ["strategy", "finance"] else "general"
                ],
                "risk_classification": risk,
                "applicable_project_types": ["web", "mobile", "backend", "trading", "data", "platform", "gaming", "general"],
                "source_file": str(rel_path),
                "source_version": "b37b5bb33b78f2c1d6567d98e25ca818e3259219",
                "sha256": sha256,
                "metadata": {
                    "color": meta.get("color", "default"),
                    "emoji": meta.get("emoji", "🤖"),
                    "vibe": meta.get("vibe", "")
                }
            }
            agents.append(agent_entry)
            
    manifest = {
        "version": "1.0.0",
        "upstream_commit": "b37b5bb33b78f2c1d6567d98e25ca818e3259219",
        "total_agents": len(agents),
        "divisions": CATEGORIES,
        "agents": agents
    }
    
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Successfully generated manifest with {len(agents)} agents at {MANIFEST_FILE}")

if __name__ == "__main__":
    build_manifest()
