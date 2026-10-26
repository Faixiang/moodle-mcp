#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle MCP Server (zero-dependency, stdio JSON-RPC 2.0)

用途：把 Moodle Web Service REST API 包成 MCP 工具，供 Agent 直接调用，
      无需启动浏览器。

配置：同目录 config.json
      {"url": "https://your-moodle.example.com", "token": "<wstoken>"}
      或用环境变量 MOODLE_URL / MOODLE_TOKEN 覆盖。

注意：stdout 只输出 JSON-RPC 帧，所有日志写 stderr。
"""

import sys
import os
import json
import time
import ssl
import datetime
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
SERVER_VERSION = "1.1.0"


def log(msg):
    sys.stderr.write("[moodle-mcp] %s\n" % msg)
    sys.stderr.flush()


class MoodleError(Exception):
    pass


# ---------------------------------------------------------------- 配置

def load_config():
    cfg = {
        "url": os.environ.get("MOODLE_URL", "").strip(),
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
    site = (cfg.get("url") or "").strip()
    if not site:
        raise MoodleError(
            "未配置 Moodle 站点地址。请编辑 %s 写入 "
            "{\"url\":\"https://your-moodle.example.com\",\"token\":\"<wstoken>\"}，"
            "或设置环境变量 MOODLE_URL。" % CONFIG_PATH
        )
    endpoint = site.rstrip("/") + "/webservice/rest/server.php"

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


# ---------------------------------------------------------------- 工具函数

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
    """返回 (status, timemodified, graded)。status: submitted / draft / new"""
    try:
        st = moodle_call("mod_assign_get_submission_status", {"assignid": assign_id}, cfg=cfg)
    except MoodleError as exc:
        return ("unknown(%s)" % str(exc).split(":")[0], 0, None)
    last = st.get("lastattempt") or {}
    sub = last.get("submission") or {}
    status = sub.get("status") or "new"
    graded = bool((last.get("gradingstatus") or "").lower().startswith("graded"))
    return (status, sub.get("timemodified") or 0, graded)


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


# ---------------------------------------------------------------- 渲染

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

    # 1. 新增
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

    # 2/3. 作业
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
    lines.append("> 局限：Turnitin(turnitintooltwo) 与 quiz 模块不在 mod_assign API 覆盖范围，需单独核对。")
    return "\n".join(lines)


# ---------------------------------------------------------------- 工具定义

TOOLS = [
    {
        "name": "moodle_site_info",
        "description": "校验 Moodle Token 并返回站点信息与当前账号可用的 Web Service 函数清单（用于诊断权限）。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "moodle_list_courses",
        "description": "列出当前账号已选的全部课程（课程ID、简称、全称）。",
        "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False},
    },
    {
        "name": "moodle_recent_updates",
        "description": "列出最近 N 天内课程新增/更新的内容（作业、资源、公告等），按时间倒序。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "回溯天数，默认 7", "default": 7},
                "course_ids": {"type": "array", "items": {"type": "integer"}, "description": "限定课程ID，省略则全部"},
            },
        },
    },
    {
        "name": "moodle_pending_assignments",
        "description": "列出未提交作业并按临期/逾期/无压力分类，含截止时间与剩余天数。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "ahead_days": {"type": "integer", "description": "临期判定窗口天数，默认 14", "default": 14},
                "course_ids": {"type": "array", "items": {"type": "integer"}, "description": "限定课程ID，省略则全部"},
            },
        },
    },
    {
        "name": "moodle_weekly_digest",
        "description": "一次性生成课业简报：近 N 天新增 + 临期未交 + 逾期未交 + 统计。这是最常用的汇总工具。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "description": "新增回溯天数，默认 7", "default": 7},
                "ahead_days": {"type": "integer", "description": "临期窗口天数，默认 14", "default": 14},
            },
        },
    },
    {
        "name": "moodle_course_files",
        "description": "列出指定课程的章节结构与课件文件（文件名、下载直链、修改时间），不下载文件。",
        "inputSchema": {
            "type": "object",
            "properties": {"course_id": {"type": "integer", "description": "课程ID"}},
            "required": ["course_id"],
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

    if name == "moodle_course_files":
        cid = int(args["course_id"])
        data = moodle_call("core_course_get_contents", {"courseid": cid}, cfg=cfg)
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
                            "url": cnt.get("fileurl"),
                        })
                out.append({
                    "section": sec_name,
                    "module": mod.get("name"),
                    "type": mod.get("modname"),
                    "url": mod.get("url"),
                    "files": files,
                })
        return json.dumps(out, ensure_ascii=False, indent=2)

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
