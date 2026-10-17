# PersonalOS Starter

Ein Gedächtnis für dich und deine KI-Agenten, gebaut aus einfachen Markdown-Dateien. Agenten wie Claude Code lesen es zu Beginn jeder Sitzung, damit sie wissen, wer du bist, woran du arbeitest und wie du arbeiten willst.

Dieser Starter enthält nur den Rahmen: Regeln, Datenmodell, Vorlagen, Prüfungen und Skills. Persönliche Inhalte sind keine drin. Die füllst du bei der Einrichtung im Gespräch mit deinem Agenten aus.

## Das brauchst du

- **Git** und **Python 3**, auf dem Mac meist schon vorhanden (`git --version`, `python3 --version`)
- einen KI-Agenten, der in einem Ordner arbeiten kann, zum Beispiel **Claude Code**
- optional **Obsidian**, um die Dateien bequem zu lesen und zu verlinken

## Einrichtung in vier Schritten

### 1. Eigene Kopie anlegen

Hol dir den Starter und mach ihn zu deinem eigenen Repository, ohne Verbindung zum Original:

```bash
git clone https://github.com/leons1809/PersonalOS-Starter.git PersonalOS
cd PersonalOS
rm -rf .git
git init
```

### 2. Agenten im Ordner starten

```bash
claude
```

### 3. Einrichtung starten

Schreib einfach:

> Richte mein PersonalOS ein.

Der Agent erkennt auch von selbst, dass das System noch nicht eingerichtet ist, und bietet es dir an.

### 4. Im Gespräch ausfüllen

Der Agent führt dich in etwa 15 Minuten durch ein paar Fragen, eine nach der anderen:

1. Name und wie du angesprochen werden willst. Er wird automatisch überall im System eingesetzt.
2. Was du machst, wie du arbeitest und Entscheidungen triffst.
3. Wie viel Agenten selbst erledigen sollen und wann sie fragen sollen.
4. Wichtige Menschen, Rollen und Werte.
5. Optional die ersten Personen und Projekte.

Jede Frage kannst du überspringen. Bevor etwas gespeichert wird, siehst du eine Zusammenfassung. Am Ende prüft der Agent alles und speichert die Einrichtung lokal mit Git.

## Danach

- **Backup:** Leg ein **privates** Repository an, etwa auf GitHub, und pushe dorthin. Dein PersonalOS enthält persönliche Informationen, also niemals öffentlich.
- **Alltag:** Sag deinem Agenten Dinge wie „Halt fest, was wir heute gemacht haben“ oder „Leg eine Aufgabe an …“. Er ordnet neue Informationen dem richtigen Ort zu.
- **Später ändern:** Alles bleibt normale Textdatei. Du kannst jederzeit sagen „Pass meine Arbeitsweise in USER an“ oder die Dateien direkt bearbeiten.

## Aufbau

| Ort | Inhalt |
|---|---|
| [AGENTS.md](AGENTS.md) | Einstieg für jeden Agenten |
| [USER.md](USER.md) | kompakter Steckbrief über dich |
| [INDEX.md](INDEX.md) | Übersicht aller Bereiche |
| `identity/`, `people/`, `companies/`, `projects/` … | deine Inhalte, anfangs leer |
| `system/` | Regeln, Datenmodell und Vorlagen |
| `skills/` | Abläufe wie `setup`, `log`, `task-manager` und `pos-verify` |

Integrationen wie Kalender, Aufgaben-Apps oder ein eigener Server sind nicht enthalten. Sie lassen sich später als eigene Module ergänzen.
