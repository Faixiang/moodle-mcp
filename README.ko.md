---
AIGC:
    Label: "1"
    ContentProducer: 001191440300708461136T1XGW3
    ProduceID: c6eb62ba6ec5a28db2139adf23a2fe4b_70da5a89d14e11f196c5525400248c00
    ReservedCode1: vlCzcQS8GHkvJCg6Q4zclVQD3rp287wPQV58vYp4pQyzbAbh3QrUJeR9Zu/8yc0RgpqI7hDNNhg9U3DiX8HNO/s6Dmq5PMGuS80FcPRgl5pTF6yyD9Mu0hKC6OpXcX5BuND4LaP5elpGZ+485+8IaDzXZJ9/vUG3qA6+LloN3F2lsw2SpvAd2Gse6VM=
    ContentPropagator: 001191440300708461136T1XGW3
    PropagateID: c6eb62ba6ec5a28db2139adf23a2fe4b_70da5a89d14e11f196c5525400248c00
    ReservedCode2: vlCzcQS8GHkvJCg6Q4zclVQD3rp287wPQV58vYp4pQyzbAbh3QrUJeR9Zu/8yc0RgpqI7hDNNhg9U3DiX8HNO/s6Dmq5PMGuS80FcPRgl5pTF6yyD9Mu0hKC6OpXcX5BuND4LaP5elpGZ+485+8IaDzXZJ9/vUG3qA6+LloN3F2lsw2SpvAd2Gse6VM=
---

# moodle-mcp

[English](README.md) · [简体中文](README.zh-CN.md) · [繁體中文](README.zh-TW.md) · [日本語](README.ja.md) · **한국어** · [Español](README.es.md) · [Français](README.fr.md) · [Deutsch](README.de.md) · [Português](README.pt-BR.md) · [Русский](README.ru.md)

**Moodle Web Service API**를 AI 에이전트가 바로 호출할 수 있는 MCP(Model Context Protocol) 서버로 감싼 것입니다. 브라우저도, 스크래퍼도, 페이지 클릭도 필요 없습니다.

Moodle은 전 세계 수많은 대학과 교육기관의 LMS를 떠받치고 있지만, 범용 MCP 서버는 없었습니다. 이 프로젝트가 그 빈틈을 채웁니다. 단일 파일, 의존성 없음, 6개 도구. Web Services가 켜진 Moodle 3.x/4.x라면 어느 사이트에서든 동작합니다.

> pip 패키지도, node도, 브라우저도 필요 없습니다. `python server.py` 하나면 됩니다.

## 왜 필요한가

에이전트는 강의계획서를 읽고 내일 마감인 과제를 알려줄 수 있습니다. 하지만 대부분의 강의 자료는 로그인 벽 뒤에 있습니다. 헤드리스 브라우저로 Moodle을 긁는 방식은 느리고 잘 깨지며 WAF에 걸리기 쉽습니다. Moodle 자체에 안정적이고 문서화된 REST API가 이미 있는데, 빠진 것은 MCP 래퍼뿐입니다.

이 서버는 파이썬 표준 라이브러리(`urllib`, `json`, `ssl`)만 사용하며, JSON-RPC 2.0 over stdio로 통신합니다. Claude Desktop, Cursor, Marvis 또는 MCP 호환 클라이언트에 그대로 연결할 수 있습니다.

## 도구

| 도구 | 설명 | 인자 |
|---|---|---|
| `moodle_site_info` | 토큰을 검증하고 사이트 이름, Moodle 버전, 현재 사용자, 사용 가능한 함수 목록을 반환합니다(진단용). | — |
| `moodle_list_courses` | 수강 중인 모든 강의를 강의 ID, 약칭, 전체 이름과 함께 나열합니다. | — |
| `moodle_recent_updates` | 최근 N일 내 추가·갱신된 항목(과제, 파일, 공지)을 최신순으로 반환합니다. | `days`(기본 7), `course_ids` |
| `moodle_pending_assignments` | 미제출 과제를 **마감 임박** / **기한 초과** / **여유** 세 가지로 분류하고 마감 시각과 남은 일수를 함께 표시합니다. | `ahead_days`(기본 14), `course_ids` |
| `moodle_course_files` | 강의 한 개의 섹션 구성과 파일 목록(다운로드 직링크, 수정 시각 포함). **메타데이터만 반환하며 파일은 전혀 내려받지 않습니다.** | `course_id` |
| `moodle_weekly_digest` | 한 번에 종합: 최근 갱신 + 마감 임박 + 기한 초과 + 통계. 시작점으로 권장합니다. | `days`(기본 7), `ahead_days`(기본 14) |

모든 도구는 **읽기 전용**입니다. 과제 제출, 수강 신청, 삭제, 편집 인터페이스는 의도적으로 제공하지 않습니다.

## 설치

### 1. 토큰 발급

Moodle은 개인 액세스 토큰이 필요합니다. 사이트 상황에 따라 하나를 선택하세요.

**A. 웹 UI(권장, SSO 계정도 가능)**

1. 사용하는 Moodle 사이트에 로그인
2. 프로필 사진 → *환경 설정* → *계정* → *보안* → *액세스 키 관리*
3. "만들기"를 누르고 이름에 `moodle-mcp`, 서비스에 *Moodle mobile web service* 선택
4. 생성된 키를 복사

**B. 스크립트로 모바일 서비스 사용(사이트에 로컬 비밀번호가 남아 있을 때만 가능)**

```bash
python get_token.py
```

스크립트는 `/login/token.php`와 `moodle_mobile_app` 서비스로 토큰을 교환하고 즉시 검증합니다. 비밀번호 입력은 화면에 표시되지 않고 로그에도 남지 않습니다. SSO 전용 계정이면 `invalidlogin`이 반환되므로 A 방법을 사용하세요.

**C. 환경 변수**

```bash
MOODLE_URL=https://moodle.your-school.edu
MOODLE_TOKEN=your_token_here
```

### 2. 설정

`server.py`와 같은 디렉터리에 `config.json`을 만듭니다.

```json
{
  "url": "https://moodle.your-school.edu",
  "token": "your_token_here"
}
```

환경 변수가 설정 파일보다 우선합니다.

### 3. 서버 등록

Claude Desktop / Cursor (`mcp.json`):

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

`args`에는 `server.py`의 절대 경로를 넣으세요. 파이썬이 여러 개 설치되어 있다면 `command`에 인터프리터 전체 경로를 지정합니다.

## 사용 예

> "이번 주에 아직 안 낸 과제 뭐 있어?"

에이전트가 `moodle_weekly_digest`를 호출하면 바로 읽을 수 있는 요약이 돌아옵니다.

```
## 향후 7일 내 마감·미제출
| 강의 | 과제 | 마감 | 남음 |
| CIS225 Data Structures | A10021 Crosswords | 2026-10-29 23:59 | 3일 |
| CIS225 Data Structures | A10022 Cow Jogging | 2026-10-29 23:59 | 3일 |

## 기한 초과
| CIS225 Data Structures | A10009 Dancing | 2026-10-11 23:59 | 15일 초과 |

## 통계
제출/채점 완료: 51 ｜ 미제출 합계: 25(임박 4, 초과 14, 기타 7)
```

## 알려진 제한

- **Turnitin(`turnitintooltwo`)과 `quiz` 모듈은 지원하지 않습니다.** 별도 모듈이라 `mod_assign` 의미론을 갖지 않으므로 마감은 웹에서 확인해야 합니다.
- 마감 시각이 설정되지 않은 과제는 "미설정"으로 표시됩니다.
- 주간 요약은 **미제출** 항목만 집계합니다. 제출했으나 채점되지 않은 항목은 통계 수치에는 들어가지만 표에는 나오지 않습니다.
- 일부 사이트의 WAF는 연속 요청에 `502`를 돌려줍니다. 이 서버는 요청 직렬화와 150ms 간격을 이미 적용했습니다. 그래도 발생하면 간격을 늘려 재시도하세요.
- 사이트에서 Web Services가 활성화되어 있고 계정에 `webservice/rest:use` 권한이 있어야 합니다. 대부분 사이트는 전체 함수를 허용하지만, 모바일용 일부만 여는 사이트도 있습니다.

## 보안

- 토큰은 **자격 증명**입니다. `config.json`이나 환경 변수에만 두고 저장소에 커밋하지 마세요. `.gitignore`에 `config.json`과 `get_token.log`가 이미 제외되어 있습니다.
- `get_token.py`는 비밀번호 내용을 기록하지 않고 길이만 남기며, 입력은 `getpass`를 사용합니다.
- 모든 도구가 읽기 전용이므로 토큰이 유출되어도 이 서버로는 과제를 수정하거나 삭제할 수 없습니다. 유출을 인지하면 "액세스 키 관리"에서 폐기하세요.
- 패킷 캡처를 공개하지 마세요. `wstoken`이 요청 본문에 포함됩니다.

## 호환성

| 항목 | 내용 |
|---|---|
| Python | 3.8+ (표준 라이브러리만 사용) |
| MCP 프로토콜 | `2024-11-05` |
| Moodle | 3.x / 4.x, Web Services와 REST 프로토콜 활성화 필요 |
| 검증 환경 | Moodle 4.3.6, 435개 함수가 허용된 계정(전체 권한) |

## 라이선스

MIT — [LICENSE](LICENSE) 참고.
*（内容由AI生成，仅供参考）*
