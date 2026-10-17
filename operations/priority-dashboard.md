---
schema_version: pos-v1
id: 01a0251c-9ee7-7315-a87d-b8c885d2ca93
type: view-record
title: "Priority Dashboard"
created: 2026-08-21
updated: 2026-10-18
lifecycle: active
canonical_system_ref: "[[system/truth-systems/personalos]]"
authority_scope: pointer
view_kind: dashboard
derivation_mode: generated
source_owner_refs: ["[[operations/actions/index]]", "[[operations/attention-triggers/index]]"]
---

# Priority Dashboard

## Purpose

Morgentaugliche, dynamische Prioritätssicht über kanonische Actions, Attention Trigger und relevante Owner. Diese Datei ist kein Task-Speicher: Sie besitzt keine Checkboxen, keine unabhängige Completion und keinen eigenen Action-Lifecycle.

## Source Owners

Kanonische Ausführungswahrheit: [[operations/actions/index]]. Neubewertung ohne aktuelle Action: [[operations/attention-triggers/index]]. Keine temporäre manuelle Steuerung hinterlegt. Project-, Domain-, Deadline- und Evidenzwahrheit verbleibt bei den jeweils verlinkten Ownern.

## Derivation

Automatische Präzedenz: wirksame explizite Overrides → echte Deadlines/Zusagen im rollierenden Sieben-Tage-Fenster → explizite Critical-/High-Priorität und tatsächlich laufende Arbeit → Project-Impact → weiche Targets als Tie-Breaker → Opportunities. Freitext-Cadences beeinflussen das Ranking nicht.

### Manueller Control

Kein manueller Override aktiv. Die folgenden Punkte sind generierte Empfehlungen.

### Aktueller Fokus

- Keine belastbare aktuelle Fokus-Action aus den kanonischen Records ableitbar.

### Nächste sieben Tage

- Keine zusätzliche Action im rollierenden Fenster bis 2026-10-24.

### 30-Tage-Lebens- und Reisegates

- Kein zusätzliches persönliches Gate bis 2026-11-17 außerhalb des Hauptfokus.

### Kunden-, Cashflow- und Waiting-Risiken

- Keine im relevanten Horizont fällige externe Rückmeldung, Cashflow-Prüfung oder Neubewertung.

### Admin-Batch

- Routinebelege werden gesammelt und erst im Monatsendfenster als gemeinsamer Buchungs-Batch eingeblendet.

### Stale Review

- Keine zusätzliche stale oder dringende Action außerhalb des Hauptfokus.

## Freshness

Generiert am `2026-10-18T01:09:07+02:00` · Zeitzone `Europe/Berlin` · Rebuild-Grund `manual` · Source-Digest `3000ab8743594d9411b97dcba9525ac0d59eea865c9f924e1deda27e7bccd30a`.

Expliziter Refresh nach Prioritätsänderung: `python3 skills/priority-dashboard/scripts/rebuild.py --reason manual-priority-change`. Nach Action-/Trigger-/Owner-Änderung: derselbe Befehl mit `--reason operational-state-change`. Zusätzlich läuft täglich ein Service-Host-Rebuild vor 06:00; es gibt keinen Realtime-Watcher.

## Limitations

Die Sicht kann nur vorhandene, aktuelle kanonische Records priorisieren. Ideen, Freitext-Cadences oder vermutete Arbeit werden nicht in Actions umgedeutet. `due` bleibt eine echte Frist; `target` ist nur ein weiches Planungsdatum und erzeugt allein keinen Fokus. Kalendertermine begrenzen reale Kapazität, werden hier aber nicht als zweite Taskliste gespiegelt. Alte überfällige Actions bleiben im Stale Review sichtbar. Änderungen an Completion, Lifecycle, Deadline oder Project State erfolgen ausschließlich beim jeweiligen Owner.
