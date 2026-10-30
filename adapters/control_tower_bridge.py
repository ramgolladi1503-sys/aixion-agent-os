#!/usr/bin/env python3
"""
control_tower_bridge.py — Telemetry bridge between Aixion Agent OS and Aixion Control Tower.
Transfers task state transitions, agent team selections, and approval requests into Control Tower's event stream.
"""

import sys
import json
import uuid
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

class ControlTowerBridge:
    def __init__(self, telemetry_file: Path = None):
        self.telemetry_file = telemetry_file or (BASE_DIR / "orchestration" / "control_tower_telemetry.jsonl")
        self.telemetry_file.parent.mkdir(parents=True, exist_ok=True)

    def emit_event(self, event_type: str, task_id: str, payload: dict):
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        record = {
            "event_id": f"EVT-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": now,
            "event_type": event_type,
            "task_id": task_id,
            "payload": payload,
            "source": "aixion_agent_os"
        }
        with open(self.telemetry_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return record

    def get_recent_events(self, limit: int = 10):
        if not self.telemetry_file.exists():
            return []
        lines = self.telemetry_file.read_text(encoding="utf-8").strip().split("\n")
        events = [json.loads(line) for line in lines if line.strip()]
        return events[-limit:]

if __name__ == "__main__":
    bridge = ControlTowerBridge()
    evt = bridge.emit_event("TASK_ROUTED", "TASK-TEST-01", {
        "team": ["UI Designer", "Frontend Developer", "QA Engineer"],
        "lifecycle_state": "REQUIREMENT_READY"
    })
    print("Emitted event to Control Tower bridge:", evt["event_id"])
    print("Recent events:", len(bridge.get_recent_events()))
