# Validation Log

## 체크리스트 기준

### 비개발자 운영 가능성
- CLI 명령이 1줄로 실행 가능한가?
- 에러 메시지가 한국어로 출력되는가?
- .env 설정 외 코드 수정 없이 동작하는가?

### 보안
- .env 키가 코드에 하드코딩되어 있지 않은가?
- credentials.json / token.json이 .gitignore에 포함되어 있는가?
- 업로드 전 사용자 승인 단계가 있는가?

### 에이전트 독립성
- 각 에이전트가 단독 실행 가능한가?
- 에이전트 간 역할 중복이 없는가?

### API 안정성
- YouTube API quota 초과 처리가 있는가?
- Claude API max_tokens 제한이 설정되어 있는가?
- OAuth 토큰 만료 시 자동 갱신이 되는가?

---

## 검증 기록

### 2026-06-03 - Phase 1 초기 구조
- 상태: 구현 진행 중
- 미검증 항목: upload_agent, analytics_agent (미구현)

### 2026-06-10 - Phase 4 에이전트 주행 검증

#### CLI 주행 검증 ✓
- `python main.py autopilot --mock --skip-sync` → ep002 선택·스크립트·SEO·썸네일 브리프까지 1커맨드 완료
- `python main.py strategy --mock` → 인사이트 3개 + 주제 테이블 출력 정상
- `python main.py thumbnail --episode 002 --mock` → 브리프 파일 생성 정상
- 모든 CLI 에러 메시지 한국어 출력 확인

#### 대시보드 API 검증 ✓ (FastAPI TestClient)
- `/api/health` → ok
- `/api/strategy/latest` → available=True, 주제 3개 반환
- `/api/strategy/run` (mock) → 백그라운드 job 완료 확인
- `/api/strategy/thumbnail/002` → available=True
- `/api/strategy/autopilot` → job_id 발급 정상
- `/api/pipeline/episodes` → ['001', '002'] 반환, ep002 status=seo_ready

#### 프론트엔드 빌드 검증 ✓
- `tsc --noEmit` 통과 (타입 에러 없음)
- `vite build` 통과 (156KB JS 번들)

#### EP002 스크립트 품질 검토 (MOCK 한계 및 실운영 수정 제안)

**현재 MOCK 스크립트 문제점:**
1. 오프닝이 "처음 AI를 만났던 그 날" — EP001 노트 내용과 혼용된 MOCK 템플릿. 실제 생성 시 ep002 노트("유튜브 자동화 시스템 구축 과정")에 맞게 재생성 필요
2. 본론 2/3가 [MOCK 섹션] 자리표시자 — 실제 API 키로 재생성 시 ep002 노트의 시행착오(Make.com 시도 → 직접 구축 결정, OAuth 3시간 전투 등)가 반드시 포함되어야 함
3. SEO 제목 "AI를 처음 만나다 — 프롬프트가 뭔지도 몰랐던 그 날"은 EP001 템플릿 재사용. ep002 주제("유튜브 자동화 직접 만들기")로 재생성 필요

**채널 톤 부합 여부 (ep002 노트 기준):**
- ✓ 비개발자 진정성: 노트에 "에러 메시지를 복붙할 줄 알면 된다", "이 시스템은 지금도 완벽하지 않다" 등 진정성 있는 소재가 풍부함
- ✓ 실패 공개 원칙: Make.com/n8n 시도 후 직접 구축으로 전환한 과정, OAuth 3시간 전투 등 실패·시행착오 소재가 명확히 기록됨
- ✓ 과정 중심: "이 영상도 이 시스템으로 만들어진 거다" — 메타적 공개로 채널 차별화 가능
- ⚠️ 보완 필요: 실제 스크립트 생성 후, "Make.com 금지" 맥락(자동화 원칙)을 시청자가 이해할 수 있게 편집할 것

**실운영 전 필수 작업:**
1. `ANTHROPIC_API_KEY` 또는 `GENERATION_MODE=cli` 활성화 후 `python main.py generate --note content/source-notes/ep002.md` 재실행
2. 생성된 실제 스크립트에서 오프닝이 EP002 주제(자동화 구축 과정)로 시작하는지 확인
3. SEO 제목이 ep002 노트 핵심 메시지("비개발자 자동화 구축")를 반영하는지 확인
