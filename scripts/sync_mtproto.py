#!/usr/bin/env python3
"""Sync MTProto proxy list from SoliSpirit/mtproto and build markdown links."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from html import escape
from pathlib import Path
from time import sleep
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_SOURCE_URL = "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt"
TXT_PATH = Path("all_proxies.txt")
MD_PATH = Path("all_proxies.md")
HTML_PATH = Path("all_proxies.html")


def fetch_source(url: str, timeout: int, max_retries: int, backoff_base: float) -> str:
    attempt = 0
    while True:
        attempt += 1
        request = Request(url, headers={"User-Agent": "mtproto-sync-bot/1.0"})
        try:
            with urlopen(request, timeout=timeout) as response:  # nosec: B310 - trusted static source
                return response.read().decode("utf-8")
        except HTTPError as exc:
            if exc.code == 429 and attempt <= max_retries:
                retry_after_header = exc.headers.get("Retry-After", "").strip()
                retry_after: float | None = None
                if retry_after_header.isdigit():
                    retry_after = float(retry_after_header)

                backoff_delay = backoff_base * (2 ** (attempt - 1))
                delay = retry_after if retry_after is not None else backoff_delay
                print(
                    f"HTTP 429 from upstream (attempt {attempt}/{max_retries + 1}). "
                    f"Sleeping {delay:.1f}s before retry."
                )
                sleep(delay)
                continue
            raise
        except URLError:
            if attempt <= max_retries:
                delay = backoff_base * (2 ** (attempt - 1))
                print(
                    f"Network error from upstream (attempt {attempt}/{max_retries + 1}). "
                    f"Sleeping {delay:.1f}s before retry."
                )
                sleep(delay)
                continue
            raise


def normalize_lines(raw: str) -> list[str]:
    lines: list[str] = []
    seen: set[str] = set()
    for line in raw.splitlines():
        value = line.strip()
        if not value:
            continue
        if not (value.startswith("tg://proxy?") or value.startswith("https://t.me/proxy?")):
            continue
        if value in seen:
            continue
        seen.add(value)
        lines.append(value)
    return lines


def proxy_query(proxy_url: str) -> str | None:
    parsed = urlparse(proxy_url)
    params = parse_qs(parsed.query)
    query_pairs = []
    for key in ("server", "port", "secret"):
        if key in params and params[key]:
            query_pairs.append((key, params[key][0]))

    if not query_pairs:
        return None

    return urlencode(query_pairs)


def to_clickable_link(proxy_url: str) -> str:
    query = proxy_query(proxy_url)
    if query is None:
        return proxy_url

    return f"https://t.me/proxy?{query}"


def to_direct_link(proxy_url: str) -> str:
    query = proxy_query(proxy_url)
    if query is None:
        return proxy_url

    return f"tg://proxy?{query}"


def proxy_target(proxy_url: str) -> str:
    parsed = urlparse(proxy_url)
    params = parse_qs(parsed.query)
    server = params.get("server", ["unknown"])[0]
    port = params.get("port", ["?"])[0]
    return f"{server}:{port}"


def proxy_secret_mode(proxy_url: str) -> tuple[str, str]:
    parsed = urlparse(proxy_url)
    params = parse_qs(parsed.query)
    secret = params.get("secret", [""])[0].lower()
    if secret.startswith("ee"):
        return ("tls", "TLS masquerading")
    if secret.startswith("dd"):
        return ("random-padding", "Random padding")
    return ("unknown", "Unknown")


def build_markdown(proxies: list[str], source: str, txt_sha256: str, last_sync: str) -> str:
    header = [
        "# MTProto Proxy Links",
        "",
        f"Source: `{source}`",
        f"Last sync: {last_sync}",
        f"TXT SHA256: `{txt_sha256}`",
        f"Total proxies: **{len(proxies)}**",
        "",
        "Click any link below to open it directly in Telegram:",
        "",
    ]
    body = [
        f"- {i:04d}\\. [{proxy_target(proxy)}]({to_clickable_link(proxy)})"
        for i, proxy in enumerate(proxies, start=1)
    ]
    return "\n".join(header + body) + "\n"


def build_html(proxies: list[str], source: str, txt_sha256: str, last_sync: str) -> str:
    rows = []
    for i, proxy in enumerate(proxies, start=1):
        target = proxy_target(proxy)
        mode_class, mode_label = proxy_secret_mode(proxy)
        direct_link = to_direct_link(proxy)
        fallback_link = to_clickable_link(proxy)
        rows.append(
            "        <li class=\"proxy-row\">"
            f"<span class=\"proxy-index\">{i:04d}</span>"
            f"<span class=\"proxy-mode proxy-mode-{mode_class}\" title=\"{escape(mode_label, quote=True)}\" aria-label=\"{escape(mode_label, quote=True)}\"></span>"
            f"<span class=\"proxy-target\">{escape(target)}</span>"
            f"<a class=\"button primary\" href=\"{escape(direct_link, quote=True)}\">Open</a>"
            f"<a class=\"button secondary\" href=\"{escape(fallback_link, quote=True)}\">t.me</a>"
            f"<button class=\"button secondary copy\" type=\"button\" data-link=\"{escape(direct_link, quote=True)}\">Copy</button>"
            "</li>"
        )

    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "  <meta charset=\"utf-8\">\n"
        "  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "  <title>MTProto Proxy Links</title>\n"
        "  <style>\n"
        "    :root { color-scheme: light dark; --bg: #f6f7f9; --fg: #14161a; --muted: #5c6675; --line: #d8dde5; --primary: #168acd; --primary-fg: #ffffff; --surface: #ffffff; --surface-alt: #eef2f6; --mode-tls: #16a34a; --mode-random-padding: #f59e0b; --mode-unknown: #dc2626; }\n"
        "    @media (prefers-color-scheme: dark) { :root { --bg: #111418; --fg: #f2f4f7; --muted: #a8b0bd; --line: #303743; --primary: #2ea6e6; --primary-fg: #061018; --surface: #181d24; --surface-alt: #222936; --mode-tls: #22c55e; --mode-random-padding: #fbbf24; --mode-unknown: #f87171; } }\n"
        "    * { box-sizing: border-box; }\n"
        "    body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.5 system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; }\n"
        "    main { width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 32px 0 48px; }\n"
        "    h1 { margin: 0 0 12px; font-size: 32px; line-height: 1.15; }\n"
        "    p { margin: 0 0 16px; color: var(--muted); }\n"
        "    .header-link { display: inline-flex; align-items: center; margin-left: 10px; color: var(--primary); font-weight: 600; text-decoration: none; white-space: nowrap; }\n"
        "    .header-link:hover { text-decoration: underline; }\n"
        "    .meta { display: grid; gap: 6px; margin: 18px 0 24px; color: var(--muted); font-size: 14px; }\n"
        "    .meta code { color: var(--fg); overflow-wrap: anywhere; }\n"
        "    .legend { display: flex; flex-wrap: wrap; gap: 12px 18px; margin: 0 0 20px; padding: 12px 14px; border: 1px solid var(--line); border-radius: 8px; background: var(--surface); }\n"
        "    .legend-item { display: inline-flex; align-items: center; gap: 8px; color: var(--muted); font-size: 14px; }\n"
        "    .proxy-list { list-style: none; padding: 0; margin: 0; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: var(--surface); }\n"
        "    .proxy-row { display: grid; grid-template-columns: 64px 18px minmax(0, 1fr) 88px 80px 80px; gap: 10px; align-items: center; padding: 10px 12px; border-top: 1px solid var(--line); }\n"
        "    .proxy-row:first-child { border-top: 0; }\n"
        "    .proxy-index { color: var(--muted); font-variant-numeric: tabular-nums; }\n"
        "    .proxy-mode { display: inline-block; width: 12px; height: 12px; border-radius: 999px; box-shadow: inset 0 0 0 1px rgb(0 0 0 / 0.18); }\n"
        "    .proxy-mode-tls { background: var(--mode-tls); }\n"
        "    .proxy-mode-random-padding { background: var(--mode-random-padding); }\n"
        "    .proxy-mode-unknown { background: var(--mode-unknown); }\n"
        "    .proxy-target { min-width: 0; overflow-wrap: anywhere; font-family: ui-monospace, SFMono-Regular, Consolas, \"Liberation Mono\", monospace; }\n"
        "    .button { display: inline-flex; align-items: center; justify-content: center; min-height: 36px; border: 1px solid var(--line); border-radius: 6px; padding: 0 12px; font: inherit; text-decoration: none; cursor: pointer; }\n"
        "    .primary { border-color: var(--primary); background: var(--primary); color: var(--primary-fg); }\n"
        "    .secondary { background: var(--surface-alt); color: var(--fg); }\n"
        "    .button:focus-visible { outline: 3px solid var(--primary); outline-offset: 2px; }\n"
        "    @media (max-width: 720px) { main { width: min(100% - 20px, 1120px); padding-top: 20px; } h1 { font-size: 26px; } .proxy-row { grid-template-columns: 54px 18px minmax(0, 1fr); } .button { width: 100%; } .primary { grid-column: 1 / 2; } .secondary { grid-column: auto; } }\n"
        "  </style>\n"
        "</head>\n"
        "<body>\n"
        "  <main>\n"
        "    <h1>MTProto Proxy Links</h1>\n"
        "    <p>Use Open for a direct tg://proxy link. Use t.me only if direct links are blocked or not registered on this device.<a class=\"header-link\" href=\"https://github.com/Grim1313/mtproto-for-telegram\">Repository</a></p>\n"
        "    <div class=\"legend\">\n"
        "      <span class=\"legend-item\"><span class=\"proxy-mode proxy-mode-tls\" title=\"TLS masquerading\" aria-hidden=\"true\"></span><span><strong>ee</strong> = TLS masquerading</span></span>\n"
        "      <span class=\"legend-item\"><span class=\"proxy-mode proxy-mode-random-padding\" title=\"Random padding\" aria-hidden=\"true\"></span><span><strong>dd</strong> = Random padding</span></span>\n"
        "      <span class=\"legend-item\"><span class=\"proxy-mode proxy-mode-unknown\" title=\"Unknown\" aria-hidden=\"true\"></span><span><strong>other</strong> = Unknown</span></span>\n"
        "    </div>\n"
        "    <div class=\"meta\">\n"
        f"      <div>Source: <code>{escape(source)}</code></div>\n"
        f"      <div>Last sync: {escape(last_sync)}</div>\n"
        f"      <div>TXT SHA256: <code>{escape(txt_sha256)}</code></div>\n"
        f"      <div>Total proxies: <strong>{len(proxies)}</strong></div>\n"
        "    </div>\n"
        "    <ol class=\"proxy-list\">\n"
        + "\n".join(rows)
        + "\n"
        "    </ol>\n"
        "  </main>\n"
        "  <script>\n"
        "    document.addEventListener('click', async (event) => {\n"
        "      const button = event.target.closest('.copy');\n"
        "      if (!button) return;\n"
        "      const value = button.dataset.link;\n"
        "      try {\n"
        "        await navigator.clipboard.writeText(value);\n"
        "      } catch {\n"
        "        const input = document.createElement('textarea');\n"
        "        input.value = value;\n"
        "        input.style.position = 'fixed';\n"
        "        input.style.opacity = '0';\n"
        "        document.body.appendChild(input);\n"
        "        input.focus();\n"
        "        input.select();\n"
        "        document.execCommand('copy');\n"
        "        input.remove();\n"
        "      }\n"
        "      const previous = button.textContent;\n"
        "      button.textContent = 'Copied';\n"
        "      setTimeout(() => { button.textContent = previous; }, 1200);\n"
        "    });\n"
        "  </script>\n"
        "</body>\n"
        "</html>\n"
    )


def resolve_last_sync_timestamp(previous_md: str | None, txt_changed: bool) -> str:
    if txt_changed or not previous_md:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    for line in previous_md.splitlines():
        if line.startswith("Last sync: "):
            return line.removeprefix("Last sync: ").strip()

    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Use local all_proxies.txt as input instead of downloading from upstream.",
    )
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL, help="Upstream URL for all_proxies.txt")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    parser.add_argument("--max-retries", type=int, default=4, help="Number of retries for transient upstream errors")
    parser.add_argument(
        "--backoff-base",
        type=float,
        default=1.5,
        help="Base delay in seconds for exponential backoff between retries",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.local_only:
        raw = TXT_PATH.read_text(encoding="utf-8")
    else:
        raw = fetch_source(args.source_url, args.timeout, args.max_retries, args.backoff_base)

    proxies = normalize_lines(raw)
    normalized_txt = "\n".join(proxies) + "\n"
    txt_sha256 = hashlib.sha256(normalized_txt.encode("utf-8")).hexdigest()

    previous_txt = TXT_PATH.read_text(encoding="utf-8") if TXT_PATH.exists() else None
    previous_md = MD_PATH.read_text(encoding="utf-8") if MD_PATH.exists() else None
    previous_html = HTML_PATH.read_text(encoding="utf-8") if HTML_PATH.exists() else None
    txt_changed = previous_txt != normalized_txt

    if txt_changed:
        TXT_PATH.write_text(normalized_txt, encoding="utf-8")

    last_sync = resolve_last_sync_timestamp(previous_md, txt_changed)
    rendered_md = build_markdown(proxies, args.source_url, txt_sha256, last_sync)
    rendered_html = build_html(proxies, args.source_url, txt_sha256, last_sync)

    if previous_md != rendered_md:
        MD_PATH.write_text(rendered_md, encoding="utf-8")

    if previous_html != rendered_html:
        HTML_PATH.write_text(rendered_html, encoding="utf-8")

    print(f"Synced {len(proxies)} proxies")


if __name__ == "__main__":
    main()
