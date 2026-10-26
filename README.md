# moodle-mcp

**English** · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português (BR)](README.pt-BR.md) · [Русский](README.ru.md)

An MCP (Model Context Protocol) server that exposes the **Moodle Web Service API** as tools an AI agent can call directly — no browser, no scraping, no clicking.

Moodle powers a large share of universities and colleges worldwide, yet it had no general-purpose MCP server. This project fills that gap: one zero-dependency Python file, six tools, works against any Moodle 3.x/4.x site with Web Services enabled.

```
No pip install. No node. No browser. Just python server.py.
```

---

## Why

Agents are good at reading a syllabus and telling you what is due tomorrow — but most course content sits behind a login wall. Scraping Moodle with a headless browser is slow, brittle, and tends to trip WAFs. Moodle already ships a stable, documented REST API; it just needed an MCP wrapper.

This server uses only the Python standard library (`urllib`, `json`, `ssl`). It speaks JSON-RPC 2.0 over stdio, so it drops into Claude Desktop, Cursor, Marvis, or any MCP-compatible client.

## Tools

| Tool | What it does | Arguments |
|---|---|---|
| `moodle_site_info` | Validate the token, return site name, Moodle version, current user and the list of web-service functions the account may call (diagnostics). | — |
| `moodle_list_courses` | List every enrolled course with id, shortname and fullname. | — |
| `moodle_recent_updates` | Content added or updated in the last N days (assignments, files, announcements), newest first. | `days` (default 7), `course_ids` |
| `moodle_pending_assignments` | Unsubmitted assignments, split into **due soon** / **overdue** / **no pressure**, with deadline and days remaining. | `ahead_days` (default 14), `course_ids` |
| `moodle_course_files` | Section structure and file list for one course, including direct download URLs and modified times. **Metadata only — nothing is downloaded.** | `course_id` |
| `moodle_weekly_digest` | The one-shot summary: recent additions + due-soon + overdue + counts. Best starting point. | `days` (default 7), `ahead_days` (default 14) |

All tools are **read-only**. There is deliberately no submit / enrol / delete / edit endpoint.

## Install

### 1. Get a token

Moodle needs a personal access token. Pick whichever works for your site:

**A. Web UI (recommended, works with SSO accounts)**

1. Log in to your Moodle site
2. Avatar → *Preferences* → *Account* → *Security* → *Manage access keys*
3. *Create*, name it `moodle-mcp`, service = *Moodle mobile web service*
4. Copy the token

**B. Mobile-app service via script (only if your site has local passwords)**

```bash
python get_token.py
```

Walks through `/login/token.php` with the `moodle_mobile_app` service and validates the result. Password input is hidden and never logged. If your account is SSO-only this will return `invalidlogin` — use method A instead.

**C. Environment variables**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. Configure

Create `config.json` next to `server.py`:

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Environment variables take precedence over the file.

### 3. Register the server

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

Use an absolute path to `server.py`. If you have several Python installs, point `command` at the full interpreter path.

## Example

> "What do I still owe this week?"

The agent calls `moodle_weekly_digest` and gets back a ready-to-read brief:

```
## Due in the next 7 days, not submitted
| Course | Item | Deadline | Left |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 days |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 days |

## Overdue
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 days late |

## Totals
Submitted/graded: 51 | Outstanding: 25 (due soon 4, overdue 14, other 7)
```

## Known limitations

- **Turnitin (`turnitintooltwo`) and `quiz` activities are not covered.** They are separate modules without `mod_assign` semantics; their deadlines must be checked in the web UI.
- Assignments with no deadline configured show as `not set`.
- Weekly digest reports *unsubmitted* items only. Submitted-but-ungraded items appear under the counts, not the tables.
- Rate limiting: some sites run a WAF that returns `502` on rapid consecutive requests. The server serialises calls and pauses 150 ms between them; if you still get `502`, back off and retry.
- Requires the site to have Web Services enabled and your account to hold the `webservice/rest:use` capability. Many admins grant the full function list; some restrict it to the mobile-only subset.

## Security notes

- The token is a **credential**. Store it in `config.json` or an environment variable, never in a repo. `.gitignore` already excludes `config.json` and `get_token.log`.
- `get_token.py` never logs the password — only its length — and reads it with `getpass`.
- Every tool is read-only by design, so a leaked token cannot modify or delete coursework through this server. Revoke it from *Manage access keys* if it leaks.
- Do not publish captured HTTP traffic: `wstoken` appears in the request body.

## Compatibility

| Component | Notes |
|---|---|
| Python | 3.8+ (standard library only) |
| MCP protocol | `2024-11-05` |
| Moodle | 3.x / 4.x with Web Services + REST protocol enabled |
| Verified against | Moodle 4.3.6, full 435-function grant |

## License

MIT — see [LICENSE](LICENSE).
