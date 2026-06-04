# 구현 계획: 프로슈테크 빌더 유튜브 자동화 시스템

## 프로젝트 한 줄 정의
비개발자 AI 성장 기록을 히스토리 영상 시리즈로 자동 제작·업로드하고, Bucky 에이전트와 연동하여 장기 운영 가능한 유튜브 자동화 대시보드 구축

---

## 마스터 하네스 구조

```
[사용자 입력/트리거]
        │
        ▼
[Main Harness: main.py]
  ├── Content Agent     → 노트 → 스크립트 생성
  ├── SEO Agent         → 제목/설명/태그 생성
  ├── Upload Agent      → YouTube API 업로드
  ├── Analytics Agent   → 성과 데이터 수집
  └── Bucky Sync Agent  → Obsidian vault 동기화
        │
        ▼
[대시보드 API: FastAPI]
        │
        ▼
[대시보드 UI: React]
```

---

## 서브에이전트 업무분장

### Main Harness (`main.py`)
- 입력: CLI 명령 또는 대시보드 API 요청
- 출력: 파이프라인 실행 결과 + llm-wiki/current-state.md 업데이트
- 연결: 모든 서브에이전트 순차 호출

### Content Agent (`agents/content_agent.py`)
- 입력: `content/source-notes/` 마크다운 파일
- 출력: `content/scripts/episode_NNN.md`
- 도구: Anthropic SDK, claude-sonnet-4-6
- 금지: 파일 없이 실행, 토큰 무제한 사용

### SEO Agent (`agents/seo_agent.py`)
- 입력: 스크립트 파일 (`content/scripts/episode_NNN.md`)
- 출력: `content/scripts/episode_NNN_seo.json`
- 도구: Anthropic SDK
- 포함: 제목(60자 이내), 설명(500자), 태그 10개, 해시태그 5개

### Upload Agent (`agents/upload_agent.py`)
- 입력: 영상 파일 경로 + SEO JSON
- 출력: YouTube video_id + URL → `content/published/` 기록
- 도구: google-api-python-client, YouTube Data API v3
- 필수: 업로드 전 사용자 승인 프롬프트

### Analytics Agent (`agents/analytics_agent.py`)
- 입력: `content/published/` 기록
- 출력: `content/analytics/report_YYYYMMDD.json`
- 도구: YouTube Analytics API
- 주기: 주 1회 자동 실행 (APScheduler)

### Bucky Sync Agent (`agents/bucky_sync_agent.py`)
- 입력: `G:\내 드라이브\obsidian-agent-brain-system\` 경로
- 출력: `content/source-notes/` 동기화 파일
- 도구: Python watchdog, shutil
- 동기화 대상: 성장기 기록 노트 (태그: #youtube 또는 #성장기)

---

## 파일 구조

```
D:\ai프로젝트\유튜브자동화시작하기\
├── .env                            # API 키 (절대 커밋 금지)
├── .gitignore
├── requirements.txt
├── main.py                         # 메인 하네스 + CLI
│
├── agents/
│   ├── __init__.py
│   ├── content_agent.py
│   ├── seo_agent.py
│   ├── upload_agent.py
│   ├── analytics_agent.py
│   └── bucky_sync_agent.py
│
├── dashboard/
│   ├── api/
│   │   ├── main.py                 # FastAPI 앱
│   │   └── routes/
│   │       ├── pipeline.py         # 파이프라인 상태
│   │       ├── youtube.py          # YouTube 통계
│   │       └── bucky.py            # Bucky 동기화
│   └── frontend/                   # React + Vite
│       ├── package.json
│       └── src/
│           ├── App.tsx
│           ├── components/
│           │   ├── PipelineView.tsx
│           │   ├── YouTubeStats.tsx
│           │   └── EpisodeManager.tsx
│           └── pages/
│
├── content/
│   ├── source-notes/               # Bucky에서 동기화된 성장 노트
│   ├── scripts/                    # 생성된 스크립트 + SEO
│   ├── queue/                      # 영상 파일 + 메타데이터 (업로드 대기)
│   ├── published/                  # 발행 완료 기록 JSON
│   └── analytics/                  # 분석 리포트
│
├── llm-wiki/
│   ├── project-overview.md
│   ├── agent-registry.md
│   ├── current-state.md
│   ├── decision-log.md
│   ├── validation-log.md
│   └── handoff-prompt.md
│
└── templates/
    ├── episode_script.md           # 스크립트 생성 프롬프트 템플릿
    ├── seo_template.json           # SEO 출력 구조
    └── series_guide.md             # 시리즈 구성 가이드
```

---

## MVP 우선순위 (Phase 1 — 1~2주)

### Step 1: 프로젝트 초기화
- [x] 파일 구조 생성
- [ ] `.env` 키 설정 가이드 작성
- [ ] `requirements.txt` 작성
- [ ] `llm-wiki/` 문서 초기화

### Step 2: 콘텐츠 파이프라인 (CLI)
- [ ] `templates/episode_script.md` — 스크립트 생성 프롬프트 작성
- [ ] `agents/content_agent.py` — 노트 → 스크립트 변환
- [ ] `agents/seo_agent.py` — SEO 메타데이터 생성
- [ ] `main.py` — CLI: `python main.py generate --note <파일>`

### Step 3: YouTube 업로드 연동
- [ ] Google Cloud 프로젝트 설정 가이드
- [ ] `agents/upload_agent.py` — YouTube Data API v3
- [ ] OAuth 2.0 토큰 관리 (`token.json` 로컬 저장)
- [ ] CLI: `python main.py upload --episode 001`

### Step 4: 첫 히스토리 영상 테스트
- [ ] 성장기 Episode 001 노트 작성
- [ ] 스크립트 생성 실행
- [ ] SEO 생성 실행
- [ ] 테스트 업로드 (비공개)

---

## Phase 2 — 대시보드 (2~3주)

- [ ] FastAPI 서버 (`dashboard/api/`)
- [ ] React 대시보드 (`dashboard/frontend/`)
  - 파이프라인 뷰 (대기/생성/검토/예약/발행)
  - YouTube 최신 통계
  - 에피소드 목록 + 관리
- [ ] APScheduler — 분석 주간 자동 실행

---

## Phase 3 — Bucky 연동 + 고도화 (4주~)

- [ ] `agents/bucky_sync_agent.py` — Obsidian 동기화
- [ ] Analytics 피드백 루프 (성과 → 다음 콘텐츠 방향)
- [ ] 썸네일 브리프 생성 (텍스트 프롬프트 → 직접 제작 가이드)
- [ ] 대시보드 Bucky 상태 뷰 추가

---

## LLM Wiki 문서 역할

### `/llm-wiki/project-overview.md`
- 채널 정체성 (프로슈테크 빌더)
- 핵심 시청자 정의
- 콘텐츠 축 (4단계)
- 운영 원칙

### `/llm-wiki/agent-registry.md`
- 에이전트 목록 + 책임 + 입력 + 출력
- 중복 금지 기준

### `/llm-wiki/current-state.md`
- 현재 파이프라인 단계
- 완료된 에피소드 목록
- 다음 작업
- 보류 중인 결정

### `/llm-wiki/decision-log.md`
- 채널/콘텐츠/자동화 결정 기록
- 결정 사유 포함

### `/llm-wiki/validation-log.md`
- Codex 검증 결과
- 비개발자 운영 가능성 점검

### `/llm-wiki/handoff-prompt.md`
- 다음 세션 시작 프롬프트 (항상 최신 유지)
- 현재 목표 + 완료 항목 + 다음 작업

---

## Handoff 구조

다음 세션 시작 시:
```
"llm-wiki/handoff-prompt.md 를 읽고 현재 단계부터 이어서 진행해줘"
```

---

## 차단 요소

- Make.com / n8n 사용 금지
- 영상 자동 편집 (복잡도 초과 — Phase 3 이후 실험적으로만)
- 사용자 승인 없이 자동 업로드 (반드시 수동 승인 단계 유지)
- SNS 자동 크로스포스팅 (MVP 외)
- 썸네일 자동 생성 (MVP에서는 텍스트 브리프만)

---

## Codex 검증 범위

- 각 에이전트 독립 실행 가능 여부
- YouTube API 오류 처리 (401, 403, quota 초과)
- `.env` 키 코드 내 하드코딩 여부
- Claude API max_tokens 설정 여부
- 업로드 전 사용자 승인 단계 존재 여부
- 비개발자가 CLI 없이 대시보드만으로 운영 가능한지

---

## 환경 설정 요건 (.env)

```
# Anthropic
ANTHROPIC_API_KEY=

# YouTube / Google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
YOUTUBE_CHANNEL_ID=

# Bucky
BUCKY_VAULT_PATH=G:\내 드라이브\obsidian-agent-brain-system\

# 경로
CONTENT_BASE_PATH=D:\ai프로젝트\유튜브자동화시작하기\content
```

---

## 착수용 작업지시서

### 즉시 실행 (Step 1)
```
1. requirements.txt 생성
   anthropic, google-api-python-client, google-auth-oauthlib,
   fastapi, uvicorn, apscheduler, watchdog, python-dotenv

2. llm-wiki/ 문서 6개 초기화

3. templates/episode_script.md 작성
   (스크립트 생성용 Claude 프롬프트 템플릿)

4. agents/content_agent.py 구현
   입력: 노트 파일 경로
   출력: content/scripts/episode_NNN.md

5. agents/seo_agent.py 구현
   입력: 스크립트 파일
   출력: content/scripts/episode_NNN_seo.json

6. main.py CLI 구현
   python main.py generate --note source-notes/ep001.md
```

### Google API 설정 (병행 작업)
```
1. console.cloud.google.com → 새 프로젝트 생성
2. YouTube Data API v3 활성화
3. YouTube Analytics API 활성화
4. OAuth 2.0 클라이언트 ID 생성 (Desktop app)
5. credentials.json 다운로드 → 프로젝트 루트에 저장
```

---

## 평가 체크리스트 (Kai)

- [x] 비개발자 운영 가능한 구조인가?
- [x] Make.com/n8n 없이 구현 가능한가?
- [x] 사용자 승인 없이 자동 업로드되지 않는가?
- [x] 에이전트 역할 중복이 없는가?
- [x] 세션 간 handoff 구조가 있는가?
- [x] MVP 범위가 2주 내 구현 가능한가?
- [x] .env에 모든 비밀키가 분리되어 있는가?
- [x] Codex 검증 범위가 명확한가?
- [ ] Google Cloud 설정 가이드가 포함되어야 함 (착수 전 추가 필요)
- [ ] 첫 에피소드 노트 소스가 준비되어야 함 (사용자 작성 필요)
