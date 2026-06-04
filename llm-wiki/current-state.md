# Current State

## 현재 단계
Phase 2 완료 — FastAPI 대시보드 + React UI 실행 가능

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

## API 엔드포인트
- GET  /api/health
- GET  /api/pipeline/episodes — 에피소드 목록
- GET  /api/pipeline/summary  — 파이프라인 단계별 카운트
- POST /api/pipeline/generate — 스크립트 생성 (백그라운드 실행)
- GET  /api/pipeline/job/{id} — 생성 작업 상태 폴링
- GET  /api/youtube/stats     — 채널 통계 (credentials 없으면 미연결 반환)
- GET  /api/youtube/upload-preview/{ep} — 업로드 미리보기
- POST /api/youtube/upload/{ep} — 업로드 확인 실행

## 다음 작업 (Phase 3 후보)
1. .env 설정 후 실제 스크립트 생성 테스트
2. Google Cloud Console credentials.json 설정
3. 에피소드 추가 및 파이프라인 전체 검증

## 리스크
- YouTube OAuth credentials.json 미설정 시 upload 불가 (대시보드는 graceful 처리)
- GENERATION_MODE=cli 기본값 — Claude CLI 세션 필요
- GENERATION_MODE=api 전환 시 ANTHROPIC_API_KEY 필요
