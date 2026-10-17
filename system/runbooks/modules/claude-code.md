---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4dffada732d5"
type: runbook
title: "Claude Code mit dem PersonalOS verbinden"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# Claude Code mit dem PersonalOS verbinden

## Purpose

Claude Code als austauschbaren Agenten an dieselbe Kontextwahrheit anbinden.

## Trigger

Claude Code soll im PersonalOS arbeiten.

## Preconditions

Der Agent kann den lokalen Ordner lesen und respektiert die Bootstrap-Reihenfolge.

## Procedure

Root-Kontext laden, Aufgabe planen, Owner bestimmen, kontrolliert ändern und den zuständigen Check ausführen.

## Verification

Werkzeugspezifische Hinweise widersprechen keiner Systemregel und erzeugen keine zweite Wahrheit.

## Escalation

Bei Abweichungen gilt die PersonalOS-Systemwahrheit, nicht eine duplizierte Adapterregel.

## Change History

- **2026-09-17** | Modul aktiviert.
