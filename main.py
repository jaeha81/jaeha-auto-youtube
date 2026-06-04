"""
프로슈테크 빌더 유튜브 자동화 시스템 — 메인 하네스 CLI
사용법:
  python main.py generate --note content/source-notes/ep001.md
  python main.py generate --note content/source-notes/ep001.md --seo-only
  python main.py upload --episode 001
  python main.py list
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


if __name__ == "__main__":
    app()
