"""
Thumbnail Agent: 스크립트 + SEO → 썸네일 제작 텍스트 브리프 생성
입력: content/scripts/episode_NNN.md + episode_NNN_seo.json
출력: content/scripts/episode_NNN_thumbnail.md

이미지 자동 생성은 하지 않음 (plan.md 차단 요소) — 사람이 직접 제작할 수 있는
텍스트 브리프(문구/구도/색상 가이드)만 생성.

GENERATION_MODE=cli  → claude CLI 사용 (A안, $100 구독)
GENERATION_MODE=api  → Anthropic SDK 사용 (B안, 소액 과금)
"""

import json
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "content" / "scripts"

SYSTEM_PROMPT = """당신은 유튜브 썸네일 기획 전문가입니다.
"프로슈테크 빌더" 채널은 비개발자 출신 AI 성장 과정을 공개하는 교육형 채널입니다.
타깃 시청자: AI를 배우고 싶은 비개발자 직장인 (30~50대)

썸네일 원칙:
- 메인 문구는 8자 이내, 모바일에서 한눈에 읽히는 크기
- 과장/낚시 금지 — 영상 내용과 일치하는 진정성 있는 문구
- 사람 얼굴(표정) + 큰 텍스트 조합이 기본 구도"""

USER_PROMPT_TEMPLATE = """아래 영상 스크립트와 제목을 바탕으로 썸네일 제작 브리프를 마크다운으로 작성해주세요.

영상 제목: {title}

스크립트 (앞부분):
{script_excerpt}

반드시 아래 구조로 작성:
## 시안 A (추천)
- 메인 문구: (8자 이내)
- 서브 문구: (15자 이내, 선택)
- 구도: (인물 위치, 텍스트 위치)
- 색상: (배경/텍스트 색상 가이드)
- 표정/소품: (촬영 가이드)

## 시안 B
(같은 구조)

## 시안 C
(같은 구조)

## 공통 주의사항
- (모바일 가독성 등 체크포인트 2~3개)"""

MOCK_BRIEF = """## 시안 A (추천)
- 메인 문구: AI 첫 도전
- 서브 문구: 비개발자의 솔직한 기록
- 구도: 인물 우측 1/3, 텍스트 좌측 상단 대형 배치
- 색상: 배경 짙은 남색(#1e293b), 메인 텍스트 흰색 + 노란색 포인트
- 표정/소품: 살짝 당황한 표정, 노트북 화면이 보이게

## 시안 B
- 메인 문구: 3주만에 포기
- 서브 문구: 그래도 다시 시작한 이유
- 구도: 인물 정면 중앙, 텍스트 상하 분할
- 색상: 배경 흰색, 텍스트 검정 + 빨간색 강조
- 표정/소품: 한숨 쉬는 표정, 메모로 가득한 노트

## 시안 C
- 메인 문구: 비개발자 AI
- 서브 문구: 진짜 성장기 1편
- 구도: 인물 좌측, 우측에 큰 숫자 "EP.1"
- 색상: 배경 보라 그라데이션(#6366f1), 흰색 텍스트
- 표정/소품: 미소, 손가락으로 화면 가리키기

## 공통 주의사항
- 모바일에서 메인 문구가 읽히는지 축소해서 확인
- 영상 내용과 문구가 일치하는지 확인 (낚시 금지)
- [MOCK — 실제 브리프는 python main.py thumbnail --episode NNN 으로 생성]"""


def generate_thumbnail_brief(episode: str, mock: bool = False) -> str:
    """
    에피소드 스크립트와 SEO를 읽어 썸네일 브리프를 생성하고 저장.
    반환값: 저장된 브리프 파일 경로
    """
    episode = episode.zfill(3)
    script_path = SCRIPTS_DIR / f"episode_{episode}.md"
    seo_path = SCRIPTS_DIR / f"episode_{episode}_seo.json"

    if not script_path.exists():
        raise FileNotFoundError(f"스크립트 파일을 찾을 수 없습니다: {script_path}")

    title = ""
    if seo_path.exists():
        try:
            title = json.loads(seo_path.read_text(encoding="utf-8")).get("title", "")
        except Exception:
            pass

    if mock:
        brief = MOCK_BRIEF
        mode_label = "MOCK"
    else:
        from agents.claude_runner import run, current_mode

        mode_label = current_mode()
        print(f"[Thumbnail Agent] 썸네일 브리프 생성 중... 에피소드 {episode} ({mode_label})")
        script_content = script_path.read_text(encoding="utf-8")
        brief = run(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT_TEMPLATE.format(
                title=title or f"에피소드 {episode}",
                script_excerpt=script_content[:3000],
            ),
            max_tokens=1536,
        )

    output_path = SCRIPTS_DIR / f"episode_{episode}_thumbnail.md"
    header = (
        f"# 에피소드 {episode} — 썸네일 브리프\n\n"
        f"영상 제목: {title or '(SEO 미생성)'}\n"
        f"생성일: {date.today()}\n"
        f"생성 방식: {mode_label}\n\n---\n\n"
    )
    output_path.write_text(header + brief, encoding="utf-8")

    print(f"[Thumbnail Agent] 완료: {output_path}")
    return str(output_path)
