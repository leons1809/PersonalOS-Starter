---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4e00e8997e0e"
type: runbook
title: "Codex mit dem PersonalOS verbinden"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# Codex mit dem PersonalOS verbinden

## Purpose

Codex kontrolliert auf die gemeinsame Kontextschicht zugreifen lassen.

## Trigger

Codex soll im PersonalOS lesen oder arbeiten.

## Preconditions

Der Workspace zeigt auf den PersonalOS-Ordner und die Root-Bootstrap-Dateien sind vorhanden.

## Procedure

Zuerst AGENTS, INDEX, USER, SOUL und system/index lesen lassen; danach den zuständigen Owner und die passende Prüfung bestimmen.

## Verification

Codex nennt vor einer Änderung Quelle, Ziel-Owner und Verifikation.

## Escalation

Bei widersprüchlichem Kontext nicht raten, sondern den Owner prüfen oder den Nutzer fragen.

## Change History

- **2026-09-17** | Modul aktiviert.
