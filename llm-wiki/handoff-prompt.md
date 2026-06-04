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
Phase 3: 실제 운영 검증 (API 키 설정 → 실제 스크립트 생성 → 업로드 테스트)

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

## 이어서 할 작업 (Phase 3)
1. .env 설정: ANTHROPIC_API_KEY 또는 GENERATION_MODE=cli 확인
2. 실제 스크립트 생성 테스트 (python main.py generate --note content/source-notes/ep001.md)
3. Google Cloud Console: credentials.json 설정 → YouTube API 연동
4. 대시보드에서 업로드 플로우 전체 검증

## 금지할 반복 작업
- Phase 1, 2 파일 재생성
- Make.com / n8n 관련 제안
- GENERATION_MODE 전환 구조 제거
- 사용자 승인 없는 자동 업로드 구현
