"""
Upload Agent: YouTube Data API v3 영상 업로드
입력: 영상 파일 경로 + SEO JSON 경로
출력: content/published/episode_NNN_published.json
"""

import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]

CATEGORY_MAP = {
    "교육": "27",
    "과학기술": "28",
    "엔터테인먼트": "24",
}

BASE_DIR = Path(__file__).parent.parent
TOKEN_PATH = BASE_DIR / "token.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
PUBLISHED_DIR = BASE_DIR / "content" / "published"


def _get_youtube_service():
    """OAuth 2.0 인증 후 YouTube 서비스 객체 반환"""
    creds = None

    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_PATH.exists():
                raise FileNotFoundError(
                    "credentials.json 파일이 없습니다.\n"
                    "Google Cloud Console에서 OAuth 2.0 클라이언트 ID를 생성하고\n"
                    f"credentials.json 파일을 {CREDENTIALS_PATH} 에 저장하세요."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)

        TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

    return build("youtube", "v3", credentials=creds)


def upload_video(video_path: str, seo_path: str) -> dict:
    """
    YouTube에 영상 업로드.
    반환값: {"video_id": ..., "url": ..., "title": ...}
    """
    video_file = Path(video_path)
    seo_file = Path(seo_path)

    if not video_file.exists():
        raise FileNotFoundError(f"영상 파일을 찾을 수 없습니다: {video_path}")
    if not seo_file.exists():
        raise FileNotFoundError(f"SEO 파일을 찾을 수 없습니다: {seo_path}")

    seo_data = json.loads(seo_file.read_text(encoding="utf-8"))
    category_id = CATEGORY_MAP.get(seo_data.get("category", "교육"), "27")
    visibility = seo_data.get("visibility", "private")

    youtube = _get_youtube_service()

    body = {
        "snippet": {
            "title": seo_data["title"],
            "description": seo_data["description"],
            "tags": seo_data.get("tags", []),
            "categoryId": category_id,
        },
        "status": {
            "privacyStatus": visibility,
        },
    }

    media = MediaFileUpload(str(video_file), chunksize=-1, resumable=True)

    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media,
    )

    print(f"[Upload Agent] 업로드 시작: {video_file.name}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"[Upload Agent] 진행률: {pct}%")

    video_id = response["id"]
    url = f"https://youtu.be/{video_id}"

    # 발행 기록 저장
    PUBLISHED_DIR.mkdir(parents=True, exist_ok=True)
    import re
    ep_match = re.search(r"(\d+)", seo_file.stem)
    ep_num = ep_match.group(1).zfill(3) if ep_match else "000"
    published_record = {
        "video_id": video_id,
        "url": url,
        "title": seo_data["title"],
        "uploaded_at": datetime.now().isoformat(),
        "visibility": visibility,
        "video_file": str(video_file),
    }
    record_path = PUBLISHED_DIR / f"episode_{ep_num}_published.json"
    record_path.write_text(
        json.dumps(published_record, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"[Upload Agent] 완료: {url}")
    return published_record
