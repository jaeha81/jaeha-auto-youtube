"""
Content Agent: 성장기 노트 → 영상 스크립트 변환
입력: content/source-notes/ 마크다운 파일
출력: content/scripts/episode_NNN.md

GENERATION_MODE=cli  → claude CLI 사용 (A안, $100 구독)
GENERATION_MODE=api  → Anthropic SDK 사용 (B안, 소액 과금)
"""

import re
import os
from pathlib import Path
from dotenv import load_dotenv
from agents.claude_runner import run, current_mode

load_dotenv()

SYSTEM_PROMPT = """당신은 "프로슈테크 빌더" 유튜브 채널의 스크립트 작가입니다.
이 채널은 비개발자 출신 AI 성장 과정을 공개하는 교육형 채널입니다.

핵심 원칙:
- AI를 가르치는 것이 아니라 함께 성장하는 과정을 보여주는 채널
- 성공뿐 아니라 실패, 수정, 시행착오도 진정성 있게 공개
- 시청자는 AI를 어려워하는 비개발자 직장인
- 전문 용어는 쉬운 말로 풀어서 설명
- 인테리어 현장 경험을 AI 학습 경험과 연결하는 시각 유지"""

USER_PROMPT_TEMPLATE = """다음 성장기 노트를 바탕으로 유튜브 영상 스크립트를 작성해주세요.

에피소드 번호: {episode_number}
시리즈: AI 성장기

원본 노트:
{note_content}

작성 기준:
- 총 8분 이내 분량 (A4 3~4장 수준)
- 구어체, 자연스러운 말투
- 시청자에게 직접 말하는 형식 ("여러분", "저는" 사용)
- 전문 용어 등장 시 괄호로 쉬운 설명 추가
- 실패나 시행착오가 있다면 솔직하게 포함

반드시 아래 구조로 작성:
## 오프닝 (30초)
## 본론 1 - 상황/배경 (2분)
## 본론 2 - 시도한 것 / 실패한 것 (3분)
## 본론 3 - 결론 / 배운 것 (2분)
## 클로징 (30초)"""


def _extract_episode_number(note_path: Path) -> str:
    match = re.search(r"(\d+)", note_path.stem)
    return match.group(1).zfill(3) if match else "001"


def _get_output_path(episode_number: str, base_path: str) -> Path:
    scripts_dir = Path(base_path) / "content" / "scripts"
    scripts_dir.mkdir(parents=True, exist_ok=True)
    return scripts_dir / f"episode_{episode_number}.md"


def generate_script(note_path: str) -> str:
    """
    노트 파일을 읽어 영상 스크립트를 생성하고 파일로 저장.
    반환값: 저장된 스크립트 파일 경로
    """
    note_file = Path(note_path)
    if not note_file.exists():
        raise FileNotFoundError(f"노트 파일을 찾을 수 없습니다: {note_path}")

    note_content = note_file.read_text(encoding="utf-8")
    if not note_content.strip():
        raise ValueError(f"노트 파일이 비어 있습니다: {note_path}")

    episode_number = _extract_episode_number(note_file)
    base_path = os.getenv("CONTENT_BASE_PATH", str(note_file.parent.parent.parent))

    print(f"[Content Agent] 스크립트 생성 중... 에피소드 {episode_number} ({current_mode()})")

    script_content = run(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT_TEMPLATE.format(
            episode_number=episode_number,
            note_content=note_content,
        ),
        max_tokens=4096,
    )

    output_path = _get_output_path(episode_number, base_path)
    header = (
        f"# 에피소드 {episode_number} — 스크립트\n\n"
        f"원본 노트: {note_file.name}\n"
        f"생성일: {__import__('datetime').date.today()}\n"
        f"생성 방식: {current_mode()}\n\n---\n\n"
    )
    output_path.write_text(header + script_content, encoding="utf-8")

    print(f"[Content Agent] 완료: {output_path}")
    return str(output_path)
