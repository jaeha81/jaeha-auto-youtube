# Google Cloud 설정 가이드

YouTube Data API v3 + YouTube Analytics API를 사용하기 위한 1회성 설정 절차.

---

## 1단계 — Google Cloud 프로젝트 생성

1. [console.cloud.google.com](https://console.cloud.google.com) 접속 (Google 계정 로그인)
2. 상단 프로젝트 선택 드롭다운 → **새 프로젝트**
3. 프로젝트 이름: `prosutech-youtube` (자유 지정)
4. **만들기** 클릭 → 프로젝트 활성화 대기 (수 초)

---

## 2단계 — API 활성화

1. 좌측 메뉴 → **API 및 서비스** → **라이브러리**
2. 검색창에 `YouTube Data API v3` 검색 → **사용 설정**
3. 다시 라이브러리로 돌아와 `YouTube Analytics API` 검색 → **사용 설정**

---

## 3단계 — OAuth 동의 화면 구성

1. **API 및 서비스** → **OAuth 동의 화면**
2. User Type: **외부** 선택 → **만들기**
3. 앱 이름: `프로슈테크 빌더` / 사용자 지원 이메일: 본인 이메일 입력
4. 개발자 연락처 이메일: 본인 이메일 입력 → **저장 후 계속**
5. 범위(Scopes) 페이지: **저장 후 계속** (기본값 유지)
6. 테스트 사용자: **+ 사용자 추가** → 본인 Google 계정 이메일 추가 → **저장 후 계속**

> **중요**: 앱을 "프로덕션" 상태로 게시하지 않아도 테스트 사용자로 등록하면 본인은 사용 가능.

---

## 4단계 — OAuth 2.0 클라이언트 ID 생성

1. **API 및 서비스** → **사용자 인증 정보**
2. **+ 사용자 인증 정보 만들기** → **OAuth 클라이언트 ID**
3. 애플리케이션 유형: **데스크톱 앱**
4. 이름: `youtube-automation` → **만들기**
5. 팝업에서 **JSON 다운로드** 클릭
6. 다운로드된 파일을 아래 경로로 이동/이름 변경:

```
D:\ai프로젝트\유튜브자동화시작하기\credentials.json
```

> `credentials.json`은 `.gitignore`에 포함됨 — 절대 커밋 금지.

---

## 5단계 — .env 파일 설정

```bash
# .env.example → .env 복사
copy .env.example .env
```

`.env` 파일을 열어 아래 값 입력:

```
GOOGLE_CLIENT_ID=<credentials.json의 client_id 값>
GOOGLE_CLIENT_SECRET=<credentials.json의 client_secret 값>
YOUTUBE_CHANNEL_ID=<YouTube 채널 ID>
```

### YouTube 채널 ID 확인 방법
1. YouTube Studio (studio.youtube.com) 접속
2. 좌측 메뉴 → **설정** → **채널** → **고급 설정**
3. "채널 ID" 항목 복사 (`UC`로 시작하는 24자리 문자열)

---

## 6단계 — 최초 인증 (토큰 발급)

credentials.json 설정 후 첫 실행 시 브라우저 창이 열립니다:

```bash
python main.py upload --episode 001
```

또는 대시보드의 **YouTube 연결** 버튼 클릭.

1. 브라우저에서 Google 계정 선택
2. "Google이 확인하지 않은 앱" 경고 → **고급** → **프로슈테크 빌더(안전하지 않음)으로 이동** 클릭
3. 권한 허용
4. 자동으로 `token.json` 생성됨 → 이후 재인증 불필요

> `token.json`도 `.gitignore`에 포함됨 — 절대 커밋 금지.

---

## 확인 명령어

```bash
# YouTube API 연결 상태 확인
python -c "from agents.upload_agent import check_credentials; check_credentials()"

# Analytics API 테스트
python -c "from agents.analytics_agent import collect_analytics; collect_analytics()"
```

또는 대시보드 (http://localhost:5173) → Bucky 탭 → **Analytics 수집** 버튼

---

## 문제 해결

| 오류 | 원인 | 해결 |
|------|------|------|
| `credentials.json not found` | 파일 위치 오류 | 프로젝트 루트에 있는지 확인 |
| `redirect_uri_mismatch` | OAuth 설정 오류 | 애플리케이션 유형이 **데스크톱 앱**인지 확인 |
| `quota exceeded` | API 일일 한도 초과 | 다음 날 재시도 (무료 할당량: 업로드 6회/일) |
| `access_denied` | 테스트 사용자 미등록 | OAuth 동의 화면 → 테스트 사용자에 이메일 추가 |
| `invalid_grant` | token.json 만료 | `token.json` 삭제 후 재인증 |

---

## 완료 체크리스트

- [ ] credentials.json 프로젝트 루트에 저장됨
- [ ] .env 파일에 YOUTUBE_CHANNEL_ID 입력됨
- [ ] OAuth 동의 화면에 본인 이메일이 테스트 사용자로 등록됨
- [ ] `python main.py upload --episode 001` 실행 시 브라우저 인증 성공
- [ ] token.json 자동 생성됨
