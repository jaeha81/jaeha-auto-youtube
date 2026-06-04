"""
Claude Runner: CLI 방식(A안)과 API 방식(B안) 전환 레이어
.env의 GENERATION_MODE=cli 또는 api 로 전환

A안 (cli)  : claude -p "..." — $100 구독 내 운영
B안 (api)  : anthropic SDK  — 구독 외 소액 과금, 더 빠름
"""

import os
import subprocess
from dotenv import load_dotenv

load_dotenv()

MODE = os.getenv("GENERATION_MODE", "cli").lower()


def run(system_prompt: str, user_prompt: str, max_tokens: int = 4096) -> str:
    """
    system_prompt + user_prompt 를 Claude에 전송하고 응답 텍스트를 반환.
    GENERATION_MODE 환경변수에 따라 CLI 또는 API 중 하나를 자동 선택.
    """
    if MODE == "api":
        return _run_api(system_prompt, user_prompt, max_tokens)
    return _run_cli(system_prompt, user_prompt)


def _run_cli(system_prompt: str, user_prompt: str) -> str:
    """A안: claude CLI 호출 ($100 구독 소진)"""
    full_prompt = f"{system_prompt}\n\n---\n\n{user_prompt}"

    result = subprocess.run(
        ["claude", "-p", full_prompt],
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=120,
    )

    if result.returncode != 0:
        err = result.stderr.strip() or "알 수 없는 오류"
        raise RuntimeError(
            f"claude CLI 오류 (종료코드 {result.returncode}): {err}\n"
            "해결방법: 터미널에서 'claude' 명령어가 실행되는지 확인하세요."
        )

    output = result.stdout.strip()
    if not output:
        raise ValueError("claude CLI가 빈 응답을 반환했습니다. 프롬프트를 확인하세요.")

    return output


def _run_api(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    """B안: Anthropic SDK 직접 호출 (구독 외 소액 과금)"""
    try:
        import anthropic
    except ImportError:
        raise ImportError("B안 사용을 위해 'pip install anthropic' 이 필요합니다.")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(".env 파일에 ANTHROPIC_API_KEY 가 설정되지 않았습니다.")

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )
    return message.content[0].text


def current_mode() -> str:
    """현재 어떤 방식으로 실행 중인지 반환"""
    return "CLI (A안 — $100 구독)" if MODE == "cli" else "API (B안 — 소액 과금)"
