---
schema_version: pos-v1
id: "01a0aca7-b214-738f-9b72-d6eb079a0f0a"
type: owner-index
title: "Finance"
created: "2026-09-17"
updated: "2026-09-17"
index_scope: root
---

# Finance

## Purpose

Kanonischer Einstieg in Konten, Belege, Rechnungen, wiederkehrende Verpflichtungen, Kosten, Zeiten und Steuerdossiers.

## Ownership and Boundaries

Finanzdaten sind besonders sensibel. Binäre Belege können extern liegen, müssen aber durch nachvollziehbare Records referenziert bleiben.

## Navigation

Objektfamilien werden erst mit dem ersten echten Finance Record als Unterbereich angelegt.

- Konten und Zahlungsquellen: `finance/konten/`
- Wiederkehrende Verpflichtungen: `finance/recurring/`

## Maintenance

Secrets und vollständige Zahlungsdaten gehören nicht in Markdown. Rechtlich autoritative Buchungswahrheit bleibt beim jeweiligen Fachsystem.
