---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4dfe2807050e"
type: runbook
title: "PersonalOS sichern und versionieren"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# PersonalOS sichern und versionieren

## Purpose

Änderungen nachvollziehbar machen und Wiederherstellung ermöglichen.

## Trigger

Das PersonalOS enthält erhaltenswerten eigenen Kontext.

## Preconditions

Sensible Dateien, Secrets, Binärdaten und externe Datensätze sind klassifiziert. Der einzige automatische Git-Writer ist bestimmt.

## Procedure

Ignore-Regeln prüfen, lokales Git testen, genau einen automatischen Git-Writer festlegen, privates Remote bewusst wählen und zusätzliche Backups für nicht versionierte Daten einrichten. Andere Hosts führen keinen parallelen automatischen Commit- oder Push-Prozess für dasselbe Repository aus.

## Verification

Eine Testdatei kann aus Git und ein ausgeschlossener Datentyp aus dem separaten Backup wiederhergestellt werden. Es ist nachgewiesen, dass nur der festgelegte Host automatisch zu Git schreibt.

## Escalation

Bei versehentlich versionierten Secrets Veröffentlichung stoppen, Zugangsdaten rotieren und Historie gezielt bereinigen.

## Change History

- **2026-09-17** | Modul aktiviert.
