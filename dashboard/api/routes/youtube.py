import json
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

BASE_DIR = Path(__file__).parent.parent.parent.parent
SCRIPTS_DIR = BASE_DIR / "content" / "scripts"
PUBLISHED_DIR = BASE_DIR / "content" / "published"
TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"

SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]


def _channel_stats() -> dict:
    if not TOKEN_PATH.exists():
        return {"connected": False, "subscribers": None, "total_views": None, "video_count": None}
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build

        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        yt = build("youtube", "v3", credentials=creds)
        resp = yt.channels().list(part="statistics", mine=True).execute()

        if resp.get("items"):
            s = resp["items"][0]["statistics"]
            return {
                "connected": True,
                "subscribers": int(s.get("subscriberCount", 0)),
                "total_views": int(s.get("viewCount", 0)),
                "video_count": int(s.get("videoCount", 0)),
            }
        return {"connected": True, "subscribers": 0, "total_views": 0, "video_count": 0}
    except Exception as exc:
        return {"connected": False, "subscribers": None, "total_views": None, "video_count": None, "error": str(exc)}


@router.get("/stats")
async def youtube_stats():
    stats = _channel_stats()
    published_count = len(list(PUBLISHED_DIR.glob("*_published.json"))) if PUBLISHED_DIR.exists() else 0
    return {**stats, "published_locally": published_count}


@router.get("/upload-preview/{episode}")
async def upload_preview(episode: str):
    ep_num = episode.zfill(3)
    seo_path = SCRIPTS_DIR / f"episode_{ep_num}_seo.json"
    if not seo_path.exists():
        raise HTTPException(status_code=404, detail=f"SEO 파일 없음: episode_{ep_num}_seo.json")

    data = json.loads(seo_path.read_text(encoding="utf-8"))
    return {
        "episode": ep_num,
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "tags": data.get("tags", []),
        "visibility": data.get("visibility", "private"),
        "category": data.get("category", "교육"),
    }


class UploadRequest(BaseModel):
    confirmed: bool
    video_path: str | None = None


@router.post("/upload/{episode}")
async def upload_video(episode: str, req: UploadRequest):
    if not req.confirmed:
        raise HTTPException(status_code=400, detail="업로드 승인 필요 (confirmed=true)")

    ep_num = episode.zfill(3)
    seo_path = SCRIPTS_DIR / f"episode_{ep_num}_seo.json"
    if not seo_path.exists():
        raise HTTPException(status_code=404, detail="SEO 파일 없음")

    if not TOKEN_PATH.exists() and not CREDENTIALS_PATH.exists():
        raise HTTPException(status_code=503, detail="YouTube 인증 파일 없음 (credentials.json 필요)")

    video_path = req.video_path
    if not video_path:
        queue_dir = BASE_DIR / "content" / "queue"
        candidates = list(queue_dir.glob(f"*{ep_num}*")) if queue_dir.exists() else []
        if not candidates:
            raise HTTPException(status_code=404, detail="queue 폴더에 영상 파일 없음")
        video_path = str(candidates[0])

    script = (
        f"from agents.upload_agent import upload_video as uv; "
        f"import json; print(json.dumps(uv(r'{video_path}', r'{seo_path}')))"
    )
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(BASE_DIR), capture_output=True, text=True, encoding="utf-8", timeout=300,
    )

    if result.returncode != 0:
        raise HTTPException(status_code=500, detail=f"업로드 실패: {result.stderr[:500]}")

    return json.loads(result.stdout.strip())
