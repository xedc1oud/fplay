import asyncio
import concurrent.futures
import curses
import subprocess
from urllib.parse import quote

import typer
import yt_dlp
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

TARGET_PREFIX = "https://m.vkvideo.ru/video-"
MAX_LINKS = 5

app = typer.Typer()


async def ensure_chromium():
    try:
        async with async_playwright() as p:
            await p.chromium.launch(headless=True)
    except Exception as e:
        if "Executable doesn't exist" in str(e):
            print("[!] Browsers not found. Starting installation...")
            subprocess.run(
                [sys.executable, "-m", "playwright", "install", "chromium"], check=True
            )
            print("[+] Installation completed successfully!")
        else:
            raise e


def clean_url(url: str) -> str:
    return url.split("?")[0]


async def search_vkvideo(query: str) -> list[str]:
    encoded_query = quote(query)
    url = f"https://m.vkvideo.ru/?q={encoded_query}&action=search&showAutoLoginModal=1"

    while True:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await (await browser.new_context()).new_page()
            await Stealth().apply_stealth_async(page)

            try:
                await page.goto(url, wait_until="load", timeout=30_000)
                await page.wait_for_selector(
                    f'a[href^="{TARGET_PREFIX}"]', timeout=30_000
                )
            except Exception:
                await browser.close()
                typer.echo(typer.style("[!] Retrying...", fg=typer.colors.YELLOW))
                continue

            links = await page.evaluate("""
                () => Array.from(document.querySelectorAll('a'))
                           .map(a => a.href)
            """)
            await browser.close()

        seen = set()
        filtered = []
        for link in links:
            if link.startswith(TARGET_PREFIX):
                clean = clean_url(link)
                if clean not in seen:
                    seen.add(clean)
                    filtered.append(clean)

        if filtered:
            return filtered[:MAX_LINKS]


def _get_video_info(url: str) -> dict | None:
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        if not info:
            return None
        formats = info.get("formats") or []
        if not formats:
            return None
        return {
            "title": info.get("title", ""),
            "duration": info.get("duration", 0),
            "source_url": url,
        }


async def get_all_video_info(urls: list[str]) -> list[dict]:
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_LINKS) as pool:
        tasks = [loop.run_in_executor(pool, _get_video_info, url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    out = []
    for url, result in zip(urls, results):
        if isinstance(result, Exception) or result is None:
            typer.echo(typer.style(f"[!] Skipping: {url}", fg=typer.colors.RED))
        else:
            out.append(result)
    return out


async def async_main(query: str) -> list[dict]:
    typer.echo(typer.style(f"[?] Searching: {query}", fg=typer.colors.CYAN))
    results = await search_vkvideo(query)
    typer.echo(
        typer.style(
            f"[*] Found {len(results)} results, fetching info...", fg=typer.colors.GREEN
        )
    )
    return await get_all_video_info(results)


def fmt_duration(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h:
        return f"{h}:{m:02}:{s:02}"
    return f"{m}:{s:02}"


def play(source_url: str):
    typer.echo(typer.style("[*] Fetching stream...", fg=typer.colors.GREEN))
    ydl_opts = {"quiet": True, "no_warnings": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(source_url, download=False)
        formats = info.get("formats") or []
        if not formats:
            typer.echo(typer.style("[!] No formats found.", fg=typer.colors.RED))
            return
        best = max(formats, key=lambda f: f.get("height") or 0)
        url = best.get("url", source_url)
        headers = best.get("http_headers", {})

    args = ["mpv", "--fs", "--really-quiet"]
    ua = headers.get("User-Agent")
    if ua:
        args += [f"--user-agent={ua}"]
    for k, v in headers.items():
        if k.lower() != "user-agent":
            args += [f"--http-header-fields={k}: {v}"]
    args.append(url)

    subprocess.run(args)


def draw(stdscr, infos):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_CYAN, -1)
    curses.init_pair(3, curses.COLOR_YELLOW, -1)
    curses.init_pair(4, curses.COLOR_WHITE, -1)

    selected = 0

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        header = " [>] fplay — use arrows to navigate, enter to play, q to quit"
        stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
        stdscr.addstr(0, 0, header[: w - 1])
        stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(1, 0, "─" * (w - 1))
        stdscr.attroff(curses.color_pair(4))

        for i, info in enumerate(infos):
            row = i + 2
            duration = fmt_duration(info["duration"])
            marker = "[>]" if i == selected else "[ ]"
            prefix = f" {marker} {i + 1}. "
            suffix = f"  [{duration}]"
            title = info["title"][: w - len(prefix) - len(suffix) - 1]
            line = f"{prefix}{title}{suffix}"

            if i == selected:
                stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
                stdscr.addstr(row, 0, line[: w - 1])
                stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
            else:
                stdscr.attron(curses.color_pair(3))
                stdscr.addstr(row, 0, f" {marker} ")
                stdscr.attroff(curses.color_pair(3))
                stdscr.attron(curses.color_pair(4))
                rest = f"{i + 1}. {title}{suffix}"
                stdscr.addstr(row, len(marker) + 2, rest[: w - len(marker) - 3])
                stdscr.attroff(curses.color_pair(4))

        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(len(infos) + 2, 0, "─" * (w - 1))
        stdscr.attroff(curses.color_pair(4))

        stdscr.refresh()
        key = stdscr.getch()

        if key == curses.KEY_UP and selected > 0:
            selected -= 1
        elif key == curses.KEY_DOWN and selected < len(infos) - 1:
            selected += 1
        elif key in (curses.KEY_ENTER, 10, 13):
            raise SystemExit(infos[selected]["source_url"])
        elif key == ord("q"):
            return


@app.command()
def main(query: str = typer.Argument(None, help="Search query")):
    ensure_chromium()

    if not query:
        query = typer.prompt(typer.style("[?] Input query", fg=typer.colors.CYAN))

    infos = asyncio.run(async_main(query))
    if not infos:
        typer.echo(typer.style("[!] Nothing found.", fg=typer.colors.RED))
        return

    typer.echo(typer.style("[*] Opening player...", fg=typer.colors.GREEN))

    url_to_play = None

    def _draw(stdscr):
        nonlocal url_to_play
        try:
            draw(stdscr, infos)
        except SystemExit as e:
            url_to_play = str(e)

    curses.wrapper(_draw)

    if url_to_play:
        typer.echo(typer.style(f"[>] Playing: {url_to_play}", fg=typer.colors.CYAN))
        play(url_to_play)


if __name__ == "__main__":
    app()
