---
schema_version: pos-v1
id: "01a0aca7-b241-70f1-9bf3-4e056ca203e0"
type: runbook
title: "Mehrere Hosts sicher verbinden"
created: "2026-09-17"
updated: "2026-09-17"
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
system_refs: ["[[system/contracts/normative-system-architecture]]"]
---

# Mehrere Hosts sicher verbinden

## Purpose

Mehrere Laufzeiten an dieselbe PersonalOS-Wahrheit anbinden.

## Trigger

Ein zweiter Rechner oder dauerhafter Host soll das System lesen oder bearbeiten.

## Preconditions

Synchronisation, Konfliktverhalten, Berechtigungen und Backup sind getestet. Der aktuelle automatische Git-Writer ist bekannt.

## Procedure

1. Alle Hosts und ihren benötigten Lese- oder Schreibzugriff inventarisieren.
2. Pro PersonalOS-Repository genau einen automatischen Git-Writer festlegen.
3. Weitere Hosts lesend anbinden oder den Arbeitsbestand über einen getrennten Dateitransport bereitstellen.
4. Auf allen weiteren Hosts automatische Commit-, Pull-, Merge- und Push-Prozesse deaktiviert lassen.
5. Konflikt-, Offline- und Wiederherstellungsverhalten mit einer Testkopie prüfen.
6. Automatische Prozesse erst nach erfolgreicher Prüfung für den echten Bestand zulassen.

Ein Writer-Wechsel beginnt mit dem Stopp des bisherigen Writers. Danach werden letzter Commit, Remote-Stand, offene Änderungen und Dateisynchronisation abgeglichen. Der neue Writer startet erst, wenn der alte Host nachweislich nicht mehr automatisch schreibt.

## Verification

Alle Hosts sehen denselben bestätigten Stand. Genau ein automatischer Git-Writer ist aktiv, ein Konflikt kann ohne Datenverlust gelöst werden und ein Writer-Wechsel ist getestet.

## Escalation

Bei ungeklärtem Drift alle automatischen Git-Writes stoppen und einen kanonischen Stand festlegen.

## Change History

- **2026-09-17** | Modul aktiviert.
