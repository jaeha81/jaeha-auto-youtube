"""
Analytics Agent: YouTube 채널 성과 데이터 수집 + 분석 리포트 생성
입력: content/published/ 발행 기록 JSON
출력: content/analytics/report_YYYYMMDD.json

실행 조건:
  - credentials.json + token.json 존재 시 YouTube Analytics API 호출
  - 없으면 published 기록 기반 로컬 집계로 대체
"""

import json
import os
from datetime import date, timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent.parent
PUBLISHED_DIR = BASE_DIR / "content" / "published"
ANALYTICS_DIR = BASE_DIR / "content" / "analytics"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = BASE_DIR / "token.json"

SCOPES = ["https://www.googleapis.com/auth/yt-analytics.readonly"]


def _get_youtube_analytics_service():
    """YouTube Analytics API 서비스 객체 반환. credentials 없으면 None."""
    if not CREDENTIALS_PATH.exists():
        return None
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build

        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                from google.auth.transport.requests import Request
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_PATH), SCOPES
                )
                creds = flow.run_local_server(port=0)
            TOKEN_PATH.write_text(creds.to_json(), encoding="utf-8")

        return build("youtubeAnalytics", "v2", credentials=creds)
    except Exception as e:
        print(f"[Analytics Agent] YouTube Analytics 연결 실패: {e}")
        return None


def _fetch_video_stats(service, video_id: str, channel_id: str) -> dict:
    """단일 영상 Analytics 데이터 조회."""
    end_date = date.today().isoformat()
    start_date = (date.today() - timedelta(days=28)).isoformat()

    try:
        response = service.reports().query(
            ids=f"channel=={channel_id}",
            startDate=start_date,
            endDate=end_date,
            metrics="views,estimatedMinutesWatched,averageViewDuration,likes,comments,subscribersGained",
            filters=f"video=={video_id}",
            dimensions="video",
        ).execute()

        rows = response.get("rows", [])
        if not rows:
            return {}

        row = rows[0]
        return {
            "views": row[1],
            "watch_minutes": row[2],
            "avg_view_duration_sec": row[3],
            "likes": row[4],
            "comments": row[5],
            "subscribers_gained": row[6],
            "period": f"{start_date} ~ {end_date}",
        }
    except Exception as e:
        print(f"[Analytics Agent] 영상 {video_id} 통계 조회 실패: {e}")
        return {}


def _load_published_episodes() -> list[dict]:
    """published/ 폴더에서 발행 기록 목록 로드."""
    if not PUBLISHED_DIR.exists():
        return []
    episodes = []
    for f in sorted(PUBLISHED_DIR.glob("episode_*_published.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            episodes.append(data)
        except Exception:
            pass
    return episodes


def collect_analytics() -> str:
    """
    발행된 모든 에피소드의 성과를 수집하고 리포트 파일로 저장.
    반환값: 저장된 리포트 파일 경로
    """
    ANALYTICS_DIR.mkdir(parents=True, exist_ok=True)

    episodes = _load_published_episodes()
    if not episodes:
        print("[Analytics Agent] 발행된 에피소드가 없습니다.")
        return ""

    channel_id = os.getenv("YOUTUBE_CHANNEL_ID", "")
    service = _get_youtube_analytics_service()

    report = {
        "generated_date": date.today().isoformat(),
        "total_episodes": len(episodes),
        "episodes": [],
        "summary": {},
        "api_connected": service is not None,
    }

    total_views = 0
    total_watch_minutes = 0

    for ep in episodes:
        video_id = ep.get("video_id", "")
        ep_entry = {
            "episode": ep.get("episode_number", ""),
            "title": ep.get("title", ""),
            "video_id": video_id,
            "published_at": ep.get("published_at", ""),
            "url": ep.get("url", ""),
        }

        if service and video_id and channel_id:
            stats = _fetch_video_stats(service, video_id, channel_id)
            ep_entry.update(stats)
            total_views += stats.get("views", 0)
            total_watch_minutes += stats.get("watch_minutes", 0)
        else:
            ep_entry["note"] = "YouTube Analytics 미연결 — credentials.json 설정 후 재실행"

        report["episodes"].append(ep_entry)

    report["summary"] = {
        "total_views": total_views,
        "total_watch_minutes": total_watch_minutes,
        "avg_views_per_episode": total_views // len(episodes) if episodes else 0,
    }

    report_path = ANALYTICS_DIR / f"report_{date.today().strftime('%Y%m%d')}.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"[Analytics Agent] 리포트 저장 완료: {report_path}")
    print(f"  - 에피소드 수: {len(episodes)}")
    print(f"  - 총 조회수: {total_views:,}")
    print(f"  - API 연결: {'✓' if service else '✗ (로컬 집계)'}")

    return str(report_path)


def get_latest_report() -> dict:
    """가장 최근 분석 리포트를 딕셔너리로 반환. 없으면 빈 딕셔너리."""
    if not ANALYTICS_DIR.exists():
        return {}
    reports = sorted(ANALYTICS_DIR.glob("report_*.json"), reverse=True)
    if not reports:
        return {}
    try:
        return json.loads(reports[0].read_text(encoding="utf-8"))
    except Exception:
        return {}
