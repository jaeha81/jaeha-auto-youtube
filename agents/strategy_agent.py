"""
Strategy Agent: 성과 데이터 → 다음 콘텐츠 방향 제안 (Analytics 피드백 루프)
입력: content/analytics/ 최근 리포트 + content/published/ 발행 기록 + 기존 노트/스크립트 목록
출력: content/strategy/strategy_YYYYMMDD.json

GENERATION_MODE=cli  → claude CLI 사용 (A안, $100 구독)
GENERATION_MODE=api  → Anthropic SDK 사용 (B안, 소액 과금)

중복 금지: 스크립트/SEO를 직접 생성하지 않음 — 다음 에피소드 "방향"만 제안
"""

import json
import re
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "content" / "scripts"
NOTES_DIR = BASE_DIR / "content" / "source-notes"
STRATEGY_DIR = BASE_DIR / "content" / "strategy"

SYSTEM_PROMPT = """당신은 "프로슈테크 빌더" 유튜브 채널의 콘텐츠 전략가입니다.
이 채널은 비개발자 출신 AI 성장 과정을 공개하는 교육형 채널입니다.

채널 콘텐츠 축 (4단계):
- 1단계 AI 성장기: 입문, 시행착오, 실패, 실제 학습 과정
- 2단계 에이전트 구축기: GPT/Claude/Gemini/Codex/Obsidian 실제 구축 공개
- 3단계 사업 적용기: 인테리어 자동화, 콘텐츠 자동화, 수익화 실험
- 4단계 미래 실험실: AI 에이전트 네트워크, 디지털 기업, 미래 직업 실험

핵심 시청자: AI를 배우고 싶지만 두려움을 느끼는 비개발자 직장인 (30~50대)
운영 원칙: 성공도 실패도 공개, 결과보다 과정 중심, 사람의 진정성이 중심

반드시 JSON만 출력하고 다른 텍스트는 절대 포함하지 마세요."""

USER_PROMPT_TEMPLATE = """아래 채널 운영 데이터를 분석하여 다음 콘텐츠 방향을 제안해주세요.

## 최근 성과 리포트
{analytics_summary}

## 지금까지 만든 에피소드 (제목 목록)
{episode_titles}

## 아직 스크립트화되지 않은 노트
{pending_notes}

분석 기준:
- 성과가 좋은 주제/형식은 강화, 반응 없는 방향은 수정 제안
- 이미 다룬 주제와 중복되지 않는 새 에피소드 주제 3개 제안
- 각 주제는 채널 콘텐츠 축(1~4단계) 중 하나에 연결
- 비개발자 시청자가 검색할 법한 키워드 포함

반드시 아래 JSON 구조 그대로 출력하세요. JSON 외 다른 텍스트 없이 JSON만 출력합니다.

{{
  "insights": ["성과 분석 인사이트 1", "인사이트 2", "인사이트 3"],
  "next_topics": [
    {{
      "priority": 1,
      "title": "제안 에피소드 가제",
      "content_axis": "1단계 AI 성장기",
      "angle": "어떤 관점/이야기로 풀어낼지 2~3문장",
      "target_keywords": ["검색 키워드1", "키워드2", "키워드3"],
      "reason": "이 주제를 제안하는 근거"
    }}
  ]
}}"""


def _summarize_analytics() -> str:
    """최근 분석 리포트를 프롬프트용 텍스트로 요약. 없으면 안내 문구 반환."""
    from agents.analytics_agent import get_latest_report

    report = get_latest_report()
    if not report:
        return "(분석 리포트 없음 — 아직 발행/수집된 성과 데이터가 없습니다. 채널 정체성과 노트 기반으로만 제안하세요.)"

    lines = [
        f"리포트 생성일: {report.get('generated_date', '?')}",
        f"발행 에피소드 수: {report.get('total_episodes', 0)}",
    ]
    summary = report.get("summary", {})
    if summary:
        lines.append(f"총 조회수: {summary.get('total_views', 0)}")
        lines.append(f"총 시청 시간(분): {summary.get('total_watch_minutes', 0)}")
    for ep in report.get("episodes", []):
        entry = f"- EP{ep.get('episode', '?')} {ep.get('title', '')}"
        if "views" in ep:
            entry += f" | 조회수 {ep['views']} | 평균시청 {ep.get('avg_view_duration_sec', '?')}초"
        lines.append(entry)
    return "\n".join(lines)


def _list_episode_titles() -> str:
    """기존 에피소드 SEO 제목 목록."""
    titles = []
    if SCRIPTS_DIR.exists():
        for seo_file in sorted(SCRIPTS_DIR.glob("episode_*_seo.json")):
            try:
                data = json.loads(seo_file.read_text(encoding="utf-8"))
                titles.append(f"- {data.get('title', seo_file.stem)}")
            except Exception:
                titles.append(f"- {seo_file.stem}")
    return "\n".join(titles) if titles else "(아직 없음)"


def _list_pending_notes() -> str:
    """스크립트가 아직 생성되지 않은 노트 목록."""
    pending = []
    if NOTES_DIR.exists():
        for note in sorted(NOTES_DIR.glob("*.md")):
            m = re.search(r"(\d+)", note.stem)
            ep_num = m.group(1).zfill(3) if m else None
            if ep_num and (SCRIPTS_DIR / f"episode_{ep_num}.md").exists():
                continue
            pending.append(f"- {note.name}")
    return "\n".join(pending) if pending else "(없음)"


def _mock_strategy() -> dict:
    """API 없이 구조 검증용 샘플 전략."""
    return {
        "insights": [
            "[MOCK] 발행 데이터가 쌓이면 실제 성과 기반 인사이트가 생성됩니다.",
            "[MOCK] 실패 공개형 에피소드가 채널 정체성과 가장 잘 맞습니다.",
            "[MOCK] 실행: python main.py strategy (API 키 또는 claude CLI 필요)",
        ],
        "next_topics": [
            {
                "priority": 1,
                "title": "비개발자가 유튜브 자동화 시스템을 직접 만든 과정 전부 공개",
                "content_axis": "2단계 에이전트 구축기",
                "angle": "이 채널의 자동화 시스템 자체를 소재로, 막혔던 지점과 해결 과정을 그대로 보여준다.",
                "target_keywords": ["유튜브 자동화", "비개발자 AI", "클로드 코드"],
                "reason": "[MOCK] 과정 공개형 콘텐츠는 채널 핵심 메시지와 직결됨",
            },
            {
                "priority": 2,
                "title": "AI에게 일을 시키다 3번 실패한 이야기",
                "content_axis": "1단계 AI 성장기",
                "angle": "실패 사례 3가지를 솔직하게 복기하고 각각에서 배운 한 가지를 정리한다.",
                "target_keywords": ["AI 실패", "AI 활용법", "프롬프트"],
                "reason": "[MOCK] 실패 공개는 채널 운영 원칙(진정성)과 일치",
            },
            {
                "priority": 3,
                "title": "인테리어 현장 견적을 AI로 자동화해 본 첫 실험",
                "content_axis": "3단계 사업 적용기",
                "angle": "현장 전문가의 실무에 AI를 적용하는 첫 시도를 기록한다.",
                "target_keywords": ["AI 업무 자동화", "인테리어 AI", "현장 AI"],
                "reason": "[MOCK] 본업 연결 콘텐츠는 차별화 포인트",
            },
        ],
    }


def generate_strategy(mock: bool = False) -> str:
    """
    성과 데이터를 분석해 다음 콘텐츠 방향 제안 JSON을 생성하고 저장.
    반환값: 저장된 전략 파일 경로
    """
    STRATEGY_DIR.mkdir(parents=True, exist_ok=True)

    if mock:
        strategy = _mock_strategy()
        strategy["mock"] = True
    else:
        from agents.claude_runner import run, current_mode

        print(f"[Strategy Agent] 콘텐츠 전략 분석 중... ({current_mode()})")
        raw = run(
            system_prompt=SYSTEM_PROMPT,
            user_prompt=USER_PROMPT_TEMPLATE.format(
                analytics_summary=_summarize_analytics(),
                episode_titles=_list_episode_titles(),
                pending_notes=_list_pending_notes(),
            ),
            max_tokens=2048,
        )
        json_match = re.search(r"\{[\s\S]*\}", raw)
        if not json_match:
            raise ValueError(f"Strategy Agent가 유효한 JSON을 반환하지 않았습니다:\n{raw}")
        strategy = json.loads(json_match.group())
        strategy["mock"] = False

    strategy["generated_date"] = date.today().isoformat()

    output_path = STRATEGY_DIR / f"strategy_{date.today().strftime('%Y%m%d')}.json"
    output_path.write_text(
        json.dumps(strategy, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"[Strategy Agent] 완료: {output_path}")
    return str(output_path)


def get_latest_strategy() -> dict:
    """가장 최근 전략 제안을 딕셔너리로 반환. 없으면 빈 딕셔너리."""
    if not STRATEGY_DIR.exists():
        return {}
    files = sorted(STRATEGY_DIR.glob("strategy_*.json"), reverse=True)
    if not files:
        return {}
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except Exception:
        return {}
