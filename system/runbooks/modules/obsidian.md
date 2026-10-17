---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4e0634e1371c"
type: runbook
title: "Obsidian als Oberfläche verbinden"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# Obsidian als Oberfläche verbinden

## Purpose

Den PersonalOS-Ordner in Obsidian sichtbar machen, ohne eine zweite Wahrheit zu erzeugen.

## Trigger

Obsidian soll als Editor und Navigator genutzt werden.

## Preconditions

Der Kern funktioniert bereits als normaler lokaler Ordner.

## Procedure

Eine Kopie als Vault öffnen, Links prüfen und Plugins nur einzeln nach echtem Bedarf ergänzen.

## Verification

Dateien bleiben außerhalb von Obsidian lesbar und Agenten greifen auf denselben Ordner zu.

## Escalation

Bei Plugin-Abhängigkeiten zuerst prüfen, ob die Funktion mit Markdown und vorhandenen Regeln lösbar ist.

## Change History

- **2026-09-17** | Modul aktiviert.
