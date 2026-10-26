<div align="center">

<img src="docs/banner.svg" alt="Moodle-Mcp" width="100%">

# Moodle-Mcp

### 让 AI Agent 真正能用的 Moodle

直接从 Moodle Web Service API 读取作业、截止时间与课程文件——不浏览器、不爬虫、不点页面。

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="零依赖">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>

<p>
<a href="README.md">English</a> ·
<b>简体中文</b> ·
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

> **配套 Skill —— [moodle-course-watch](https://github.com/Faixiang/moodle-course-watch)**
> 本 server 提供管道，skill 提供其上的工作流：检测新发布课业、镜像缺失周文件夹、列出未提交活动、对下载的文件做
> 专业讲述并划分重点等级。它以 git submodule 形式挂在 [`skill/moodle-course-watch/`](skill/moodle-course-watch/)（克隆时需加 `--recurse-submodules`），
> 也有独立仓库供只想装 skill 的人单独克隆。

## 界面预览 🖥️

<img src="docs/preview.svg" alt="MCP 会话示例" width="100%">

---

## 为什么需要它 🎯

Moodle 支撑着全球大量高校的教学平台，却一直没有通用的 MCP 服务器。用无头浏览器抓取既慢又脆弱，还容易触发 WAF；而 Moodle 本身已带有稳定、有文档的 REST API。

本项目就是缺失的那层封装：**一个零依赖的 Python 文件，六个只读工具**，适用于任何开启 Web Services 的 Moodle 3.x/4.x 站点。

```text
不装 pip 包。不装 node。不开浏览器。只要 python server.py。
```

## 功能特性 ✨

### 数据获取
- **看得懂截止时间** — 作业自动分为「临期」「逾期」「无压力」，剩余天数直接算好
- **每周简报** — 新增内容＋临期＋逾期一次取回，排版即可直接阅读
- **课程文件** — 章节结构与文件清单，含下载直链与修改时间；只给元数据，不下载文件
- **内置诊断** — `moodle_site_info` 报告站点版本、账号身份，以及 Token 实际可调用的函数清单

### 工程实现
- **零依赖** — 只用 Python 标准库（`urllib`、`json`、`ssl`），不污染运行环境
- **单文件** — `server.py` 拷到哪里都能跑，没有包结构，没有构建步骤
- **stdio JSON-RPC 2.0** — 直接接入 Claude Desktop、Cursor、Marvis 或任何兼容 MCP 的客户端
- **对 WAF 友好** — 请求串行化并间隔 150 ms，因为猛打 Moodle 只会换回 `502`
- **设计上只读** — 代码里不存在提交、选课、编辑、删除接口

## 工具 🧰

| 工具 | 作用 | 参数 |
|---|---|---|
| `moodle_site_info` | 校验 Token，返回站点名称、Moodle 版本、当前用户与该账号可调用的函数清单（诊断用）。 | — |
| `moodle_list_courses` | 列出全部已选课程，含课程 ID、简称、全称。 | — |
| `moodle_recent_updates` | 最近 N 天内新增或更新的内容（作业、文件、公告），按时间倒序。 | `days`（默认 7）、`course_ids` |
| `moodle_pending_assignments` | 未提交作业，分为**临期** / **逾期** / **无压力**三类，含截止时间与剩余天数。 | `ahead_days`（默认 14）、`course_ids` |
| `moodle_course_files` | 单个课程的章节结构与文件清单，含下载直链与修改时间。**只返回元数据，不下载任何文件。** | `course_id` |
| `moodle_download_week` | 把某一周的文件（课件 + 作业附件）下载到本地 `Week N` 文件夹：自动建目录、校验文件大小、跳过已存在文件。省略 `dest_root` 时只返回待下载清单。 | `course_id`、`week`（如 `6` 或 `"Week 6"`，填 `all` 为全部周次）、`dest_root` |
| `moodle_weekly_digest` | 一次性汇总：近期新增 + 临期未交 + 逾期未交 + 统计。建议作为起点。 | `days`（默认 7）、`ahead_days`（默认 14） |

## 配置要求 📦

| 项目 | 说明 |
|---|---|
| Python | 3.8+（仅标准库） |
| MCP 协议 | `2024-11-05` |
| Moodle | 3.x / 4.x，需开启 Web Services 与 REST 协议 |
| 账号 | 具备 `webservice/rest:use` 权限 |
| 实测环境 | Moodle 4.3.6，账号获授 435 个函数（完整权限） |

## 快速开始 🚀

### ① 获取 Token

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

脚本经 `/login/token.php` 与 `moodle_mobile_app` 服务换取 Token 并立即校验。密码输入不回显、不写日志。若账号仅有 SSO，会返回 `invalidlogin`，请改用 A 方案。

**C. 环境变量**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② 配置

在 `server.py` 同目录创建 `config.json`（也可复制 `config.example.json`）：

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

环境变量优先级高于配置文件。

### ③ 注册服务器

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

### ④ 验证

让客户端调用 `moodle_site_info`。配置正确时会返回站点名称、Moodle 版本与你的用户记录。失败请见下文「常见问题」。

## 配置参考 ⚙️

| 键 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `url` / `MOODLE_URL` | 字符串 | 是 | Moodle 站点根地址，末尾不带路径 |
| `token` / `MOODLE_TOKEN` | 字符串 | 是 | 由「管理存取金钥」生成的个人 Token |
| `config.json` | 文件 | 可选 | 从 `server.py` 所在目录读取 |

优先级：环境变量 → `config.json` → 报错。

## 使用示例 💬

> 「我这周还欠什么？」

Agent 调用 `moodle_weekly_digest`，直接得到一份可读简报：

```text
## 未来 7 天到期且未提交
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | 3 天 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 天 |

## 已逾期
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 逾期 15 天 |

## 统计
已提交/已批改：51 ｜ 未交合计：25（临期 4，逾期 14，其他 7）
```

其他好用的指令：

| 你说 | 落到哪个工具 |
|---|---|
| 「CIS225 这周新增了什么材料？」 | `moodle_recent_updates` |
| 「列出 GER405 的文件，别下载」 | `moodle_course_files` |
| 「哪些课程没有逾期？」 | `moodle_pending_assignments` |
| 「我的 Token 还有效吗？」 | `moodle_site_info` |

## 常见问题 🤔

<details>
<summary><b>运行 get_token.py 返回 <code>invalidlogin</code></b></summary>

你的账号只走 SSO/OIDC，`/login/token.php` 没有本地密码可校验。改用 A 方案，在「管理存取金钥」里自建 Token。
</details>

<details>
<summary><b>调用时返回 <code>502</code> 或连接被重置</b></summary>

站点 WAF 在限流。本服务器已做串行化并间隔 150 ms；若仍触发，请等几分钟重试，并避免同时并行调用多个工具。
</details>

<details>
<summary><b>工具返回空列表</b></summary>

依次检查三点：站点已开启 Web Services 与 REST 协议；账号具备 `webservice/rest:use`；传入的 `course_ids` 过滤条件正确。建议先跑 `moodle_site_info`——若函数清单很短，说明管理员只开放了移动端子集。
</details>

<details>
<summary><b>看不到 Turnitin 或 quiz 的截止时间</b></summary>

属预期行为。`turnitintooltwo` 与 `quiz` 是独立模块，不具备 `mod_assign` 语义，本服务器读不到，需到网页端核对。
</details>

<details>
<summary><b>某个作业截止时间显示「not set」</b></summary>

教师没有为该作业设置截止时间，没有数值可计算。作业仍会列出，避免你漏掉它的存在。
</details>

<details>
<summary><b>Windows 终端中文乱码</b></summary>

输出为 UTF-8。老式控制台请先执行 `chcp 65001`，或改用 Windows Terminal。
</details>

## 安全须知 🔒

- Token 属于**凭据**。只放 `config.json` 或环境变量，不要提交到仓库；`.gitignore` 已排除 `config.json` 与 `get_token.log`。
- `get_token.py` 不记录密码内容，只记长度，读取用 `getpass`。
- 全部工具只读，即使 Token 泄露，也无法通过本服务器修改或删除课业。一旦泄露，请到「管理存取金钥」撤销。
- 不要公开抓包记录：`wstoken` 会出现在请求体中。

## 兼容性 ✅

| 客户端 / 平台 | 状态 |
|---|---|
| Claude Desktop | 可用（stdio 服务器条目） |
| Cursor | 可用（`mcp.json`） |
| Marvis | 可用（MCP 注册表） |
| 其他 MCP 客户端 | 可用——标准 JSON-RPC 2.0 over stdio |
| Windows / macOS / Linux | 可用——无平台相关代码 |

## 路线图 🗺️

- [ ] 在 API 允许范围内支持 Turnitin 与 quiz 截止时间
- [ ] 可选本地缓存，减少大课程列表的重复往返
- [ ] 为选修课程极多的账号提供分页提示
- [ ] 补充提交**状态**细节（已批改／有反馈）——仍保持只读
- [ ] 抽出同款工具面，适配非 Moodle 的 LMS

## 参与贡献 🤝

欢迎 issue 与 pull request。整个服务器只有一个文件，通读 `server.py` 只需几分钟。

- 坚持零依赖：只用标准库。
- 所有工具保持只读。
- 绝不提交 `config.json`、Token 或抓包记录。
- 新增工具时，请同步更新工具表与**所有语言**的 README。

## 反馈建议 📢

Bug 与功能建议：[提交 issue](https://github.com/Faixiang/moodle-mcp/issues)。

## 许可证 📝

MIT —— 见 [LICENSE](LICENSE)。
