#!/usr/bin/env python3
"""Report submission status of Moodle activities for selected courses.

Reuses a local moodle-mcp style server.py (collect_assignments + submission_state),
so no extra dependency is needed. Course ids are never hard-coded.

Usage:
    python submission_status.py --mcp-dir <moodle-mcp-dir> --courses <id1>,<id2>
    python submission_status.py --courses <id> --pattern "assignment|tutorial"
    python submission_status.py --courses <id> --json

Environment:
    MOODLE_MCP_DIR   directory holding server.py + config.json (fallback for --mcp-dir)
"""

import argparse
import json
import os
import re
import sys

DEFAULT_MCP_DIR = os.environ.get("MOODLE_MCP_DIR", "")


def load_server(mcp_dir):
    if not mcp_dir:
        sys.exit("error: --mcp-dir or MOODLE_MCP_DIR is required")
    if mcp_dir not in sys.path:
        sys.path.insert(0, mcp_dir)
    import server  # noqa: E402
    return server


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--courses", required=True, help="comma separated course ids")
    ap.add_argument("--pattern", default="assignment|tutorial",
                    help="case-insensitive regex on activity name; empty string keeps all")
    ap.add_argument("--mcp-dir", default=DEFAULT_MCP_DIR)
    ap.add_argument("--json", action="store_true", help="machine readable output")
    args = ap.parse_args()

    course_ids = [int(x) for x in args.courses.split(",") if x.strip()]
    rx = re.compile(args.pattern, re.I) if args.pattern else None

    server = load_server(args.mcp_dir)
    rows = server.collect_assignments(courseids=course_ids)

    items = []
    for a in rows:
        if rx and not rx.search(a["name"]):
            continue
        status, modified, graded = server.submission_state(a["assign_id"])
        items.append({
            "course_id": a["course_id"],
            "course": a.get("course", ""),
            "assign_id": a["assign_id"],
            "name": a["name"],
            "status": "graded" if graded else status,
            "raw_status": status,
            "graded": bool(graded),
            "due": server.ts2s(a["duedate"]),
            "due_epoch": a["duedate"],
            "modified": server.ts2s(modified),
        })

    pending = [i for i in items if i["status"] != "submitted"]

    if args.json:
        print(json.dumps({"total": len(items), "pending": pending, "all": items},
                         ensure_ascii=False, indent=2))
        return

    print("纳入活动 %d 个，未交 %d 个" % (len(items), len(pending)))
    for i in items:
        flag = "未交" if i["status"] != "submitted" else "已交"
        print("  [%s] %s | %s | 截止 %s | 最后改动 %s" % (
            flag, i["name"], i["status"], i["due"], i["modified"]))


if __name__ == "__main__":
    main()
