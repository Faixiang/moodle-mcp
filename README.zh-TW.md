<div align="center">

<img src="docs/banner.svg" alt="Moodle-Mcp" width="100%">

# Moodle-Mcp

### 讓 AI Agent 真正能用的 Moodle

直接從 Moodle Web Service API 讀取作業、截止時間與課程檔案——不開瀏覽器、不寫爬蟲、不用逐頁點擊。

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="零依賴">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>

<p>
<a href="README.md">English</a> ·
<a href="README.zh-CN.md">简体中文</a> ·
<b>繁體中文</b> ·
<a href="README.ja.md">日本語</a> ·
<a href="README.ko.md">한국어</a> ·
<a href="README.es.md">Español</a> ·
<a href="README.fr.md">Français</a> ·
<a href="README.de.md">Deutsch</a> ·
<a href="README.pt-BR.md">Português</a> ·
<a href="README.ru.md">Русский</a>
</p>

</div>

## 介面預覽 🖥️

<img src="docs/preview.svg" alt="MCP 工作階段示例" width="100%">

---

## 為何需要 🎯

Moodle 支撐着全球大量院校的教學平台，卻一直沒有通用的 MCP 伺服器。用無頭瀏覽器抓取既慢又脆弱，還容易觸發 WAF；而 Moodle 本身已有穩定且有文件的 REST API。

本專案就是缺失的那層封裝：**一個零依賴的 Python 檔案，六個唯讀工具**，適用於任何已開啟 Web Services 的 Moodle 3.x/4.x 站點。

```text
不必裝 pip 套件。不必裝 node。不必開瀏覽器。只要 python server.py。
```

## 功能特性 ✨

### 資料取得
- **看得懂截止時間** — 作業自動分為「臨期」「逾期」「無壓力」，剩餘天數直接算好
- **每週簡報** — 新增內容＋臨期＋逾期一次取回，排版即可直接閱讀
- **課程檔案** — 章節結構與檔案清單，含下載直連與修改時間；只給中繼資料，不下載檔案
- **內建診斷** — `moodle_site_info` 回報站點版本、帳號身分，以及 Token 實際可呼叫的函數清單

### 工程實現
- **零依賴** — 只用 Python 標準庫（`urllib`、`json`、`ssl`），不污染執行環境
- **單一檔案** — `server.py` 複製到哪裡都能跑，沒有套件結構，沒有建置步驟
- **stdio JSON-RPC 2.0** — 直接接入 Claude Desktop、Cursor、Marvis 或任何相容 MCP 的客戶端
- **對 WAF 友善** — 請求序列化並間隔 150 ms，因為猛打 Moodle 只會換回 `502`
- **設計上唯讀** — 程式碼中不存在提交、選課、編輯、刪除介面

## 工具 🧰

| 工具 | 作用 | 參數 |
|---|---|---|
| `moodle_site_info` | 驗證 Token，回傳站點名稱、Moodle 版本、目前使用者與該帳號可呼叫的函數清單（診斷用）。 | — |
| `moodle_list_courses` | 列出所有已選課程，含課程 ID、簡稱、全名。 | — |
| `moodle_recent_updates` | 最近 N 天內新增或更新的內容（作業、檔案、公告），按時間倒序。 | `days`（預設 7）、`course_ids` |
| `moodle_pending_assignments` | 未提交作業，分為**臨期** / **逾期** / **無壓力**三類，含截止時間與剩餘天數。 | `ahead_days`（預設 14）、`course_ids` |
| `moodle_course_files` | 單一課程的章節結構與檔案清單，含下載直連與修改時間。**只回傳中繼資料，不下載任何檔案。** | `course_id` |
| `moodle_download_week` | 把某一週的檔案（課件 + 作業附件）下載到本機 `Week N` 資料夾：自動建立目錄、驗證檔案大小、跳過已存在檔案。省略 `dest_root` 時僅回傳待下載清單。 | `course_id`、`week`（如 `6` 或 `"Week 6"`，填 `all` 為全部週次）、`dest_root` |
| `moodle_weekly_digest` | 一次過彙總：近期新增 + 臨期未交 + 逾期未交 + 統計。建議作為起點。 | `days`（預設 7）、`ahead_days`（預設 14） |

## 配置要求 📦

| 項目 | 說明 |
|---|---|
| Python | 3.8+（僅標準庫） |
| MCP 協定 | `2024-11-05` |
| Moodle | 3.x / 4.x，需開啟 Web Services 與 REST 協定 |
| 帳號 | 具備 `webservice/rest:use` 權限 |
| 實測環境 | Moodle 4.3.6，帳號獲授 435 個函數（完整權限） |

## 快速開始 🚀

### ① 取得 Token

Moodle 需要個人存取金鑰。按站點情況任選一種：

**A. 網頁端（建議，SSO 帳號亦適用）**

1. 登入你的 Moodle 站點
2. 頭像 → *偏好設定* → *帳戶* → *安全性* → *管理存取金鑰*
3. 點「建立」，名稱填 `moodle-mcp`，服務選 *Moodle mobile web service*
4. 複製產生的金鑰

**B. 以腳本走行動服務（僅當站點保留本地密碼時可用）**

```bash
python get_token.py
```

腳本經 `/login/token.php` 與 `moodle_mobile_app` 服務換取 Token 並即時驗證。密碼輸入不回顯、不寫日誌。若帳號只有 SSO，會回傳 `invalidlogin`，請改用 A 方案。

**C. 環境變數**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② 設定

在 `server.py` 同目錄建立 `config.json`（亦可複製 `config.example.json`）：

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

環境變數優先於設定檔。

### ③ 註冊伺服器

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

`args` 請填 `server.py` 的絕對路徑。若本機有多個 Python 版本，把 `command` 指向完整解譯器路徑。

### ④ 驗證

讓客戶端呼叫 `moodle_site_info`。設定正確時會回傳站點名稱、Moodle 版本與你的使用者紀錄。失敗請見下文「常見問題」。

## 設定參考 ⚙️

| 鍵 | 類型 | 必填 | 說明 |
|---|---|---|---|
| `url` / `MOODLE_URL` | 字串 | 是 | Moodle 站點根位址，結尾不帶路徑 |
| `token` / `MOODLE_TOKEN` | 字串 | 是 | 由「管理存取金鑰」產生的個人 Token |
| `config.json` | 檔案 | 選填 | 從 `server.py` 所在目錄讀取 |

優先順序：環境變數 → `config.json` → 報錯。

## 使用示例 💬

> 「我這星期還欠什麼？」

Agent 呼叫 `moodle_weekly_digest`，即得一份可讀簡報：

```text
## 未來 7 天到期且未提交
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | 3 天 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 天 |

## 已逾期
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 逾期 15 天 |

## 統計
已提交／已批改：51 ｜ 未交合計：25（臨期 4，逾期 14，其他 7）
```

其他好用的指令：

| 你說 | 落到哪個工具 |
|---|---|
| 「CIS225 這星期新增了什麼材料？」 | `moodle_recent_updates` |
| 「列出 GER405 的檔案，別下載」 | `moodle_course_files` |
| 「哪些課程沒有逾期？」 | `moodle_pending_assignments` |
| 「我的 Token 還有效嗎？」 | `moodle_site_info` |

## 常見問題 🤔

<details>
<summary><b>執行 get_token.py 回傳 <code>invalidlogin</code></b></summary>

你的帳號只走 SSO/OIDC，`/login/token.php` 沒有本地密碼可校驗。改用 A 方案，在「管理存取金鑰」自行建立 Token。
</details>

<details>
<summary><b>呼叫時回傳 <code>502</code> 或連線被重置</b></summary>

站點 WAF 在限流。本伺服器已做序列化並間隔 150 ms；若仍觸發，請等幾分鐘重試，並避免同時並行呼叫多個工具。
</details>

<details>
<summary><b>工具回傳空清單</b></summary>

依次檢查三點：站點已開啟 Web Services 與 REST 協定；帳號具備 `webservice/rest:use`；傳入的 `course_ids` 篩選條件正確。建議先跑 `moodle_site_info`——若函數清單很短，代表管理員只開放了行動端子集。
</details>

<details>
<summary><b>看不到 Turnitin 或 quiz 的截止時間</b></summary>

屬預期行為。`turnitintooltwo` 與 `quiz` 是獨立模組，不具備 `mod_assign` 語意，本伺服器讀不到，需到網頁端核對。
</details>

<details>
<summary><b>某個作業截止時間顯示「not set」</b></summary>

教師沒有為該作業設定截止時間，沒有數值可計算。作業仍會列出，避免你漏掉它的存在。
</details>

<details>
<summary><b>Windows 終端中文亂碼</b></summary>

輸出為 UTF-8。舊式主控台請先執行 `chcp 65001`，或改用 Windows Terminal。
</details>

## 安全須知 🔒

- Token 屬**憑證**。只放 `config.json` 或環境變數，不要提交到倉庫；`.gitignore` 已排除 `config.json` 與 `get_token.log`。
- `get_token.py` 不記錄密碼內容，只記長度，讀取使用 `getpass`。
- 全部工具唯讀，即使 Token 外洩，亦無法透過本伺服器修改或刪除課業。一旦外洩，請到「管理存取金鑰」撤銷。
- 不要公開抓包紀錄：`wstoken` 會出現在請求主體中。

## 相容性 ✅

| 客戶端 / 平台 | 狀態 |
|---|---|
| Claude Desktop | 可用（stdio 伺服器項目） |
| Cursor | 可用（`mcp.json`） |
| Marvis | 可用（MCP 註冊表） |
| 其他 MCP 客戶端 | 可用——標準 JSON-RPC 2.0 over stdio |
| Windows / macOS / Linux | 可用——無平台相關程式碼 |

## 路線圖 🗺️

- [ ] 在 API 允許範圍內支援 Turnitin 與 quiz 截止時間
- [ ] 選用本地快取，減少大課程清單的重複往返
- [ ] 為選修課程極多的帳號提供分頁提示
- [ ] 補充提交**狀態**細節（已批改／有回饋）——仍保持唯讀
- [ ] 抽出同款工具面，適配非 Moodle 的 LMS

## 參與貢獻 🤝

歡迎 issue 與 pull request。整個伺服器只有一個檔案，通讀 `server.py` 只需幾分鐘。

- 堅持零依賴：只用標準庫。
- 所有工具保持唯讀。
- 絕不提交 `config.json`、Token 或抓包紀錄。
- 新增工具時，請同步更新工具表與**所有語言**的 README。

## 回饋建議 📢

Bug 與功能建議：[提交 issue](https://github.com/Faixiang/moodle-mcp/issues)。

## 授權 📝

MIT —— 見 [LICENSE](LICENSE)。
