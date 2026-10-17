---
schema_version: pos-v1
id: 01a0cb06-d142-79ab-996c-a622aaa0470d
type: rule
title: "Minimal Record Content"
created: 2026-09-22
updated: 2026-09-22
lifecycle: active
decision_refs: ["[[decisions/2026/2026-09-17-adopt-personalos-foundation]]"]
---

# Minimal Record Content

## Rule

Ein Record enthält **nur die Information, die ihm gehört und die dauerhaft gilt**. Alles, was einem anderen Owner gehört, sich laufend ändert oder nur den Anlass des Schreibens erklärt, bleibt draußen.

Die Prüffrage vor jedem Satz lautet: **Ist das hier die Wahrheit dieses Records, oder erkläre ich nur, wie ich darauf gekommen bin?**

## Scope and Trigger

Gilt für jeden Write in PersonalOS, durch Menschen wie durch Agenten. Besonders beim Verarbeiten von Gesprächen: Dort fällt viel Kontext an, der beim Verstehen hilft, aber nicht in den Record gehört.

## Required Behavior

**Nicht in einen Record gehören:**

1. **Fremde Wahrheit.** Termine gehören in den Kalender, Ergebnisse und Tabellen zu ihrem Fachsystem, Dateien zum Asset-Owner. Im Record steht höchstens der Zeiger, siehe [[system/truth-systems/index]].
2. **Volatiles.** Was in vier Wochen falsch ist, wird nicht als Wahrheit geschrieben. Wenn es doch festgehalten werden muss, dann ausdrücklich als datierte Momentaufnahme.
3. **Die Umstände der Entstehung.** Warum ein Termin nicht passte, wer gerade keine Zeit hatte, welche Alternativen verworfen wurden. Das Ergebnis zählt, nicht der Weg dorthin. Bewusste Entscheidungen mit Begründung gehören nach `decisions/`.
4. **Kontext, der einem anderen Owner gehört.** Eine Beobachtung über eine Person gehört in ihren Record, nicht in das Projekt, in dem sie zufällig auftauchte.
5. **Vorsorgliche Struktur.** Keine leeren Abschnitte, keine Platzhalter, keine Felder „für später“.

**Beispiel.** In ein Trainingsprojekt gehört: erste Einheit Freitag oder Samstag, in der Wettkampfwoche keine mehr, eine Verletzung als Einschränkung. Nicht hinein gehören: ein einzelner Termin am Donnerstag, ein ausgefallenes Training am Mittwoch und ein Abendessen — alles Kalenderwahrheit.

**Faustregel:** Wenn eine Aufzählung anfängt, wie ein Wochenplan auszusehen, ist es Kalenderwahrheit und kein Record.

## Exceptions

- **Datierte Momentaufnahmen** sind erlaubt, wenn sie ausdrücklich als solche gekennzeichnet sind und der Zeitpunkt dabeisteht, etwa ein Kontostand oder ein Tabellenplatz in einem Tageseintrag.
- **Tagesrecords und Journale** dürfen Verlauf und Stimmung enthalten. Dort ist der Zeitpunkt selbst der Owner.
- **Entscheidungen** dürfen verworfene Alternativen nennen, das ist dort Teil der Wahrheit.
- Fehlt der richtige Owner noch, darf die Information vorübergehend nach `inbox/` und wird von dort verarbeitet.

## Verification

Beim Prüfen eines Writes: Lässt sich ein Satz streichen, ohne dass die Aussage des Records verloren geht, gehört er nicht hinein. Enthält ein Record Daten, für die ein anderes System zuständig ist, wird er gekürzt und auf den Owner verwiesen.

## Change History

- **2026-09-22** | Regel formuliert. Dateiname und Titel nach der Konvention englisch, Inhalt deutsch.
