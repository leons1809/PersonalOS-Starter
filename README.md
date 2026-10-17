# PersonalOS Starter

Ein Markdown-basiertes Kontextsystem für dich und deine KI-Agenten. Dieser Starter enthält nur den Rahmen: Regeln, Datenmodell, Vorlagen, Prüfungen und Skills. Persönliche Inhalte sind keine enthalten.

## Erste Schritte

1. Den Platzhalter **Max Mustermann** (und kurz **Max**) überall durch deinen eigenen Namen ersetzen.
2. [USER.md](USER.md) und [identity/me.md](identity/me.md) ausfüllen, am besten zusammen mit deinem Agenten.
3. Den Ordner in Obsidian öffnen und einen Agenten wie Claude Code darin starten. Der Agent liest zuerst [AGENTS.md](AGENTS.md).
4. Nach Änderungen prüfen:

   ```bash
   python3 skills/pos-verify/scripts/run.py --changed-from git
   ```

## Aufbau

- [INDEX.md](INDEX.md) zeigt alle Bereiche und wofür sie zuständig sind.
- `system/` enthält Regeln, Verträge, Datenmodell und Vorlagen.
- `skills/` enthält ausführbare Abläufe, zum Beispiel `log`, `task-manager` und `pos-verify`.
- Alle anderen Ordner sind leer und füllen sich mit deinen eigenen Inhalten.

Integrationen wie Kalender, Notion oder ein eigener Server sind nicht enthalten und werden bei Bedarf als eigene Module ergänzt.
