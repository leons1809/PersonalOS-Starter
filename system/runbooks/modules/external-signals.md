---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4e01f9db3b3a"
type: runbook
title: "Externe Signale verarbeiten"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# Externe Signale verarbeiten

## Purpose

Externen Input nachvollziehbar in belastbaren PersonalOS-Kontext überführen.

## Trigger

Eine Nachricht, ein Call, eine E-Mail oder ein Feed enthält möglicherweise relevanten Kontext.

## Preconditions

Quelle, Zeitpunkt, Beteiligte und Datenschutzgrenze sind bekannt.

## Procedure

Quelle datenschutzgerecht erfassen oder referenzieren. Für einen lokalen Call [[skills/analyse-call/SKILL|analyse-call]] verwenden. Bei angebundenen Quellen zusätzlich Zugriff, Abrufgrenze und Fehlerverhalten dokumentieren. Erst danach Aussagen extrahieren, Unsicherheit markieren, Ziel-Owner bestimmen und Änderungen kontrolliert bestätigen.

## Verification

Input, Interpretation und übernommene Wahrheit bleiben unterscheidbar und rückverfolgbar.

## Escalation

Bei sensiblen Daten, unklarer Zustimmung oder widersprüchlichen Aussagen nicht automatisch übernehmen.

## Change History

- **2026-09-17** | Modul aktiviert.
