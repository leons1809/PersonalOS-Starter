"""Tests für pos_capture.py. Laufen auf einer Kopie des PersonalOS, nie auf dem Original.

    python3 -m unittest discover -s skills/log/scripts -p 'test_pos_capture.py'
"""
from __future__ import annotations

import fcntl
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("pos_capture.py")
REPO = SCRIPT.parents[3]
TODAY = date.today().isoformat()
BASE = {"title": "Testnotiz", "input_kind": "chat", "original": "Bitte merk dir das.",
        "understanding": ["Max will etwas festhalten."], "source": "Test, Chat-Nachricht"}


class PosCaptureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="pos-capture-test-")
        cls.root = Path(cls.tmp) / "PersonalOS"
        shutil.copytree(REPO, cls.root, ignore=shutil.ignore_patterns(".git", "__pycache__", ".obsidian"))
        cls.lock = str(Path(cls.tmp) / "write.lock")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def run_tool(self, *args, data=None, lock=True, timeout_s="60"):
        env = dict(os.environ, POS_ROOT=str(self.root), POS_WRITE_LOCK_TIMEOUT=timeout_s)
        env.pop("POS_WRITE_LOCK", None)
        if lock:
            env["POS_WRITE_LOCK"] = self.lock
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=json.dumps(data if data is not None else BASE),
                              capture_output=True, text=True, env=env, timeout=120)

    def captures(self):
        return set((self.root / "inbox/captures").glob("*.md"))

    def test_create_valid_capture(self):
        result = self.run_tool(data={**BASE, "uncertain": ["Was ist gemeint?"], "owner_hint": "finance/belege"})
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / result.stdout.splitlines()[0]).read_text(encoding="utf-8")
        self.assertIn(f"created: {TODAY}", text)
        self.assertIn("> Bitte merk dir das.", text)
        self.assertIn("- Max will etwas festhalten.", text)
        self.assertIn("**Deutung unsicher:**", text)
        self.assertIn("Vermuteter Owner: finance/belege.", text)
        self.assertIn(f"- **{TODAY}** | Capture angelegt.", text)

    def test_original_with_markdown_is_quoted_and_valid(self):
        original = "# Überschrift\n---\n## Timeline\nlifecycle: processed\n\nNoch eine Zeile"
        result = self.run_tool(data={**BASE, "original": original})
        self.assertEqual(result.returncode, 0, result.stderr)
        text = (self.root / result.stdout.splitlines()[0]).read_text(encoding="utf-8")
        self.assertIn("> # Überschrift\n> ---\n> ## Timeline\n> lifecycle: processed\n>\n> Noch eine Zeile", text)
        self.assertIn("lifecycle: unprocessed", text)

    def test_refuses_bad_input(self):
        before = self.captures()
        cases = [
            {**BASE, "input_kind": "email"},
            {**BASE, "title": ""},
            {**BASE, "title": "zwei\nzeilen"},
            {**BASE, "understanding": []},
            {**BASE, "understanding": ["## Timeline"]},
            {**BASE, "source": "---"},
            {**BASE, "original": "   "},
            {**BASE, "path": "../../SOUL.md"},
            ["keine", "objekt"],
        ]
        for data in cases:
            self.assertEqual(self.run_tool(data=data).returncode, 1, data)
        self.assertEqual(before, self.captures())

    def test_failed_check_leaves_no_file(self):
        os.environ["POS_ROOT"] = str(self.root)
        spec = importlib.util.spec_from_file_location("pos_capture_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        rel, content = module.build(dict(BASE), date.today())
        broken = content.replace("## Retention", "## Falscher Abschnitt")
        self.assertTrue(module.write_checked(rel, broken, keep=True))
        self.assertFalse((self.root / rel).exists())

    def test_never_overwrites(self):
        result = self.run_tool()
        rel = result.stdout.splitlines()[0]
        original = (self.root / rel).read_text(encoding="utf-8")
        os.environ["POS_ROOT"] = str(self.root)
        spec = importlib.util.spec_from_file_location("pos_capture_under_test2", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with self.assertRaises(module.Refused):
            module.write_checked(rel, "x", keep=True)
        self.assertEqual(original, (self.root / rel).read_text(encoding="utf-8"))

    def test_dry_run_writes_nothing(self):
        before = self.captures()
        for lock in (True, False):
            result = self.run_tool("--dry-run", lock=lock)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Probelauf", result.stdout)
        self.assertEqual(before, self.captures())

    def test_held_lock_blocks_write(self):
        before = self.captures()
        fd = os.open(self.lock, os.O_RDONLY | os.O_CREAT, 0o664)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            result = self.run_tool(timeout_s="1")
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Schreibsperre", result.stderr)
        self.assertEqual(before, self.captures())


if __name__ == "__main__":
    unittest.main()
