#!/usr/bin/env python3
"""Explainable deterministic agent routing across the full catalog."""
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MANIFEST_FILE = BASE_DIR / "catalog" / "manifest.json"
ROLE_TEMPLATES = {
    "frontend": [("Product/UX", "product"), ("Frontend Engineer", "frontend"), ("QA", "testing")],
    "backend": [("Architect", "architecture"), ("Backend Engineer", "backend"), ("QA", "testing")],
    "trading": [("Product/Analyst", "product"), ("Quant/Risk", "finance"), ("Backend Engineer", "backend"), ("Independent QA", "testing")],
    "security": [("Security Engineer", "security"), ("Developer", "backend"), ("Independent QA", "testing")],
    "general": [("Architect", "architecture"), ("Developer", "backend"), ("Independent QA", "testing")],
}
SPECIALIZED_TAGS = {
    "frontend": {"frontend", "ui", "ux", "react", "css", "tailwind", "screen", "modal", "component"},
    "backend": {"backend", "api", "database", "sql", "migration", "fastapi", "endpoint"},
    "trading": {"trading", "broker", "quant", "portfolio", "candle", "slippage", "nifty", "sentinel", "order execution"},
    "security": {"security", "vulnerability", "auth", "injection", "pentest", "privilege"},
}
HIGH_RISK_WORDS = {"live trading", "broker", "kill switch", "credentials", "secret", "production deploy", "order execution", "delete database"}

class AgentRouter:
    def __init__(self, manifest_path=MANIFEST_FILE):
        data = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
        agents = data.get("agents", [])
        if not agents or len({a["id"] for a in agents}) != len(agents):
            raise ValueError("Agent manifest empty or contains duplicate IDs")
        self.agents = agents

    @staticmethod
    def _contains(text, term):
        return re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text) is not None

    def classify_task(self, prompt, project_constraints=None):
        text = prompt.casefold()
        constraints = project_constraints or {}
        project_type = str(constraints.get("project_type", "")).casefold()
        scores = {
            domain: sum(1 for word in words if self._contains(text, word))
            for domain, words in SPECIALIZED_TAGS.items()
        }
        if project_type in {"trading", "security", "frontend", "backend"}:
            scores[project_type] += 3
        domain = max(scores, key=lambda key: scores[key])
        if not scores[domain]:
            domain = "general"
        return {"domain": domain, "is_safety_critical":
                bool(constraints.get("safety_critical", False)) or
                any(self._contains(text, phrase) for phrase in HIGH_RISK_WORDS)}

    def select_team(self, task_prompt, project_constraints=None):
        classification = self.classify_task(task_prompt, project_constraints)
        domain = classification["domain"]
        used = set()
        team = []
        unresolved = []
        for role, capability in ROLE_TEMPLATES[domain]:
            candidates = []
            for agent in self.agents:
                if agent["id"] in used:
                    continue
                caps = set(agent.get("capabilities", []))
                division = agent.get("division", "")
                score = 0
                if capability in caps:
                    score += 10
                if "division:" + capability in caps:
                    score += 12
                if capability == "architecture" and "architect" in agent.get("display_name", "").lower():
                    score += 5
                if capability == "testing" and division == "testing":
                    score += 8
                if capability == "security" and division == "security":
                    score += 8
                if capability == "finance" and division == "finance":
                    score += 8
                if capability == "product" and division in {"product", "project-management"}:
                    score += 8
                if score:
                    candidates.append((score, agent))
            if not candidates:
                unresolved.append({"role": role, "capability": capability})
                continue
            candidates.sort(key=lambda entry: (-entry[0], entry[1]["id"]))
            score, agent = candidates[0]
            used.add(agent["id"])
            team.append({
                "agile_role": role, "agent_id": agent["id"],
                "display_name": agent["display_name"], "division": agent["division"],
                "risk": agent.get("risk_classification", "UNKNOWN"),
                "rationale": f"Capability {capability} matched with score {score}",
            })
        return {
            "task_prompt": task_prompt, "domain": domain,
            "safety_critical": classification["is_safety_critical"],
            "team_size": len(team), "total_catalog_size": len(self.agents),
            "selected_team": team, "unresolved_roles": unresolved,
            "routing_status": "COMPLETE" if not unresolved else "INCOMPLETE",
            "selection_rationale": [a["rationale"] for a in team],
        }

if __name__ == "__main__":
    router = AgentRouter()
    prompt = " ".join(sys.argv[1:]) or "Build React modal"
    print(json.dumps(router.select_team(prompt), indent=2))
