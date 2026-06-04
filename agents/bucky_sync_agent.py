"""
Bucky Sync Agent: Obsidian vault → content/source-notes/ 동기화
입력: BUCKY_VAULT_PATH 환경변수 경로
출력: content/source-notes/ 마크다운 파일
동기화 기준: 파일명에 'ep'/'episode' 포함 또는 파일 내 #youtube #성장기 태그
"""

import os
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
SOURCE_NOTES_DIR = BASE_DIR / "content" / "source-notes"

SYNC_KEYWORDS = ["#youtube", "#성장기", "#유튜브", "#프로슈테크"]
SYNC_FILENAME_PATTERNS = ["ep", "episode", "성장기", "유튜브"]


def _is_sync_target(file_path: Path) -> bool:
    """동기화 대상 파일인지 판단"""
    name_lower = file_path.stem.lower()
    if any(pat in name_lower for pat in SYNC_FILENAME_PATTERNS):
        return True
    try:
        content = file_path.read_text(encoding="utf-8", errors="ignore")
        return any(kw in content for kw in SYNC_KEYWORDS)
    except Exception:
        return False


def sync_notes() -> int:
    """
    Obsidian vault에서 노트를 source-notes/로 복사.
    반환값: 동기화된 파일 수
    """
    vault_path = os.getenv("BUCKY_VAULT_PATH", "")
    if not vault_path:
        raise ValueError(
            ".env 파일에 BUCKY_VAULT_PATH가 설정되지 않았습니다.\n"
            "예: BUCKY_VAULT_PATH=G:\\내 드라이브\\obsidian-agent-brain-system\\"
        )

    vault = Path(vault_path)
    if not vault.exists():
        raise FileNotFoundError(f"Obsidian vault 경로를 찾을 수 없습니다: {vault_path}")

    SOURCE_NOTES_DIR.mkdir(parents=True, exist_ok=True)

    synced = 0
    for md_file in vault.rglob("*.md"):
        if md_file.name.startswith("."):
            continue
        if _is_sync_target(md_file):
            dest = SOURCE_NOTES_DIR / md_file.name
            shutil.copy2(str(md_file), str(dest))
            print(f"[Bucky Sync] 동기화: {md_file.name}")
            synced += 1

    if synced == 0:
        print("[Bucky Sync] 동기화할 파일을 찾지 못했습니다.")
        print(f"  조건: 파일명에 {SYNC_FILENAME_PATTERNS} 포함 또는")
        print(f"  내용에 {SYNC_KEYWORDS} 태그 포함")

    return synced
