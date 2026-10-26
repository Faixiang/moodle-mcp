#!/usr/bin/env python3
"""Probe a Moodle site before trusting any course-watch report.

Prints what the skill needs in order to adapt to this particular site:
site identity, Web Service health, sample courses, module-type census,
section naming (to infer week folders) and how many activities carry a due date.

Usage:
    python check_site.py --mcp-dir <moodle-mcp-dir>
    python check_site.py --mcp-dir <moodle-mcp-dir> --courses <id1>,<id2>

Requires: a moodle-mcp style server.py (loadable as a module) plus its config.json.
"""

import argparse
import collections
import json
import os
import sys

DEFAULT_MCP_DIR = os.environ.get("MOODLE_MCP_DIR", "")


def load_server(mcp_dir):
    if not mcp_dir:
        sys.exit("error: --mcp-dir or MOODLE_MCP_DIR is required")
    if not os.path.isfile(os.path.join(mcp_dir, "server.py")):
        sys.exit("error: %s does not contain server.py" % mcp_dir)
    if mcp_dir not in sys.path:
        sys.path.insert(0, mcp_dir)
    import server  # noqa: E402
    return server


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mcp-dir", default=DEFAULT_MCP_DIR)
    ap.add_argument("--courses", default="", help="comma separated course ids to census")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    server = load_server(args.mcp_dir)
    out = {}

    cfg = server.load_config()
    out["endpoint_url"] = cfg.get("url")

    # 1. site identity and web service health
    try:
        info = server.moodle_call("core_webservice_get_site_info", {})
        funcs = info.get("functions") or []
        out["site"] = {
            "url": cfg.get("url"),
            "sitename": info.get("sitename"),
            "release": info.get("release"),
            "user": info.get("username"),
            "userid": info.get("userid"),
            "functions": len(funcs),
            "can_query_assign": any(f.get("name", "").startswith("mod_assign_get_assignments") for f in funcs),
            "can_query_quiz": any(f.get("name", "").startswith("mod_quiz_get_") for f in funcs),
        }
    except Exception as e:
        sys.exit("site info failed — check token and that Web Service is enabled: %r" % (e,))

    # 2. courses
    try:
        courses = (server.list_courses(cfg=cfg) or {}).get("courses") or []
    except Exception:
        courses = []
    out["courses"] = [{"id": c.get("id"), "shortname": c.get("shortname"), "fullname": c.get("fullname")}
                      for c in courses]

    # 3. per-course census
    detail = {}
    ids = [int(x) for x in args.courses.split(",") if x.strip()] or [c["id"] for c in out["courses"][:8]]
    for cid in ids:
        try:
            sections = server.moodle_call("core_course_get_contents", {"courseid": cid}) or []
        except Exception as e:
            detail[cid] = {"error": repr(e)[:200]}
            continue
        mods = collections.Counter(m.get("modname") for s in sections for m in s.get("modules", []))
        assigns = [a for a in server.collect_assignments(courseids=[cid])]
        detail[cid] = {
            "sections": [s.get("name") for s in sections][:8],
            "modules": dict(mods),
            "assign_total": len(assigns),
            "assign_with_duedate": sum(1 for a in assigns if a.get("duedate")),
            "quiz_present": mods.get("quiz", 0),
            "turnitin_present": mods.get("turnitintooltwo", 0),
        }
    out["census"] = detail

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return

    s = out["site"]
    print("接口地址: %s" % out.get("endpoint_url"))
    print("站点: %s | Moodle %s | user=%s (id=%s) | 可用函数 %d" % (
        s["sitename"], s["release"], s["user"], s["userid"], s["functions"]))
    print("mod_assign 可用: %s | mod_quiz 可用: %s" % (s["can_query_assign"], s["can_query_quiz"]))
    print("课程数: %d" % len(out["courses"]))
    for c in out["courses"][:12]:
        print("  [%s] %s" % (c["id"], c["shortname"]))
    print("--- 课程结构抽样 ---")
    for cid, d in out["census"].items():
        if "error" in d:
            print("  %s: 读取失败 %s" % (cid, d["error"]))
            continue
        print("  %s: 章节样例=%s | assign=%d(有截止日 %d) | quiz=%d | turnitin=%d" % (
            cid, [x for x in d["sections"] if x][:5], d["assign_total"],
            d["assign_with_duedate"], d["quiz_present"], d["turnitin_present"]))
        print("      模块类型: %s" % d["modules"])
    print("--- 未暴露状态的类型: %s ---" % (
        sorted({k for d in detail.values() if "modules" in d for k in d["modules"]
                if k in ("turnitintooltwo", "quiz", "workshop")}) or "无"))


if __name__ == "__main__":
    main()
