"""
Strategy 라우트: 콘텐츠 전략(Analytics 피드백 루프) + 썸네일 브리프 + 에이전트 주행
업로드는 이 라우트에서 절대 실행하지 않음 — youtube.py의 승인 플로우만 사용
"""

import subprocess
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent.parent
SCRIPTS_DIR = BASE_DIR / "content" / "scripts"

_jobs: dict[str, dict] = {}


class RunRequest(BaseModel):
    mock: bool = False


@router.get("/latest")
async def latest_strategy():
    """가장 최근 콘텐츠 전략 제안 반환."""
    try:
        from agents.strategy_agent import get_latest_strategy
        strategy = get_latest_strategy()
        if not strategy:
            return {"available": False, "message": "전략 제안이 없습니다. '전략 분석 실행'을 눌러 생성하세요."}
        return {"available": True, "strategy": strategy}
    except Exception as e:
        return {"available": False, "message": str(e)}


@router.post("/run")
async def run_strategy(req: RunRequest):
    """콘텐츠 전략 분석 실행 (백그라운드)."""
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status": "running", "output": "", "error": ""}

    def _run():
        try:
            from agents.strategy_agent import generate_strategy
            path = generate_strategy(mock=req.mock)
            _jobs[job_id] = {"status": "done", "output": path, "error": ""}
        except Exception as exc:
            _jobs[job_id] = {"status": "error", "output": "", "error": str(exc)}

    threading.Thread(target=_run, daemon=True).start()
    return {"job_id": job_id, "status": "started"}


@router.get("/thumbnail/{episode}")
async def get_thumbnail_brief(episode: str):
    """에피소드 썸네일 브리프 내용 반환."""
    ep_num = episode.zfill(3)
    brief_path = SCRIPTS_DIR / f"episode_{ep_num}_thumbnail.md"
    if not brief_path.exists():
        return {"available": False, "episode": ep_num, "message": "썸네일 브리프가 없습니다."}
    return {
        "available": True,
        "episode": ep_num,
        "content": brief_path.read_text(encoding="utf-8"),
    }


@router.post("/thumbnail/{episode}")
async def generate_thumbnail(episode: str, req: RunRequest):
    """에피소드 썸네일 브리프 생성."""
    ep_num = episode.zfill(3)
    if not (SCRIPTS_DIR / f"episode_{ep_num}.md").exists():
        raise HTTPException(status_code=404, detail=f"스크립트 없음: episode_{ep_num}.md — 먼저 스크립트를 생성하세요.")
    try:
        from agents.thumbnail_agent import generate_thumbnail_brief
        path = generate_thumbnail_brief(ep_num, mock=req.mock)
        return {
            "success": True,
            "brief_path": path,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/autopilot")
async def run_autopilot(req: RunRequest):
    """에이전트 주행 실행 (동기화→스크립트→SEO→썸네일 브리프). 업로드는 포함되지 않음."""
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status": "running", "output": "", "error": ""}

    def _run():
        cmd = [sys.executable, "-X", "utf8", "main.py", "autopilot"]
        if req.mock:
            cmd.append("--mock")
        try:
            result = subprocess.run(
                cmd, cwd=str(BASE_DIR), capture_output=True, text=True,
                encoding="utf-8", timeout=300,
            )
            _jobs[job_id] = {
                "status": "done" if result.returncode == 0 else "error",
                "output": result.stdout,
                "error": result.stderr,
            }
        except Exception as exc:
            _jobs[job_id] = {"status": "error", "output": "", "error": str(exc)}

    threading.Thread(target=_run, daemon=True).start()
    return {"job_id": job_id, "status": "started"}


@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]
