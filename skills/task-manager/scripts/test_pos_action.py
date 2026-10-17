"""Tests für pos_action.py. Laufen auf einer Kopie des PersonalOS, nie auf dem Original.

    python3 -m unittest discover -s skills/task-manager/scripts -p 'test_pos_action.py'
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
from datetime import date, timedelta
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("pos_action.py")
REPO = SCRIPT.parents[3]
TODAY = date.today()
FUTURE = (TODAY + timedelta(days=30)).isoformat()
PAST = (TODAY - timedelta(days=3)).isoformat()


class PosActionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="pos-action-test-")
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
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=json.dumps(data or {}),
                              capture_output=True, text=True, env=env, timeout=120)

    def actions(self):
        return set((self.root / "operations/actions").glob("*.md"))

    def create(self, **extra):
        data = {"title": "Testaufgabe", "truth": "Max will etwas testen.", "outcome": "Test ist gelaufen.",
                "done": "Erledigt, wenn der Test lief.", "next": "Test starten.", **extra}
        result = self.run_tool("create", data=data)
        self.assertEqual(result.returncode, 0, result.stderr)
        rel = result.stdout.splitlines()[0]
        return rel, rel.split("/")[-1].removesuffix(".md")

    def read(self, rel):
        return (self.root / rel).read_text(encoding="utf-8")

    # -------------------------------------------------------------- anlegen

    def test_create_writes_valid_record_with_server_date(self):
        rel, _ = self.create(priority="high", target=FUTURE, owners=["identity/me"])
        text = self.read(rel)
        self.assertIn(f"created: {TODAY.isoformat()}", text)
        self.assertIn(f"target: {FUTURE}", text)
        self.assertIn("action_priority: high", text)
        self.assertIn(f"Max will etwas testen. (Max Mustermann, {TODAY.isoformat()})", text)
        self.assertIn(f"- **{TODAY.isoformat()}** | Action created.", text)
        self.assertIn('affected_owner_refs: ["[[identity/me]]"]', text)

    def test_supplied_attribution_is_not_doubled(self):
        rel, rid = self.create(truth=f"Max will etwas testen. (Max Mustermann, {TODAY.isoformat()})")
        result = self.run_tool("update", rid, data={"note": "x", "truth": "Neu. (Max Mustermann, 2026-01-01) (Max Mustermann, 2026-01-01)"})
        self.assertEqual(result.returncode, 0, result.stderr)
        text = self.read(rel)
        self.assertIn(f"Max will etwas testen. (Max Mustermann, {TODAY.isoformat()})\n", text)
        self.assertIn(f"Neu. (Max Mustermann, {TODAY.isoformat()})\n", text)
        self.assertNotIn("2026-01-01", text)

    def test_create_waiting_requires_follow_up(self):
        before = self.actions()
        result = self.run_tool("create", data={"title": "x", "truth": "x", "outcome": "x", "done": "x",
                                               "next": "x", "lifecycle": "waiting", "waiting_on": "Antwort"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("follow_up_at", result.stderr)
        self.assertEqual(before, self.actions())

    def test_create_refuses_past_date(self):
        result = self.run_tool("create", data={"title": "x", "truth": "x", "outcome": "x", "done": "x",
                                               "next": "x", "due": PAST})
        self.assertEqual(result.returncode, 1)
        self.assertIn("Vergangenheit", result.stderr)

    def test_create_refuses_frontmatter_injection(self):
        before = self.actions()
        for field, value in (("truth", "ok\n---\nlifecycle: completed"), ("next", "## Timeline\n- gefälscht"),
                             ("title", "zwei\nzeilen")):
            data = {"title": "x", "truth": "x", "outcome": "x", "done": "x", "next": "x", field: value}
            result = self.run_tool("create", data=data)
            self.assertEqual(result.returncode, 1, field)
        self.assertEqual(before, self.actions())

    def test_create_refuses_bad_owner_paths(self):
        for owner in ("../../etc/passwd", "projects/gibt-es-nicht", "system/index", "projects/../SOUL"):
            data = {"title": "x", "truth": "x", "outcome": "x", "done": "x", "next": "x", "owners": [owner]}
            result = self.run_tool("create", data=data)
            self.assertEqual(result.returncode, 1, owner)

    def test_create_refuses_unknown_keys_and_enums(self):
        base = {"title": "x", "truth": "x", "outcome": "x", "done": "x", "next": "x"}
        self.assertEqual(self.run_tool("create", data={**base, "path": "x"}).returncode, 1)
        self.assertEqual(self.run_tool("create", data={**base, "priority": "urgent"}).returncode, 1)
        self.assertEqual(self.run_tool("create", data={**base, "lifecycle": "completed"}).returncode, 1)

    # -------------------------------------------------------------- ändern

    def test_update_refuses_bad_ids(self):
        for rid in ("../../SOUL", "01a0b014-247b-7ce4-8b48-d4dd9a76eb0", "01a0b014-247b-7ce4-8b48-000000000000"):
            result = self.run_tool("update", rid, data={"note": "x", "priority": "low"})
            self.assertEqual(result.returncode, 1, rid)

    def test_update_waiting_and_back_cleans_state_fields(self):
        rel, rid = self.create()
        result = self.run_tool("update", rid, data={"note": "Wartet auf Antwort.", "lifecycle": "waiting",
                                                    "waiting_on": "Antwort von Alex", "follow_up_at": FUTURE})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('waiting_on: "Antwort von Alex"', self.read(rel))
        result = self.run_tool("update", rid, data={"note": "Antwort da.", "lifecycle": "in-progress",
                                                    "truth": "Alex hat geantwortet."})
        self.assertEqual(result.returncode, 0, result.stderr)
        text = self.read(rel)
        self.assertNotIn("waiting_on", text)
        self.assertNotIn("follow_up_at", text)
        self.assertIn(f"Alex hat geantwortet. (Max Mustermann, {TODAY.isoformat()})", text)
        self.assertIn(f"- **{TODAY.isoformat()}** | Antwort da.", text)

    def test_update_requires_note_and_change(self):
        _, rid = self.create()
        self.assertEqual(self.run_tool("update", rid, data={"priority": "low"}).returncode, 1)
        self.assertEqual(self.run_tool("update", rid, data={"note": "nichts"}).returncode, 1)
        self.assertEqual(self.run_tool("update", rid, data={"note": "x", "id": "neu"}).returncode, 1)

    def test_remove_date_with_null(self):
        rel, rid = self.create(target=FUTURE)
        result = self.run_tool("update", rid, data={"note": "Ziel entfernt.", "target": None})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("target:", self.read(rel))

    def test_complete_and_cancel(self):
        rel, rid = self.create()
        self.assertEqual(self.run_tool("complete", rid, data={"note": "Test bestanden"}).returncode, 0)
        text = self.read(rel)
        self.assertIn("lifecycle: completed", text)
        self.assertIn("| Erledigt: Test bestanden", text)
        _, rid2 = self.create()
        self.assertEqual(self.run_tool("cancel", rid2, data={}).returncode, 1)
        self.assertEqual(self.run_tool("cancel", rid2, data={"reason": "doch nicht nötig"}).returncode, 0)

    # -------------------------------------------------------------- Sicherheit beim Schreiben

    def test_failed_check_restores_previous_state(self):
        rel, _ = self.create()
        original = self.read(rel)
        os.environ["POS_ROOT"] = str(self.root)
        spec = importlib.util.spec_from_file_location("pos_action_under_test", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        broken = original.replace("## Done Boundary", "## Falscher Abschnitt")
        error = module.write_checked(rel, broken, keep=True)
        self.assertTrue(error)
        self.assertEqual(original, self.read(rel))
        new_rel = "operations/actions/01a0b014-247b-7ce4-8b48-111111111111.md"
        self.assertTrue(module.write_checked(new_rel, broken, keep=True))
        self.assertFalse((self.root / new_rel).exists())

    def test_dry_run_writes_nothing(self):
        before = self.actions()
        data = {"title": "x", "truth": "x", "outcome": "x", "done": "x", "next": "x"}
        for lock in (True, False):
            result = self.run_tool("create", "--dry-run", data=data, lock=lock)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Probelauf", result.stdout)
        self.assertEqual(before, self.actions())

    def test_held_lock_blocks_write(self):
        before = self.actions()
        fd = os.open(self.lock, os.O_RDONLY | os.O_CREAT, 0o664)
        fcntl.flock(fd, fcntl.LOCK_EX)
        try:
            data = {"title": "x", "truth": "x", "outcome": "x", "done": "x", "next": "x"}
            result = self.run_tool("create", data=data, timeout_s="1")
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Schreibsperre", result.stderr)
        self.assertEqual(before, self.actions())

    def test_every_existing_action_round_trips(self):
        """Jede bestehende Aufgabe lässt sich ändern, ohne dass die Prüfung rot wird."""
        for path in sorted((REPO / "operations/actions").glob("0*.md")):
            rid = path.stem
            result = self.run_tool("update", rid, "--dry-run", data={"note": "Rundlauf-Test.", "truth": "Test."})
            self.assertEqual(result.returncode, 0, f"{rid}: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
