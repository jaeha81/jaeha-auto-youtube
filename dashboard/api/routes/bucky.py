"""
Bucky 라우트: Obsidian vault 동기화 상태 + 수동 동기화 트리거
"""

import os
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent.parent
NOTES_DIR = BASE_DIR / "content" / "source-notes"


class SyncResult(BaseModel):
    success: bool
    synced_count: int
    message: str
    timestamp: str


@router.get("/status")
async def bucky_status():
    """Bucky vault 연결 상태 및 동기화된 노트 현황."""
    vault_path = os.getenv("BUCKY_VAULT_PATH", "")
    vault_connected = bool(vault_path) and Path(vault_path).exists()

    notes = list(NOTES_DIR.glob("*.md")) if NOTES_DIR.exists() else []
    note_list = []
    for f in sorted(notes):
        stat = f.stat()
        note_list.append({
            "filename": f.name,
            "size_kb": round(stat.st_size / 1024, 1),
            "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        })

    return {
        "vault_connected": vault_connected,
        "vault_path": vault_path if vault_connected else None,
        "notes_dir": str(NOTES_DIR),
        "synced_notes": len(notes),
        "notes": note_list,
    }


@router.post("/sync", response_model=SyncResult)
async def bucky_sync():
    """Obsidian vault → source-notes 수동 동기화 실행."""
    try:
        from agents.bucky_sync_agent import sync_notes
        count = sync_notes()
        return SyncResult(
            success=True,
            synced_count=count,
            message=f"{count}개 노트 동기화 완료",
            timestamp=datetime.now().isoformat(),
        )
    except Exception as e:
        return SyncResult(
            success=False,
            synced_count=0,
            message=f"동기화 실패: {str(e)}",
            timestamp=datetime.now().isoformat(),
        )


@router.get("/analytics/latest")
async def latest_analytics():
    """가장 최근 분석 리포트 반환."""
    try:
        from agents.analytics_agent import get_latest_report
        report = get_latest_report()
        if not report:
            return {"available": False, "message": "분석 리포트가 없습니다. 에피소드를 발행 후 analytics를 실행하세요."}
        return {"available": True, "report": report}
    except Exception as e:
        return {"available": False, "message": str(e)}


@router.post("/analytics/collect")
async def collect_analytics():
    """YouTube 성과 데이터 수집 및 리포트 생성."""
    try:
        from agents.analytics_agent import collect_analytics as run_collect
        report_path = run_collect()
        if not report_path:
            return {"success": False, "message": "발행된 에피소드가 없습니다."}
        return {
            "success": True,
            "report_path": report_path,
            "message": "분석 리포트 생성 완료",
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        return {"success": False, "message": str(e)}
