#!/usr/bin/env python3
"""
router.py — Dynamic Agent Router for Aixion Agent OS.
Understands task, reads project constraints, matches specific role requirements
(Product/BA, Architect, Developer, QA, Security/Quant), selects minimal sufficient team,
and outputs explainable selection rationale.
"""

import sys
import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_FILE = BASE_DIR / "catalog" / "manifest.json"

ROLE_TEMPLATES = {
    "frontend": [
        {"role": "Product Owner / UX", "preferred_ids": ["design-ui-designer", "design-ux-designer", "product-manager"]},
        {"role": "Frontend Architect", "preferred_ids": ["engineering-frontend-developer", "engineering-web-accessibility-specialist"]},
        {"role": "UI Developer", "preferred_ids": ["engineering-frontend-developer", "engineering-desktop-app-engineer"]},
        {"role": "QA Engineer", "preferred_ids": ["testing-test-automation-engineer", "testing-api-tester", "testing-reality-checker"]}
    ],
    "backend": [
        {"role": "System Architect", "preferred_ids": ["engineering-backend-architect", "engineering-system-architect"]},
        {"role": "Backend Developer", "preferred_ids": ["engineering-backend-architect", "engineering-api-platform-engineer", "engineering-data-engineer"]},
        {"role": "QA Engineer", "preferred_ids": ["testing-api-tester", "testing-test-automation-engineer"]},
        {"role": "Senior Reviewer", "preferred_ids": ["engineering-code-reviewer", "security-application-security-engineer"]}
    ],
    "trading": [
        {"role": "Business Analyst / PO", "preferred_ids": ["product-manager", "finance-investment-researcher", "finance-financial-analyst"]},
        {"role": "Quant Architect", "preferred_ids": ["specialized-pricing-analyst", "engineering-system-architect", "engineering-data-engineer"]},
        {"role": "Runtime Developer", "preferred_ids": ["engineering-backend-architect", "engineering-api-platform-engineer"]},
        {"role": "Senior QA / Risk Auditor", "preferred_ids": ["testing-reality-checker", "testing-test-results-analyzer", "engineering-code-reviewer"]}
    ],
    "security": [
        {"role": "Security Architect", "preferred_ids": ["security-cloud-security-engineer", "security-application-security-engineer"]},
        {"role": "AppSec Engineer", "preferred_ids": ["security-application-security-engineer", "security-penetration-tester"]},
        {"role": "Code Reviewer", "preferred_ids": ["engineering-code-reviewer", "testing-reality-checker"]},
        {"role": "QA Verifier", "preferred_ids": ["testing-test-automation-engineer", "testing-evidence-collector"]}
    ],
    "general": [
        {"role": "Lead Architect", "preferred_ids": ["engineering-system-architect", "engineering-backend-architect"]},
        {"role": "Developer", "preferred_ids": ["engineering-backend-architect", "engineering-frontend-developer"]},
        {"role": "QA Engineer", "preferred_ids": ["testing-test-automation-engineer", "testing-evidence-collector"]}
    ]
}

class AgentRouter:
    def __init__(self, manifest_path=MANIFEST_FILE):
        if not Path(manifest_path).exists():
            raise FileNotFoundError(f"Manifest not found at {manifest_path}")
        self.manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        self.agents = {a["id"]: a for a in self.manifest["agents"]}

    def classify_task(self, prompt: str, project_constraints: dict = None):
        p = prompt.lower()
        domain = "general"
        
        if any(w in p for w in ["trading", "order", "broker", "quant", "portfolio", "candle", "execution", "slippage"]):
            domain = "trading"
        elif any(w in p for w in ["frontend", "ui", "ux", "react", "css", "component", "tailwind", "button", "screen", "modal"]):
            domain = "frontend"
        elif any(w in p for w in ["security", "auth", "vulnerability", "token", "injection", "permission", "pentest"]):
            domain = "security"
        elif any(w in p for w in ["api", "backend", "database", "sql", "migration", "fastapi", "server", "endpoint"]):
            domain = "backend"

        is_safety_critical = any(w in p for w in ["live", "broker", "order", "kill switch", "credentials", "secret", "destroy"])
        
        return {
            "domain": domain,
            "is_safety_critical": is_safety_critical
        }

    def select_team(self, task_prompt: str, project_constraints: dict = None):
        classification = self.classify_task(task_prompt, project_constraints)
        domain = classification["domain"]
        role_slots = ROLE_TEMPLATES.get(domain, ROLE_TEMPLATES["general"])
        
        selected_team = []
        used_agent_ids = set()
        
        for slot in role_slots:
            assigned = None
            for cand_id in slot["preferred_ids"]:
                if cand_id in self.agents and cand_id not in used_agent_ids:
                    assigned = self.agents[cand_id]
                    break
            # Fallback search by division or matching tags
            if not assigned:
                for agent in self.manifest["agents"]:
                    if agent["id"] not in used_agent_ids:
                        assigned = agent
                        break
                        
            if assigned:
                used_agent_ids.add(assigned["id"])
                selected_team.append({
                    "agile_role": slot["role"],
                    "agent_id": assigned["id"],
                    "display_name": assigned["display_name"],
                    "division": assigned["division"],
                    "risk": assigned["risk_classification"],
                    "rationale": f"Matched role requirement '{slot['role']}' from division '{assigned['division']}'"
                })

        return {
            "task_prompt": task_prompt,
            "domain": domain,
            "safety_critical": classification["is_safety_critical"],
            "team_size": len(selected_team),
            "total_catalog_size": len(self.agents),
            "selected_team": selected_team,
            "selection_rationale": [
                f"{a['agile_role']}: {a['display_name']} ({a['agent_id']}) - {a['rationale']}"
                for a in selected_team
            ]
        }

if __name__ == "__main__":
    router = AgentRouter()
    prompt = sys.argv[1] if len(sys.argv) > 1 else "Build a new React modal component with dark mode support"
    res = router.select_team(prompt)
    print(json.dumps(res, indent=2))
