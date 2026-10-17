---
schema_version: pos-v1
id: 01a14c20-3c52-72fb-97d4-1bcf73953806
type: conversation-stream
title: "Direktnachrichten an den Agenten"
created: 2026-10-18
updated: 2026-10-18
stream_state: active
source_channel: agent
participant_refs: ["[[identity/me]]"]
---

# Direktnachrichten an den Agenten

## Current Truth

Herkunft für Angaben, die direkt im Chat mit dem eigenen Agenten gemacht werden. Records, die daraus entstehen, verweisen mit `evidence_refs` auf diesen Stream.

## Participants

- [[identity/me]]

## Coverage

Laufend. Der Chat-Verlauf selbst liegt beim jeweiligen Agenten, nicht im PersonalOS.

## Open Source Gaps

Der Chat-Verlauf ist nicht im PersonalOS archiviert.

## Owner Links

- [[operations/index]]

## Timeline

- **2026-10-18** | Conversation stream created.
