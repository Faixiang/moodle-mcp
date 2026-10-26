<div align="center">

<img src="docs/banner.svg" alt="moodle-mcp" width="100%">

# moodle-mcp

### Your Moodle, as tools an AI agent can actually use

Read assignments, deadlines and course files straight out of the Moodle Web Service API — no browser, no scraping, no clicking.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="Zero dependencies">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>

<p>
<b>English</b> ·
<a href="README.zh-CN.md">简体中文</a> ·
<a href="README.zh-TW.md">繁體中文</a> ·
<a href="README.ja.md">日本語</a> ·
<a href="README.ko.md">한국어</a> ·
<a href="README.es.md">Español</a> ·
<a href="README.fr.md">Français</a> ·
<a href="README.de.md">Deutsch</a> ·
<a href="README.pt-BR.md">Português</a> ·
<a href="README.ru.md">Русский</a>
</p>

</div>

## Preview 🖥️

<img src="docs/preview.svg" alt="Example MCP session" width="100%">

---

## Why this exists 🎯

Moodle powers a large share of universities and colleges worldwide, yet it had no general-purpose MCP server. Scraping it with a headless browser is slow, brittle and tends to trip WAFs — while Moodle itself already ships a stable, documented REST API.

This project is the missing wrapper: **one zero-dependency Python file, six read-only tools**, working against any Moodle 3.x/4.x site with Web Services enabled.

```text
No pip install. No node. No browser. Just python server.py.
```

## Features ✨

### Data retrieval
- **Deadline-aware** — assignments split into *due soon*, *overdue* and *no pressure*, with days remaining computed for you
- **Weekly digest** — recent additions + deadlines + overdue in a single call, formatted for direct reading
- **Course files** — section structure and file lists with direct download URLs and modified times, metadata only, nothing downloaded
- **Diagnostics built in** — `moodle_site_info` reports site version, account identity and which functions your token may actually call

### Engineering
- **Zero dependencies** — Python standard library only (`urllib`, `json`, `ssl`), so nothing pollutes your runtime
- **Single file** — copy `server.py` anywhere; no package layout, no build step
- **stdio JSON-RPC 2.0** — drops into Claude Desktop, Cursor, Marvis or any MCP-compatible client
- **WAF-friendly** — serialised calls with a 150 ms gap, because hammering Moodle gets you `502`
- **Read-only by design** — no submit, enrol, edit or delete endpoint exists in the code

## Tools 🧰

| Tool | What it does | Arguments |
|---|---|---|
| `moodle_site_info` | Validate the token, return site name, Moodle version, current user and the list of web-service functions the account may call (diagnostics). | — |
| `moodle_list_courses` | List every enrolled course with id, shortname and fullname. | — |
| `moodle_recent_updates` | Content added or updated in the last N days (assignments, files, announcements), newest first. | `days` (default 7), `course_ids` |
| `moodle_pending_assignments` | Unsubmitted assignments, split into **due soon** / **overdue** / **no pressure**, with deadline and days remaining. | `ahead_days` (default 14), `course_ids` |
| `moodle_course_files` | Section structure and file list for one course, including direct download URLs and modified times. **Metadata only — nothing is downloaded.** | `course_id` |
| `moodle_weekly_digest` | The one-shot summary: recent additions + due-soon + overdue + counts. Best starting point. | `days` (default 7), `ahead_days` (default 14) |

## Requirements 📦

| Component | Notes |
|---|---|
| Python | 3.8+ (standard library only) |
| MCP protocol | `2024-11-05` |
| Moodle | 3.x / 4.x with Web Services + REST protocol enabled |
| Account | Holds the `webservice/rest:use` capability |
| Verified against | Moodle 4.3.6, full 435-function grant |

## Quick start 🚀

### ① Get a token

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

Walks through `/login/token.php` with the `moodle_mobile_app` service and validates the result. Password input is hidden and never logged. If your account is SSO-only this returns `invalidlogin` — use method A instead.

**C. Environment variables**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② Configure

Create `config.json` next to `server.py` (or copy `config.example.json`):

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

Environment variables take precedence over the file.

### ③ Register the server

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

### ④ Verify

Ask your client to call `moodle_site_info`. A working setup returns the site name, Moodle version and your user record. If it fails, jump to [Troubleshooting](#troubleshooting-).

## Configuration reference ⚙️

| Key | Type | Required | Description |
|---|---|---|---|
| `url` / `MOODLE_URL` | string | yes | Base URL of your Moodle site, no trailing path |
| `token` / `MOODLE_TOKEN` | string | yes | Personal access token from *Manage access keys* |
| `config.json` | file | optional | Read from the directory containing `server.py` |

Precedence: environment variables → `config.json` → error.

## Usage examples 💬

> "What do I still owe this week?"

The agent calls `moodle_weekly_digest` and gets back a ready-to-read brief:

```text
## Due in the next 7 days, not submitted
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | 3 days |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 days |

## Overdue
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 days late |

## Totals
Submitted/graded: 51 | Outstanding: 25 (due soon 4, overdue 14, other 7)
```

Other prompts that work well:

| Prompt | Tool it lands on |
|---|---|
| "What new material appeared in CIS225 this week?" | `moodle_recent_updates` |
| "List the files in GER405, don't download anything" | `moodle_course_files` |
| "Which of my courses have nothing overdue?" | `moodle_pending_assignments` |
| "Is my token still valid?" | `moodle_site_info` |

## Troubleshooting 🤔

<details>
<summary><b><code>invalidlogin</code> when running get_token.py</b></summary>

Your account authenticates through SSO/OIDC only, so `/login/token.php` has no local password to check. Use method A — create the token in *Manage access keys* instead.
</details>

<details>
<summary><b><code>502</code> or connection reset during a call</b></summary>

The site's WAF is rate-limiting you. This server already serialises calls and pauses 150 ms between them; if you still hit it, wait a few minutes and retry, and avoid firing several tools in parallel.
</details>

<details>
<summary><b>Tools return empty lists</b></summary>

Check three things: Web Services and the REST protocol are enabled site-wide; the account has `webservice/rest:use`; and any `course_ids` filter you passed is correct. Run `moodle_site_info` first — if the function list is short, the admin restricted your grant to the mobile subset.
</details>

<details>
<summary><b>Turnitin or quiz deadlines are missing</b></summary>

Expected. `turnitintooltwo` and `quiz` are separate modules without `mod_assign` semantics, so this server does not see them. Check those in the web UI.
</details>

<details>
<summary><b>A deadline shows as "not set"</b></summary>

The teacher never configured a due date for that assignment. There is nothing to compute; the item still appears so you don't forget it exists.
</details>

<details>
<summary><b>Garbled characters in Windows terminals</b></summary>

Output is UTF-8. In legacy consoles run `chcp 65001` first, or use Windows Terminal.
</details>

## Security notes 🔒

- The token is a **credential**. Store it in `config.json` or an environment variable, never in a repo. `.gitignore` already excludes `config.json` and `get_token.log`.
- `get_token.py` never logs the password — only its length — and reads it with `getpass`.
- Every tool is read-only by design, so a leaked token cannot modify or delete coursework through this server. Revoke it from *Manage access keys* if it leaks.
- Do not publish captured HTTP traffic: `wstoken` appears in the request body.

## Compatibility ✅

| Client / Platform | Status |
|---|---|
| Claude Desktop | Works (stdio server entry) |
| Cursor | Works (`mcp.json`) |
| Marvis | Works (MCP registry) |
| Any MCP client | Works — plain JSON-RPC 2.0 over stdio |
| Windows / macOS / Linux | Works — no platform-specific code |

## Roadmap 🗺️

- [ ] Turnitin and quiz deadline support where the API allows
- [ ] Optional local cache to cut repeated round-trips on large course lists
- [ ] Pagination hints for accounts enrolled in very many courses
- [ ] Submission *status* details (graded / feedback available) — still read-only
- [ ] Non-Moodle LMS adapters sharing the same tool surface

## Contributing 🤝

Issues and pull requests are welcome. The whole server is one file — read `server.py` top to bottom in a few minutes.

- Keep the zero-dependency rule: standard library only.
- Keep every tool read-only.
- Never commit `config.json`, tokens or captured traffic.
- If you add a tool, document it in the Tools table and in every language's README.

## Feedback 📢

Bugs and feature requests: [open an issue](https://github.com/Faixiang/moodle-mcp/issues).

## License 📝

MIT — see [LICENSE](LICENSE).
