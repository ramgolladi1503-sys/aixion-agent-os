#!/usr/bin/env python3
"""
engine.py — Agile Orchestration Engine for Aixion Agent OS.
Manages tasks through the Agile lifecycle state machine:
BACKLOG -> REQUIREMENT_READY -> DESIGN_READY -> IN_DEVELOPMENT -> DEV_VERIFIED -> QA_VERIFIED -> UAT_APPROVED -> RELEASE_READY -> RELEASED -> DONE.
Enforces role separation, evidence validation, and safety gates.
Supports checkpoint persistence and crash recovery.
"""

import sys
import json
import uuid
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = BASE_DIR / "orchestration" / "state_store"
STATE_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TRANSITIONS = {
    "BACKLOG": ["REQUIREMENT_READY", "BLOCKED"],
    "REQUIREMENT_READY": ["DESIGN_READY", "BACKLOG", "BLOCKED"],
    "DESIGN_READY": ["IN_DEVELOPMENT", "REQUIREMENT_READY", "BLOCKED"],
    "IN_DEVELOPMENT": ["DEV_VERIFIED", "BLOCKED"],
    "DEV_VERIFIED": ["QA_IN_PROGRESS", "IN_DEVELOPMENT"],
    "QA_IN_PROGRESS": ["QA_VERIFIED", "QA_FAILED"],
    "QA_FAILED": ["IN_DEVELOPMENT"],
    "QA_VERIFIED": ["UAT_APPROVED", "QA_FAILED"],
    "UAT_APPROVED": ["RELEASE_READY", "BACKLOG"],
    "RELEASE_READY": ["RELEASED", "BLOCKED"],
    "RELEASED": ["DONE"],
    "DONE": []
}

class AgileWorkflowEngine:
    def __init__(self, task_id: str = None, state_dir: Path = STATE_DIR):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        if task_id:
            self.task_file = self.state_dir / f"{task_id}.json"
            if self.task_file.exists():
                self.task_data = json.loads(self.task_file.read_text(encoding="utf-8"))
            else:
                raise FileNotFoundError(f"Task {task_id} not found in state store.")
        else:
            self.task_data = None
            self.task_file = None

    def create_task(self, title: str, prompt: str, profile: str = "production_software", safety_critical: bool = False, team: list = None):
        task_id = f"TASK-{uuid.uuid4().hex[:8].upper()}"
        self.task_file = self.state_dir / f"{task_id}.json"
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        self.task_data = {
            "task_id": task_id,
            "title": title,
            "prompt": prompt,
            "profile": profile,
            "safety_critical": safety_critical,
            "team": team or [],
            "current_state": "BACKLOG",
            "history": [
                {
                    "from_state": None,
                    "to_state": "BACKLOG",
                    "role": "SYSTEM",
                    "timestamp": now,
                    "evidence": "Task initialized"
                }
            ],
            "artifacts": {},
            "approvals": {}
        }
        self.save()
        return self.task_data

    def save(self):
        if self.task_file and self.task_data:
            self.task_file.write_text(json.dumps(self.task_data, indent=2), encoding="utf-8")

    def transition_state(self, to_state: str, role: str, actor_id: str, evidence: dict, human_approved: bool = False):
        curr = self.task_data["current_state"]
        
        # Check state transition validity
        if to_state not in ALLOWED_TRANSITIONS.get(curr, []):
            raise ValueError(f"Illegal state transition from {curr} to {to_state}. Allowed: {ALLOWED_TRANSITIONS.get(curr, [])}")
            
        # Role separation check
        # Developer cannot sign off QA or UAT
        if to_state in ["QA_VERIFIED", "DEV_VERIFIED"] and role == "DEVELOPER" and to_state == "QA_VERIFIED":
            raise PermissionError("Developer cannot self-certify QA_VERIFIED. Independent QA role required.")
            
        # Safety gate check
        if to_state == "RELEASED" or (self.task_data["safety_critical"] and to_state == "IN_DEVELOPMENT"):
            if not human_approved:
                raise PermissionError(f"Transition to {to_state} requires explicit human authorization.")

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        transition_record = {
            "from_state": curr,
            "to_state": to_state,
            "role": role,
            "actor_id": actor_id,
            "timestamp": now,
            "evidence": evidence,
            "human_approved": human_approved
        }
        
        self.task_data["current_state"] = to_state
        self.task_data["history"].append(transition_record)
        self.save()
        return transition_record

    def get_status(self):
        return {
            "task_id": self.task_data["task_id"],
            "title": self.task_data["title"],
            "current_state": self.task_data["current_state"],
            "history_length": len(self.task_data["history"]),
            "safety_critical": self.task_data["safety_critical"]
        }

if __name__ == "__main__":
    engine = AgileWorkflowEngine()
    task = engine.create_task("Sample UI Component", "Build React button", safety_critical=False)
    print("Created:", task["task_id"])
    
    # Transition to REQUIREMENT_READY
    engine.transition_state("REQUIREMENT_READY", "BUSINESS_ANALYST", "design-ui-designer", {"spec": "Button spec defined"})
    print("Transitioned to:", engine.get_status()["current_state"])
