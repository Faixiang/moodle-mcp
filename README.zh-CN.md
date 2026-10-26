---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c6eb62ba6ec5a28db2139adf23a2fe4b_6beb8160d14e11f196c5525400248c00
    ReservedCode1: LXm3YpoI/YJhz2g406eMmzXmVfmfW+H59T/r3fpyveurOvYV5D1WwJZZyUh0jHCRTAwSaUMIvtqgEDe4q8kxqhiNpNjUuX0FdCQIykzRlZxIUbs+7Z/O396BRY/zh+MG0yJfKsuraywli4BxXkSe+gyg4/DIKazf4rGExpWH5n8Cyj6PjGojueVnLik=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c6eb62ba6ec5a28db2139adf23a2fe4b_6beb8160d14e11f196c5525400248c00
    ReservedCode2: LXm3YpoI/YJhz2g406eMmzXmVfmfW+H59T/r3fpyveurOvYV5D1WwJZZyUh0jHCRTAwSaUMIvtqgEDe4q8kxqhiNpNjUuX0FdCQIykzRlZxIUbs+7Z/O396BRY/zh+MG0yJfKsuraywli4BxXkSe+gyg4/DIKazf4rGExpWH5n8Cyj6PjGojueVnLik=
---

# moodle-mcp

[English](README.md) · **简体中文** · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt-BR.md) · [Русский](README.ru.md)

把 **Moodle Web Service API** 封装成 AI Agent 可直接调用的 MCP（Model Context Protocol）服务器——不用浏览器，不用爬虫，不用点页面。

Moodle 支撑着全球大量高校的教学平台，却一直没有通用的 MCP 服务器。本项目补上这一块：单文件、零依赖、六个工具，适用于任何已开启 Web Services 的 Moodle 3.x/4.x 站点。

> 不装 pip 包，不装 node，不装浏览器。只要 `python server.py`。

## 为什么需要它

Agent 能读懂教学大纲、能告诉你明天要交什么——但大部分课程内容锁在登录墙后面。用无头浏览器抓 Moodle 既慢又脆，还容易触发 WAF。Moodle 本身就带一套稳定、有文档的 REST API，缺的只是一个 MCP 封装。

本服务器只使用 Python 标准库（`urllib`、`json`、`ssl`），以 JSON-RPC 2.0 over stdio 通信，可直接接入 Claude Desktop、Cursor、Marvis 或任何兼容 MCP 的客户端。

## 工具

| 工具 | 作用 | 参数 |
|---|---|---|
| `moodle_site_info` | 校验 Token，返回站点名称、Moodle 版本、当前用户以及该账号可调用的函数清单（诊断用）。 | — |
| `moodle_list_courses` | 列出全部已选课程，含课程 ID、简称、全称。 | — |
| `moodle_recent_updates` | 最近 N 天内新增或更新的内容（作业、文件、公告），按时间倒序。 | `days`（默认 7）、`course_ids` |
| `moodle_pending_assignments` | 未提交作业，分为**临期** / **逾期** / **无压力**三类，含截止时间与剩余天数。 | `ahead_days`（默认 14）、`course_ids` |
| `moodle_course_files` | 单个课程的章节结构与文件清单，含下载直链与修改时间。**只返回元数据，不下载任何文件。** | `course_id` |
| `moodle_weekly_digest` | 一次性汇总：近期新增 + 临期未交 + 逾期未交 + 统计。建议作为起点。 | `days`（默认 7）、`ahead_days`（默认 14） |

所有工具均为**只读**。故意不提供提交、选课、删除、编辑类接口。

## 安装

### 1. 获取 Token

Moodle 需要个人访问金钥。按站点情况任选一种：

**A. 网页端（推荐，SSO 账号也适用）**

1. 登录你的 Moodle 站点
2. 头像 → *偏好设定* → *账户* → *安全性* → *管理存取金钥*
3. 点「建立」，名称填 `moodle-mcp`，服务选 *Moodle mobile web service*
4. 复制生成的金钥

**B. 用脚本走移动服务（仅当站点保留本地密码时可用）**

```bash
python get_token.py
```

脚本通过 `/login/token.php` 与 `moodle_mobile_app` 服务换取 Token 并立即校验。密码输入不回显，也不写入日志。若账号仅有 SSO 登录方式，这里会返回 `invalidlogin`，请改用 A 方案。

**C. 环境变量**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. 配置

在 `server.py` 同目录下创建 `config.json`：

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

环境变量优先级高于配置文件。

### 3. 注册服务器

Claude Desktop / Cursor（`mcp.json`）：

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

`args` 请用 `server.py` 的绝对路径。若本机有多个 Python 版本，把 `command` 指向完整解释器路径。

## 示例

> 「我这周还欠什么？」

Agent 调用 `moodle_weekly_digest`，直接得到一份可读简报：

```
## 未来 7 天到期且未提交
| 课程 | 作业 | 截止 | 剩余 |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 天 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 天 |

## 已逾期
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 逾期 15 天 |

## 统计
已提交/已批改：51 ｜ 未交合计：25（临期 4，逾期 14，其他 7）
```

## 已知限制

- **不覆盖 Turnitin（`turnitintooltwo`）与 `quiz` 模块**。它们是独立模块，不具备 `mod_assign` 语义，截止时间需到网页端核对。
- 未设置截止时间的作业会显示为「未设置」。
- 周报只统计**未提交**项；已提交未批改的计入统计数，不出现在表格中。
- 部分站点 WAF 会对连续请求返回 `502`。服务器已做串行化并每次间隔 150 ms；若仍出现，请降频重试。
- 需要站点开启 Web Services，且账号具备 `webservice/rest:use` 权限。多数站点授予完整函数列表，也有站点仅开放移动端子集。

## 安全须知

- Token 属于**凭据**。只放 `config.json` 或环境变量，不要提交到仓库；`.gitignore` 已排除 `config.json` 与 `get_token.log`。
- `get_token.py` 不记录密码内容，只记长度，读取用 `getpass`。
- 全部工具只读，即使 Token 泄露，也无法通过本服务器修改或删除课业。一旦泄露，请到「管理存取金钥」撤销。
- 不要公开抓包记录：`wstoken` 会出现在请求体中。

## 兼容性

| 组件 | 说明 |
|---|---|
| Python | 3.8+（仅标准库） |
| MCP 协议 | `2024-11-05` |
| Moodle | 3.x / 4.x，需开启 Web Services 与 REST 协议 |
| 实测环境 | Moodle 4.3.6，账号获授 435 个函数（完整权限） |

## 许可证

MIT —— 见 [LICENSE](LICENSE)。
*（内容由AI生成，仅供参考）*
