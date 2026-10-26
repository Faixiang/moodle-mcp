# moodle-mcp

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · **Deutsch** · [Português](README.pt-BR.md) · [Русский](README.ru.md)

Ein MCP-Server (Model Context Protocol), der die **Web-Service-API von Moodle** als Werkzeuge bereitstellt, die ein KI-Agent direkt aufrufen kann. Kein Browser, kein Scraper, kein Klicken durch Seiten.

Moodle trägt die Lernplattformen unzähliger Hochschulen weltweit – einen allgemeinen MCP-Server dafür gab es bisher nicht. Dieses Projekt schließt die Lücke: eine einzige Datei, keine Abhängigkeiten, sechs Werkzeuge, nutzbar mit jeder Moodle-Instanz 3.x/4.x, in der Web Services aktiviert sind.

> Kein pip-Paket, kein node, kein Browser. Nur `python server.py`.

## Warum es das gibt

Ein Agent kann einen Syllabus lesen und Ihnen sagen, was morgen fällig ist – aber der Großteil der Kursinhalte liegt hinter einer Anmeldeschranke. Moodle mit einem Headless-Browser zu scrapen ist langsam, brüchig und löst oft den WAF aus. Moodle bringt bereits eine stabile, dokumentierte REST-API mit; gefehlt hat nur die MCP-Hülle.

Der Server nutzt ausschließlich die Python-Standardbibliothek (`urllib`, `json`, `ssl`) und spricht JSON-RPC 2.0 über stdio. Er lässt sich direkt an Claude Desktop, Cursor, Marvis oder jeden MCP-kompatiblen Client anbinden.

## Werkzeuge

| Werkzeug | Zweck | Parameter |
|---|---|---|
| `moodle_site_info` | Prüft das Token und liefert Instanzname, Moodle-Version, aktuellen Nutzer sowie die für das Konto freigegebenen Funktionen (Diagnose). | — |
| `moodle_list_courses` | Listet alle belegten Kurse mit ID, Kurzname und vollständigem Namen. | — |
| `moodle_recent_updates` | In den letzten N Tagen neu hinzugekommene oder geänderte Inhalte (Aufgaben, Dateien, Ankündigungen), neueste zuerst. | `days` (Standard 7), `course_ids` |
| `moodle_pending_assignments` | Nicht abgegebene Aufgaben, geteilt in **bald fällig** / **überfällig** / **entspannt**, mit Abgabetermin und verbleibenden Tagen. | `ahead_days` (Standard 14), `course_ids` |
| `moodle_course_files` | Abschnittsstruktur und Dateiliste eines Kurses, inklusive Direktlink und Änderungsdatum. **Liefert nur Metadaten, lädt keine Datei herunter.** | `course_id` |
| `moodle_weekly_digest` | Alles auf einmal: aktuelle Änderungen + bald fällig + überfällig + Statistik. Empfohlener Einstieg. | `days` (Standard 7), `ahead_days` (Standard 14) |

Alle Werkzeuge sind **schreibgeschützt**. Schnittstellen zum Abgeben, Belegen, Löschen oder Bearbeiten fehlen bewusst.

## Installation

### 1. Token besorgen

Moodle verlangt ein persönliches Zugriffstoken. Wählen Sie je nach Instanz:

**A. Weboberfläche (empfohlen, funktioniert auch mit SSO-Konten)**

1. In der Moodle-Instanz anmelden
2. Profilbild → *Einstellungen* → *Konto* → *Sicherheit* → *Zugangsschlüssel verwalten*
3. „Erstellen" wählen, Name `moodle-mcp`, Dienst *Moodle mobile web service*
4. Den erzeugten Schlüssel kopieren

**B. Skript über den Mobile-Dienst (nur wenn die Instanz lokale Passwörter speichert)**

```bash
python get_token.py
```

Das Skript tauscht die Zugangsdaten über `/login/token.php` und den Dienst `moodle_mobile_app` gegen ein Token und prüft es sofort. Das Passwort wird weder angezeigt noch protokolliert. Bei reinen SSO-Konten kommt `invalidlogin` zurück – dann bitte Variante A verwenden.

**C. Umgebungsvariablen**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. Konfiguration

`config.json` im selben Verzeichnis wie `server.py` anlegen:

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Umgebungsvariablen haben Vorrang vor der Konfigurationsdatei.

### 3. Server registrieren

Claude Desktop / Cursor (`mcp.json`):

```json
{
  "mcpServers": {
    "moodle": {
      "command": "python",
      "args": ["/absolute/path/to/moodle-mcp/server.py"]
    }
  }
}
```

In `args` gehört der absolute Pfad zu `server.py`. Bei mehreren Python-Versionen auf `command` den vollständigen Interpreterpfad setzen.

## Beispiel

> „Was ist diese Woche noch offen?"

Der Agent ruft `moodle_weekly_digest` auf und erhält eine direkt lesbare Übersicht:

```
## In den nächsten 7 Tagen fällig, nicht abgegeben
| Kurs | Aufgabe | Fällig | Verbleibend |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 Tage |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 Tage |

## Überfällig
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 Tage überfällig |

## Statistik
Abgegeben/bewertet: 51 ｜ Offen gesamt: 25 (bald fällig 4, überfällig 14, sonstige 7)
```

## Bekannte Einschränkungen

- **Turnitin (`turnitintooltwo`) und das `quiz`-Modul werden nicht abgedeckt.** Beide sind eigenständige Module ohne `mod_assign`-Semantik; Fristen dort bitte in der Weboberfläche prüfen.
- Aufgaben ohne gesetzte Frist erscheinen als „nicht gesetzt".
- Der Wochenbericht zählt nur **nicht abgegebene** Einträge; abgegebene, aber unbewertete Aufgaben fließen in die Statistik ein, erscheinen aber nicht in den Tabellen.
- Manche WAFs antworten auf aufeinanderfolgende Anfragen mit `502`. Der Server serialisiert bereits und wartet 150 ms zwischen den Aufrufen; tritt es dennoch auf, mit größerem Abstand erneut versuchen.
- Die Instanz muss Web Services aktiviert haben und das Konto die Berechtigung `webservice/rest:use` besitzen. Meist wird die vollständige Funktionsliste freigegeben, bei manchen Instanzen nur die Mobile-Teilmenge.

## Sicherheit

- Das Token ist ein **Geheimnis**. Nur in `config.json` oder Umgebungsvariablen ablegen, niemals committen; `.gitignore` schließt `config.json` und `get_token.log` bereits aus.
- `get_token.py` protokolliert das Passwort nicht, nur seine Länge, und liest es per `getpass`.
- Alle Werkzeuge sind schreibgeschützt: Selbst bei einem geleakten Token lassen sich damit keine Aufgaben ändern oder löschen. Im Zweifel den Schlüssel unter „Zugangsschlüssel verwalten" widerrufen.
- Keine Mitschnitte veröffentlichen – das `wstoken` steht im Request-Body.

## Kompatibilität

| Komponente | Details |
|---|---|
| Python | 3.8+ (nur Standardbibliothek) |
| MCP-Protokoll | `2024-11-05` |
| Moodle | 3.x / 4.x mit aktivierten Web Services und REST-Protokoll |
| Getestete Umgebung | Moodle 4.3.6, Konto mit 435 freigegebenen Funktionen (Vollzugriff) |

## Lizenz

MIT — siehe [LICENSE](LICENSE).
