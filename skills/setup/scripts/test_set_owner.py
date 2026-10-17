#!/usr/bin/env python3
"""Tests für set_owner.py, jeweils auf einer Kopie des PersonalOS.

    python3 -m unittest discover -s skills/setup/scripts -p 'test_set_owner.py'
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


class SetOwnerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.mkdtemp(prefix="set-owner-test-")
        self.root = Path(self.tmp) / "PersonalOS"
        shutil.copytree(REPO, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".obsidian"))
        self.script = self.root / "skills/setup/scripts/set_owner.py"

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_tool(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(self.script), *args], capture_output=True, text=True)

    def read(self, rel: str) -> str:
        return (self.root / rel).read_text(encoding="utf-8")

    def test_replaces_all_forms_and_keeps_registry_green(self) -> None:
        result = self.run_tool("--name", "Jonas Beispiel")
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("Jonas Beispiel", self.read("AGENTS.md"))
        self.assertIn("Jonas Beispiels", self.read("system/truth-systems/personalos.md"))
        self.assertIn("Jonas' Wortlaut", self.read("skills/log/scripts/pos_capture.py"))
        self.assertIn('ATTRIBUTION = "Jonas Beispiel"', self.read("skills/task-manager/scripts/pos_action.py"))
        self.assertIn("people/jonas-beispiel.md", self.read("system/conventions/core/record-naming-and-temporal-paths.md"))
        self.assertIn("Max Mustermann", self.read("skills/setup/SKILL.md"))
        leftovers = subprocess.run(["grep", "-rIl", "--exclude-dir=setup", "Max Mustermann", str(self.root)],
                                   capture_output=True, text=True).stdout.strip()
        self.assertEqual(leftovers, "")
        check = subprocess.run([sys.executable, str(self.root / "system/data-model/scripts/pos_v1.py"),
                                "--root", str(self.root), "check-registry"], capture_output=True, text=True)
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)

    def test_dry_run_writes_nothing(self) -> None:
        before = self.read("AGENTS.md")
        result = self.run_tool("--name", "Anna Test", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Probelauf", result.stdout)
        self.assertEqual(before, self.read("AGENTS.md"))

    def test_second_run_is_a_no_op(self) -> None:
        self.assertEqual(self.run_tool("--name", "Anna Test").returncode, 0)
        result = self.run_tool("--name", "Anna Test")
        self.assertEqual(result.returncode, 0)
        self.assertIn("nichts zu tun", result.stdout)

    def test_refuses_invalid_name(self) -> None:
        result = self.run_tool("--name", "[[Hack]]")
        self.assertEqual(result.returncode, 1)
        self.assertIn("ABGELEHNT", result.stderr)


if __name__ == "__main__":
    unittest.main()
