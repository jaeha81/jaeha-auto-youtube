# Agent Registry

## Main Harness
- 파일: main.py
- 책임: 전체 파이프라인 조율, CLI 진입점
- 입력: CLI 명령 (generate / upload / analytics / sync)
- 출력: 파이프라인 실행 결과 + current-state.md 업데이트
- 연결: 모든 서브에이전트 순차 호출

## Content Agent
- 파일: agents/content_agent.py
- 책임: 성장기 노트 → 영상 스크립트 변환
- 입력: content/source-notes/ 마크다운 파일 경로
- 출력: content/scripts/episode_NNN.md
- 도구: Anthropic SDK (claude-sonnet-4-6)
- 중복 금지: SEO 생성 담당하지 않음

## SEO Agent
- 파일: agents/seo_agent.py
- 책임: 영상 메타데이터(제목/설명/태그) 생성
- 입력: content/scripts/episode_NNN.md
- 출력: content/scripts/episode_NNN_seo.json
- 도구: Anthropic SDK
- 중복 금지: 스크립트 내용 수정하지 않음

## Upload Agent
- 파일: agents/upload_agent.py
- 책임: YouTube Data API v3 업로드
- 입력: 영상 파일 경로 + episode_NNN_seo.json
- 출력: content/published/episode_NNN_published.json (video_id, URL, 업로드 시각)
- 도구: google-api-python-client
- 필수 제약: 업로드 전 사용자 승인 프롬프트 반드시 포함

## Analytics Agent
- 파일: agents/analytics_agent.py
- 책임: YouTube Analytics 데이터 수집
- 입력: content/published/ 기록
- 출력: content/analytics/report_YYYYMMDD.json
- 도구: YouTube Analytics API
- 실행 주기: 수동 또는 주 1회 APScheduler

## Bucky Sync Agent
- 파일: agents/bucky_sync_agent.py
- 책임: Obsidian vault → content/source-notes/ 동기화
- 입력: BUCKY_VAULT_PATH 환경변수 경로
- 출력: content/source-notes/ 마크다운 파일
- 동기화 기준: 파일명 또는 태그 #youtube #성장기 포함 노트
- 중복 금지: 스크립트 생성하지 않음
