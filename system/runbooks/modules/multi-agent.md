---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4e041a40b02b"
type: runbook
title: "Mehrere Agenten koordinieren"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# Mehrere Agenten koordinieren

## Purpose

Agentenarbeit teilen, ohne widersprüchliche Wahrheiten oder Schreibkonflikte zu erzeugen.

## Trigger

Eine Aufgabe soll von mehreren Agenten bearbeitet werden.

## Preconditions

Scope, Owner, Abhängigkeiten und Schreibflächen sind vorab geklärt.

## Procedure

Arbeit in unabhängige Einheiten zerlegen, Quellen mitgeben, Ergebnisse prüfen und nur kontrolliert in den kanonischen Owner übernehmen.

## Verification

Jede dauerhafte Aussage besitzt nach der Zusammenführung genau einen Owner und einen nachvollziehbaren Ursprung.

## Escalation

Bei überlappenden Schreibflächen oder widersprüchlichen Ergebnissen serialisieren und menschlich entscheiden.

## Change History

- **2026-09-17** | Modul aktiviert.
