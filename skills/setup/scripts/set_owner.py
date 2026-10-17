#!/usr/bin/env python3
"""Setzt den Namen der Besitzerin oder des Besitzers im ganzen PersonalOS ein.

Der Starter benutzt "Max Mustermann" als Platzhalter für die Person, der das
PersonalOS gehört. Dieses Skript ersetzt ihn in allen Textdateien einmalig.

Aufruf:

  python3 skills/setup/scripts/set_owner.py --name "Vorname Nachname" [--first Vorname] [--dry-run]

Sicherheitsgrenzen: ändert nur Textdateien innerhalb des PersonalOS, nie `.git/`,
und bricht ab, wenn der Platzhalter nicht mehr vorkommt. Danach werden die
abgeleiteten Datenmodell-Artefakte neu erzeugt.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".obsidian"}
SUFFIXES = {".md", ".py", ".json", ".jsonl", ".yaml", ".yml", ".fixture", ".txt"}
SELF = {Path(__file__).resolve(), (ROOT / "skills/setup/SKILL.md").resolve(),
        (ROOT / "skills/setup/scripts/test_set_owner.py").resolve()}
PLACEHOLDER = "Max Mustermann"


def genitive(name: str) -> str:
    """Deutscher Genitiv eines Namens: "Jonas'" oder "Annas"."""
    return f"{name}'" if name[-1].lower() in "sxzß" else f"{name}s"


def slug(name: str) -> str:
    text = name.lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue").replace("ß", "ss")
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def replacements(full: str, first: str) -> list[tuple[re.Pattern, str]]:
    pairs = [
        (r"Max Mustermann's", f"{full}'s"),
        (r"Max Mustermanns", genitive(full)),
        (r"Max Mustermann", full),
        (r"max-mustermann", slug(full)),
        (r"\bMax's", f"{first}'s"),
        (r"\bMax'", genitive(first)),
        (r"\bMax\b", first),
    ]
    return [(re.compile(p), r.replace("\\", "\\\\")) for p, r in pairs]


def candidates() -> list[Path]:
    files = []
    for path in sorted(ROOT.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.is_file() and path.suffix in SUFFIXES and path.resolve() not in SELF:
            files.append(path)
    return files


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", required=True, help="vollständiger Name, etwa 'Jonas Beispiel'")
    parser.add_argument("--first", help="Anrede oder Vorname, Standard: erstes Wort von --name")
    parser.add_argument("--dry-run", action="store_true", help="nur zeigen, was sich ändern würde")
    args = parser.parse_args(argv)

    full = " ".join(args.name.split())
    first = (args.first or full.split(" ")[0]).strip()
    if not full or not first or re.search(r"[\n\"\[\]#|]", full + first):
        print("set-owner: ABGELEHNT: Name ist leer oder enthält ungültige Zeichen", file=sys.stderr)
        return 1

    rules = replacements(full, first)
    changed: list[tuple[Path, int]] = []
    for path in candidates():
        text = path.read_text(encoding="utf-8")
        new, total = text, 0
        for pattern, value in rules:
            new, count = pattern.subn(value, new)
            total += count
        if total:
            changed.append((path, total))
            if not args.dry_run:
                path.write_text(new, encoding="utf-8")

    if not changed:
        print(f"set-owner: Platzhalter \"{PLACEHOLDER}\" kommt nicht mehr vor, nichts zu tun.")
        return 0
    for path, count in changed:
        print(f"{path.relative_to(ROOT)}: {count}")
    print(f"{len(changed)} Datei(en), Name: {full}, Anrede: {first}")
    if args.dry_run:
        print("Probelauf: nichts geschrieben.")
        return 0

    build = subprocess.run([sys.executable, str(ROOT / "system/data-model/scripts/pos_v1.py"),
                            "--root", str(ROOT), "build"], capture_output=True, text=True)
    print((build.stdout + build.stderr).strip())
    return build.returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
