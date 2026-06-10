# Current State

## 현재 단계
Phase 4 검증 완료 — 자율 주행 루프(autopilot/strategy/thumbnail/schedule) 구조·API·프론트 전체 검증됨.
다음: ANTHROPIC_API_KEY 입력 → 실제 스크립트 생성 → 영상 촬영 → 첫 발행 → analytics 수집 → 전략 루프 1회전

## 완료된 산출물

### Phase 1 (2026-06-03)
- requirements.txt / .env.example / .gitignore
- 전체 디렉토리 구조, llm-wiki/ 6개 문서, templates/ 3개
- agents/ (content_agent, seo_agent, upload_agent, bucky_sync_agent, claude_runner)
- main.py (CLI: generate / upload / list-episodes / sync)
- content/source-notes/ep001.md

### Phase 2 (2026-06-05)
- dashboard/api/main.py — FastAPI 서버 (포트 8000)
- dashboard/api/routes/pipeline.py — 에피소드 파이프라인 API
- dashboard/api/routes/youtube.py — YouTube 통계 + 업로드 API
- dashboard/frontend/ — React + Vite (포트 5173)
  - PipelineView — 5단계 파이프라인 현황
  - YouTubeStats — 채널 통계 카드
  - EpisodeManager — 에피소드 목록 + 생성/업로드 액션

### Phase 3 (2026-06-06) — 진행 중
- agents/analytics_agent.py — YouTube Analytics API 수집 + 로컬 집계 폴백
- dashboard/api/routes/bucky.py — Bucky 상태 / 동기화 / Analytics 라우트
- dashboard/api/main.py — bucky 라우터 등록
- llm-wiki/google-cloud-setup.md — Google Cloud 1회성 설정 가이드
- .env.example — PYTHONUTF8=1 추가 (Windows 한글 인코딩 문제 해결)
- mock 테스트 통과: episode_001.md + episode_001_seo.json 생성 확인

### Phase 4 (2026-06-10) — 에이전트 주행 강화
- agents/strategy_agent.py — Analytics 피드백 루프 (성과 → 다음 에피소드 주제 3개 제안)
- agents/thumbnail_agent.py — 썸네일 텍스트 브리프 생성 (시안 3개, 이미지 생성 없음)
- main.py autopilot — 동기화→노트 자동 선택→스크립트→SEO→썸네일 브리프 원커맨드 주행
- main.py strategy / thumbnail / schedule — 전략 분석 / 브리프 / 주간 자동 분석 스케줄러
- dashboard/api/routes/strategy.py — 전략/썸네일/autopilot API
- dashboard/frontend StrategyPanel — "콘텐츠 전략" 탭 (전략 카드 + 🚀 에이전트 주행 버튼)
- 검증 완료: autopilot --mock, strategy --mock, thumbnail --mock, API TestClient, tsc + vite build 통과
- 원칙 유지: 업로드는 autopilot/schedule에 포함되지 않음 — 기존 승인 플로우만 사용

## 실행 방법

### 백엔드 (FastAPI)
```bash
cd D:\ai프로젝트\유튜브자동화시작하기
python -m uvicorn dashboard.api.main:app --reload --port 8000
```

### 프론트엔드 (React)
```bash
cd D:\ai프로젝트\유튜브자동화시작하기\dashboard\frontend
npm run dev
```
→ http://localhost:5173 에서 대시보드 확인

### CLI 파이프라인
```bash
# .env 없이 구조 검증 (mock)
python -X utf8 main.py generate --note content/source-notes/ep001.md --mock

# 실제 스크립트 생성 (API 키 설정 후)
python -X utf8 main.py generate --note content/source-notes/ep001.md

# 에피소드 목록
python -X utf8 main.py list

# 에이전트 주행 (노트 자동 선택 → 스크립트 → SEO → 썸네일 브리프)
python -X utf8 main.py autopilot          # --mock 으로 구조 검증 가능

# 성과 분석 → 다음 콘텐츠 방향 제안
python -X utf8 main.py strategy

# 썸네일 브리프만 재생성
python -X utf8 main.py thumbnail --episode 001

# 주간 자동 분석 (매주 월 09:00 Analytics + 전략 갱신)
python -X utf8 main.py schedule
```

> `.env`에 `PYTHONUTF8=1` 설정 시 `-X utf8` 플래그 생략 가능

## API 엔드포인트
- GET  /api/health
- GET  /api/pipeline/episodes — 에피소드 목록
- GET  /api/pipeline/summary  — 파이프라인 단계별 카운트
- POST /api/pipeline/generate — 스크립트 생성 (백그라운드 실행)
- GET  /api/pipeline/job/{id} — 생성 작업 상태 폴링
- GET  /api/youtube/stats     — 채널 통계 (credentials 없으면 미연결 반환)
- GET  /api/youtube/upload-preview/{ep} — 업로드 미리보기
- POST /api/youtube/upload/{ep} — 업로드 확인 실행
- GET  /api/bucky/status      — Bucky vault 연결 상태 + 노트 목록
- POST /api/bucky/sync        — Obsidian → source-notes 동기화
- GET  /api/bucky/analytics/latest — 최근 Analytics 리포트
- POST /api/bucky/analytics/collect — YouTube 성과 데이터 수집
- GET  /api/strategy/latest — 최근 콘텐츠 전략 제안
- POST /api/strategy/run — 전략 분석 실행 (백그라운드)
- GET/POST /api/strategy/thumbnail/{ep} — 썸네일 브리프 조회/생성
- POST /api/strategy/autopilot — 에이전트 주행 실행 (업로드 미포함)
- GET  /api/strategy/job/{id} — 전략/주행 작업 상태 폴링

## 다음 작업 (사용자 직접 수행 필요)

### 즉시 실행 가능 (API 키 설정 후)
1. `.env` 파일에 아래 항목 입력:
   - `ANTHROPIC_API_KEY=sk-ant-...` (B안) 또는 `GENERATION_MODE=cli` 유지 (A안)
   - `YOUTUBE_CHANNEL_ID=UCxxx...`
2. EP002 실제 스크립트 생성:
   ```bash
   python -X utf8 main.py generate --note content/source-notes/ep002.md
   ```
3. `llm-wiki/google-cloud-setup.md` 절차로 credentials.json 발급

### 촬영·발행 플로우
4. EP001 또는 EP002 촬영 → `content/queue/`에 mp4 배치
5. 업로드 승인:
   ```bash
   python -X utf8 main.py upload --episode 001
   ```
6. 발행 후 analytics 수집: `python -X utf8 main.py strategy` (실제 성과 기반 주제 제안)

### 장기 운영
7. 스케줄러 상시 실행: `python -X utf8 main.py schedule`

## 리스크
- YouTube OAuth credentials.json 미설정 시 upload 불가 (대시보드는 graceful 처리)
- GENERATION_MODE=cli 기본값 — Claude CLI 세션 필요
- GENERATION_MODE=api 전환 시 ANTHROPIC_API_KEY 필요
- Windows 터미널에서 한글 + 특수문자 출력 시 cp949 오류 → python -X utf8 또는 PYTHONUTF8=1 필수
