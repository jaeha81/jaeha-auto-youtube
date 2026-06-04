"""
SEO Agent: 영상 스크립트 → 유튜브 메타데이터 생성
입력: content/scripts/episode_NNN.md
출력: content/scripts/episode_NNN_seo.json

GENERATION_MODE=cli  → claude CLI 사용 (A안, $100 구독)
GENERATION_MODE=api  → Anthropic SDK 사용 (B안, 소액 과금)
"""

import json
import re
from pathlib import Path
from dotenv import load_dotenv
from agents.claude_runner import run, current_mode

load_dotenv()

SYSTEM_PROMPT = """당신은 유튜브 SEO 전문가입니다.
"프로슈테크 빌더" 채널은 AI 비개발자 성장 과정을 공개하는 교육형 채널입니다.
타깃 시청자: AI를 배우고 싶은 비개발자 직장인 (30~50대 중심)
채널 핵심 키워드: AI 비개발자, 프로슈테크빌더, AI 성장기, AI 자동화, 비개발자 AI

반드시 JSON만 출력하고 다른 텍스트는 절대 포함하지 마세요."""

USER_PROMPT_TEMPLATE = """아래 영상 스크립트를 분석하여 유튜브 업로드용 메타데이터를 JSON 형식으로 생성해주세요.

스크립트:
{script_content}

반드시 아래 JSON 구조 그대로 출력하세요. JSON 외 다른 텍스트 없이 JSON만 출력합니다.

{{
  "title": "제목 (60자 이내, 핵심 키워드 포함, 클릭하고 싶은 제목)",
  "description": "설명 (500자 이내, 첫 줄 핵심 요약, 채널 소개 포함)",
  "tags": ["태그1", "태그2", "태그3", "태그4", "태그5", "태그6", "태그7", "태그8", "태그9", "태그10"],
  "hashtags": ["#해시태그1", "#해시태그2", "#해시태그3", "#해시태그4", "#해시태그5"],
  "category": "교육",
  "visibility": "private"
}}"""


def _extract_episode_number(script_path: Path) -> str:
    match = re.search(r"(\d+)", script_path.stem)
    return match.group(1).zfill(3) if match else "001"


def generate_seo(script_path: str) -> str:
    """
    스크립트 파일을 읽어 SEO 메타데이터 JSON을 생성하고 저장.
    반환값: 저장된 SEO JSON 파일 경로
    """
    script_file = Path(script_path)
    if not script_file.exists():
        raise FileNotFoundError(f"스크립트 파일을 찾을 수 없습니다: {script_path}")

    script_content = script_file.read_text(encoding="utf-8")
    episode_number = _extract_episode_number(script_file)

    print(f"[SEO Agent] SEO 생성 중... 에피소드 {episode_number} ({current_mode()})")

    raw = run(
        system_prompt=SYSTEM_PROMPT,
        user_prompt=USER_PROMPT_TEMPLATE.format(script_content=script_content),
        max_tokens=1024,
    )

    json_match = re.search(r"\{[\s\S]*\}", raw)
    if not json_match:
        raise ValueError(f"SEO Agent가 유효한 JSON을 반환하지 않았습니다:\n{raw}")

    seo_data = json.loads(json_match.group())

    output_path = script_file.parent / f"episode_{episode_number}_seo.json"
    output_path.write_text(
        json.dumps(seo_data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[SEO Agent] 완료: {output_path}")
    return str(output_path)
