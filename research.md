# Research: 프로슈테크 빌더 유튜브 자동화 시스템

## 1. 프로젝트 컨텍스트

### 사용자 프로필
- 비개발자 출신 인테리어 엔지니어
- AI 독학 후 "프로슈테크 빌더" 개념 직접 정의
- 목표: AI 비개발자 성장 과정을 공개하는 교육형 유튜버
- 성공/실패/수정 모두 콘텐츠화하는 "슈퍼 샘플" 방식

### 핵심 콘텐츠 축
- 1단계: AI 성장기 (입문 ~ 시행착오)
- 2단계: 에이전트 구축기
- 3단계: 사업 적용기 (인테리어 자동화 등)
- 4단계: 미래 실험실

---

## 2. 기술 스택 분석

### 제약 조건
- Make.com, n8n 사용 금지
- Claude Code / Codex $100 구독 활용
- YouTube 자동 업로드 필수
- Bucky (Obsidian Agent Brain System) 연동 필수

### 선택 스택 근거

| 계층 | 선택 기술 | 이유 |
|------|----------|------|
| 자동화 엔진 | Python 3.11 | 범용성, Claude/YouTube API 연동 |
| AI 생성 | Anthropic SDK + claude-sonnet-4-6 | 이미 구독 중, 비용 효율 |
| YouTube 연동 | YouTube Data API v3 | 공식 업로드/분석 API |
| 스케줄러 | APScheduler (Python) | Make.com/n8n 없이 트리거 구현 |
| 대시보드 백엔드 | FastAPI | 경량, Python 동일 생태계 |
| 대시보드 프론트엔드 | React + Vite | 반응형 파이프라인 뷰 |
| Bucky 연동 | 파일 시스템 직접 읽기 | Obsidian vault = 로컬 마크다운 |
| 상태 관리 | LLM Wiki 마크다운 파일 | 컨텍스트 절감, 세션 이어받기 |

### YouTube Data API v3 업로드 요건
- Google Cloud Console 프로젝트 필요
- OAuth 2.0 인증 (업로드 = 사용자 인증 필수)
- 하루 업로드 할당량: 10,000 units (영상 1개 ≈ 1,600 units)
- 필요 scope: `youtube.upload`, `youtube.readonly`

### Claude API 비용 예측 (스크립트 생성 기준)
- claude-sonnet-4-6: 입력 $3/1M tokens, 출력 $15/1M tokens
- 영상 스크립트 1편 생성: ~2,000 tokens → $0.03 수준
- 월 10편 기준 비용: ~$0.30 (무시 가능 수준)

---

## 3. 에이전트 아키텍처 분석

### 필수 에이전트 (MVP)
1. **Main Harness** - 파이프라인 조율자
2. **Content Agent** - 노트 → 영상 스크립트
3. **SEO Agent** - 제목/설명/태그 생성
4. **Upload Agent** - YouTube API 업로드

### 권장 에이전트 (Phase 2)
5. **Analytics Agent** - 성과 데이터 수집
6. **Bucky Sync Agent** - Obsidian 동기화

### 제외 에이전트 (복잡도 과도)
- 영상 편집 에이전트 (VideoEditor): 영상 파일 처리 복잡도가 MVP 범위 초과
- SNS 크로스포스팅 에이전트: MVP 외 범위
- 자동 썸네일 생성: 이미지 생성 API 비용 + 연동 복잡도

---

## 4. 히스토리 영상 시리즈 구조 분석

### 소스 데이터
- Obsidian vault의 성장 기록 노트
- 유튜브자동화시작하기/ 폴더의 마크다운 파일들
- 새로 작성될 성장기 에피소드 노트

### 시리즈 포맷
```
[AI 성장기] 시리즈 - 추천 포맷
- 오프닝: 오늘 에피소드 한 줄 요약 (30초)
- 본론 1: 상황/배경 (2분)
- 본론 2: 시도한 것 / 실패한 것 (3분)
- 본론 3: 결론 / 배운 것 (2분)
- 클로징: 다음 에피소드 예고 (30초)
총 8분 이내 권장
```

---

## 5. 대시보드 기능 분석

### 핵심 기능 (비개발자 운영 가능 수준)
- 콘텐츠 파이프라인 뷰: 대기 → 스크립트 생성 → 검토 → 예약 → 발행
- YouTube 통계 요약: 최신 조회수, 구독자 증감
- 에피소드 관리 목록
- 업로드 스케줄 설정
- Bucky 동기화 버튼

### 제외 기능 (MVP 외)
- 댓글 관리 자동화
- A/B 썸네일 테스트
- 수익화 분석 대시보드

---

## 6. Bucky 연동 방식 분석

### Obsidian Vault 접근
- 경로: `G:\내 드라이브\obsidian-agent-brain-system\`
- 방식: Python 파일 시스템 직접 읽기 (watchdog 라이브러리)
- Bucky Sync Agent가 vault 변경 감지 → content/source-notes/ 동기화

### LLM Wiki 구조 (상태 관리)
- `llm-wiki/handoff-prompt.md` → 다음 세션 시작 프롬프트
- `llm-wiki/current-state.md` → 현재 파이프라인 상태
- 세션 간 컨텍스트 낭비 없이 이어받기 가능

---

## 7. 위험 요소 분석

| 위험 | 수준 | 완화 방법 |
|------|------|----------|
| YouTube OAuth 토큰 만료 | 중 | refresh_token 자동 갱신 구현 |
| Claude API 과금 초과 | 낮 | 토큰 예산 설정 (max_tokens) |
| Obsidian vault 경로 변경 | 중 | .env에 경로 설정 |
| 영상 파일 없이 업로드 시도 | 중 | 파이프라인 입력 검증 |
| 과도한 자동화로 검토 없이 업로드 | 높 | 업로드 전 사용자 승인 단계 강제 |
