#!/usr/bin/env python3
"""Pure unit tests for GitHub discovery without remote writes."""
import json
import unittest
from unittest.mock import patch
from onboarding.github_reconcile import eligible_repositories, reconcile

class ReconcileTests(unittest.TestCase):
    @patch("onboarding.github_reconcile.run")
    def test_only_opted_in_nonfork_repositories(self, run):
        run.return_value = json.dumps([
            {"nameWithOwner":"owner/managed","isArchived":False,"isFork":False,
             "repositoryTopics":[{"name":"aixion-managed"}]},
            {"nameWithOwner":"owner/unrelated","isArchived":False,"isFork":False,
             "repositoryTopics":[{"name":"other"}]},
            {"nameWithOwner":"owner/fork","isArchived":False,"isFork":True,
             "repositoryTopics":[{"name":"aixion-managed"}]},
            {"nameWithOwner":"owner/archived","isArchived":True,"isFork":False,
             "repositoryTopics":[{"name":"aixion-managed"}]}
        ])
        self.assertEqual(eligible_repositories("owner"), ["owner/managed"])

    @patch("onboarding.github_reconcile.subprocess.run")
    @patch("onboarding.github_reconcile.eligible_repositories")
    def test_dry_run_never_clones_or_writes(self, repos, subprocess_run):
        repos.return_value = ["owner/new-project"]
        subprocess_run.return_value.returncode = 1
        result = reconcile("owner", apply=False)
        self.assertEqual(result, [{"repo":"owner/new-project","status":"needs_onboarding"}])
        self.assertEqual(subprocess_run.call_count, 1)
        self.assertEqual(subprocess_run.call_args.args[0][:2], ["gh","api"])

    @patch("onboarding.github_reconcile.eligible_repositories")
    def test_apply_requires_credentials(self, repos):
        with patch.dict("os.environ", {"GH_TOKEN":"","GITHUB_TOKEN":""}):
            with self.assertRaises(RuntimeError):
                reconcile("owner", apply=True)
        repos.assert_not_called()

if __name__ == "__main__":
    unittest.main()
