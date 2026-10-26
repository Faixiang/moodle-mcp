---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c6eb62ba6ec5a28db2139adf23a2fe4b_6ec27cc5d14e11f18460525400393706
    ReservedCode1: 90bvCjfpVbcMI+76NWhZIoTdjRJXL/rgP3FUNbrPN9IbLuxvXByznZHDTchNYC0AP3sf/I9RWRkqtVGWNC718xkZzU91s1PJXwRhBSY6rjCntPZmH8YR+71PE+UhZTgMlYHPRrKSamJBdZ/ApzeiaV6UsggIRjTFbJj21wchFFXTk5NgV622NB2c27Q=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c6eb62ba6ec5a28db2139adf23a2fe4b_6ec27cc5d14e11f18460525400393706
    ReservedCode2: 90bvCjfpVbcMI+76NWhZIoTdjRJXL/rgP3FUNbrPN9IbLuxvXByznZHDTchNYC0AP3sf/I9RWRkqtVGWNC718xkZzU91s1PJXwRhBSY6rjCntPZmH8YR+71PE+UhZTgMlYHPRrKSamJBdZ/ApzeiaV6UsggIRjTFbJj21wchFFXTk5NgV622NB2c27Q=
---

# moodle-mcp

[English](README.md) · [简体中文](README.zh-CN.md) · **繁體中文** · [日本語](README.ja.md) · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt-BR.md) · [Русский](README.ru.md)

把 **Moodle Web Service API** 封裝成 AI Agent 可直接呼叫的 MCP（Model Context Protocol）伺服器——不開瀏覽器、不寫爬蟲、不用逐頁點擊。

Moodle 支撐着全球大量院校的教學平台，卻一直沒有通用的 MCP 伺服器。本專案補上這塊空缺：單一檔案、零依賴、六個工具，適用於任何已開啟 Web Services 的 Moodle 3.x/4.x 站點。

> 不必裝 pip 套件，不必裝 node，不必開瀏覽器。只要 `python server.py`。

## 為何需要

Agent 看得懂教學大綱、能告訴你明天要交什麼——但大部分課程內容鎖在登入牆之後。用無頭瀏覽器抓 Moodle 既慢又脆弱，還容易觸發 WAF。Moodle 本身已有穩定且有文件的 REST API，欠缺的只是一層 MCP 封裝。

本伺服器只用 Python 標準庫（`urllib`、`json`、`ssl`），以 JSON-RPC 2.0 over stdio 通訊，可直接接入 Claude Desktop、Cursor、Marvis 或任何相容 MCP 的客戶端。

## 工具

| 工具 | 作用 | 參數 |
|---|---|---|
| `moodle_site_info` | 驗證 Token，回傳站點名稱、Moodle 版本、目前使用者，以及該帳號可呼叫的函數清單（診斷用）。 | — |
| `moodle_list_courses` | 列出所有已選課程，含課程 ID、簡稱、全名。 | — |
| `moodle_recent_updates` | 最近 N 天內新增或更新的內容（作業、檔案、公告），按時間倒序。 | `days`（預設 7）、`course_ids` |
| `moodle_pending_assignments` | 未提交作業，分為**臨期** / **逾期** / **無壓力**三類，含截止時間與剩餘天數。 | `ahead_days`（預設 14）、`course_ids` |
| `moodle_course_files` | 單一課程的章節結構與檔案清單，含下載直連與修改時間。**只回傳中繼資料，不下載任何檔案。** | `course_id` |
| `moodle_weekly_digest` | 一次過彙總：近期新增 + 臨期未交 + 逾期未交 + 統計。建議作為起點。 | `days`（預設 7）、`ahead_days`（預設 14） |

所有工具皆為**唯讀**。刻意不提供提交、選課、刪除、編輯類介面。

## 安裝

### 1. 取得 Token

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

腳本經 `/login/token.php` 與 `moodle_mobile_app` 服務換取 Token 並即時驗證。密碼輸入不回顯，亦不寫入日誌。若帳號只有 SSO 登入方式，此處會回傳 `invalidlogin`，請改用 A 方案。

**C. 環境變數**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. 設定

在 `server.py` 同目錄建立 `config.json`：

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

環境變數優先於設定檔。

### 3. 註冊伺服器

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

## 範例

> 「我這星期還欠什麼？」

Agent 呼叫 `moodle_weekly_digest`，即得一份可讀簡報：

```
## 未來 7 天到期且未提交
| 課程 | 作業 | 截止 | 剩餘 |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 天 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 天 |

## 已逾期
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 逾期 15 天 |

## 統計
已提交／已批改：51 ｜ 未交合計：25（臨期 4，逾期 14，其他 7）
```

## 已知限制

- **不涵蓋 Turnitin（`turnitintooltwo`）與 `quiz` 模組**。兩者為獨立模組，不具 `mod_assign` 語意，截止時間須到網頁端核對。
- 未設定截止時間的作業會顯示為「未設定」。
- 週報只統計**未提交**項目；已提交未批改者計入統計數，不會出現在表格。
- 部分站點 WAF 會對連續請求回應 `502`。伺服器已做序列化並每次間隔 150 ms；若仍出現，請降頻重試。
- 需要站點開啟 Web Services，且帳號具備 `webservice/rest:use` 權限。多數站點授予完整函數清單，亦有站點只開放行動端子集。

## 安全須知

- Token 屬**憑證**。只放 `config.json` 或環境變數，不要提交到倉庫；`.gitignore` 已排除 `config.json` 與 `get_token.log`。
- `get_token.py` 不記錄密碼內容，只記長度，讀取使用 `getpass`。
- 全部工具唯讀，即使 Token 外洩，亦無法透過本伺服器修改或刪除課業。一旦外洩，請到「管理存取金鑰」撤銷。
- 不要公開抓包紀錄：`wstoken` 會出現在請求主體中。

## 相容性

| 元件 | 說明 |
|---|---|
| Python | 3.8+（僅標準庫） |
| MCP 協定 | `2024-11-05` |
| Moodle | 3.x / 4.x，需開啟 Web Services 與 REST 協定 |
| 實測環境 | Moodle 4.3.6，帳號獲授 435 個函數（完整權限） |

## 授權

MIT —— 見 [LICENSE](LICENSE)。
*（内容由AI生成，仅供参考）*
