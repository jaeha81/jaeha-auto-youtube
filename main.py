"""
프로슈테크 빌더 유튜브 자동화 시스템 — 메인 하네스 CLI
사용법:
  python main.py generate --note content/source-notes/ep001.md
  python main.py generate --note content/source-notes/ep001.md --seo-only
  python main.py upload --episode 001
  python main.py list
  python main.py autopilot              # 에이전트 주행: 동기화→스크립트→SEO→썸네일 브리프
  python main.py strategy               # 성과 분석 → 다음 콘텐츠 방향 제안
  python main.py thumbnail --episode 001
  python main.py schedule               # 주간 자동 분석 스케줄러 (장기 운영)
"""

import json
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

load_dotenv()

app = typer.Typer(help="프로슈테크 빌더 유튜브 자동화 시스템")
console = Console()

BASE_DIR = Path(__file__).parent
SCRIPTS_DIR = BASE_DIR / "content" / "scripts"
NOTES_DIR = BASE_DIR / "content" / "source-notes"
PUBLISHED_DIR = BASE_DIR / "content" / "published"


# ──────────────────────────────────────────
# generate 명령
# ──────────────────────────────────────────

@app.command()
def generate(
    note: str = typer.Option(..., "--note", "-n", help="노트 파일 경로 (예: content/source-notes/ep001.md)"),
    seo_only: bool = typer.Option(False, "--seo-only", help="스크립트는 건너뛰고 SEO만 생성"),
    script_file: str = typer.Option(None, "--script", "-s", help="SEO 전용 모드에서 사용할 스크립트 파일"),
    mock: bool = typer.Option(False, "--mock", help="API 없이 파이프라인 구조 테스트 (샘플 파일 생성)"),
):
    """노트 → 스크립트 → SEO 메타데이터 생성"""

    console.print(Panel("[bold cyan]프로슈테크 빌더 콘텐츠 파이프라인[/bold cyan]", expand=False))

    if mock:
        _run_mock(note)
        return

    if seo_only:
        if not script_file:
            console.print("[red]--seo-only 모드에서는 --script 옵션으로 스크립트 파일을 지정해야 합니다.[/red]")
            raise typer.Exit(1)
        _run_seo(script_file)
        return

    note_path = Path(note)
    if not note_path.is_absolute():
        note_path = BASE_DIR / note_path

    if not note_path.exists():
        console.print(f"[red]노트 파일을 찾을 수 없습니다: {note_path}[/red]")
        console.print(f"[yellow]팁: content/source-notes/ 폴더에 노트 파일을 넣어주세요.[/yellow]")
        raise typer.Exit(1)

    # Step 1: 스크립트 생성
    console.print("\n[bold]Step 1/2[/bold] 스크립트 생성 중...")
    try:
        from agents.content_agent import generate_script
        script_path = generate_script(str(note_path))
        console.print(f"[green]✓ 스크립트 생성 완료:[/green] {script_path}")
    except Exception as e:
        console.print(f"[red]스크립트 생성 실패: {e}[/red]")
        raise typer.Exit(1)

    # Step 2: SEO 생성
    _run_seo(script_path)


def _run_mock(note: str):
    """API 없이 샘플 파일을 생성하여 파이프라인 구조를 검증"""
    import re
    note_path = Path(note)
    if not note_path.is_absolute():
        note_path = BASE_DIR / note_path

    match = re.search(r"(\d+)", note_path.stem)
    ep_num = match.group(1).zfill(3) if match else "001"
    note_content = note_path.read_text(encoding="utf-8") if note_path.exists() else "(노트 없음)"

    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)

    # 샘플 스크립트 생성
    script_path = SCRIPTS_DIR / f"episode_{ep_num}.md"
    script_path.write_text(
        f"# 에피소드 {ep_num} — 스크립트\n\n"
        f"원본 노트: {note_path.name}\n"
        f"생성일: {__import__('datetime').date.today()}\n"
        f"모드: MOCK (실제 API 키 설정 후 재실행 필요)\n\n---\n\n"
        f"## 오프닝 (30초)\n\n"
        f"여러분, 안녕하세요. 프로슈테크 빌더입니다.\n"
        f"오늘은 제가 처음 AI를 만났던 그 날의 이야기를 해보려고 합니다.\n\n"
        f"## 본론 1 - 상황/배경 (2분)\n\n"
        f"[MOCK: 실제 스크립트는 python main.py generate --note {note_path.name} 으로 생성하세요]\n\n"
        f"원본 노트 내용:\n{note_content}\n\n"
        f"## 본론 2 - 시도한 것 / 실패한 것 (3분)\n\n"
        f"[MOCK 섹션]\n\n"
        f"## 본론 3 - 결론 / 배운 것 (2분)\n\n"
        f"[MOCK 섹션]\n\n"
        f"## 클로징 (30초)\n\n"
        f"다음 에피소드에서 뵙겠습니다. 구독과 좋아요 부탁드립니다!\n",
        encoding="utf-8",
    )
    console.print(f"[green]✓ 스크립트 생성 (MOCK):[/green] {script_path}")

    # 샘플 SEO JSON 생성
    seo_path = SCRIPTS_DIR / f"episode_{ep_num}_seo.json"
    seo_path.write_text(
        json.dumps({
            "title": f"[AI 성장기 {ep_num}편] AI를 처음 만나다 — 프롬프트가 뭔지도 몰랐던 그 날 | 프로슈테크빌더",
            "description": "비개발자가 AI를 처음 만났을 때의 솔직한 이야기입니다.\n처음엔 아무것도 몰랐고, 3주 만에 포기했습니다.\n그 경험에서 배운 것들을 공유합니다.\n\n[MOCK — 실제 API 키 설정 후 재생성 필요]",
            "tags": ["AI비개발자", "프로슈테크빌더", "AI성장기", "AI자동화", "비개발자AI", "AI공부", "AI독학", "클로드", "ChatGPT활용", "AI유튜버"],
            "hashtags": ["#AI비개발자", "#프로슈테크빌더", "#AI성장기", "#AI자동화", "#비개발자AI"],
            "category": "교육",
            "visibility": "private",
            "mock": True,
        }, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    console.print(f"[green]✓ SEO 생성 (MOCK):[/green] {seo_path}")

    console.print(Panel(
        "[bold yellow]MOCK 실행 완료[/bold yellow]\n"
        "파이프라인 구조 검증됨. 실제 스크립트 생성을 위해:\n"
        "1. .env.example → .env 복사\n"
        "2. ANTHROPIC_API_KEY 입력\n"
        f"3. python main.py generate --note {note_path.name}",
        expand=False,
    ))


def _run_seo(script_path: str):
    console.print("\n[bold]Step 2/2[/bold] SEO 메타데이터 생성 중...")
    try:
        from agents.seo_agent import generate_seo
        seo_path = generate_seo(script_path)
        console.print(f"[green]✓ SEO 생성 완료:[/green] {seo_path}")

        # SEO 내용 미리보기
        seo_data = json.loads(Path(seo_path).read_text(encoding="utf-8"))
        console.print("\n[bold cyan]── SEO 미리보기 ──[/bold cyan]")
        console.print(f"제목: [yellow]{seo_data.get('title', '')}[/yellow]")
        console.print(f"태그: {', '.join(seo_data.get('tags', [])[:5])} ...")

    except Exception as e:
        console.print(f"[red]SEO 생성 실패: {e}[/red]")
        raise typer.Exit(1)

    console.print(Panel(
        "[bold green]파이프라인 완료![/bold green]\n"
        "다음 단계: 영상을 촬영하고 content/queue/ 폴더에 넣은 후\n"
        "[cyan]python main.py upload --episode NNN[/cyan] 을 실행하세요.",
        expand=False,
    ))


# ──────────────────────────────────────────
# upload 명령
# ──────────────────────────────────────────

@app.command()
def upload(
    episode: str = typer.Option(..., "--episode", "-e", help="에피소드 번호 (예: 001)"),
    video: str = typer.Option(None, "--video", "-v", help="영상 파일 경로 (지정 안 하면 queue에서 자동 탐색)"),
):
    """YouTube에 영상 업로드 (사용자 승인 후 진행)"""

    episode = episode.zfill(3)
    seo_path = SCRIPTS_DIR / f"episode_{episode}_seo.json"

    if not seo_path.exists():
        console.print(f"[red]SEO 파일을 찾을 수 없습니다: {seo_path}[/red]")
        console.print("[yellow]먼저 'python main.py generate --note <노트파일>'을 실행하세요.[/yellow]")
        raise typer.Exit(1)

    # 영상 파일 탐색
    if video:
        video_path = Path(video)
    else:
        queue_dir = BASE_DIR / "content" / "queue"
        candidates = list(queue_dir.glob(f"*{episode}*"))
        if not candidates:
            candidates = list(queue_dir.glob("*.mp4")) + list(queue_dir.glob("*.mov"))
        if not candidates:
            console.print(f"[red]content/queue/ 폴더에 영상 파일이 없습니다.[/red]")
            console.print("[yellow]촬영한 영상을 content/queue/ 폴더에 넣어주세요.[/yellow]")
            raise typer.Exit(1)
        video_path = candidates[0]

    if not video_path.exists():
        console.print(f"[red]영상 파일을 찾을 수 없습니다: {video_path}[/red]")
        raise typer.Exit(1)

    # SEO 미리보기 + 승인 요청
    seo_data = json.loads(seo_path.read_text(encoding="utf-8"))

    console.print(Panel("[bold yellow]업로드 전 확인[/bold yellow]", expand=False))
    console.print(f"영상 파일: [cyan]{video_path.name}[/cyan]")
    console.print(f"제목: [yellow]{seo_data.get('title')}[/yellow]")
    console.print(f"공개 설정: [cyan]{seo_data.get('visibility', 'private')}[/cyan]")
    console.print(f"설명:\n{seo_data.get('description', '')[:200]}...")

    confirmed = typer.confirm("\n위 내용으로 YouTube에 업로드하시겠습니까?")
    if not confirmed:
        console.print("[yellow]업로드 취소됨.[/yellow]")
        raise typer.Exit(0)

    # 업로드 실행
    console.print("\n[bold]업로드 중...[/bold]")
    try:
        from agents.upload_agent import upload_video
        result = upload_video(str(video_path), str(seo_path))
        console.print(f"\n[bold green]✓ 업로드 완료![/bold green]")
        console.print(f"YouTube URL: [cyan]https://youtu.be/{result['video_id']}[/cyan]")
    except Exception as e:
        console.print(f"[red]업로드 실패: {e}[/red]")
        raise typer.Exit(1)


# ──────────────────────────────────────────
# list 명령
# ──────────────────────────────────────────

@app.command()
def list_episodes():
    """생성된 에피소드 목록 보기"""

    table = Table(title="에피소드 현황", show_header=True, header_style="bold cyan")
    table.add_column("번호", width=6)
    table.add_column("스크립트", width=12)
    table.add_column("SEO", width=8)
    table.add_column("발행", width=8)
    table.add_column("제목", width=50)

    episodes = sorted(SCRIPTS_DIR.glob("episode_*.md"))
    if not episodes:
        console.print("[yellow]생성된 에피소드가 없습니다. 'python main.py generate --note <파일>'을 먼저 실행하세요.[/yellow]")
        return

    for ep_file in episodes:
        match = __import__("re").search(r"episode_(\d+)\.md", ep_file.name)
        if not match:
            continue
        num = match.group(1)
        seo_exists = (SCRIPTS_DIR / f"episode_{num}_seo.json").exists()
        published_exists = (PUBLISHED_DIR / f"episode_{num}_published.json").exists()

        title = ""
        if seo_exists:
            seo_data = json.loads(
                (SCRIPTS_DIR / f"episode_{num}_seo.json").read_text(encoding="utf-8")
            )
            title = seo_data.get("title", "")[:48]

        table.add_row(
            num,
            "[green]✓[/green]",
            "[green]✓[/green]" if seo_exists else "[red]✗[/red]",
            "[green]✓[/green]" if published_exists else "[dim]대기[/dim]",
            title,
        )

    console.print(table)


# ──────────────────────────────────────────
# sync 명령 (Bucky 연동)
# ──────────────────────────────────────────

@app.command()
def sync():
    """Bucky(Obsidian vault)에서 성장기 노트 동기화"""
    console.print("[bold]Bucky Sync Agent 실행 중...[/bold]")
    try:
        from agents.bucky_sync_agent import sync_notes
        count = sync_notes()
        console.print(f"[green]✓ 동기화 완료: {count}개 노트[/green]")
    except Exception as e:
        console.print(f"[red]동기화 실패: {e}[/red]")
        raise typer.Exit(1)


# ──────────────────────────────────────────
# thumbnail 명령
# ──────────────────────────────────────────

@app.command()
def thumbnail(
    episode: str = typer.Option(..., "--episode", "-e", help="에피소드 번호 (예: 001)"),
    mock: bool = typer.Option(False, "--mock", help="API 없이 샘플 브리프 생성"),
):
    """스크립트 기반 썸네일 제작 브리프 생성 (텍스트 브리프만, 이미지 생성 없음)"""
    try:
        from agents.thumbnail_agent import generate_thumbnail_brief
        brief_path = generate_thumbnail_brief(episode, mock=mock)
        console.print(f"[green]✓ 썸네일 브리프 생성 완료:[/green] {brief_path}")
    except Exception as e:
        console.print(f"[red]썸네일 브리프 생성 실패: {e}[/red]")
        raise typer.Exit(1)


# ──────────────────────────────────────────
# strategy 명령 (Analytics 피드백 루프)
# ──────────────────────────────────────────

@app.command()
def strategy(
    mock: bool = typer.Option(False, "--mock", help="API 없이 샘플 전략 생성"),
):
    """성과 데이터 분석 → 다음 콘텐츠 방향 제안"""
    console.print(Panel("[bold cyan]콘텐츠 전략 분석 (Analytics 피드백 루프)[/bold cyan]", expand=False))
    try:
        from agents.strategy_agent import generate_strategy
        strategy_path = generate_strategy(mock=mock)
        data = json.loads(Path(strategy_path).read_text(encoding="utf-8"))
    except Exception as e:
        console.print(f"[red]전략 분석 실패: {e}[/red]")
        raise typer.Exit(1)

    console.print("\n[bold cyan]── 인사이트 ──[/bold cyan]")
    for insight in data.get("insights", []):
        console.print(f"  • {insight}")

    table = Table(title="다음 에피소드 제안", show_header=True, header_style="bold cyan")
    table.add_column("순위", width=4)
    table.add_column("가제", width=40)
    table.add_column("콘텐츠 축", width=16)
    table.add_column("키워드", width=30)
    for topic in data.get("next_topics", []):
        table.add_row(
            str(topic.get("priority", "")),
            topic.get("title", ""),
            topic.get("content_axis", ""),
            ", ".join(topic.get("target_keywords", [])),
        )
    console.print(table)
    console.print(f"\n전략 파일: [cyan]{strategy_path}[/cyan]")


# ──────────────────────────────────────────
# autopilot 명령 (에이전트 주행)
# ──────────────────────────────────────────

@app.command()
def autopilot(
    note: str = typer.Option(None, "--note", "-n", help="노트 파일 경로 (생략 시 미처리 노트 자동 선택)"),
    mock: bool = typer.Option(False, "--mock", help="API 없이 전체 주행 구조 테스트"),
    skip_sync: bool = typer.Option(False, "--skip-sync", help="Bucky 동기화 단계 건너뛰기"),
):
    """에이전트 주행: 동기화 → 노트 선택 → 스크립트 → SEO → 썸네일 브리프 (업로드는 별도 승인 필요)"""

    console.print(Panel(
        "[bold cyan]에이전트 주행 (Autopilot)[/bold cyan]\n"
        "동기화 → 노트 선택 → 스크립트 → SEO → 썸네일 브리프\n"
        "[dim]업로드는 자동 실행되지 않습니다 — 'python main.py upload' 에서 승인 후 진행[/dim]",
        expand=False,
    ))

    # Step 1: Bucky 동기화 (실패해도 계속 진행)
    if not skip_sync:
        console.print("\n[bold]Step 1/4[/bold] Bucky 노트 동기화...")
        try:
            from agents.bucky_sync_agent import sync_notes
            count = sync_notes()
            console.print(f"[green]✓ 동기화 완료: {count}개 노트[/green]")
        except Exception as e:
            console.print(f"[yellow]동기화 건너뜀 (vault 미연결): {e}[/yellow]")
    else:
        console.print("\n[bold]Step 1/4[/bold] Bucky 동기화 건너뜀 (--skip-sync)")

    # Step 2: 대상 노트 선택
    console.print("\n[bold]Step 2/4[/bold] 대상 노트 선택...")
    if note:
        note_path = Path(note)
        if not note_path.is_absolute():
            note_path = BASE_DIR / note_path
    else:
        note_path = _find_unprocessed_note()
        if not note_path:
            console.print("[yellow]처리할 노트가 없습니다. 모든 노트가 이미 스크립트화되었습니다.[/yellow]")
            console.print("[dim]새 노트를 content/source-notes/ 에 추가하거나 Bucky vault에 작성하세요.[/dim]")
            raise typer.Exit(0)

    if not note_path.exists():
        console.print(f"[red]노트 파일을 찾을 수 없습니다: {note_path}[/red]")
        raise typer.Exit(1)
    console.print(f"[green]✓ 대상 노트:[/green] {note_path.name}")

    # Step 3: 스크립트 + SEO 생성
    import re as _re
    match = _re.search(r"(\d+)", note_path.stem)
    ep_num = match.group(1).zfill(3) if match else "001"

    console.print("\n[bold]Step 3/4[/bold] 스크립트 + SEO 생성...")
    if mock:
        _run_mock(str(note_path))
    else:
        try:
            from agents.content_agent import generate_script
            script_path = generate_script(str(note_path))
            console.print(f"[green]✓ 스크립트:[/green] {script_path}")
            from agents.seo_agent import generate_seo
            seo_path = generate_seo(script_path)
            console.print(f"[green]✓ SEO:[/green] {seo_path}")
        except Exception as e:
            console.print(f"[red]생성 실패: {e}[/red]")
            raise typer.Exit(1)

    # Step 4: 썸네일 브리프
    console.print("\n[bold]Step 4/4[/bold] 썸네일 브리프 생성...")
    try:
        from agents.thumbnail_agent import generate_thumbnail_brief
        brief_path = generate_thumbnail_brief(ep_num, mock=mock)
        console.print(f"[green]✓ 썸네일 브리프:[/green] {brief_path}")
    except Exception as e:
        console.print(f"[yellow]썸네일 브리프 실패 (계속 진행): {e}[/yellow]")

    # 주행 완료 요약 — 업로드는 사람 승인 게이트 유지
    console.print(Panel(
        f"[bold green]에이전트 주행 완료 — EP{ep_num} 업로드 준비됨[/bold green]\n\n"
        f"남은 수동 단계 (사람 승인 필요):\n"
        f"1. content/scripts/episode_{ep_num}.md 스크립트 검토\n"
        f"2. episode_{ep_num}_thumbnail.md 브리프로 썸네일 제작\n"
        f"3. 영상 촬영 후 content/queue/ 에 배치\n"
        f"4. [cyan]python main.py upload --episode {ep_num}[/cyan] (승인 후 업로드)",
        expand=False,
    ))


def _find_unprocessed_note() -> Path | None:
    """스크립트가 아직 생성되지 않은 가장 앞 번호의 노트 반환."""
    import re as _re
    if not NOTES_DIR.exists():
        return None
    for note_file in sorted(NOTES_DIR.glob("*.md")):
        m = _re.search(r"(\d+)", note_file.stem)
        if not m:
            continue
        ep_num = m.group(1).zfill(3)
        if not (SCRIPTS_DIR / f"episode_{ep_num}.md").exists():
            return note_file
    return None


# ──────────────────────────────────────────
# schedule 명령 (장기 운영 자동화)
# ──────────────────────────────────────────

@app.command()
def schedule(
    day: str = typer.Option("mon", "--day", help="주간 실행 요일 (mon~sun)"),
    hour: int = typer.Option(9, "--hour", help="실행 시각 (0~23시)"),
):
    """주 1회 Analytics 수집 + 콘텐츠 전략 갱신 스케줄러 (Ctrl+C로 종료)"""
    try:
        from apscheduler.schedulers.blocking import BlockingScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        console.print("[red]apscheduler가 설치되지 않았습니다: pip install apscheduler[/red]")
        raise typer.Exit(1)

    def weekly_job():
        console.print(f"\n[bold]── 주간 자동 실행 ({__import__('datetime').datetime.now():%Y-%m-%d %H:%M}) ──[/bold]")
        try:
            from agents.analytics_agent import collect_analytics
            report_path = collect_analytics()
            if report_path:
                console.print(f"[green]✓ Analytics 리포트:[/green] {report_path}")
        except Exception as e:
            console.print(f"[yellow]Analytics 수집 실패: {e}[/yellow]")
        try:
            from agents.strategy_agent import generate_strategy
            strategy_path = generate_strategy()
            console.print(f"[green]✓ 콘텐츠 전략 갱신:[/green] {strategy_path}")
        except Exception as e:
            console.print(f"[yellow]전략 갱신 실패: {e}[/yellow]")

    scheduler = BlockingScheduler()
    scheduler.add_job(weekly_job, CronTrigger(day_of_week=day, hour=hour))

    console.print(Panel(
        f"[bold cyan]주간 자동 분석 스케줄러 시작[/bold cyan]\n"
        f"매주 {day} {hour:02d}:00 — Analytics 수집 + 콘텐츠 전략 갱신\n"
        f"[dim]업로드는 절대 자동 실행되지 않습니다. Ctrl+C로 종료.[/dim]",
        expand=False,
    ))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        console.print("\n[yellow]스케줄러 종료됨.[/yellow]")


if __name__ == "__main__":
    app()
