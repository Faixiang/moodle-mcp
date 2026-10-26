---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c6eb62ba6ec5a28db2139adf23a2fe4b_262acd13d15311f196c5525400248c00
    ReservedCode1: R6nT9b1/IGSKvLCGFGm5p+MbdNz0d4sqtkCkS7nEP/uceBFMOc+AqgdXa7vnx0HPQhLy6lneB8DjXtsEzEiDMedxVCtPQ0bEGMvIfi5edMEBtl6dLqBXhv7efcpYJPxwZNXrv7cubUqFAcRhqRlmcJo2YQkbtLvMzjKq+kZu1QYgabIlN+DCu8Oadns=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c6eb62ba6ec5a28db2139adf23a2fe4b_262acd13d15311f196c5525400248c00
    ReservedCode2: R6nT9b1/IGSKvLCGFGm5p+MbdNz0d4sqtkCkS7nEP/uceBFMOc+AqgdXa7vnx0HPQhLy6lneB8DjXtsEzEiDMedxVCtPQ0bEGMvIfi5edMEBtl6dLqBXhv7efcpYJPxwZNXrv7cubUqFAcRhqRlmcJo2YQkbtLvMzjKq+kZu1QYgabIlN+DCu8Oadns=
---

<div align="center">

<img src="docs/banner.svg" alt="moodle-mcp" width="100%">

# Moodle-Mcp
### AI 에이전트가 실제로 쓸 수 있는 Moodle

Moodle Web Service API에서 과제, 마감일, 강의 자료를 직접 가져옵니다. 브라우저도, 스크레이퍼도, 페이지 클릭도 필요 없습니다.

<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-yellow.svg" alt="MIT License"></a>
<img src="https://img.shields.io/badge/python-3.8%2B-3772FF?logo=python&logoColor=white" alt="Python 3.8+">
<img src="https://img.shields.io/badge/MCP-2024--11--05-8A2BE2" alt="MCP 2024-11-05">
<img src="https://img.shields.io/badge/Moodle-3.x%20%7C%204.x-F98012?logo=moodle&logoColor=white" alt="Moodle 3.x / 4.x">
<img src="https://img.shields.io/badge/dependencies-0-success" alt="의존성 없음">
<a href="https://github.com/Faixiang/moodle-mcp/stargazers"><img src="https://img.shields.io/github/stars/Faixiang/moodle-mcp?style=social" alt="GitHub stars"></a>

<p>
<a href="README.md">English</a> ·
<a href="README.zh-CN.md">简体中文</a> ·
<a href="README.zh-TW.md">繁體中文</a> ·
<a href="README.ja.md">日本語</a> ·
<b>한국어</b> ·
<a href="README.es.md">Español</a> ·
<a href="README.fr.md">Français</a> ·
<a href="README.de.md">Deutsch</a> ·
<a href="README.pt-BR.md">Português</a> ·
<a href="README.ru.md">Русский</a>
</p>

</div>

## 미리보기 🖥️

<img src="docs/preview.svg" alt="MCP 세션 예시" width="100%">

---

## 왜 필요한가 🎯

Moodle은 전 세계 대학의 학습 플랫폼이지만, 범용 MCP 서버는 오랫동안 없었습니다. 헤드리스 브라우저 수집은 느리고 잘 깨지며 WAF에 차단되기 쉽습니다. 반면 Moodle 자체에는 안정적이고 문서화된 REST API가 있습니다.

이 프로젝트가 바로 그 빠진 계층입니다. **의존성 없는 Python 파일 하나, 읽기 전용 도구 여섯 개**. Web Services가 켜진 Moodle 3.x/4.x라면 어디든 동작합니다.

```text
pip 설치 없음. node 없음. 브라우저 없음. 그냥 python server.py.
```

## 주요 기능 ✨

### 데이터 수집
- **마감일을 그대로 읽는다** — 과제를 «곧 마감» «기한 초과» «여유 있음»으로 자동 분류하고 남은 일수까지 계산
- **주간 다이제스트** — 신규 콘텐츠 + 마감 임박 + 기한 초과를 한 번에 받아 바로 읽을 수 있는 형태로 정리
- **강의 자료** — 섹션 구조와 파일 목록, 다운로드 직링크와 수정 시각 포함. 메타데이터만 반환하고 파일은 내려받지 않음
- **내장 진단** — `moodle_site_info`가 사이트 버전, 계정 정보, 그리고 Token으로 실제 호출 가능한 함수 목록을 보고

### 구현
- **의존성 제로** — Python 표준 라이브러리(`urllib`, `json`, `ssl`)만 사용해 환경을 오염시키지 않음
- **단일 파일** — `server.py`를 복사하면 어디서든 실행. 패키지 구조도 빌드 단계도 없음
- **stdio JSON-RPC 2.0** — Claude Desktop, Cursor, Marvis 및 모든 MCP 호환 클라이언트에 바로 연결
- **WAF 배려** — 요청을 직렬화하고 150 ms 간격 유지. Moodle을 계속 두드리면 `502`만 돌아옵니다
- **설계부터 읽기 전용** — 제출, 수강신청, 편집, 삭제 코드가 존재하지 않음

## 도구 🧰

| 도구 | 역할 | 인자 |
|---|---|---|
| `moodle_site_info` | Token을 검증하고 사이트 이름, Moodle 버전, 현재 사용자, 사용 가능한 함수 목록을 반환합니다(진단용). | — |
| `moodle_list_courses` | 수강 중인 모든 강좌를 나열합니다. 강좌 ID, 약칭, 전체 이름 포함. | — |
| `moodle_recent_updates` | 최근 N일 내 추가·변경된 항목(과제, 파일, 공지)을 최신순으로 반환합니다. | `days`(기본 7), `course_ids` |
| `moodle_pending_assignments` | 미제출 과제를 **마감 임박** / **기한 초과** / **여유 있음**으로 분류하고 마감 시각과 남은 일수를 표시합니다. | `ahead_days`(기본 14), `course_ids` |
| `moodle_course_files` | 한 강좌의 섹션 구조와 파일 목록, 다운로드 직링크·수정 시각 포함. **메타데이터만 반환하며 파일은 내려받지 않습니다.** | `course_id` |
| `moodle_weekly_digest` | 한 번에 요약: 신규 + 마감 임박 + 기한 초과 + 통계. 시작점으로 권장합니다. | `days`(기본 7), `ahead_days`(기본 14) |

## 요구 사항 📦

| 항목 | 내용 |
|---|---|
| Python | 3.8 이상(표준 라이브러리만) |
| MCP 프로토콜 | `2024-11-05` |
| Moodle | 3.x / 4.x, Web Services와 REST 프로토콜 활성화 필요 |
| 계정 | `webservice/rest:use` 권한 보유 |
| 검증 환경 | Moodle 4.3.6, 435개 함수가 부여된 계정(전체 권한) |

## 빠른 시작 🚀

### ① Token 발급

Moodle은 개인 액세스 키가 필요합니다. 사이트 상황에 따라 하나를 선택하세요.

**A. 웹 UI(권장, SSO 계정도 가능)**

1. Moodle 사이트에 로그인
2. 프로필 사진 → *환경설정* → *계정* → *보안* → *액세스 키 관리*
3. «만들기»를 누르고 이름에 `moodle-mcp`, 서비스에 *Moodle mobile web service* 선택
4. 생성된 키를 복사

**B. 스크립트로 모바일 서비스 사용(사이트에 로컬 비밀번호가 남아 있을 때만)**

```bash
python get_token.py
```

`/login/token.php`와 `moodle_mobile_app` 서비스로 Token을 받아 즉시 검증합니다. 비밀번호는 화면에 표시되지 않고 로그에도 남지 않습니다. SSO 전용 계정은 `invalidlogin`이 반환되므로 A 방법을 사용하세요.

**C. 환경 변수**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### ② 설정

`server.py`와 같은 디렉터리에 `config.json`을 만듭니다(`config.example.json` 복사 가능).

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

환경 변수가 설정 파일보다 우선합니다.

### ③ 서버 등록

Claude Desktop / Cursor(`mcp.json`):

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

`args`에는 `server.py`의 절대 경로를 넣으세요. Python이 여러 개라면 `command`를 인터프리터 전체 경로로 지정합니다.

### ④ 검증

클라이언트에서 `moodle_site_info`를 호출하세요. 설정이 맞으면 사이트 이름, Moodle 버전, 사용자 정보가 반환됩니다. 실패하면 아래 «자주 묻는 질문»을 확인하세요.

## 설정 참조 ⚙️

| 키 | 형식 | 필수 | 설명 |
|---|---|---|---|
| `url` / `MOODLE_URL` | 문자열 | 예 | Moodle 사이트 루트 URL(끝에 경로 없음) |
| `token` / `MOODLE_TOKEN` | 문자열 | 예 | «액세스 키 관리»에서 만든 개인 Token |
| `config.json` | 파일 | 선택 | `server.py`와 같은 디렉터리에서 읽음 |

우선순위: 환경 변수 → `config.json` → 오류.

## 사용 예시 💬

> «이번 주에 아직 안 한 과제 뭐야?»

에이전트가 `moodle_weekly_digest`를 호출해 바로 읽을 수 있는 요약을 받습니다.

```text
## 7일 내 마감·미제출
| CIS225 Data Structures | A10021 Crosswords  | 2026-10-29 23:59 | 3일 남음 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3일 남음 |

## 기한 초과
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15일 초과 |

## 통계
제출/채점 완료: 51 ｜ 미제출 합계: 25(마감 임박 4, 초과 14, 기타 7)
```

그 밖에 쓸 만한 지시:

| 발화 | 호출되는 도구 |
|---|---|
| «CIS225에 이번 주 새 자료 있어?» | `moodle_recent_updates` |
| «GER405 파일 목록만 보여줘, 다운로드는 하지 마» | `moodle_course_files` |
| «기한 초과가 없는 강좌는?» | `moodle_pending_assignments` |
| «내 Token 아직 유효해?» | `moodle_site_info` |

## 자주 묻는 질문 🤔

<details>
<summary><b>get_token.py가 <code>invalidlogin</code>을 반환</b></summary>

계정이 SSO/OIDC 전용이라 `/login/token.php`가 검증할 로컬 비밀번호가 없습니다. A 방법으로 «액세스 키 관리»에서 Token을 직접 생성하세요.
</details>

<details>
<summary><b>호출 시 <code>502</code>가 나오거나 연결이 끊김</b></summary>

사이트 WAF의 속도 제한입니다. 이 서버는 직렬화와 150 ms 간격을 적용하고 있으며, 그래도 발생하면 몇 분 기다린 뒤 재시도하고 여러 도구를 동시에 호출하지 마세요.
</details>

<details>
<summary><b>도구가 빈 목록을 반환</b></summary>

세 가지를 순서대로 확인하세요. Web Services와 REST가 켜져 있는지, 계정에 `webservice/rest:use`가 있는지, `course_ids` 필터가 올바른지. 먼저 `moodle_site_info`를 실행해 보세요. 함수 목록이 매우 짧다면 관리자가 모바일용 하위 집합만 개방한 것입니다.
</details>

<details>
<summary><b>Turnitin이나 quiz 마감일이 보이지 않음</b></summary>

정상 동작입니다. `turnitintooltwo`와 `quiz`는 독립 모듈로 `mod_assign`의 의미론을 갖지 않아 읽을 수 없습니다. 웹 UI에서 확인하세요.
</details>

<details>
<summary><b>마감일이 «not set»으로 표시됨</b></summary>

교수자가 해당 과제에 마감일을 설정하지 않아 계산할 값이 없습니다. 누락을 막기 위해 과제 자체는 목록에 남깁니다.
</details>

<details>
<summary><b>Windows 터미널에서 한글이 깨짐</b></summary>

출력은 UTF-8입니다. 구형 콘솔에서는 `chcp 65001`을 실행하거나 Windows Terminal을 사용하세요.
</details>

## 보안 🔒

- Token은 **자격 증명**입니다. `config.json`이나 환경 변수에만 두고 저장소에 커밋하지 마세요. `.gitignore`가 `config.json`과 `get_token.log`를 제외합니다.
- `get_token.py`는 비밀번호 내용을 기록하지 않고 길이만 남기며, 입력은 `getpass`를 사용합니다.
- 모든 도구는 읽기 전용입니다. Token이 유출되어도 이 서버로 과제를 수정·삭제할 수 없습니다. 유출 시 «액세스 키 관리»에서 폐기하세요.
- 통신 캡처를 공개하지 마세요. `wstoken`이 요청 본문에 포함됩니다.

## 호환성 ✅

| 클라이언트 / 플랫폼 | 상태 |
|---|---|
| Claude Desktop | 지원(stdio 서버 항목) |
| Cursor | 지원(`mcp.json`) |
| Marvis | 지원(MCP 레지스트리) |
| 기타 MCP 클라이언트 | 지원 — 표준 JSON-RPC 2.0 over stdio |
| Windows / macOS / Linux | 지원 — 플랫폼 종속 코드 없음 |

## 로드맵 🗺️

- [ ] API가 허용하는 범위에서 Turnitin과 quiz 마감일 지원
- [ ] 대형 강좌 목록의 왕복을 줄이는 선택적 로컬 캐시
- [ ] 수강 강좌가 매우 많은 계정을 위한 페이지 분할 안내
- [ ] 제출 **상태** 세부 정보(채점 완료/피드백 있음) — 읽기 전용 유지
- [ ] 동일한 도구면을 비 Moodle LMS로 확장

## 기여 🤝

이슈와 풀 리퀘스트를 환영합니다. 서버는 파일 하나뿐이고 `server.py`는 몇 분이면 다 읽힙니다.

- 의존성 제로 유지(표준 라이브러리만).
- 모든 도구는 읽기 전용으로 유지.
- `config.json`, Token, 통신 캡처는 절대 커밋하지 않기.
- 도구를 추가하면 도구 표와 **모든 언어** README를 함께 갱신.

## 피드백 📢

버그와 기능 제안은 [이슈를 남겨 주세요](https://github.com/Faixiang/moodle-mcp/issues).

## 라이선스 📝

MIT — [LICENSE](LICENSE) 참고.
*（内容由AI生成，仅供参考）*
