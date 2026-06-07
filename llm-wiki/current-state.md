# Current State

## 현재 단계
Phase 3 진행 중 — 스크립트 생성 파이프라인 검증 완료, 다음: 영상 촬영 → 업로드 테스트

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

## 다음 작업 (사용자 직접 수행 필요)
1. `.env.example` → `.env` 복사 후 API 키 입력
   - `PYTHONUTF8=1` (Windows 인코딩)
   - `ANTHROPIC_API_KEY` 또는 `GENERATION_MODE=cli` 유지
   - `YOUTUBE_CHANNEL_ID` 입력
2. `llm-wiki/google-cloud-setup.md` 절차대로 credentials.json 발급
3. 실제 스크립트 생성 테스트:
   ```bash
   python -X utf8 main.py generate --note content/source-notes/ep001.md
   ```
4. Episode 001 촬영 후 content/queue/ 에 영상 파일 배치
5. 업로드 테스트 (비공개):
   ```bash
   python -X utf8 main.py upload --episode 001
   ```

## 리스크
- YouTube OAuth credentials.json 미설정 시 upload 불가 (대시보드는 graceful 처리)
- GENERATION_MODE=cli 기본값 — Claude CLI 세션 필요
- GENERATION_MODE=api 전환 시 ANTHROPIC_API_KEY 필요
- Windows 터미널에서 한글 + 특수문자 출력 시 cp949 오류 → python -X utf8 또는 PYTHONUTF8=1 필수
