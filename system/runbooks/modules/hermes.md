---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4e02e2d65b89"
type: runbook
title: "Hermes sicher anbinden"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# Hermes sicher anbinden

## Purpose

Hermes als optionale Laufzeit an die gemeinsame PersonalOS-Wahrheit anbinden.

## Trigger

Ein dauerhaft oder remote erreichbarer Agent wird benötigt.

## Preconditions

Kern und Synchronisation funktionieren; Schreibrechte und externe Wirkungen sind geklärt.

## Procedure

Zuerst lesend lokal testen, dann Pfade parametrisieren, Berechtigungen begrenzen und jede Automation separat freigeben.

## Verification

Hermes liest dieselben kanonischen Dateien und besitzt keine konkurrierende Memory-Schicht.

## Escalation

Bei Drift, fehlender Synchronisation oder unklaren Schreibrechten alle automatischen Läufe stoppen.

## Change History

- **2026-09-17** | Modul aktiviert.
