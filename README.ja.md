<div align="center">

<img src="docs/banner.svg" alt="Moodle-Mcp" width="100%">

# Moodle-Mcp

### AI エージェントが本当に使える Moodle

Moodle の Web Service API から課題・締切・コース資料を直接取得。ブラウザもスクレイパーもクリック作業も不要です。

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="依存ゼロ">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>
<img src="https://img.shields.io/badge/version-1.3.0-1f6feb" alt="Version 1.3.0">
<img src="https://img.shields.io/badge/status-actively%20maintained-brightgreen" alt="Actively maintained">

<p>
<a href="README.md">English</a> ·
<a href="README.zh-CN.md">简体中文</a> ·
<a href="README.zh-TW.md">繁體中文</a> ·
<b>日本語</b> ·
<a href="README.ko.md">한국어</a> ·
<a href="README.es.md">Español</a> ·
<a href="README.fr.md">Français</a> ·
<a href="README.de.md">Deutsch</a> ·
<a href="README.pt-BR.md">Português</a> ·
<a href="README.ru.md">Русский</a>
</p>

</div>
> **Companion skill — [moodle-course-watch](https://github.com/Faixiang/moodle-course-watch)**
> This server is the plumbing; the skill is the workflow on top of it: new coursework diffing, missing week folders,
> unsubmitted activity list, and a graded walkthrough of downloaded files. Mounted here as a git submodule at
> [`skill/moodle-course-watch/`](skill/moodle-course-watch/) (clone with `--recurse-submodules`), and also published
> standalone.


> **継続的にメンテナンスしています。** 最新リリースは **v1.3.0**（2026-10-27）：クイズはもう盲点ではありません。`moodle_quiz_status` が実際の受験状況と得点を読み取ります。変更履歴は[文末](README.md#changelog-)にあります。

## プレビュー 🖥️

<img src="docs/preview.svg" alt="MCP セッション例" width="100%">

---

## なぜ必要か 🎯

Moodle は世界中の大学の教育基盤ですが、汎用的な MCP サーバーは長らく存在しませんでした。ヘッドレスブラウザでの取得は遅く脆く、WAF に弾かれがちです。一方 Moodle 自身は安定した文書化済みの REST API を持っています。

本プロジェクトはその欠けていた層です。**依存ゼロの Python ファイル 1 本、読み取り専用ツール 6 個**。Web Services が有効な Moodle 3.x/4.x ならどこでも動きます。

```text
pip 不要。node 不要。ブラウザ不要。python server.py だけ。
```

## 機能 ✨

### データ取得
- **締切がそのまま読める** — 課題を「まもなく締切」「期限超過」「余裕あり」に自動分類し、残り日数も算出
- **週次ダイジェスト** — 新着＋締切間近＋期限超過を一度に取得、そのまま読める形で整形
- **コース資料** — セクション構成とファイル一覧、ダウンロード直リンクと更新日時付き。メタデータのみでダウンロードはしません
- **診断機能** — `moodle_site_info` がサイトのバージョン、アカウント、そして Token で実際に呼べる関数一覧を報告

### 実装
- **依存ゼロ** — Python 標準ライブラリ（`urllib`、`json`、`ssl`）のみ。環境を汚しません
- **単一ファイル** — `server.py` をコピーすればどこでも動作。パッケージ構成もビルド手順もなし
- **stdio JSON-RPC 2.0** — Claude Desktop、Cursor、Marvis、その他 MCP 対応クライアントに直接接続
- **WAF に配慮** — リクエストを直列化し 150 ms 間隔。Moodle を叩き続けても `502` が返るだけです
- **設計から読み取り専用** — 提出・登録・編集・削除のコードは存在しません

## ツール 🧰

| ツール | 役割 | 引数 |
|---|---|---|
| `moodle_site_info` | Token を検証し、サイト名・Moodle バージョン・現在のユーザー・利用可能な関数一覧を返します（診断用）。 | — |
| `moodle_list_courses` | 受講中コースをすべて列挙。コース ID・略称・正式名称を含みます。 | — |
| `moodle_recent_updates` | 直近 N 日間に追加・更新されたもの（課題・ファイル・お知らせ）を新しい順に返します。 | `days`（既定 7）、`course_ids` |
| `moodle_pending_assignments` | 未提出の課題を**締切間近** / **期限超過** / **余裕あり**に分類し、締切と残り日数を併記。 | `ahead_days`（既定 14）、`course_ids` |
| `moodle_quiz_status` | クイズごとの受験状況（**提出済み** / **進行中** / **未受験**）を取得し、最高得点・公開期間・制限時間・「受付終了」フラグを併記。 | `course_ids`、`only_pending` |
| `moodle_course_files` | 1 コースのセクション構成とファイル一覧、ダウンロード直リンク・更新日時付き。**メタデータのみで、ファイルは取得しません。** | `course_id` |
| `moodle_download_week` | 指定した週のファイル（スライド + 課題添付）をローカルの `Week N` フォルダーへダウンロード。フォルダー作成・サイズ検証・既存ファイルのスキップを自動化。`dest_root` を省略すると一覧のみ返します。 | `course_id`、`week`（例 `6` または `"Week 6"`、`all` で全週）、`dest_root` |
| `moodle_weekly_digest` | 一括サマリー：新着＋締切間近＋期限超過＋統計。まずはこれから。 | `days`（既定 7）、`ahead_days`（既定 14） |

## 動作要件 📦

| 項目 | 内容 |
|---|---|
| Python | 3.8 以上（標準ライブラリのみ） |
| MCP プロトコル | `2024-11-05` |
| Moodle | 3.x / 4.x、Web Services と REST プロトコルが有効であること |
| アカウント | `webservice/rest:use` 権限 |
| 検証済み環境 | Moodle 4.3.6、435 関数が付与されたアカウント（フル権限） |

## クイックスタート 🚀

### ① Token を取得

Moodle は個人用アクセスキーを必要とします。サイトの状況に応じて選択してください。

**A. Web UI（推奨、SSO アカウントでも可）**

1. Moodle にログイン
2. プロフィール画像 → *設定* → *アカウント* → *セキュリティ* → *アクセスキーの管理*
3. 「作成」を押し、名前を `moodle-mcp`、サービスを *Moodle mobile web service* に設定
4. 生成されたキーをコピー

**B. スクリプト経由（サイトにローカルパスワードが残っている場合のみ）**

```bash
python get_token.py
```

`/login/token.php` と `moodle_mobile_app` サービスで Token を取得し、その場で検証します。パスワードは非表示入力で、ログにも残しません。SSO 専用アカウントでは `invalidlogin` が返るため、A の方法を使ってください。

**C. 環境変数**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② 設定

`server.py` と同じディレクトリに `config.json` を作成します（`config.example.json` の複製でも可）。

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

環境変数は設定ファイルより優先されます。

### ③ サーバーを登録

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

`args` には `server.py` の絶対パスを指定してください。複数の Python がある場合は `command` をインタプリタのフルパスにします。

### ④ 検証

クライアントから `moodle_site_info` を呼び出します。設定が正しければサイト名・Moodle バージョン・ユーザー情報が返ります。失敗した場合は下の「よくある質問」を参照してください。

## 設定リファレンス ⚙️

| キー | 型 | 必須 | 説明 |
|---|---|---|---|
| `url` / `MOODLE_URL` | 文字列 | はい | Moodle サイトのルート URL（末尾にパスを付けない） |
| `token` / `MOODLE_TOKEN` | 文字列 | はい | 「アクセスキーの管理」で生成した個人 Token |
| `config.json` | ファイル | 任意 | `server.py` と同じディレクトリから読み込み |

優先順位：環境変数 → `config.json` → エラー。

## 使用例 💬

> 「今週まだ残っている課題は？」

エージェントが `moodle_weekly_digest` を呼び、そのまま読めるサマリーを返します。

```text
## 7 日以内に締切・未提出
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | あと 3 日 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | あと 3 日 |

## 期限超過
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 日超過 |

## 統計
提出済み／採点済み：51 ｜ 未提出合計：25（締切間近 4、超過 14、その他 7）
```

その他の便利な指示：

| 発話 | 呼ばれるツール |
|---|---|
| 「CIS225 で今週追加された資料は？」 | `moodle_recent_updates` |
| 「GER405 のファイルを一覧にして、取得はしないで」 | `moodle_course_files` |
| 「期限超過がないコースは？」 | `moodle_pending_assignments` |
| 「Token はまだ有効？」 | `moodle_site_info` |

## よくある質問 🤔

<details>
<summary><b>get_token.py が <code>invalidlogin</code> を返す</b></summary>

アカウントが SSO/OIDC 専用で、`/login/token.php` が検証できるローカルパスワードがありません。A の方法で「アクセスキーの管理」から Token を作成してください。
</details>

<details>
<summary><b>呼び出しが <code>502</code> になる、または接続が切れる</b></summary>

サイトの WAF によるレート制限です。本サーバーは直列化と 150 ms 間隔を実装済みですが、それでも発生する場合は数分待って再試行し、複数ツールの並列呼び出しを避けてください。
</details>

<details>
<summary><b>ツールが空のリストを返す</b></summary>

3 点を順に確認してください。Web Services と REST が有効か。アカウントに `webservice/rest:use` があるか。`course_ids` の絞り込みが正しいか。まず `moodle_site_info` を実行し、関数一覧が極端に短い場合は管理者がモバイル用サブセットのみ開放しています。
</details>

<details>
<summary><b>Turnitin や quiz の締切が見えない</b></summary>

想定どおりの動作です。`turnitintooltwo` と `quiz` は独立モジュールで `mod_assign` の意味論を持たないため取得できません。Web UI で確認してください。
</details>

<details>
<summary><b>締切が「not set」と表示される</b></summary>

教員がその課題に締切を設定していないため、計算できる値がありません。見落としを防ぐため、課題自体は一覧に残します。
</details>

<details>
<summary><b>Windows のターミナルで文字化けする</b></summary>

出力は UTF-8 です。旧来のコンソールでは `chcp 65001` を実行するか、Windows Terminal を使用してください。
</details>

## セキュリティ 🔒

- Token は**認証情報**です。`config.json` か環境変数にのみ置き、リポジトリにコミットしないでください。`.gitignore` は `config.json` と `get_token.log` を除外済みです。
- `get_token.py` はパスワードの内容を記録せず、長さのみを記録します。入力は `getpass` を使用。
- すべてのツールは読み取り専用です。Token が漏れても本サーバー経由で課題を変更・削除することはできません。漏洩時は「アクセスキーの管理」で失効させてください。
- 通信キャプチャを公開しないでください。`wstoken` はリクエスト本文に含まれます。

## 互換性 ✅

| クライアント / 環境 | 状態 |
|---|---|
| Claude Desktop | 対応（stdio サーバー登録） |
| Cursor | 対応（`mcp.json`） |
| Marvis | 対応（MCP レジストリ） |
| その他の MCP クライアント | 対応 — 標準 JSON-RPC 2.0 over stdio |
| Windows / macOS / Linux | 対応 — プラットフォーム依存コードなし |

## ロードマップ 🗺️

- [ ] API が許す範囲で Turnitin と quiz の締切に対応
- [ ] 大規模コース一覧の往復を減らす任意のローカルキャッシュ
- [ ] 受講コースが極端に多いアカウント向けのページング案内
- [ ] 提出**状態**の詳細（採点済み／フィードバックあり）— 読み取り専用のまま
- [ ] 同じツール面を非 Moodle LMS へ展開

## コントリビューション 🤝

issue と pull request を歓迎します。サーバーは 1 ファイルのみで、`server.py` は数分で読み切れます。

- 依存ゼロを維持する（標準ライブラリのみ）。
- すべてのツールを読み取り専用に保つ。
- `config.json`、Token、通信キャプチャは決してコミットしない。
- ツールを追加したら、ツール表と**すべての言語**の README を更新する。

## フィードバック 📢

バグ報告・機能要望は [issue を立ててください](https://github.com/Faixiang/moodle-mcp/issues)。

## ライセンス 📝

MIT — [LICENSE](LICENSE) を参照。
