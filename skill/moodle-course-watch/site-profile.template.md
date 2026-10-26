---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c6eb62ba6ec5a28db2139adf23a2fe4b_2a20535fd16711f18460525400393706
    ReservedCode1: FobDWyMlYZr6kIAalinYobI//bj885tW57/ikygAV7MLewgKqrPCRICuX1QK0POJ+EmlDCOpfLxSakXAAvaaDDw+/lY/QwCVExizoa80dZFYg8Nu0vq9r8AfA5tz4DhaiEjo+8eUtM40WA/a0hu4v6jTOTCX9NGQORDbguEaNCDu+gb9AFinCx3GTUY=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c6eb62ba6ec5a28db2139adf23a2fe4b_2a20535fd16711f18460525400393706
    ReservedCode2: FobDWyMlYZr6kIAalinYobI//bj885tW57/ikygAV7MLewgKqrPCRICuX1QK0POJ+EmlDCOpfLxSakXAAvaaDDw+/lY/QwCVExizoa80dZFYg8Nu0vq9r8AfA5tz4DhaiEjo+8eUtM40WA/a0hu4v6jTOTCX9NGQORDbguEaNCDu+gb9AFinCx3GTUY=
---

# Site profile — 填写后才能跑本 skill

复制本文件为 `site-profile.md`，逐项填好。**任何一项填"未知"，都不要开始跑巡检**：猜错的巡检会安静地报"本周没新东西"，整个学期都发现不了。

## 1. 站点

| 项 | 值 | 怎么得到 |
|---|---|---|
| Site root URL | | 浏览器地址栏去掉 `course/` 之后的部分 |
| Moodle 版本 | | `scripts/check_site.py` 输出的 `Moodle x.y` |
| Web Service 是否开启 | 是 / 否 | 未开启会返回 `accessexception` 或 `invalidtoken` |
| Token 获取方式 | `/login/token.php`（moodle_mobile_app）/ 管理存取金鑰手建 / OIDC 无 token | 各校不同，多数学校只对 mobile app service 放行 |
| 是否限流 | 否 / 是（阈值） | 连续 POST 出现 502/429 即为限流，调用要串行、间隔 ≥0.15s |

## 2. 课程

| 课程 | course id | 本地目录 |
|---|---|---|
| | | |

course id 只能从 `core_enrol_get_users_courses` 取，不要从 URL 猜。

## 3. 结构适配（换学校必改）

| 项 | 值 | 说明 |
|---|---|---|
| 章节（week）命名 | 例：`Week 1 (10 Sept 2026)` / `Topic 2` / `1/Oct/2026 (Public Holiday)` | 镜像下载要跟随用户已有命名，不要另造一套 |
| 作业模块类型 | 例：`assign` 为主，另有 `turnitintooltwo`、`quiz` | 用 `check_site.py --courses` 的模块普查确认 |
| 作业名称过滤正则 | 默认 `(?i)assignment|tutorial` | 各校命名不同，如 `coursework|lab` |
| 截止日期是否可见 | 有 duedate / 全为空 | 空就报"未设置"，不许编 |
| 学期与周次换算 | 例：第 1 教学周 = 9/10 那周 | 用户按自身校历填 |

## 4. 基线（脚本自动维护）

| 课程 | 已见 cmid 列表 | 更新时间 |
|---|---|---|
| | | |

首次运行前留空；第一次巡检会把当前全部 cmid 记为基线，之后只报告新增 id。

## 5. 交付偏好

| 项 | 值 |
|---|---|
| 文件内容讲述 | 必做：逐份专业讲述文件内容，语体专业、术语准确，不在对话外落盘 |
| 重点分级 | 必做：必记 / 理解 / 了解 三级自动划分，并说明定级理由 |
| 是否要重点笔记 | 要 / 不要（要则按 SKILL.md Step 5 生成 Markdown） |
| 输出目录 | 默认与周文件夹同级 |
*（内容由AI生成，仅供参考）*
