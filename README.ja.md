# moodle-mcp

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · **日本語** · [한국어](README.ko.md) · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt-BR.md) · [Русский](README.ru.md)

**Moodle Web Service API** を AI エージェントから直接呼び出せる MCP（Model Context Protocol）サーバーに変換します。ブラウザ不要、スクレイパー不要、ページをクリックする必要もありません。

Moodle は世界の多くの大学・教育機関で使われている LMS ですが、汎用的な MCP サーバーは存在しませんでした。本プロジェクトはその空白を埋めるものです。単一ファイル・依存ゼロ・6 つのツールで、Web Services が有効な Moodle 3.x/4.x であればどのサイトでも動作します。

> pip パッケージも node もブラウザも不要。`python server.py` だけで動きます。

## なぜ必要か

エージェントはシラバスを読み、明日の締切を教えてくれます。しかし多くのコース内容はログインの壁の向こうにあります。ヘッドレスブラウザで Moodle をスクレイピングする方法は遅く、壊れやすく、WAF に阻まれがちです。Moodle 自体に安定した文書化済みの REST API があるのですから、足りないのは MCP のラッパーだけです。

本サーバーは Python 標準ライブラリ（`urllib`、`json`、`ssl`）のみを使用し、JSON-RPC 2.0 over stdio で通信します。Claude Desktop、Cursor、Marvis、その他 MCP 対応クライアントにそのまま接続できます。

## ツール

| ツール | 説明 | 引数 |
|---|---|---|
| `moodle_site_info` | トークンを検証し、サイト名・Moodle バージョン・現在のユーザー・利用可能な関数一覧を返します（診断用）。 | — |
| `moodle_list_courses` | 受講中の全コースを ID・略称・正式名称とともに一覧表示します。 | — |
| `moodle_recent_updates` | 直近 N 日間に追加・更新された内容（課題、ファイル、アナウンス）を新しい順に返します。 | `days`（既定 7）、`course_ids` |
| `moodle_pending_assignments` | 未提出の課題を**期限間近** / **期限超過** / **余裕あり**の 3 分類で、締切と残り日数付きで返します。 | `ahead_days`（既定 14）、`course_ids` |
| `moodle_course_files` | 1 コースのセクション構成とファイル一覧（ダウンロード直リンク、更新日時を含む）。**メタデータのみを返し、ファイルは一切ダウンロードしません。** | `course_id` |
| `moodle_weekly_digest` | まとめて取得：最近の更新＋期限間近＋期限超過＋集計。まずはこれから始めるのがおすすめです。 | `days`（既定 7）、`ahead_days`（既定 14） |

すべてのツールは**読み取り専用**です。提出・履修登録・削除・編集のインターフェースは意図的に用意していません。

## インストール

### 1. トークンの取得

Moodle は個人用アクセストークンを必要とします。サイトの状況に応じて次のいずれかを選んでください。

**A. Web UI（推奨。SSO アカウントでも可）**

1. 自分の Moodle サイトにログイン
2. プロフィール画像 → *プリファレンス* → *アカウント* → *セキュリティ* → *アクセスキーの管理*
3. 「作成」をクリックし、名前を `moodle-mcp`、サービスを *Moodle mobile web service* に設定
4. 生成されたキーをコピー

**B. スクリプトで Mobile サービスを利用（サイトにローカルパスワードが残っている場合のみ）**

```bash
python get_token.py
```

このスクリプトは `/login/token.php` と `moodle_mobile_app` サービス経由でトークンを取得し、即座に検証します。パスワード入力はエコーされず、ログにも残りません。SSO のみのアカウントでは `invalidlogin` が返るため、A の方法を使ってください。

**C. 環境変数**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. 設定

`server.py` と同じディレクトリに `config.json` を作成します。

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

環境変数は設定ファイルより優先されます。

### 3. サーバーの登録

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

`args` には `server.py` の絶対パスを指定してください。複数の Python がある環境では、`command` にインタープリタのフルパスを指定します。

## 使用例

> 「今週、まだ出していない課題は？」

エージェントが `moodle_weekly_digest` を呼び出し、そのまま読めるサマリーが返ります。

```
## 今後 7 日以内に締切・未提出
| コース | 課題 | 締切 | 残り |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3 日 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3 日 |

## 期限超過
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15 日超過 |

## 集計
提出済み／採点済み：51 ｜ 未提出合計：25（期限間近 4、超過 14、その他 7）
```

## 既知の制限

- **Turnitin（`turnitintooltwo`）と `quiz` モジュールには対応していません。** これらは独立したモジュールで `mod_assign` のセマンティクスを持たないため、締切は Web UI で確認してください。
- 締切が未設定の課題は「未設定」と表示されます。
- 週次ダイジェストは**未提出**の項目のみを集計対象とします。提出済み・未採点のものは件数には入りますが、表には出ません。
- 一部サイトの WAF は連続リクエストに `502` を返します。本サーバーは直列化と 150 ms の間隔を実装済みです。それでも発生する場合は間隔を空けて再試行してください。
- サイト側で Web Services が有効化され、アカウントに `webservice/rest:use` 権限が必要です。多くのサイトは全関数を許可していますが、モバイル用サブセットのみのサイトもあります。

## セキュリティ

- トークンは**認証情報**です。`config.json` か環境変数にのみ置き、リポジトリにコミットしないでください。`.gitignore` は `config.json` と `get_token.log` を除外済みです。
- `get_token.py` はパスワードの内容を記録せず、長さのみを記録します。入力には `getpass` を使用しています。
- すべてのツールは読み取り専用です。トークンが漏れても、本サーバー経由で課題を変更・削除することはできません。漏洩に気付いたら「アクセスキーの管理」から失効させてください。
- パケットキャプチャを公開しないでください。`wstoken` がリクエストボディに含まれます。

## 対応環境

| 項目 | 内容 |
|---|---|
| Python | 3.8 以上（標準ライブラリのみ） |
| MCP プロトコル | `2024-11-05` |
| Moodle | 3.x / 4.x（Web Services と REST プロトコルの有効化が必要） |
| 検証済み環境 | Moodle 4.3.6、435 関数を許可されたアカウント（フル権限） |

## ライセンス

MIT — [LICENSE](LICENSE) を参照してください。
