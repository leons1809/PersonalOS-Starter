---
schema_version: pos-v1
id: "01a0aca7-b214-738f-9b72-d6e82ba5558a"
type: owner-index
title: "Daily"
created: "2026-09-17"
updated: "2026-09-17"
index_scope: root
---

# Daily

## Purpose

Einstieg in den zeitlichen Querschnitt aus Day Records, Activity Contributions und optionalen Journal Entries.

## Ownership and Boundaries

Daily zeigt, was an einem Tag geschah. Es ersetzt weder Domain Truth noch Actions, Interactions oder Automation Receipts.

## Navigation

Tageskontext liegt unter `daily/<year>/<date>/` und wird nach Datum gefunden.

## Maintenance

Es werden nur Tage materialisiert, für die tatsächlich relevanter Activity oder Journal Context existiert.
