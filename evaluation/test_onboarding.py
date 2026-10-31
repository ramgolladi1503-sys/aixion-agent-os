#!/usr/bin/env python3
"""Portable onboarding tests. Run: PYTHONPATH=. python -m unittest evaluation.test_onboarding"""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from onboarding.onboard import onboard_project

class OnboardingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name) / "sample"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], check=True)

    def test_new_repo_gets_governance(self):
        result = onboard_project(self.repo, project_type="web")
        self.assertEqual(result["status"], "onboarded")
        self.assertTrue((self.repo / "AGENTS.md").is_file())
        self.assertTrue((self.repo / ".github/workflows/aixion-governance.yml").is_file())
        config = json.loads((self.repo / ".aixion/config.json").read_text())
        self.assertNotIn("agent_os_root", config)
        self.assertEqual(config["project_type"], "web")

    def test_existing_instructions_preserved(self):
        (self.repo / "AGENTS.md").write_text("Critical local rule\n")
        result = onboard_project(self.repo)
        self.assertEqual(result["files"]["AGENTS.md"], "preserved")
        self.assertEqual((self.repo / "AGENTS.md").read_text(), "Critical local rule\n")

    def test_repeated_onboarding_no_overwrite(self):
        onboard_project(self.repo)
        conf = self.repo / ".aixion/config.json"
        before = conf.read_text()
        result = onboard_project(self.repo, project_type="trading")
        self.assertEqual(result["status"], "already_onboarded")
        self.assertEqual(conf.read_text(), before)

    def test_invalid_existing_config_is_not_destroyed(self):
        conf = self.repo / ".aixion/config.json"
        conf.parent.mkdir()
        conf.write_text("{invalid")
        with self.assertRaises(ValueError):
            onboard_project(self.repo)
        self.assertEqual(conf.read_text(), "{invalid")

    def test_non_git_rejected(self):
        other = Path(self.tmp.name) / "other"
        other.mkdir()
        with self.assertRaises(ValueError):
            onboard_project(other)

    def test_tech_detection(self):
        (self.repo / "pyproject.toml").write_text("[project]\nname='x'\n")
        result = onboard_project(self.repo)
        self.assertIn("python", result["config"]["tech_stack"])

if __name__ == "__main__":
    unittest.main()
