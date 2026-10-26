---
name: moodle-course-watch
description: Watch a Moodle course end to end on any school's site — detect newly published Assignment/Tutorial activities, mirror missing week folders into a local course directory, report which activities are still unsubmitted, and give a professional walkthrough of downloaded lecture notes and assignment briefs with key points graded automatically (spoken to the user in chat, no report file), plus an optional exam-notes deliverable. Use when the user asks for a weekly course check, or says any trigger phrase in any language — EN: anything new in this course this week / download Week N / what have I not submitted / what does this handout cover / make me revision notes; 简体: 看下这门课这周有没有新东西 / 补下载 Week N / 我哪些作业没交 / 这份讲义讲了什么 / 帮我做重点笔记 / 课件补下载 / 讲义速览 / 复习重点整理; 繁體: 看下這門課這週有沒有新東西 / 補下載 Week N / 我哪些作業沒交 / 這份講義講了什麼 / 幫我做重點筆記 / 課件補下載 / 講義速覽 / 複習重點整理.
---

# Moodle Course Watch

A portable course watch for anyone on any Moodle site: four read-only jobs (new-activity detection, missing-week
download, unsubmitted-activity listing, professional walkthrough of the week's material with key points graded) plus one optional deliverable —
assembled 重点笔记 / revision outline for whoever actually wants to study from the files. Nothing is ever submitted,
edited or uploaded to Moodle.

It is deliberately **not turnkey**: every school's Moodle differs, so the profile below has to be filled in by the
user before the first run. Treat that step as part of the skill, not as setup friction to skip.

## Trigger phrases, by language

The same five jobs, phrased in whichever language the user writes in. Match on intent, not on exact strings.

| Job | English | 简体 | 繁體 |
|---|---|---|---|
| New activities | anything new this week / any new coursework posted | 看下这门课这周有没有新东西 / 有没有新发布的作业 | 看下這門課這週有沒有新東西 / 有沒有新發布的作業 |
| Missing-week download | download Week 6 / grab the Week 7 files | 补下载 Week 6 / 把第 7 周的文件下下来 | 補下載 Week 6 / 把第 7 週的檔案下載下來 |
| Submission status | what haven't I submitted / which are still open | 我哪些作业没交 / 还有哪些没交 | 我哪些作業沒交 / 還有哪些沒交 |
| File walkthrough | what does this handout cover / walk me through these slides | 这份讲义讲了什么 / 这几份课件讲了什么 | 這份講義講了什麼 / 這幾份課件講了什麼 |
| Exam notes | make me revision notes / build a key-points sheet | 帮我做重点笔记 / 整理复习重点 | 幫我做重點筆記 / 整理複習重點 |

Reply in the language the user used. Keep file names, activity titles and Moodle terms in their original form
when quoting them.

## Setup gate — do not skip

This skill must not assume any particular university. Moodle deployments differ in hostname, token policy, module naming, section naming and rate limiting. **Before the first real run on a new site, stop and adapt.** A skill that guesses the site's shape will silently report "no new work" all semester.

Ask the user, and record the answers in `site-profile.md` next to this file — copy it from
`site-profile.template.md` first. **No `site-profile.md`, no run.** If the user opens this skill on a site they have
never profiled, the correct first action is to fill that table, not to run Step 1.

## File layout

```
moodle-course-watch/
  SKILL.md                    this file
  site-profile.template.md    blank profile to copy → site-profile.md (user-specific, do not ship)
  scripts/check_site.py       site probe: identity, functions, module census, week naming, duedate coverage
  scripts/submission_status.py  submission state per activity (reuses local moodle-mcp server.py)
```


| Question | Why it matters |
|---|---|
| Site root URL? | Everything hangs off `https://<host>`; do not guess from a course name |
| How is the Web Service token issued? | `/login/token.php` with the `moodle_mobile_app` service, or a manually created token under 管理存取金鑰 / Preferences → Security keys, or OAuth2/OIDC where a plain token may be impossible |
| Is the Web Service actually enabled? | A blocked site answers `invalidtoken`/service disabled; SSO-only accounts often cannot mint one at all |
| Course id for the target course? | Take it from `core_enrol_get_users_courses`, never from a URL guess |
| Local course directory and week-folder naming? | `Week 6`, `W6`, `Week06`, `Topic 6` — mirror what the user already has |
| Which activities count as coursework? | Some sites use `assign` for everything, others use `turnitintooltwo`, `quiz`, `workshop`, custom plugins |
| Does the site rate-limit? | Aggressive WAFs return 502 on burst POSTs; keep calls serial, ~0.15 s apart |

Run `scripts/check_site.py --mcp-dir <dir>` and hand the output to the user: it prints site name, Moodle version, function count, sample courses, module-type census for selected courses, section names (to infer week naming) and how many activities actually carry a `duedate`. Only after that table is filled should Step 1–3 run against a new site.

If the site cannot issue a token (pure SSO, Web Service disabled), say so plainly and fall back to `browser-agent` for page-level reading. Do not invent status.

## Prerequisites

- A local MCP server exposing Moodle Web Service tools. The reference implementation is `moodle-mcp`
  (7 tools: `moodle_site_info`, `moodle_list_courses`, `moodle_recent_updates`, `moodle_pending_assignments`,
  `moodle_weekly_digest`, `moodle_course_files`, `moodle_download_week`), pointed at by `MOODLE_MCP_DIR`.
- Download links must be `pluginfile.php?forcedownload=1&token=<token>`. A `pluginfile.php` URL without a token
  returns JSON, and `view.php?id=` needs a browser session — never treat either as a file.

## Step 1 — New activities

List the course's `assign` modules via `moodle_course_files` (or `core_course_get_contents` for raw `modname`),
and diff their `cmid` values against the baseline in `site-profile.md`. A new cmid is a new activity: report its
name and the section it sits in, then update the baseline. Never infer "new" from a name string — ids only.

## Step 2 — Mirror the missing week

Call `moodle_download_week` with `course_id`, `week` (number, `"Week N"` or `all`) and `dest_root`.
It creates the week folder, appends the token, verifies byte size and skips an existing file of identical size.
Report what was new, skipped or failed. If the user's existing folders use another naming scheme, pass the
matching week value and keep their convention rather than creating a parallel one.

## Step 3 — Submission status

```
python scripts/submission_status.py --courses <id1>,<id2> --mcp-dir <dir>
python scripts/submission_status.py --courses <id> --pattern "assignment|tutorial" --json
```

It prints `submitted` / `draft` / `new` plus `graded` and last-modified time per activity. Default name filter is
`(?i)assignment|tutorial`; adjust it in `site-profile.md` when the school names coursework differently.
Unsubmitted means any status other than `submitted`. A blank `duedate` is common — report it as 未设置, never invent one.

## Step 4 — Professional walkthrough with graded key points

After a download, read every file and report its content **to the user in the conversation**. This is a briefing, not a
deliverable: no summary file, no report document, nothing written to disk. Write a file only when the user asks for one
(Step 5) or explicitly asks for a report.

Register: professional and precise. Use the course's own terminology, attribute claims to where they appear in the
document, do not replace definitions with metaphors and do not use chatty framing ("basically it's about…"). The
user is a lecturer and an AI/ICT student — brief them as a peer, not as a beginner.

For each file, always cover these five parts, in this order:

1. **文件定位** — file name, week, type (lecture notes / tutorial sheet / assignment brief), page or slide count, and
   what section of the course it belongs to.
2. **内容讲述** — what the document actually says: its structure, the topics in sequence, what each section establishes
   and what it concludes with. For an assignment brief: the deliverable, the number and weighting of parts, the
   submission format and the stated deadline. Concrete, not impressionistic.
3. **重点划分 (always automatic — never ask whether to do it)** — grade every key item and say why it sits at that level:
   - **必记** — definitions, theorems, formulas together with their conditions of validity, anything the assessment
     will test directly.
   - **理解** — derivations, the reasoning behind a method, why a condition is required.
   - **了解** — motivation, historical context, illustrative variants.
   Present as a compact list or table, highest grade first, so the user can see the weighting at a glance rather than
   re-reading the file.
4. **衔接关系** — what the file assumes from the previous week, and what the pending assignment or the next file
   builds on from it, when that is visible in the material.
5. **待确认** — anything unreadable: scrambled formula layers, missing figures, truncated exports. State it plainly
   instead of paraphrasing a formula that could not be parsed.

Length follows the material, not a word count: a two-page brief gets a few lines, a forty-slide lecture gets a
structured list. Never pad and never truncate a 必记 item to save space.

Math handling: extract the text layer first, read scrambled pages visually page by page, and quote formulas as
formulas with their conditions — never describe an unread formula in prose or reconstruct one from memory.

## Step 5 — Optional exam notes

Some users want 重点笔记 / 复习提纲 / cheat sheet rather than a summary. Offer it, do not impose it.
When asked, produce one Markdown file (convert to PDF only if requested) with: definition table, formula table
with conditions of validity, worked-example steps, common mistakes, and a five-minute recall list at the end.
Output path is the user's choice; default to the same week folder, named `<week> 重点笔记.md`.
Never write this file during a routine check.

## Blind spots to state, never hide

- Turnitin (`turnitintooltwo`) and `quiz` submission states are not exposed by the standard Web Service.
  The activity is visible, the status is not. Say it is unverifiable instead of marking it 已交 or 未交.
- Custom plugins (workshop, custom assignment types) may or may not appear under `mod_assign_get_assignments`;
  verify with a module census before promising coverage.
- `core_course_get_updates_since` is not in every site's mobile-service whitelist; rely on module ids.
