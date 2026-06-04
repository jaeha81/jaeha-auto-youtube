import json
import re
import subprocess
import sys
import threading
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent.parent
SCRIPTS_DIR = BASE_DIR / "content" / "scripts"
NOTES_DIR = BASE_DIR / "content" / "source-notes"
PUBLISHED_DIR = BASE_DIR / "content" / "published"
QUEUE_DIR = BASE_DIR / "content" / "queue"

_jobs: dict[str, dict] = {}


def _episode_status(ep_num: str) -> dict:
    script_path = SCRIPTS_DIR / f"episode_{ep_num}.md"
    seo_path = SCRIPTS_DIR / f"episode_{ep_num}_seo.json"
    published_path = PUBLISHED_DIR / f"episode_{ep_num}_published.json"
    queue_files = list(QUEUE_DIR.glob(f"*{ep_num}*")) if QUEUE_DIR.exists() else []

    title = ""
    if seo_path.exists():
        data = json.loads(seo_path.read_text(encoding="utf-8"))
        title = data.get("title", "")

    if published_path.exists():
        status = "published"
    elif queue_files:
        status = "queued"
    elif seo_path.exists():
        status = "seo_ready"
    elif script_path.exists():
        status = "scripted"
    else:
        status = "draft"

    return {
        "episode": ep_num,
        "status": status,
        "title": title,
        "has_script": script_path.exists(),
        "has_seo": seo_path.exists(),
        "has_video": bool(queue_files),
        "published": published_path.exists(),
    }


@router.get("/episodes")
async def list_episodes():
    episodes: dict[str, dict] = {}

    if SCRIPTS_DIR.exists():
        for ep_file in sorted(SCRIPTS_DIR.glob("episode_*.md")):
            m = re.search(r"episode_(\d+)\.md", ep_file.name)
            if m:
                ep_num = m.group(1).zfill(3)
                episodes[ep_num] = _episode_status(ep_num)

    if NOTES_DIR.exists():
        for note_file in sorted(NOTES_DIR.glob("ep*.md")):
            m = re.search(r"(\d+)", note_file.stem)
            if m:
                ep_num = m.group(1).zfill(3)
                if ep_num not in episodes:
                    episodes[ep_num] = {
                        "episode": ep_num,
                        "status": "draft",
                        "title": note_file.stem,
                        "has_script": False,
                        "has_seo": False,
                        "has_video": False,
                        "published": False,
                    }

    return sorted(episodes.values(), key=lambda e: e["episode"])


@router.get("/summary")
async def pipeline_summary():
    episodes = await list_episodes()
    counts: dict[str, int] = {"draft": 0, "scripted": 0, "seo_ready": 0, "queued": 0, "published": 0}
    for ep in episodes:
        key = ep["status"]
        counts[key] = counts.get(key, 0) + 1
    return {"total": len(episodes), **counts}


class GenerateRequest(BaseModel):
    episode: str
    mock: bool = False


def _run_generate(job_id: str, note_path: str, mock: bool) -> None:
    cmd = [sys.executable, "-X", "utf8", "main.py", "generate", "--note", note_path]
    if mock:
        cmd.append("--mock")
    try:
        result = subprocess.run(
            cmd, cwd=str(BASE_DIR), capture_output=True, text=True,
            encoding="utf-8", timeout=120,
        )
        _jobs[job_id] = {
            "status": "done" if result.returncode == 0 else "error",
            "output": result.stdout,
            "error": result.stderr,
        }
    except Exception as exc:
        _jobs[job_id] = {"status": "error", "output": "", "error": str(exc)}


@router.post("/generate")
async def trigger_generate(req: GenerateRequest):
    ep_num = req.episode.zfill(3)

    # Locate note file
    note_path = NOTES_DIR / f"ep{ep_num}.md"
    if not note_path.exists():
        candidates = (
            list(NOTES_DIR.glob(f"ep{req.episode}*.md"))
            + list(NOTES_DIR.glob(f"*{ep_num}*.md"))
        )
        if not candidates:
            raise HTTPException(status_code=404, detail=f"노트 파일 없음: ep{ep_num}.md")
        note_path = candidates[0]

    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {"status": "running", "output": "", "error": ""}
    t = threading.Thread(
        target=_run_generate, args=(job_id, str(note_path), req.mock), daemon=True
    )
    t.start()
    return {"job_id": job_id, "status": "started", "episode": ep_num}


@router.get("/job/{job_id}")
async def get_job_status(job_id: str):
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]
