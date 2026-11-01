#!/usr/bin/env python3
"""Aixion task state machine.

This stores workflow evidence, not a security authorization token. Approvals from
external systems MUST be checked by the caller at the privileged action boundary.
"""
import datetime
import json
import os
import re
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_DIR = BASE_DIR / "orchestration" / "state_store"

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
    "DONE": [],
}
ROLE_RULES = {
    "REQUIREMENT_READY": {"BUSINESS_ANALYST", "PRODUCT_OWNER"},
    "DESIGN_READY": {"ARCHITECT", "SOLUTION_ARCHITECT"},
    "IN_DEVELOPMENT": {"DEVELOPER"},
    "DEV_VERIFIED": {"DEVELOPER"},
    "QA_IN_PROGRESS": {"QA", "SENIOR_QA"},
    "QA_VERIFIED": {"QA", "SENIOR_QA"},
    "QA_FAILED": {"QA", "SENIOR_QA"},
    "UAT_APPROVED": {"UAT", "PRODUCT_OWNER", "HUMAN_APPROVER"},
    "RELEASE_READY": {"RELEASE_ENGINEER", "RELEASE_MANAGER"},
    "RELEASED": {"RELEASE_ENGINEER", "HUMAN_APPROVER"},
    "DONE": {"RELEASE_ENGINEER", "HUMAN_APPROVER"},
}
EVIDENCE_REQUIRED = {
    "REQUIREMENT_READY": {"requirements_spec", "acceptance_criteria"},
    "DESIGN_READY": {"architecture_contract", "risk_assessment"},
    "DEV_VERIFIED": {"unit_test_results", "implementation_summary"},
    "QA_VERIFIED": {"test_execution_log", "qa_signoff", "regression_test_evidence"},
    "UAT_APPROVED": {"acceptance_proof", "uat_signoff"},
    "RELEASE_READY": {"pr_link", "ci_status", "release_notes"},
    "RELEASED": {"merge_commit_sha", "deployment_telemetry"},
}
ID_PATTERN = re.compile(r"^TASK-[A-F0-9]{8}$")

class AgileWorkflowEngine:
    def __init__(self, task_id=None, state_dir=STATE_DIR):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.task_data = None
        self.task_file = None
        if task_id is not None:
            if not isinstance(task_id, str) or not ID_PATTERN.fullmatch(task_id):
                raise ValueError("Invalid task ID")
            self.task_file = self.state_dir / (task_id + ".json")
            if not self.task_file.is_file() or self.task_file.is_symlink():
                raise FileNotFoundError("Task not found")
            self.task_data = json.loads(self.task_file.read_text(encoding="utf-8"))
            if self.task_data.get("task_id") != task_id:
                raise ValueError("Mismatched task ID")

    def create_task(self, title, prompt, profile="production_software", safety_critical=False, team=None):
        task_id = "TASK-" + uuid.uuid4().hex[:8].upper()
        self.task_file = self.state_dir / (task_id + ".json")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.task_data = {
            "task_id": task_id, "title": title, "prompt": prompt, "profile": profile,
            "safety_critical": bool(safety_critical), "team": team or [],
            "current_state": "BACKLOG", "history": [{
                "from_state": None, "to_state": "BACKLOG", "role": "SYSTEM",
                "actor_id": "system", "timestamp": now, "evidence": {"initialized": True}
            }], "artifacts": {}, "approvals": {}
        }
        self.save()
        return self.task_data

    def save(self):
        if self.task_file is None or self.task_data is None:
            raise ValueError("No task loaded")
        if self.task_file.is_symlink():
            raise PermissionError("Refusing symlink task store")
        # Filesystem durability and no partially written JSON. The state directory
        # itself must only be writable by trusted local users.
        tmp = self.state_dir / (self.task_file.name + "." + uuid.uuid4().hex + ".tmp")
        try:
            with tmp.open("x", encoding="utf-8") as file:
                json.dump(self.task_data, file, indent=2)
                file.flush()
                os.fsync(file.fileno())
            os.replace(tmp, self.task_file)
        finally:
            tmp.unlink(missing_ok=True)

    def transition_state(self, to_state, role, actor_id, evidence, human_approved=False, approval_ref=None):
        if self.task_data is None:
            raise ValueError("No task loaded")
        current = self.task_data["current_state"]
        if to_state not in ALLOWED_TRANSITIONS.get(current, []):
            raise ValueError(f"Illegal transition: {current} -> {to_state}")
        role = str(role).upper()
        if to_state in ROLE_RULES and role not in ROLE_RULES[to_state]:
            raise PermissionError(f"Role {role} cannot approve {to_state}")
        if not isinstance(actor_id, str) or not actor_id.strip():
            raise ValueError("Actor identity required")
        if not isinstance(evidence, dict):
            raise ValueError("Evidence must be a dictionary")
        required = EVIDENCE_REQUIRED.get(to_state, set())
        if any(not evidence.get(key) for key in required):
            raise ValueError(f"Missing evidence: {sorted(k for k in required if not evidence.get(k))}")
        if to_state == "QA_VERIFIED":
            developer_ids = {x["actor_id"] for x in self.task_data["history"]
                             if x["to_state"] == "DEV_VERIFIED"}
            if actor_id in developer_ids:
                raise PermissionError("Developer cannot self-certify QA")
        # This flag is a *record of an external authorization*, not proof that
        # an authenticated human approved. Do not use it to authorize GitHub
        # merges, broker actions, deployments or other privileged operations.
        requires_human = to_state in {"RELEASED", "UAT_APPROVED"} or (
            self.task_data["safety_critical"] and to_state == "IN_DEVELOPMENT")
        if requires_human and not (human_approved and isinstance(approval_ref, str) and approval_ref.strip()):
            raise PermissionError("Human authorization reference required")
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record = {
            "from_state": current, "to_state": to_state, "role": role,
            "actor_id": actor_id, "timestamp": now, "evidence": evidence,
            "human_approved": bool(human_approved), "approval_ref": approval_ref
        }
        self.task_data["current_state"] = to_state
        self.task_data["history"].append(record)
        self.save()
        return record

    def get_status(self):
        if self.task_data is None:
            raise ValueError("No task loaded")
        return {k: self.task_data[k] for k in
                ("task_id", "title", "current_state", "safety_critical")} | {
                "history_length": len(self.task_data["history"])}
