#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle MCP Server (zero-dependency, stdio JSON-RPC 2.0)

Wraps the Moodle Web Service REST API as MCP tools, so an agent can read
courses, deadlines and course files without launching a browser.

Config: config.json next to this file
        {"url": "https://moodle.sfu.edu.hk", "token": "<wstoken>"}
        The MOODLE_URL / MOODLE_TOKEN environment variables override it.

Note: stdout carries JSON-RPC frames only; every log line goes to stderr.
"""

import sys
import os
import json
import time
import ssl
import datetime
import re
import urllib.request
import urllib.parse

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
PROTOCOL_VERSION = "2024-11-05"
SERVER_NAME = "moodle-mcp"
SERVER_VERSION = "1.3.0"


def log(msg):
    sys.stderr.write("[moodle-mcp] %s\n" % msg)
    sys.stderr.flush()


class MoodleError(Exception):
    pass


# ---------------------------------------------------------------- Config

def load_config():
    cfg = {
        "url": os.environ.get("MOODLE_URL", "https://moodle.sfu.edu.hk").strip(),
        "token": os.environ.get("MOODLE_TOKEN", "").strip(),
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                disk = json.load(f)
            for k in ("url", "token"):
                if disk.get(k):
                    cfg[k] = str(disk[k]).strip()
        except Exception as exc:
            log("config.json 读取失败: %s" % exc)
    return cfg


# ---------------------------------------------------------------- HTTP

def moodle_call(function, params=None, cfg=None):
    cfg = cfg or load_config()
    token = cfg.get("token") or ""
    if not token:
        raise MoodleError(
            "未配置 Token。请编辑 %s 写入 {\"url\":\"...\",\"token\":\"<wstoken>\"}，"
            "或设置环境变量 MOODLE_TOKEN。获取方式见 README。" % CONFIG_PATH
        )
    endpoint = cfg["url"].rstrip("/") + "/webservice/rest/server.php"

    pairs = [
        ("wstoken", token),
        ("wsfunction", function),
        ("moodlewsrestformat", "json"),
    ]
    for key, val in (params or {}).items():
        if val is None:
            continue
        if isinstance(val, (list, tuple)):
            if not val:
                continue
            for i, item in enumerate(val):
                if isinstance(item, dict):
                    for k2, v2 in item.items():
                        pairs.append(("%s[%d][%s]" % (key, i, k2), str(v2)))
                else:
                    pairs.append(("%s[%d]" % (key, i), str(item)))
        elif isinstance(val, dict):
            for k2, v2 in val.items():
                pairs.append(("%s[%s]" % (key, k2), str(v2)))
        elif isinstance(val, bool):
            pairs.append((key, "1" if val else "0"))
        else:
            pairs.append((key, str(val)))

    body = urllib.parse.urlencode(pairs).encode("utf-8")
    req = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "MoodleMCP/1.0",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=40, context=ssl.create_default_context()) as resp:
            raw = resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        raise MoodleError("HTTP %s: %s" % (exc.code, exc.reason))
    except Exception as exc:
        raise MoodleError("网络请求失败: %s" % exc)

    time.sleep(0.15)

    raw = raw.strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except Exception:
        raise MoodleError("响应非 JSON，可能是登录页或防火墙拦截: %s" % raw[:300])

    if isinstance(data, dict) and (data.get("exception") or data.get("errorcode")):
        raise MoodleError("%s: %s" % (data.get("errorcode", "error"), data.get("message", "")))
    return data


# ---------------------------------------------------------------- Links and weeks

def with_token(url, cfg=None):
    """Append the token to a pluginfile URL so a script can fetch it directly."""
    if not url:
        return url
    if "token=" in url:
        return url
    cfg = cfg or load_config()
    tok = (cfg.get("token") or "").strip()
    if not tok:
        return url
    sep = "&" if "?" in url else "?"
    return url + sep + "token=" + urllib.parse.quote(tok)


def normalize_week(value):
    """Coerce 6 / '6' / 'Week 6' to an int; the all keyword stays 'all'."""
    if value is None:
        return None
    s = str(value).strip().lower()
    if s in ("all", "*", "全部", "所有"):
        return "all"
    m = re.search(r"\d+", s)
    return int(m.group(0)) if m else None


def section_week(name):
    """Read the week number from a section name, or None when unnumbered.

    Understands "Week 6", "Unit 4", "第 6 周 / 第 6 週" and number-prefixed
    topics such as "6. Sorting" or "6) Sorting". Overview blocks ("General",
    "Project Submission", "Online Judge Questions") carry no number and
    therefore return None: they can never share a slot with a real week, so a
    topic titled after its own index is never mistaken for a positional week.
    """
    s = str(name or "")
    for pat in (r"week\s*0*(\d+)", r"(?:unit|lesson|chapter|topic)\s*0*(\d+)",
                r"第\s*0*(\d+)\s*[周週]"):
        m = re.search(pat, s, re.I)
        if m:
            return int(m.group(1))
    m = re.search(r"^\s*0*(\d+)\s*[\.\)、:：]\s*\S", s)
    if m:
        return int(m.group(1))
    return None


def section_label(week, name):
    """Folder name for a section: Week N when numbered, its own title otherwise."""
    if week is not None:
        return "Week %s" % week
    safe = re.sub(r'[\\/:*?"<>|]+', " ", str(name or "")).strip()
    return safe or "Unsorted"


def assign_attachments(course_id, cfg=None):
    """Assignment brief attachments keyed by assign id: {assign_id: [file...]}."""
    try:
        raw = moodle_call("mod_assign_get_assignments", {"courseids": [int(course_id)]}, cfg=cfg)
    except MoodleError as exc:
        log("作业附件查询失败: %s" % exc)
        return {}
    out = {}
    for course in (raw.get("courses") or []):
        for a in (course.get("assignments") or []):
            files = []
            seen = set()
            for key in ("introattachments", "introfiles"):
                for f in (a.get(key) or []):
                    fn = f.get("filename")
                    if not fn or fn in seen:
                        continue
                    seen.add(fn)
                    files.append({
                        "filename": fn,
                        "filesize": f.get("filesize"),
                        "modified": ts2s(f.get("timemodified")),
                        "url": f.get("fileurl"),
                    })
            if files:
                out[a.get("id")] = files
    return out


def week_manifest(course_id, week, cfg=None):
    """Collect the downloadable files of one week, or of every week."""
    cid = int(course_id)
    data = moodle_call("core_course_get_contents", {"courseid": cid}, cfg=cfg)
    att = assign_attachments(cid, cfg=cfg)
    wanted = normalize_week(week)
    result = []
    for sec in (data or []):
        sec_name = sec.get("name") or ("Section %s" % sec.get("section"))
        w = section_week(sec_name)
        if wanted != "all" and w != wanted:
            continue
        files = []
        for mod in (sec.get("modules") or []):
            for cnt in (mod.get("contents") or []):
                if cnt.get("type") == "file" and cnt.get("fileurl"):
                    files.append({
                        "filename": cnt.get("filename") or "unnamed.bin",
                        "filesize": cnt.get("filesize"),
                        "modified": ts2s(cnt.get("timemodified")),
                        "url": with_token(cnt.get("fileurl"), cfg),
                        "from": mod.get("name"),
                    })
            if mod.get("modname") == "assign":
                for f in att.get(mod.get("instance"), []):
                    item = dict(f)
                    item["url"] = with_token(item.get("url"), cfg)
                    item["from"] = mod.get("name")
                    files.append(item)
        if not files and wanted == "all":
            continue
        result.append({"week": w, "label": section_label(w, sec_name),
                       "section": sec_name, "files": files})
    return result


def fetch_to_file(url, dest):
    """Download to dest and return (bytes written, content_type)."""
    req = urllib.request.Request(url, headers={"User-Agent": "MoodleMCP/1.1"})
    tmp = dest + ".part"
    with urllib.request.urlopen(req, timeout=180, context=ssl.create_default_context()) as resp:
        ctype = resp.headers.get("Content-Type") or ""
        first = resp.read(65536)
        if first[:1] == b"{" and b'"error' in first[:200]:
            raise MoodleError("下载被拒，站点返回：%s" % first[:200].decode("utf-8", "replace"))
        with open(tmp, "wb") as fh:
            fh.write(first)
            while True:
                chunk = resp.read(262144)
                if not chunk:
                    break
                fh.write(chunk)
    os.replace(tmp, dest)
    return os.path.getsize(dest), ctype


# ---------------------------------------------------------------- Tool functions

def ts2s(epoch):
    if not epoch:
        return "未设置"
    try:
        return datetime.datetime.fromtimestamp(int(epoch)).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(epoch)


def now_epoch():
    return int(time.time())


def get_site_info(cfg=None):
    return moodle_call("core_webservice_get_site_info", cfg=cfg)


def list_courses(cfg=None):
    info = get_site_info(cfg=cfg)
    userid = info.get("userid")
    courses = moodle_call("core_enrol_get_users_courses", {"userid": userid}, cfg=cfg)
    out = []
    for c in courses or []:
        out.append({
            "id": c.get("id"),
            "shortname": c.get("shortname"),
            "fullname": c.get("fullname"),
            "visible": c.get("visible"),
            "enddate": ts2s(c.get("enddate")) if c.get("enddate") else None,
        })
    return {"userid": userid, "username": info.get("username"), "courses": out}


def collect_assignments(cfg=None, courseids=None):
    if courseids is None:
        courseids = [c["id"] for c in list_courses(cfg=cfg)["courses"]]
    if not courseids:
        return []
    raw = moodle_call("mod_assign_get_assignments", {"courseids": courseids}, cfg=cfg)
    result = []
    for course in (raw.get("courses") or []):
        for a in (course.get("assignments") or []):
            result.append({
                "course_id": course.get("id"),
                "course": course.get("fullname") or course.get("shortname"),
                "assign_id": a.get("id"),
                "name": a.get("name"),
                "duedate": a.get("duedate") or 0,
                "cutoffdate": a.get("cutoffdate") or 0,
                "allowsubmissionsfromdate": a.get("allowsubmissionsfromdate") or 0,
                "intro": (a.get("intro") or "")[:200],
            })
    return result


def submission_state(assign_id, cfg=None):
    """Return (status, timemodified, graded); status is submitted / draft / new."""
    try:
        st = moodle_call("mod_assign_get_submission_status", {"assignid": assign_id}, cfg=cfg)
    except MoodleError as exc:
        return ("unknown(%s)" % str(exc).split(":")[0], 0, None)
    last = st.get("lastattempt") or {}
    sub = last.get("submission") or {}
    status = sub.get("status") or "new"
    graded = bool((last.get("gradingstatus") or "").lower().startswith("graded"))
    return (status, sub.get("timemodified") or 0, graded)


def quiz_report(cfg=None, courseids=None):
    """Quiz attempt state per quiz: submitted / in_progress / not_attempted.

    Unlike turnitintooltwo, quizzes do expose per-user attempts through
    mod_quiz_get_user_attempts, so a quiz is no longer a blind spot: an empty
    attempt list means never opened, a finished attempt means handed in.
    """
    courses = list_courses(cfg=cfg)
    if courseids is None:
        courseids = [c["id"] for c in courses["courses"]]
    names = {c["id"]: (c["shortname"] or c["fullname"]) for c in courses["courses"]}
    userid = courses.get("userid") or get_site_info(cfg=cfg).get("userid")
    now = now_epoch()
    rows = []
    for cid in courseids:
        try:
            data = moodle_call("mod_quiz_get_quizzes_by_courses", {"courseids": [int(cid)]}, cfg=cfg)
        except MoodleError as exc:
            log("测验清单查询跳过课程 %s: %s" % (cid, exc))
            continue
        for q in (data.get("quizzes") or []):
            qid = q.get("id")
            row = {
                "course": names.get(cid) or cid,
                "course_id": cid,
                "quiz_id": qid,
                "name": q.get("name"),
                "max_grade": q.get("grade"),
                "opens_at": ts2s(q.get("timeopen")) if q.get("timeopen") else None,
                "closes_at": ts2s(q.get("timeclose")) if q.get("timeclose") else None,
                "time_limit_min": int((q.get("timelimit") or 0) // 60) or None,
                "attempts_allowed": q.get("attempts"),
            }
            try:
                att = moodle_call("mod_quiz_get_user_attempts",
                                  {"quizid": qid, "userid": userid, "status": "all"}, cfg=cfg)
            except MoodleError as exc:
                row.update({"state": "unverifiable", "detail": str(exc)[:120],
                            "attempts": None, "best_grade": None, "finished_at": None})
                rows.append(row)
                continue
            attempts = att.get("attempts") or []
            finished = [a for a in attempts if (a.get("state") or "") == "finished"]
            running = [a for a in attempts if (a.get("state") or "") in ("inprogress", "overdue")]
            if finished:
                state = "submitted"
            elif running:
                state = "in_progress"
            elif attempts:
                state = "attempt_abandoned"
            else:
                state = "not_attempted"
            best = max([a.get("sumgrades") or 0 for a in finished], default=None)
            row.update({
                "state": state,
                "attempts": len(attempts),
                "best_grade": best,
                "finished_at": ts2s(max([a.get("timefinish") or 0 for a in finished], default=0)) if finished else None,
            })
            close_ts = q.get("timeclose") or 0
            row["expired"] = bool(close_ts and close_ts < now and state != "submitted")
            rows.append(row)
    return rows


def recent_updates(cfg=None, days=7, courseids=None):
    courses = list_courses(cfg=cfg)
    if courseids is None:
        courseids = [c["id"] for c in courses["courses"]]
    since = now_epoch() - int(days) * 86400
    rows = []
    for cid in courseids:
        try:
            data = moodle_call("core_course_get_updates_since", {"courseid": cid, "since": since}, cfg=cfg)
        except MoodleError as exc:
            log("更新查询跳过课程 %s: %s" % (cid, exc))
            continue
        for u in (data.get("instances") or []):
            for upd in (u.get("updates") or []):
                rows.append({
                    "course_id": cid,
                    "component": u.get("contextlevel") and u.get("name") or u.get("name"),
                    "name": upd.get("name"),
                    "timeupdated": upd.get("timeupdated"),
                    "itemurl": upd.get("url"),
                })
    rows.sort(key=lambda r: r.get("timeupdated") or 0, reverse=True)
    for r in rows:
        r["time_text"] = ts2s(r.get("timeupdated"))
    return rows


def pending_report(cfg=None, ahead_days=14, courseids=None):
    courses = list_courses(cfg=cfg)
    names = {c["id"]: c["fullname"] for c in courses["courses"]}
    assigns = collect_assignments(cfg=cfg, courseids=courseids)
    now = now_epoch()
    horizon = now + int(ahead_days) * 86400
    items = []
    for a in assigns:
        status, modified, graded = submission_state(a["assign_id"], cfg=cfg)
        a["status"] = status
        a["graded"] = graded
        a["submitted"] = status == "submitted"
        a["course_name"] = names.get(a["course_id"]) or a["course"]
        due = a["duedate"]
        a["due_text"] = ts2s(due)
        if not a["submitted"]:
            if due and due < now:
                a["bucket"] = "overdue"
                a["days_left"] = int((due - now) // 86400)
            elif due and due <= horizon:
                a["bucket"] = "due_soon"
                a["days_left"] = int((due - now) // 86400)
            else:
                a["bucket"] = "open"
                a["days_left"] = None
        else:
            a["bucket"] = "done"
            a["days_left"] = None
        items.append(a)
    return items


# ---------------------------------------------------------------- Rendering

def render_digest(days=7, ahead_days=14, cfg=None):
    lines = []
    info = get_site_info(cfg=cfg)
    courses = list_courses(cfg=cfg)
    cids = [c["id"] for c in courses["courses"]]

    lines.append("# Moodle 课业简报")
    lines.append("")
    lines.append("- 站点：%s" % info.get("sitename"))
    lines.append("- 账号：%s" % info.get("username"))
    lines.append("- 生成时间：%s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    lines.append("- 课程数：%d" % len(cids))
    lines.append("")

    # 1. Recent additions
    lines.append("## 一、近 %d 天新增内容" % days)
    lines.append("")
    try:
        ups = recent_updates(cfg=cfg, days=days, courseids=cids)
    except MoodleError as exc:
        ups = []
        lines.append("> 取更新失败：%s" % exc)
        lines.append("")
    if ups:
        lines.append("| 课程 | 项目 | 更新时间 |")
        lines.append("|---|---|---|")
        name_map = {c["id"]: c["fullname"] for c in courses["courses"]}
        for u in ups[:60]:
            lines.append("| %s | %s | %s |" % (name_map.get(u["course_id"], u["course_id"]), u.get("name"), u["time_text"]))
    else:
        lines.append("> 无新增（或站点未开放 core_course_get_updates_since 权限）。")
    lines.append("")

    # 2/3. Assignments
    items = pending_report(cfg=cfg, ahead_days=ahead_days, courseids=cids)

    soon = [i for i in items if i["bucket"] == "due_soon"]
    overdue = [i for i in items if i["bucket"] == "overdue"]
    openitems = [i for i in items if i["bucket"] == "open"]
    done = [i for i in items if i["bucket"] == "done"]

    lines.append("## 二、未来 %d 天到期且未提交" % ahead_days)
    lines.append("")
    if soon:
        lines.append("| 课程 | 作业 | 截止 | 剩余 |")
        lines.append("|---|---|---|---|")
        for i in sorted(soon, key=lambda x: x["duedate"]):
            lines.append("| %s | %s | %s | %d 天 |" % (i["course_name"], i["name"], i["due_text"], i["days_left"]))
    else:
        lines.append("> 无临期未交作业。")
    lines.append("")

    lines.append("## 三、已过期仍未提交")
    lines.append("")
    if overdue:
        lines.append("| 课程 | 作业 | 截止 | 逾期 |")
        lines.append("|---|---|---|---|")
        for i in sorted(overdue, key=lambda x: x["duedate"], reverse=True):
            lines.append("| %s | %s | %s | %d 天 |" % (i["course_name"], i["name"], i["due_text"], abs(i["days_left"])))
    else:
        lines.append("> 无。")
    lines.append("")

    lines.append("## 四、未提交且无临期压力")
    lines.append("")
    if openitems:
        for i in sorted(openitems, key=lambda x: x["duedate"] or 9e18):
            lines.append("- %s ｜ %s ｜ 截止：%s" % (i["course_name"], i["name"], i["due_text"]))
    else:
        lines.append("> 无。")
    lines.append("")

    lines.append("## 五、统计")
    lines.append("")
    lines.append("- 已提交/已批改：%d" % len(done))
    lines.append("- 未提交合计：%d（临期 %d，逾期 %d，其他 %d）" % (
        len(soon) + len(overdue) + len(openitems), len(soon), len(overdue), len(openitems)))
    lines.append("")
    lines.append("> 局限：Turnitin(turnitintooltwo) 不在标准 Web Service 覆盖范围，需单独核对；quiz 状态见 moodle_quiz_status。")
    return "\n".join(lines)


# ---------------------------------------------------------------- Tool definitions

TOOLS = [
    {
        "name": "moodle_site_info",
        "description": "Validate the Moodle token and return site name, version, current user and the web-service functions the account may call (diagnostics).",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "moodle_list_courses",
        "description": "List every course the account is enrolled in (id, shortname, fullname).",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "moodle_recent_updates",
        "description": "Content added or updated in the last N days (assignments, resources, announcements), newest first.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "How many days to look back (default 7)", "default": 7},
                "course_ids": {"type": "array", "items": {"type": "integer"}, "description": "Restrict to these course ids; omit for all courses"},
            },
        },
    },
    {
        "name": "moodle_pending_assignments",
        "description": "Unsubmitted assignments split into due soon / overdue / no pressure, with deadline and days remaining.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ahead_days": {"type": "integer", "description": "Due-soon window in days (default 14)", "default": 14},
                "course_ids": {"type": "array", "items": {"type": "integer"}, "description": "Restrict to these course ids; omit for all courses"},
            },
        },
    },
    {
        "name": "moodle_weekly_digest",
        "description": "One-shot brief: recent additions + due soon + overdue + counts. Best starting point.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "How many days of additions to look back (default 7)", "default": 7},
                "ahead_days": {"type": "integer", "description": "Due-soon window in days (default 14)", "default": 14},
            },
        },
    },
    {
        "name": "moodle_quiz_status",
        "description": "Per-quiz attempt state from mod_quiz_get_user_attempts: submitted / in_progress / not_attempted / attempt_abandoned, with best grade. Closes the quiz blind spot left by the assignment API.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "course_ids": {"type": "array", "items": {"type": "integer"}, "description": "Restrict to these course ids; omit for all courses"},
                "only_pending": {"type": "boolean", "description": "Return only quizzes without a finished attempt (default false)", "default": False},
            },
        },
    },
    {
        "name": "moodle_course_files",
        "description": "Section structure and files of one course (filename, token-bearing download URL, modified time). Metadata only: nothing is downloaded.",
        "inputSchema": {
            "type": "object",
            "properties": {"course_id": {"type": "integer", "description": "Course id"}},
            "required": ["course_id"],
        },
    },
    {
        "name": "moodle_download_week",
        "description": "Download course files into a local folder: each section gets a Week N subfolder (unnumbered blocks keep their own title, e.g. Online Judge Questions), with assignment attachments included. Verifies sizes and skips files already present. Omit dest_root to list what would be downloaded.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "course_id": {"type": "integer", "description": "Course id"},
                "week": {"type": ["integer", "string"], "description": "Week number, e.g. 6 or \"Week 6\"; use all for every week"},
                "dest_root": {"type": "string", "description": "Local root folder, e.g. U:\\OneDrive\\...\\CIS221 Calculus; omit to list only"},
                "overwrite": {"type": "boolean", "description": "Reserved; files of identical size are skipped by default"},
            },
            "required": ["course_id", "week"],
        },
    },
]

TOOL_MAP = {t["name"]: t for t in TOOLS}


def call_tool(name, args):
    cfg = load_config()
    args = args or {}

    if name == "moodle_site_info":
        info = get_site_info(cfg=cfg)
        funcs = info.get("functions") or []
        text = "站点：%s\n账号：%s (userid=%s)\nMoodle 版本：%s\n可用函数数：%d\n\n%s" % (
            info.get("sitename"), info.get("username"), info.get("userid"),
            info.get("release") or "未知", len(funcs),
            "\n".join(sorted(f.get("name", "") for f in funcs)) or "（函数清单未返回，可能服务未包含具体函数白名单）",
        )
        return text

    if name == "moodle_list_courses":
        data = list_courses(cfg=cfg)
        lines = ["共 %d 门课程" % len(data["courses"]), ""]
        for c in data["courses"]:
            lines.append("- [%s] %s（ID %s）" % (c["shortname"], c["fullname"], c["id"]))
        return "\n".join(lines)

    if name == "moodle_recent_updates":
        rows = recent_updates(cfg=cfg, days=int(args.get("days", 7)), courseids=args.get("course_ids"))
        if not rows:
            return "近 %s 天无新增内容，或该站点未开放 core_course_get_updates_since。" % args.get("days", 7)
        return json.dumps(rows, ensure_ascii=False, indent=2)

    if name == "moodle_pending_assignments":
        items = pending_report(cfg=cfg, ahead_days=int(args.get("ahead_days", 14)), courseids=args.get("course_ids"))
        items = [i for i in items if not i["submitted"]]
        slim = [{
            "course": i["course_name"], "name": i["name"], "due": i["due_text"],
            "bucket": i["bucket"], "days_left": i["days_left"], "status": i["status"],
        } for i in items]
        if not slim:
            return "无未提交作业。"
        return json.dumps(slim, ensure_ascii=False, indent=2)

    if name == "moodle_weekly_digest":
        return render_digest(days=int(args.get("days", 7)), ahead_days=int(args.get("ahead_days", 14)), cfg=cfg)

    if name == "moodle_quiz_status":
        rows = quiz_report(cfg=cfg, courseids=args.get("course_ids"))
        if args.get("only_pending"):
            rows = [r for r in rows if r.get("state") != "submitted"]
        if not rows:
            return "无测验记录。"
        lines = ["| 课程 | 测验 | 状态 | 开放窗口 | 尝试 | 最佳分 | 交卷时间 |", "|---|---|---|---|---|---|---|"]
        label = {"submitted": "已交", "in_progress": "进行中", "not_attempted": "未开始",
                 "attempt_abandoned": "尝试已放弃", "unverifiable": "不可判定"}
        for r in rows:
            score = "-" if r.get("best_grade") is None else "%s/%s" % (r["best_grade"], r.get("max_grade"))
            state_txt = label.get(r["state"], r["state"])
            if r.get("expired"):
                state_txt += "（窗口已关闭）"
            window = "%s ~ %s" % ((r.get("opens_at") or "?"), (r.get("closes_at") or "?"))
            if r.get("time_limit_min"):
                window += " · %d 分钟" % r["time_limit_min"]
            lines.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["course"], r["name"], state_txt, window,
                "-" if r.get("attempts") is None else r["attempts"], score, r.get("finished_at") or "-"))
        return "\n".join(lines)

    if name == "moodle_course_files":
        cid = int(args["course_id"])
        data = moodle_call("core_course_get_contents", {"courseid": cid}, cfg=cfg)
        att = assign_attachments(cid, cfg=cfg)
        out = []
        for sec in data or []:
            sec_name = sec.get("name") or ("Section %s" % sec.get("section"))
            for mod in (sec.get("modules") or []):
                files = []
                for cnt in (mod.get("contents") or []):
                    if cnt.get("type") == "file":
                        files.append({
                            "filename": cnt.get("filename"),
                            "filesize": cnt.get("filesize"),
                            "modified": ts2s(cnt.get("timemodified")),
                            "url": with_token(cnt.get("fileurl"), cfg),
                        })
                if mod.get("modname") == "assign":
                    for f in att.get(mod.get("instance"), []):
                        item = dict(f)
                        item["url"] = with_token(item.get("url"), cfg)
                        files.append(item)
                out.append({
                    "section": sec_name,
                    "module": mod.get("name"),
                    "type": mod.get("modname"),
                    "instance": mod.get("instance"),
                    "url": mod.get("url"),
                    "files": files,
                })
        return json.dumps(out, ensure_ascii=False, indent=2)

    if name == "moodle_download_week":
        cid = int(args["course_id"])
        week_arg = args.get("week")
        dest_root = (args.get("dest_root") or "").strip()
        manifest = week_manifest(cid, week_arg, cfg=cfg)
        if not manifest:
            raise MoodleError("课程 %s 未找到周次 %s，可先用 moodle_course_files 查看现有周次。" % (cid, week_arg))

        if not dest_root:
            lines = ["# 待下载清单（未指定 dest_root，仅列举）", ""]
            for m in manifest:
                lines.append("## %s（%s）" % (m["label"], m["section"]))
                if not m["files"]:
                    lines.append("- 该周暂无可下载文件")
                for f in m["files"]:
                    lines.append("- %s ｜ %s B ｜ 来自 %s" % (f["filename"], f.get("filesize"), f.get("from")))
                lines.append("")
            return "\n".join(lines)

        report = []
        ok = skip = fail = 0
        for m in manifest:
            sub = os.path.join(dest_root, m["label"])
            os.makedirs(sub, exist_ok=True)
            report.append("## %s -> %s" % (m["label"], sub))
            if not m["files"]:
                report.append("- 该周暂无可下载文件")
            for f in m["files"]:
                dest = os.path.join(sub, f["filename"])
                expect = f.get("filesize")
                try:
                    if os.path.exists(dest) and expect and os.path.getsize(dest) == int(expect):
                        report.append("- SKIP %s（已存在且大小一致）" % f["filename"])
                        skip += 1
                        continue
                    size, ctype = fetch_to_file(f["url"], dest)
                    if expect and int(expect) != size:
                        report.append("- SIZE-MISMATCH %s ｜ 落地 %s B ｜ 期望 %s B" % (f["filename"], size, expect))
                        fail += 1
                    else:
                        report.append("- OK %s ｜ %s B ｜ %s" % (f["filename"], size, ctype))
                        ok += 1
                except Exception as exc:
                    fail += 1
                    report.append("- FAIL %s ｜ %s" % (f["filename"], exc))
            report.append("")
        report.append("合计：成功 %d，跳过 %d，失败 %d" % (ok, skip, fail))
        return "\n".join(report)

    raise MoodleError("未知工具：%s" % name)


# ---------------------------------------------------------------- JSON-RPC

def send(obj):
    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def handle(msg):
    method = msg.get("method")
    mid = msg.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0", "id": mid,
            "result": {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {"tools": {"listChanged": False}},
                "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            },
        }

    if method in ("notifications/initialized", "initialized"):
        return None

    if method == "ping":
        return {"jsonrpc": "2.0", "id": mid, "result": {}}

    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}}

    if method == "tools/call":
        params = msg.get("params") or {}
        name = params.get("name")
        args = params.get("arguments") or {}
        try:
            text = call_tool(name, args)
            return {
                "jsonrpc": "2.0", "id": mid,
                "result": {"content": [{"type": "text", "text": text}], "isError": False},
            }
        except MoodleError as exc:
            return {
                "jsonrpc": "2.0", "id": mid,
                "result": {"content": [{"type": "text", "text": str(exc)}], "isError": True},
            }
        except Exception as exc:
            log("tool %s 异常: %r" % (name, exc))
            return {
                "jsonrpc": "2.0", "id": mid,
                "result": {"content": [{"type": "text", "text": "内部错误: %s" % exc}], "isError": True},
            }

    if mid is None:
        return None
    return {"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "Method not found: %s" % method}}


def main():
    log("启动，配置：%s" % CONFIG_PATH)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except Exception:
            log("无法解析输入: %s" % line[:200])
            continue
        if isinstance(msg, list):
            for m in msg:
                resp = handle(m)
                if resp:
                    send(resp)
        else:
            resp = handle(msg)
            if resp:
                send(resp)


if __name__ == "__main__":
    main()
