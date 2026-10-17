---
name: setup
description: "Use this when a new PersonalOS has not been set up yet (USER.md still says \"Noch nicht ausgefüllt\") or the person asks to set up, onboard or personalize their PersonalOS. Guides the person through a short interview, puts their name into the system and fills USER.md and identity/me.md. Do NOT use for later single changes to identity or USER context; edit the owning record directly."
metadata:
  pos_schema_version: pos-v1
  pos_id: 01a14c28-b8c5-7c0d-b073-3ff9b0720c06
  pos_type: skill
  pos_title: "Skill: setup"
  pos_created: "2026-10-18"
  pos_updated: "2026-10-18"
  pos_lifecycle: active
  pos_skill_version: 1.0.0
  pos_system_refs: ["[[system/contracts/core/bootstrap-und-portabilitaet]]", "[[system/contracts/core/personalos-mutation-contract]]", "[[system/rules/core/minimal-record-content]]"]
  pos_reads_profile_keys: ["user-context", "identity-record", "truth-system"]
  pos_writes_profile_keys: ["user-context", "identity-record", "truth-system", "person", "project"]
  pos_template_refs: ["[[system/templates/core/bootstrap/user-context]]", "[[system/templates/identity/identity-record]]", "[[system/templates/entities/person]]", "[[system/templates/project]]"]
  pos_invokes_skill_refs: ["[[skills/pos-verify/SKILL]]"]
  pos_check_refs: ["[[system/checks/pos-v1-contract]]", "[[system/checks/core/personalos-mutation-postflight]]"]
---

# Skill: setup

## Purpose

Führt eine neue Person in rund 15 Minuten durch die Einrichtung ihres PersonalOS. Am Ende steht ihr Name überall im System, [[USER]] und [[identity/me]] beschreiben sie in ihren eigenen Worten, und alles ist geprüft.

Der Starter benutzt intern „Max Mustermann“ als Platzhalter. Die Person muss davon nichts wissen und nichts von Hand ersetzen; das übernimmt Schritt 2.

## Contract

- Es wird ein Gespräch geführt, kein Formular abgearbeitet: eine Frage pro Nachricht, kurz und freundlich, auf Deutsch, solange die Person nicht anders schreibt.
- Jede Frage darf übersprungen werden. Übersprungene Abschnitte bleiben als „Noch nicht ausgefüllt.“ stehen und können später ergänzt werden.
- Geschrieben wird nur, was die Person gesagt hat. Nichts wird erfunden, ausgeschmückt oder aus dem Namen abgeleitet.
- Records enthalten nur dauerhafte Wahrheit nach [[system/rules/core/minimal-record-content]]: keine Termine, keine Tagesstände, keine Vorgeschichte des Gesprächs.
- Während der Einrichtung werden keine Gesundheitsdaten, Finanzdaten, Ausweis- oder Kontonummern, Passwörter oder Secrets abgefragt.
- Vor dem Schreiben sieht die Person eine kurze Zusammenfassung und bestätigt sie.
- Nichts wird gepusht, veröffentlicht oder an externe Dienste gesendet.

## Ablauf

### 1. Begrüßen und Erwartung setzen

Erkläre in zwei, drei Sätzen: Das PersonalOS ist ein Gedächtnis aus Markdown-Dateien, das Agenten bei jeder Sitzung lesen. Die Einrichtung dauert etwa 15 Minuten, jede Frage ist optional, alles lässt sich später ändern. Frage dann nach dem Namen.

### 2. Name einsetzen

Frage nach dem vollständigen Namen und danach, wie Agenten die Person ansprechen sollen (Standard: Vorname). Prüfe zuerst mit einem Probelauf, dann schreibe:

```bash
python3 skills/setup/scripts/set_owner.py --name "<Vorname Nachname>" --first "<Anrede>" --dry-run
python3 skills/setup/scripts/set_owner.py --name "<Vorname Nachname>" --first "<Anrede>"
```

Das Skript ersetzt den Platzhalter in allen Textdateien und erzeugt die abgeleiteten Datenmodell-Artefakte neu. Endet es nicht mit `pass`, stoppe und zeige die Meldung.

### 3. Interview

Stelle die Fragen nacheinander. Fasse längere Antworten kurz zurück, bevor du weitergehst. Leitfragen, frei formulierbar:

| Abschnitt in [[USER]] | Leitfrage |
|---|---|
| Kurzprofil | Was machst du beruflich, und woran arbeitest du gerade grundsätzlich? |
| Arbeitsweise und Denkstil | Wie arbeitest du am liebsten, und wo stehst du dir manchmal selbst im Weg? |
| Entscheidungen | Wie triffst du Entscheidungen, und wie sollen dir Agenten Optionen vorlegen? |
| Arbeitsbeziehung mit Agenten | Wie viel sollen Agenten selbst erledigen, und wann sollen sie lieber nachfragen? |
| Wichtige Beziehungen und Rollen | Welche Menschen und Rollen sind für dich gerade zentral, etwa Familie, Team, Verein, Kunden? |
| Werte und Haltung | Was ist dir wichtig, woran soll sich ein Agent im Zweifel orientieren? |

Zum Schluss: Lebt die Person in der Zeitzone `Europe/Berlin`? Wenn nicht, die richtige IANA-Zeitzone erfragen.

### 4. Zusammenfassen und bestätigen lassen

Zeige eine knappe Zusammenfassung pro Abschnitt. Übernimm Korrekturen. Schreibe erst nach einem klaren Ja.

### 5. Schreiben

- [[identity/me]] nach [[system/templates/identity/identity-record]]: `Current Truth` mit zwei bis vier Sätzen dauerhafter Wahrheit, `Core Identity` mit Beruf, Rollen und Werten. `updated` auf heute, Timeline-Eintrag „Ersteinrichtung.“.
- [[USER]] nach [[system/templates/core/bootstrap/user-context]]: jeder Abschnitt in der Ich-Form der Person, knapp und agentenrelevant. Ausführliches gehört nach [[identity/me]], nicht hierher. `updated` auf heute.
- Bei abweichender Zeitzone `default_timezone` in [[system/truth-systems/personalos]] anpassen.

### 6. Optional: erste Personen und Projekte

Frage, ob gleich ein bis drei wichtige Menschen oder laufende Vorhaben angelegt werden sollen. Wenn ja, lege sie mit [[system/templates/entities/person]] beziehungsweise [[system/templates/project]] an, nur mit dem, was gesagt wurde, und verlinke sie unter „Wichtige Beziehungen und Rollen“ in [[USER]]. Wenn nein, weitergehen.

### 7. Prüfen

```bash
python3 skills/pos-verify/scripts/run.py --files USER.md identity/me.md <weitere geänderte Dateien>
grep -rIl "Noch nicht ausgefüllt" USER.md identity/me.md
```

Behebe jeden `fail`. Übrig gebliebene „Noch nicht ausgefüllt“-Stellen sind nur erlaubt, wenn die Person die Frage übersprungen hat.

### 8. Sichern

Ist der Ordner noch kein Git-Repository, schlage `git init` vor. Committe die Einrichtung lokal mit einer kurzen Nachricht. Empfiehl ein **privates** Remote-Repository als Backup; angelegt oder gepusht wird nur auf ausdrücklichen Wunsch.

### 9. Abschluss

Sage in wenigen Sätzen, wie es weitergeht:

- „Halt fest, was wir heute gemacht haben“ sichert Kontext über [[skills/log/SKILL|log]].
- „Leg eine Aufgabe an …“ läuft über [[skills/task-manager/SKILL|task-manager]].
- Neue Informationen landen erst im Posteingang und werden dann dem richtigen Ort zugeordnet.
- Weitere Bereiche wie Finanzen, Gesundheit oder Content sind schon vorbereitet und füllen sich, sobald es etwas Dauerhaftes gibt.

## Output Format

- eingesetzter Name und Anrede,
- geänderte und neu angelegte Dateien,
- übersprungene Fragen,
- Ergebnis von `pos-verify`,
- ob lokal committet wurde.

## Anti-Patterns

- Alle Fragen auf einmal stellen oder ein langes Formular schicken.
- Antworten ausschmücken, bewerten oder Lücken mit Vermutungen füllen.
- Den Platzhalter von Hand ersetzen statt mit `set_owner.py`.
- Neue Ordner, Felder oder Profile anlegen, um Antworten unterzubringen.
- Sensible Daten abfragen, nur weil es dafür Bereiche gibt.

## Resources

- `scripts/set_owner.py` — setzt den Namen einmalig im ganzen System ein. Tests: `scripts/test_set_owner.py`.
- `filesystem` — schreibt [[USER]], [[identity/me]] und optionale erste Records.
- `shell` — führt Skript, Prüfungen und lokales Git aus.

## Change History

- **2026-10-18** | Geführte Ersteinrichtung angelegt.
