#!/usr/bin/env python3
"""Legt einen Posteingang-Eintrag unter inbox/captures/ in einem Schritt an.

Aufruf mit JSON auf stdin, optional --dry-run:

  pos-capture <<'EOF'
  {"title": "Kurzer Titel",
   "input_kind": "chat",          # chat | voice-note | handwritten | screenshot | file | url | manual | other
   "original": "Max' Wortlaut, unverändert und vollständig",
   "understanding": ["Punkt 1, wie verstanden", "..."],
   "uncertain": ["unklare Stelle und Frage dazu"],     # optional
   "owner_hint": "vermuteter Owner",                    # optional
   "source": "Chat-Nachricht von Max Mustermann, JJJJ-MM-TT, Direktnachricht an den Agenten"}
  EOF

Sicherheitsgrenzen: legt nur neue Dateien inbox/captures/<UUIDv7>.md an, überschreibt
und löscht keinen bestehenden Record, setzt Datum und Timeline von der lokalen Uhr,
zitiert Max' Wortlaut vollständig und prüft mit pos_v1 und pos-verify. Bei roter
Prüfung entsteht keine Datei. Ist POS_WRITE_LOCK gesetzt, läuft der Schreibvorgang
unter der Sperre, die sich ein paralleler Sync teilt.
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(os.environ.get("POS_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(ROOT / "system/data-model/scripts"))
from pos_v1 import uuid7  # noqa: E402
from time_context import local_date  # noqa: E402

CAPTURES = "inbox/captures"
KINDS = {"chat", "voice-note", "handwritten", "screenshot", "file", "url", "manual", "other"}
KEYS = {"title", "input_kind", "original", "understanding", "uncertain", "owner_hint", "source"}
MAX_ORIGINAL = 20000


class Refused(Exception):
    """Eingabe verletzt eine Regel. Es wurde nichts geschrieben."""


def strip_control(text: str) -> str:
    return "".join(ch for ch in text.replace("\r", "") if ch in "\n\t" or ord(ch) >= 32).strip()


def line(value, name: str, limit: int) -> str:
    """Einzeiliger Text ohne Markdown-Struktur am Zeilenanfang."""
    if not isinstance(value, str):
        raise Refused(f"`{name}` muss Text sein")
    text = strip_control(value)
    if not text:
        raise Refused(f"`{name}` ist leer")
    if "\n" in text:
        raise Refused(f"`{name}` muss einzeilig sein")
    if len(text) > limit:
        raise Refused(f"`{name}` ist länger als {limit} Zeichen")
    if text.startswith("#") or re.fullmatch(r"-{3,}|={3,}", text):
        raise Refused(f"`{name}` darf nicht mit einer Überschrift oder Trennlinie beginnen")
    return text


def items(value, name: str, *, required: bool) -> list[str]:
    if value in (None, "", []):
        if required:
            raise Refused(f"`{name}` ist Pflicht")
        return []
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list) or len(value) > 30:
        raise Refused(f"`{name}` muss eine Liste mit höchstens 30 Punkten sein")
    return [line(v, name, 500) for v in value]


def quote(original: str) -> str:
    """Max' Wortlaut bleibt vollständig erhalten, jede Zeile als Zitat."""
    return "\n".join(f"> {l}" if l else ">" for l in original.splitlines())


def build(data: dict, today: date) -> tuple[str, str]:
    unknown = sorted(set(data) - KEYS)
    if unknown:
        raise Refused(f"unbekannte Angaben: {unknown}, erlaubt sind {sorted(KEYS)}")
    title = line(data.get("title"), "title", 120).replace('"', "'")
    kind = data.get("input_kind") or "chat"
    if kind not in KINDS:
        raise Refused(f"`input_kind` muss eines von {sorted(KINDS)} sein")
    if not isinstance(data.get("original"), str) or not strip_control(data["original"]):
        raise Refused("`original` ist Pflicht")
    original = strip_control(data["original"])
    if len(original) > MAX_ORIGINAL:
        raise Refused(f"`original` ist länger als {MAX_ORIGINAL} Zeichen")
    understanding = items(data.get("understanding"), "understanding", required=True)
    uncertain = items(data.get("uncertain"), "uncertain", required=False)
    source = line(data.get("source"), "source", 300)
    owner = line(data["owner_hint"], "owner_hint", 200) if data.get("owner_hint") else ""

    truth = "So vom Agenten verstanden, noch nicht von Max bestätigt:\n\n" + "\n".join(f"- {i}" for i in understanding)
    if uncertain:
        truth += "\n\n**Deutung unsicher:**\n\n" + "\n".join(f"- {i}" for i in uncertain)
    routing = "Noch nicht verarbeitet." + (f" Vermuteter Owner: {owner}." if owner else "")
    rid = uuid7()
    d = today.isoformat()
    content = f"""---
schema_version: pos-v1
id: {rid}
type: capture
title: "{title}"
created: {d}
updated: {d}
lifecycle: unprocessed
input_kind: {kind}
---

# {title}

## Current Truth

{truth}

## Original Input

{quote(original)}

## Source Basis

{source}

## Processing and Routing

{routing}

## Retention

Unverarbeitet. Der Originaltext bleibt wörtlich erhalten.

## Timeline

- **{d}** | Capture angelegt.
"""
    return f"{CAPTURES}/{rid}.md", content


class WriteLock:
    def __init__(self) -> None:
        self.path = os.environ.get("POS_WRITE_LOCK")
        self.fd = None

    def __enter__(self):
        if self.path:
            self.fd = os.open(self.path, os.O_RDONLY | os.O_CREAT, 0o664)
            deadline = time.monotonic() + float(os.environ.get("POS_WRITE_LOCK_TIMEOUT", "60"))
            while True:
                try:
                    fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if time.monotonic() > deadline:
                        raise Refused("Schreibsperre nicht frei, bitte gleich erneut versuchen")
                    time.sleep(0.5)
        return self

    def __exit__(self, *exc):
        if self.fd is not None:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
            os.close(self.fd)


def run_checks(rel: str) -> str | None:
    checks = (
        [sys.executable, str(ROOT / "system/data-model/scripts/pos_v1.py"), "--root", str(ROOT), "validate", "--files", rel],
        [sys.executable, str(ROOT / "skills/pos-verify/scripts/run.py"), "--files", rel, "--strict-links"],
    )
    for cmd in checks:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
        if result.returncode != 0:
            return (result.stdout + result.stderr).strip()
    return None


def write_checked(rel: str, content: str, *, keep: bool) -> str | None:
    """Legt die neue Datei an, prüft sie und entfernt sie bei roter Prüfung oder keep=False."""
    path = ROOT / rel
    if path.exists():
        raise Refused(f"{rel} gibt es schon, es wird nichts überschrieben")
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    error = "unbekannter Fehler"
    try:
        error = run_checks(rel)
    finally:
        if error or not keep:
            path.unlink(missing_ok=True)
    return error


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--dry-run"]
    dry = len(args) != len(argv)
    if args:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        raw = sys.stdin.read()
        data = json.loads(raw, strict=False) if raw.strip() else {}
        if not isinstance(data, dict):
            raise Refused("Eingabe muss ein JSON-Objekt sein")
        rel, content = build(data, local_date(ROOT))
        if dry and not os.environ.get("POS_WRITE_LOCK"):
            print(content)
            print("Probelauf: nichts geschrieben, nicht geprüft.")
            return 0
        with WriteLock():
            error = write_checked(rel, content, keep=not dry)
    except Refused as refusal:
        print(f"pos-capture: ABGELEHNT: {refusal}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"pos-capture: ABGELEHNT: ungültige Eingabe ({exc})", file=sys.stderr)
        return 1
    if error:
        print("pos-capture: Prüfung rot, nichts angelegt:\n" + error, file=sys.stderr)
        return 1
    if dry:
        print(content)
        print("Probelauf: Prüfung pass, nichts geschrieben.")
        return 0
    print(rel)
    print("Prüfung: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
