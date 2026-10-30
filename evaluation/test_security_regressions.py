#!/usr/bin/env python3
"""Regression tests for hardened transition checks and agent routing.

Run: PYTHONPATH=. python3 -m unittest evaluation.test_security_regressions
"""
import json
import tempfile
import unittest
from pathlib import Path

from orchestration.engine import AgileWorkflowEngine
from routing.router import AgentRouter


class SecurityRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = Path(self.tmp.name) / "tasks"

    def engine(self):
        engine = AgileWorkflowEngine(state_dir=self.store)
        engine.create_task("Regression", "Test workflow safeguards")
        return engine

    def test_task_path_traversal_rejected(self):
        with self.assertRaises(ValueError):
            AgileWorkflowEngine(task_id="../../etc/passwd", state_dir=self.store)

    def test_missing_evidence_rejected(self):
        engine = self.engine()
        with self.assertRaises(ValueError):
            engine.transition_state("REQUIREMENT_READY", "BUSINESS_ANALYST", "ba-1", {})

    def test_role_spoof_rejected(self):
        engine = self.engine()
        with self.assertRaises(PermissionError):
            engine.transition_state("REQUIREMENT_READY", "DEVELOPER", "dev-1",
                                    {"requirements_spec": "r", "acceptance_criteria": "a"})

    def test_cannot_skip_lifecycle(self):
        engine = self.engine()
        with self.assertRaises(ValueError):
            engine.transition_state("RELEASED", "RELEASE_ENGINEER", "rel-1",
                                    {"merge_commit_sha": "abc", "deployment_telemetry": "log"},
                                    human_approved=True, approval_ref="REF-1")

    def test_qa_developer_identity_rejected(self):
        engine = self.engine()
        engine.transition_state("REQUIREMENT_READY", "BUSINESS_ANALYST", "ba-1",
                                {"requirements_spec": "r", "acceptance_criteria": "a"})
        engine.transition_state("DESIGN_READY", "ARCHITECT", "arch-1",
                                {"architecture_contract": "d", "risk_assessment": "risk"})
        engine.transition_state("IN_DEVELOPMENT", "DEVELOPER", "dev-1", {})
        engine.transition_state("DEV_VERIFIED", "DEVELOPER", "dev-1",
                                {"unit_test_results": "passed", "implementation_summary": "done"})
        engine.transition_state("QA_IN_PROGRESS", "QA", "dev-1", {})
        with self.assertRaises(PermissionError):
            engine.transition_state("QA_VERIFIED", "QA", "dev-1",
                                    {"test_execution_log": "log",
                                     "qa_signoff": "yes",
                                     "regression_test_evidence": "tests"})

    def test_safety_approval_reference_required(self):
        engine = AgileWorkflowEngine(state_dir=self.store)
        engine.create_task("Critical", "Live trading", safety_critical=True)
        engine.transition_state("REQUIREMENT_READY", "BUSINESS_ANALYST", "ba-1",
                                {"requirements_spec": "r", "acceptance_criteria": "a"})
        engine.transition_state("DESIGN_READY", "ARCHITECT", "arch-1",
                                {"architecture_contract": "d", "risk_assessment": "risk"})
        with self.assertRaises(PermissionError):
            engine.transition_state("IN_DEVELOPMENT", "DEVELOPER", "dev-1", {},
                                    human_approved=True)

    def test_checkpoint_recovers(self):
        engine = self.engine()
        task_id = engine.task_data["task_id"]
        engine.transition_state("REQUIREMENT_READY", "BUSINESS_ANALYST", "ba-1",
                                {"requirements_spec": "r", "acceptance_criteria": "a"})
        reload = AgileWorkflowEngine(task_id=task_id, state_dir=self.store)
        self.assertEqual(reload.get_status()["current_state"], "REQUIREMENT_READY")

    def test_router_no_unrelated_agent_fallback(self):
        manifest_path = Path(self.tmp.name) / "manifest.json"
        manifest_path.write_text(json.dumps({"agents": [{
            "id": "academic-only", "display_name": "Historian",
            "division": "academic", "capabilities": ["division:academic"],
            "risk_classification": "LOW"
        }]}), encoding="utf-8")
        result = AgentRouter(manifest_path).select_team("Build React UI")
        self.assertEqual(result["team_size"], 0)
        self.assertEqual(result["routing_status"], "INCOMPLETE")
        self.assertTrue(result["unresolved_roles"])

    def test_router_uses_project_context(self):
        manifest_path = Path(self.tmp.name) / "manifest.json"
        manifest_path.write_text(json.dumps({"agents": [{
            "id": "finance-analyst", "display_name": "Finance Analyst",
            "division": "finance", "capabilities": ["finance"],
            "risk_classification": "HIGH"
        }]}), encoding="utf-8")
        result = AgentRouter(manifest_path).select_team(
            "Improve performance", {"project_type": "trading", "safety_critical": True})
        self.assertEqual(result["domain"], "trading")
        self.assertTrue(result["safety_critical"])

if __name__ == "__main__":
    unittest.main()
