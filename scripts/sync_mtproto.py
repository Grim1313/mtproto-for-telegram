#!/usr/bin/env python3
"""Sync MTProto proxy list from SoliSpirit/mtproto and build markdown links."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen

DEFAULT_SOURCE_URL = "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt"
TXT_PATH = Path("all_proxies.txt")
MD_PATH = Path("all_proxies.md")


def fetch_source(url: str, timeout: int) -> str:
    request = Request(url, headers={"User-Agent": "mtproto-sync-bot/1.0"})
    with urlopen(request, timeout=timeout) as response:  # nosec: B310 - trusted static source
        return response.read().decode("utf-8")


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


def to_clickable_link(proxy_url: str) -> str:
    parsed = urlparse(proxy_url)
    if parsed.scheme == "https" and parsed.netloc == "t.me":
        return proxy_url

    params = parse_qs(parsed.query)
    query_pairs = []
    for key in ("server", "port", "secret"):
        if key in params and params[key]:
            query_pairs.append((key, params[key][0]))

    if not query_pairs:
        return proxy_url

    return f"https://t.me/proxy?{urlencode(query_pairs)}"


def proxy_label(proxy_url: str, index: int) -> str:
    parsed = urlparse(proxy_url)
    params = parse_qs(parsed.query)
    server = params.get("server", ["unknown"])[0]
    port = params.get("port", ["?"])[0]
    return f"{index:04d}. {server}:{port}"


def build_markdown(proxies: list[str], source: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    header = [
        "# MTProto Proxy Links",
        "",
        f"Source: `{source}`",
        f"Last sync: {timestamp}",
        f"Total proxies: **{len(proxies)}**",
        "",
        "Click any link below to open it directly in Telegram:",
        "",
    ]
    body = [
        f"- [{proxy_label(proxy, i)}]({to_clickable_link(proxy)})"
        for i, proxy in enumerate(proxies, start=1)
    ]
    return "\n".join(header + body) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--local-only",
        action="store_true",
        help="Use local all_proxies.txt as input instead of downloading from upstream.",
    )
    parser.add_argument("--source-url", default=DEFAULT_SOURCE_URL, help="Upstream URL for all_proxies.txt")
    parser.add_argument("--timeout", type=int, default=30, help="HTTP timeout in seconds")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.local_only:
        raw = TXT_PATH.read_text(encoding="utf-8")
    else:
        raw = fetch_source(args.source_url, args.timeout)

    proxies = normalize_lines(raw)

    TXT_PATH.write_text("\n".join(proxies) + "\n", encoding="utf-8")
    MD_PATH.write_text(build_markdown(proxies, args.source_url), encoding="utf-8")

    print(f"Synced {len(proxies)} proxies")


if __name__ == "__main__":
    main()
