#!/usr/bin/env python3
"""Legt Aufgaben unter operations/actions/ in einem Schritt an, ändert oder schließt sie.

Aufruf, Eingabe immer als JSON auf stdin:

  pos-action create            neue Aufgabe
  pos-action update <ID>       Felder ändern, Satz zur Current Truth ergänzen
  pos-action complete <ID>     abhaken
  pos-action cancel <ID>       streichen
  --dry-run                    Ergebnis zeigen, nichts dauerhaft schreiben

create:   {"title", "truth", "outcome", "done", "next",
           optional "lifecycle", "priority", "mode", "target", "due", "not_before",
           "follow_up_at", "waiting_on", "blocked_by", "owners": [Pfade], "evidence": Pfad}
update:   {"note": Timeline-Text, optional "title", "lifecycle", "priority", "mode",
           "target", "due", "not_before", "follow_up_at", "waiting_on", "blocked_by",
           "truth": Satz zum Anhängen, "next", "outcome", "done"}
           Ein Datum oder Text mit null entfernt das Feld.
complete: {"note": optional}
cancel:   {"reason": Pflicht}

Sicherheitsgrenzen: schreibt nur operations/actions/<UUIDv7>.md, löscht nie einen
bestehenden Record, nimmt nur Felder und Werte des Profils `action` an, setzt Datum,
Herkunft und Timeline selbst und prüft jede Änderung mit pos_v1 und pos-verify.
Bei roter Prüfung bleibt der alte Stand bzw. es entsteht keine Datei.
Ist POS_WRITE_LOCK gesetzt, läuft der Schreibvorgang unter dieser Sperre, die sich
ein paralleler Sync teilt. So wird nie eine ungeprüfte Datei gesichert.
"""
from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import sys
import time
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(os.environ.get("POS_ROOT", Path(__file__).resolve().parents[3]))
sys.path.insert(0, str(ROOT / "system/data-model/scripts"))
from pos_v1 import is_uuid7, split_markdown, uuid7  # noqa: E402
from time_context import local_date  # noqa: E402

ACTIONS = "operations/actions"
ATTRIBUTION = "Max Mustermann"
DEFAULT_EVIDENCE = "interactions/conversations/agent/agent-dm/conversation"
LIFECYCLES = {"ready", "in-progress", "waiting", "blocked", "deferred", "completed", "cancelled"}
PRIORITIES = {"critical", "high", "normal", "low"}
MODES = {"agent-execute", "agent-prepare", "human-only"}
DATE_FIELDS = ("due", "target", "not_before", "follow_up_at")
TEXT_FIELDS = ("waiting_on", "blocked_by")
FIELD_ORDER = (
    "schema_version", "id", "type", "title", "created", "updated", "lifecycle",
    "execution_mode", "action_priority", "due", "target", "not_before", "waiting_on",
    "blocked_by", "follow_up_at", "evidence_refs", "affected_owner_refs",
)
SECTIONS = ("Current Truth", "Desired Outcome", "Done Boundary", "Next Action",
            "Context and Evidence", "Timeline")
# Felder, die nur in einem bestimmten Status gelten, und wann sie Pflicht sind.
STATE_FIELDS = {"waiting": ("waiting_on", "follow_up_at"), "blocked": ("blocked_by",),
                "deferred": ("not_before",)}
MAX_TITLE = 120
MAX_TEXT = 2000
CREATE_KEYS = {"title", "truth", "outcome", "done", "next", "lifecycle", "priority", "mode",
               *DATE_FIELDS, *TEXT_FIELDS, "owners", "evidence"}
UPDATE_KEYS = {"note", "title", "lifecycle", "priority", "mode", *DATE_FIELDS, *TEXT_FIELDS,
               "truth", "next", "outcome", "done"}


class Refused(Exception):
    """Eingabe verletzt eine Regel. Es wurde nichts geschrieben."""


# ---------------------------------------------------------------- Eingaben prüfen

def clean_text(value, name: str, *, single_line: bool = False, limit: int = MAX_TEXT) -> str:
    if not isinstance(value, str):
        raise Refused(f"`{name}` muss Text sein")
    text = "".join(ch for ch in value if ch in "\n\t" or ord(ch) >= 32).strip()
    text = text.replace("\r", "")
    if not text:
        raise Refused(f"`{name}` ist leer")
    if len(text) > limit:
        raise Refused(f"`{name}` ist länger als {limit} Zeichen")
    if single_line and "\n" in text:
        raise Refused(f"`{name}` muss einzeilig sein")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#") or re.fullmatch(r"-{3,}|={3,}", stripped):
            raise Refused(f"`{name}` darf keine Überschriften oder Trennlinien enthalten")
    return text


def quoted(value: str) -> str:
    return '"' + value.replace("\\", "/").replace('"', "'") + '"'


def check_date(value, name: str, today: date) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise Refused(f"`{name}` muss ein Datum JJJJ-MM-TT sein")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        raise Refused(f"`{name}` ist kein gültiges Datum: {value}") from None
    if parsed < today:
        raise Refused(f"`{name}` {value} liegt in der Vergangenheit, heute ist {today.isoformat()}")
    if parsed > today + timedelta(days=5 * 366):
        raise Refused(f"`{name}` {value} liegt mehr als fünf Jahre in der Zukunft")
    return value


def check_enum(value, name: str, allowed: set[str]) -> str:
    if value not in allowed:
        raise Refused(f"`{name}` muss eines von {sorted(allowed)} sein")
    return value


def check_ref(value, name: str, prefixes: tuple[str, ...]) -> str:
    if not isinstance(value, str):
        raise Refused(f"`{name}` muss ein Pfad sein")
    ref = value.strip().removeprefix("[[").removesuffix("]]").removesuffix(".md").strip("/")
    if not re.fullmatch(r"[a-z0-9][a-z0-9/_.-]*", ref) or ".." in ref:
        raise Refused(f"`{name}` ist kein gültiger Pfad: {value}")
    if not ref.startswith(prefixes):
        raise Refused(f"`{name}` muss unter {', '.join(prefixes)} liegen: {value}")
    if not (ROOT / f"{ref}.md").is_file():
        raise Refused(f"`{name}` verweist auf einen Record, den es nicht gibt: {ref}")
    return ref


def check_keys(data: dict, allowed: set[str]) -> None:
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise Refused(f"unbekannte Angaben: {unknown}, erlaubt sind {sorted(allowed)}")


def action_path(rid: str) -> Path:
    if not is_uuid7(rid):
        raise Refused(f"keine gültige Aufgaben-ID: {rid}")
    path = ROOT / ACTIONS / f"{rid}.md"
    if not path.is_file():
        raise Refused(f"Aufgabe {rid} gibt es nicht")
    return path


# ---------------------------------------------------------------- Record bauen und ändern

def attributed(text: str, today: date) -> str:
    """Setzt die Herkunft selbst. Eine mitgelieferte Angabe am Ende wird ersetzt, nicht verdoppelt."""
    text = re.sub(r"(\s*\([^()]*,\s*\d{4}-\d{2}-\d{2}\))+\s*$", "", text).rstrip()
    return f"{text} ({ATTRIBUTION}, {today.isoformat()})"


def render_frontmatter(fields: dict[str, str]) -> str:
    lines = [f"{key}: {fields[key]}" for key in FIELD_ORDER if key in fields]
    return "---\n" + "\n".join(lines) + "\n---\n"


def parse_record(text: str) -> tuple[dict[str, str], dict[str, str], str]:
    """Liefert Rohwerte der Frontmatter, Abschnitte und Überschrift."""
    split_markdown(text)  # wirft bei kaputter Frontmatter
    end = text.find("\n---\n", 4)
    raw: dict[str, str] = {}
    for line in text[4:end].splitlines():
        key, _, value = line.partition(":")
        raw[key.strip()] = value.strip()
    unknown = sorted(set(raw) - set(FIELD_ORDER))
    if unknown:
        raise Refused(f"Record enthält Felder, die das Werkzeug nicht kennt: {unknown}")
    body = text[end + 5:]
    heading_match = re.search(r"^# .*$", body, re.M)
    if not heading_match:
        raise Refused("Record hat keine Titelüberschrift")
    sections: dict[str, str] = {}
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    if parts[0].strip() != heading_match.group(0):
        raise Refused("Record hat Text zwischen Titel und erstem Abschnitt")
    for name, content in zip(parts[1::2], parts[2::2]):
        sections[name.strip()] = content.strip("\n")
    if list(sections) != list(SECTIONS):
        raise Refused(f"Record hat nicht die erwarteten Abschnitte: {list(sections)}")
    return raw, sections, heading_match.group(0)


def render_record(fields: dict[str, str], heading: str, sections: dict[str, str]) -> str:
    body = "\n\n".join(f"## {name}\n\n{sections[name].strip()}" for name in SECTIONS)
    return f"{render_frontmatter(fields)}\n{heading}\n\n{body}\n"


def apply_state_fields(fields: dict[str, str], lifecycle: str, explicit: set[str]) -> None:
    """Entfernt Felder, die zum alten Status gehörten, und prüft Pflichtfelder."""
    for state, names in STATE_FIELDS.items():
        if state != lifecycle:
            for name in names:
                if name not in explicit:
                    fields.pop(name, None)
    for name in STATE_FIELDS.get(lifecycle, ()):
        if name not in fields:
            raise Refused(f"Status `{lifecycle}` braucht `{name}`")


def set_optional(fields: dict[str, str], data: dict, today: date) -> set[str]:
    explicit = set()
    for name in DATE_FIELDS:
        if name in data:
            explicit.add(name)
            if data[name] is None:
                fields.pop(name, None)
            else:
                fields[name] = check_date(data[name], name, today)
    for name in TEXT_FIELDS:
        if name in data:
            explicit.add(name)
            if data[name] is None:
                fields.pop(name, None)
            else:
                fields[name] = quoted(clean_text(data[name], name, single_line=True, limit=200))
    return explicit


def build_create(data: dict, today: date) -> tuple[str, str, str]:
    check_keys(data, CREATE_KEYS)
    missing = [k for k in ("title", "truth", "outcome", "done", "next") if not data.get(k)]
    if missing:
        raise Refused(f"Pflichtangaben fehlen: {missing}")
    title = clean_text(data["title"], "title", single_line=True, limit=MAX_TITLE).replace('"', "'")
    lifecycle = check_enum(data.get("lifecycle", "ready"), "lifecycle", LIFECYCLES - {"completed", "cancelled"})
    evidence = check_ref(data.get("evidence", DEFAULT_EVIDENCE), "evidence", ("interactions/",))
    owners = data.get("owners") or []
    if not isinstance(owners, list):
        raise Refused("`owners` muss eine Liste von Pfaden sein")
    owner_refs = [check_ref(o, "owners", ("projects/", "people/", "companies/", "finance/", "health/",
                                          "identity/", "operations/", "business/", "content/", "knowledge/"))
                  for o in owners]
    rid = uuid7()
    fields = {
        "schema_version": "pos-v1",
        "id": rid,
        "type": "action",
        "title": f'"{title}"',
        "created": today.isoformat(),
        "updated": today.isoformat(),
        "lifecycle": lifecycle,
        "execution_mode": check_enum(data.get("mode", "human-only"), "mode", MODES),
        "action_priority": check_enum(data.get("priority", "normal"), "priority", PRIORITIES),
        "evidence_refs": f'["[[{evidence}]]"]',
    }
    if owner_refs:
        fields["affected_owner_refs"] = "[" + ", ".join(f'"[[{o}]]"' for o in owner_refs) + "]"
    explicit = set_optional(fields, data, today)
    apply_state_fields(fields, lifecycle, explicit)
    context = [f"- Angelegt vom Agenten: [[{evidence}]]"]
    sections = {
        "Current Truth": attributed(clean_text(data["truth"], "truth"), today),
        "Desired Outcome": clean_text(data["outcome"], "outcome"),
        "Done Boundary": clean_text(data["done"], "done"),
        "Next Action": clean_text(data["next"], "next"),
        "Context and Evidence": "\n".join(context),
        "Timeline": f"- **{today.isoformat()}** | Action created.",
    }
    rel = f"{ACTIONS}/{rid}.md"
    return rel, render_record(fields, f"# {title}", sections), f"Neue Aufgabe: {title}"


def build_change(rid: str, data: dict, today: date, command: str) -> tuple[str, str, str]:
    path = action_path(rid)
    fields, sections, heading = parse_record(path.read_text(encoding="utf-8"))
    title = fields["title"].strip('"')
    if command == "complete":
        check_keys(data, {"note"})
        data = {"lifecycle": "completed",
                "note": "Erledigt" + (f": {clean_text(data['note'], 'note', single_line=True, limit=300)}" if data.get("note") else ".")}
    elif command == "cancel":
        check_keys(data, {"reason"})
        if not data.get("reason"):
            raise Refused("`reason` ist Pflicht beim Streichen")
        data = {"lifecycle": "cancelled",
                "note": f"Gestrichen: {clean_text(data['reason'], 'reason', single_line=True, limit=300)}"}
    else:
        check_keys(data, UPDATE_KEYS)
        if not data.get("note"):
            raise Refused("`note` ist Pflicht: ein Satz für die Timeline, was sich geändert hat")
        if set(data) == {"note"}:
            raise Refused("keine Änderung angegeben")
    note = clean_text(data["note"], "note", single_line=True, limit=300)

    if "title" in data:
        title = clean_text(data["title"], "title", single_line=True, limit=MAX_TITLE).replace('"', "'")
        fields["title"] = f'"{title}"'
        heading = f"# {title}"
    lifecycle = fields["lifecycle"]
    if "lifecycle" in data:
        lifecycle = check_enum(data["lifecycle"], "lifecycle", LIFECYCLES)
        fields["lifecycle"] = lifecycle
    if "priority" in data:
        fields["action_priority"] = check_enum(data["priority"], "priority", PRIORITIES)
    if "mode" in data:
        fields["execution_mode"] = check_enum(data["mode"], "mode", MODES)
    explicit = set_optional(fields, data, today)
    if "lifecycle" in data:
        apply_state_fields(fields, lifecycle, explicit)
    else:
        for name in STATE_FIELDS.get(lifecycle, ()):
            if name not in fields:
                raise Refused(f"Status `{lifecycle}` braucht `{name}`")
    if "truth" in data:
        sections["Current Truth"] += "\n\n" + attributed(clean_text(data["truth"], "truth"), today)
    for key, section in (("next", "Next Action"), ("outcome", "Desired Outcome"), ("done", "Done Boundary")):
        if key in data:
            sections[section] = clean_text(data[key], key)
    fields["updated"] = today.isoformat()
    sections["Timeline"] += f"\n- **{today.isoformat()}** | {note}"
    rel = f"{ACTIONS}/{rid}.md"
    return rel, render_record(fields, heading, sections), f"{title}: {note}"


# ---------------------------------------------------------------- Schreiben unter Sperre

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
    """Schreibt, prüft und stellt bei roter Prüfung oder keep=False den alten Stand her."""
    path = ROOT / rel
    previous = path.read_text(encoding="utf-8") if path.exists() else None
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)
    error = "unbekannter Fehler"
    try:
        error = run_checks(rel)
    finally:
        if error or not keep:
            if previous is None:
                path.unlink(missing_ok=True)
            else:
                tmp.write_text(previous, encoding="utf-8")
                os.replace(tmp, path)
    return error


def main(argv: list[str]) -> int:
    args = [a for a in argv if a != "--dry-run"]
    dry = len(args) != len(argv)
    if not args or args[0] not in {"create", "update", "complete", "cancel"}:
        print(__doc__, file=sys.stderr)
        return 2
    command = args[0]
    try:
        raw = sys.stdin.read() if not sys.stdin.isatty() else ""
        data = json.loads(raw, strict=False) if raw.strip() else {}
        if not isinstance(data, dict):
            raise Refused("Eingabe muss ein JSON-Objekt sein")
        today = local_date(ROOT)
        if command == "create":
            if len(args) != 1:
                raise Refused("create erwartet keine ID")
            rel, content, summary = build_create(data, today)
        else:
            if len(args) != 2:
                raise Refused(f"{command} erwartet genau eine ID")
            rel, content, summary = build_change(args[1], data, today, command)
        if dry and not os.environ.get("POS_WRITE_LOCK"):
            print(content)
            print("Probelauf: nichts geschrieben, nicht geprüft.")
            return 0
        with WriteLock():
            error = write_checked(rel, content, keep=not dry)
    except Refused as refusal:
        print(f"pos-action: ABGELEHNT: {refusal}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, ValueError) as exc:
        print(f"pos-action: ABGELEHNT: ungültige Eingabe ({exc})", file=sys.stderr)
        return 1
    if error:
        print("pos-action: Prüfung rot, nichts geändert:\n" + error, file=sys.stderr)
        return 1
    if dry:
        print(content)
        print("Probelauf: Prüfung pass, nichts geschrieben.")
        return 0
    print(rel)
    print(summary)
    print("Prüfung: pass")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
