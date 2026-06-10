# Handoff Prompt

## 다음 세션 시작 시 이 문장을 그대로 붙여넣기

```
D:\ai프로젝트\유튜브자동화시작하기\llm-wiki\current-state.md 와
D:\ai프로젝트\유튜브자동화시작하기\plan.md 를 읽고
현재 단계에서 이어서 진행해줘.
프로슈테크 빌더 유튜브 자동화 시스템 프로젝트야.
Make.com/n8n 금지, 업로드 전 사용자 승인 필수, GENERATION_MODE 전환 구조 유지.
```

또는 Bucky를 통한 하달:
```
G:\내 드라이브\obsidian-agent-brain-system\ObsidianVault\03_Projects\유튜브자동화시작하기\project-packet.md
위 Bucky 패킷을 읽고 Phase 3 작업을 시작해줘.
```

---

## 현재 목표
Phase 4: 에이전트 주행 실운영 검증 (autopilot 실행 → 첫 영상 발행 → 성과 수집 → strategy 루프 가동)

## 완료된 작업

### Phase 1 MVP (2026-06-03)
- requirements.txt / .env.example / .gitignore / 전체 구조
- agents/ (content_agent, seo_agent, upload_agent, bucky_sync_agent, claude_runner)
- main.py — CLI (generate / upload / list-episodes / sync / --mock)
- content/source-notes/ep001.md — 샘플 노트

### Phase 2 대시보드 (2026-06-05)
- dashboard/api/main.py — FastAPI (포트 8000)
- dashboard/api/routes/pipeline.py, youtube.py
- dashboard/frontend/ — React + Vite (포트 5173)
  - PipelineView / YouTubeStats / EpisodeManager 컴포넌트
- 실행 확인: uvicorn 서버 OK, localhost:5173 대시보드 OK, 에피소드 목록 표시 OK

## 서버 실행 명령
```bash
# 터미널 1 (백엔드)
cd D:\ai프로젝트\유튜브자동화시작하기
python -m uvicorn dashboard.api.main:app --reload --port 8000

# 터미널 2 (프론트엔드)
cd D:\ai프로젝트\유튜브자동화시작하기\dashboard\frontend
npm run dev
```

## 완료된 작업 (Phase 4 — 2026-06-10)
- agents/strategy_agent.py — Analytics 피드백 루프 (성과 → 다음 주제 제안)
- agents/thumbnail_agent.py — 썸네일 텍스트 브리프 (시안 3개)
- main.py — autopilot / strategy / thumbnail / schedule 명령 추가
- dashboard/api/routes/strategy.py + 프론트 "콘텐츠 전략" 탭 (StrategyPanel)
- mock + API + 프론트 빌드 검증 통과

## 이어서 할 작업 (Phase 4 실운영 — 사람 직접 수행)
1. .env 파일에 ANTHROPIC_API_KEY 입력 (또는 GENERATION_MODE=cli 유지)
2. python main.py generate --note content/source-notes/ep002.md  (실제 스크립트 생성)
3. google-cloud-setup.md 절차로 credentials.json 발급 → YouTube API 연동
4. EP001 또는 EP002 촬영 → content/queue/ 배치 → python main.py upload --episode NNN (승인 후)
5. 발행 완료 후: python main.py strategy  (실제 성과 기반 전략 루프 1회전)
6. 장기 운영: python main.py schedule 상시 실행

## 에이전트가 이어서 할 수 있는 작업 (API 키 없어도 가능)
- 추가 에피소드 노트 초안 작성 (ep003.md~)
- 대시보드 UI 개선 (반응형, 다크모드 등)
- validation-log.md 기준으로 upload_agent 에러 처리 보강

## 금지할 반복 작업
- Phase 1, 2, 4 파일 재생성
- Make.com / n8n 관련 제안
- GENERATION_MODE 전환 구조 제거
- 사용자 승인 없는 자동 업로드 구현
