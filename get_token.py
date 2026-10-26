#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moodle token helper. Run it in a terminal yourself: the password never
passes through any AI conversation.

Usage:
    double-click run_get_token.bat in the same folder
    or: python get_token.py

Everything is written to get_token.log in the same folder (passwords are not
recorded), so a failed run can be diagnosed afterwards.

Flow:
    1. enter the site URL (default https://moodle.sfu.edu.hk)
    2. enter username / password (getpass, nothing echoed)
    3. call /login/token.php to exchange them for a wstoken
    4. on success write config.json, then verify with core_webservice_get_site_info
"""

import os
import sys
import json
import ssl
import getpass
import datetime
import urllib.parse
import urllib.request

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
LOG_PATH = os.path.join(HERE, "get_token.log")

CANDIDATE_SERVICES = ["moodle_mobile_app", "moodle_mobile_app_service", "SFU_Service"]


def log(msg, echo=True):
    line = "[%s] %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    if echo:
        print(msg)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass


def post(url, pairs):
    body = urllib.parse.urlencode(pairs).encode("utf-8")
    req = urllib.request.Request(
        url, data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 MoodleTokenHelper/1.1",
        },
    )
    with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
        return resp.read().decode("utf-8", "replace")


def try_service(base, username, password, service):
    url = base.rstrip("/") + "/login/token.php"
    raw = post(url, {"username": username, "password": password, "service": service})
    try:
        return json.loads(raw)
    except Exception:
        return {"error": "非 JSON 响应: %s" % raw[:300]}


def verify(url, token):
    endpoint = url.rstrip("/") + "/webservice/rest/server.php"
    body = urllib.parse.urlencode({
        "wstoken": token,
        "wsfunction": "core_webservice_get_site_info",
        "moodlewsrestformat": "json",
    }).encode("utf-8")
    req = urllib.request.Request(
        endpoint, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30, context=ssl.create_default_context()) as resp:
        raw = resp.read().decode("utf-8", "replace")
    data = json.loads(raw)
    if isinstance(data, dict) and data.get("exception"):
        return None, "%s: %s" % (data.get("errorcode"), data.get("message"))
    return data, None


def main():
    print("=" * 60)
    print("Moodle Token 获取助手")
    print("日志文件：%s" % LOG_PATH)
    print("=" * 60)
    log("=== 会话开始 ===")
    log("Python: %s" % sys.version.split()[0])
    log("工作目录: %s" % HERE)

    try:
        base = input("站点地址 [https://moodle.sfu.edu.hk]: ").strip() or "https://moodle.sfu.edu.hk"
        username = input("用户名（学号或邮箱）: ").strip()
        password = getpass.getpass("密码（输入时不显示）: ")
    except (EOFError, KeyboardInterrupt):
        log("[x] 输入被中断（EOF / Ctrl+C）。请交互式运行，不要用管道输入。")
        return

    log("站点: %s" % base)
    log("用户名: %s" % username)
    log("密码长度: %d（不记录内容）" % len(password))

    if not username or not password:
        log("[x] 用户名或密码为空，退出。")
        return

    token = None
    used_service = None
    attempts = []

    log("--- 开始尝试服务名 ---")
    for svc in CANDIDATE_SERVICES:
        try:
            res = try_service(base, username, password, svc)
        except urllib.error.HTTPError as exc:
            attempts.append("%s -> HTTP %s" % (svc, exc.code))
            log("  [x] %s -> HTTP %s" % (svc, exc.code))
            continue
        except Exception as exc:
            attempts.append("%s -> 网络错误 %s" % (svc, exc))
            log("  [x] %s -> 网络错误 %s" % (svc, exc))
            continue

        if res.get("token"):
            token = res["token"]
            used_service = svc
            log("  [√] %s 成功取得 token" % svc)
            break

        code = res.get("errorcode") or res.get("error")
        msg = res.get("error") or code
        attempts.append("%s -> %s" % (svc, msg))
        log("  [x] %s 失败：%s" % (svc, msg))

        if code == "invalidlogin":
            log("      账号或密码不正确，换服务名无意义，停止尝试。")
            break

    if not token:
        log("--- 结果：未取得 Token ---")
        for a in attempts:
            log("    %s" % a)
        log("排查方向：")
        log("  1. 账号密码是否正确（部分站点要求完整邮箱登录）")
        log("  2. 该账号是否为纯 OIDC 账号（无本地密码，必须走单点登录）")
        log("  3. 管理员是否关闭了 token 登录方式")
        log("  4. 改用网页自建金钥：头像 → 偏好設定 → 安全性 → 管理存取金鑰 → 建立")
        return

    log("--- 写入配置 ---")
    cfg = {"url": base.rstrip("/"), "token": token}
    try:
        existing = {}
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                existing = json.load(f)
        existing.update(cfg)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
        log("[√] 已写入 %s" % CONFIG_PATH)
        log("    service = %s" % used_service)
        log("    token   = %s...（已脱敏）" % token[:8])
    except Exception as exc:
        log("[!] 写入失败: %s" % exc)
        return

    log("--- 验证 Token ---")
    try:
        info, err = verify(base, token)
        if info:
            funcs = info.get("functions") or []
            log("[√] 验证通过")
            log("    站点: %s" % info.get("sitename"))
            log("    账号: %s (userid=%s)" % (info.get("username"), info.get("userid")))
            log("    Moodle 版本: %s" % (info.get("release") or "未知"))
            log("    可用函数数: %d" % len(funcs))
            names = sorted(f.get("name", "") for f in funcs)
            key = [n for n in names if n in (
                "core_enrol_get_users_courses",
                "core_course_get_contents",
                "core_course_get_updates_since",
                "mod_assign_get_assignments",
                "mod_assign_get_submission_status",
                "gradereport_user_get_grade_items",
            )]
            log("    关键函数命中: %s" % (", ".join(key) if key else "（无，白名单可能仅限移动端）"))
            log("    全部函数: %s" % (", ".join(names[:120]) if names else "（未返回函数清单）"))
        else:
            log("[x] 验证失败: %s" % err)
    except Exception as exc:
        log("[x] 验证请求异常: %s" % exc)

    log("=== 会话结束 ===")
    print("\n完成。日志已写入：%s" % LOG_PATH)


if __name__ == "__main__":
    main()
