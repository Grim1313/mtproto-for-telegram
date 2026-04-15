#!/usr/bin/env python3
"""Sync MTProto proxy list from SoliSpirit/mtproto and build markdown links."""

from __future__ import annotations

import argparse
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from time import sleep
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_SOURCE_URL = "https://raw.githubusercontent.com/SoliSpirit/mtproto/master/all_proxies.txt"
TXT_PATH = Path("all_proxies.txt")
MD_PATH = Path("all_proxies.md")


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


def to_clickable_link(proxy_url: str) -> str:
    parsed = urlparse(proxy_url)
    params = parse_qs(parsed.query)
    query_pairs = []
    for key in ("server", "port", "secret"):
        if key in params and params[key]:
            query_pairs.append((key, params[key][0]))

    if not query_pairs:
        return proxy_url

    return f"tg://proxy?{urlencode(query_pairs)}"


def proxy_target(proxy_url: str) -> str:
    parsed = urlparse(proxy_url)
    params = parse_qs(parsed.query)
    server = params.get("server", ["unknown"])[0]
    port = params.get("port", ["?"])[0]
    return f"{server}:{port}"


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
    txt_changed = previous_txt != normalized_txt

    if txt_changed:
        TXT_PATH.write_text(normalized_txt, encoding="utf-8")

    last_sync = resolve_last_sync_timestamp(previous_md, txt_changed)
    rendered_md = build_markdown(proxies, args.source_url, txt_sha256, last_sync)

    if previous_md != rendered_md:
        MD_PATH.write_text(rendered_md, encoding="utf-8")

    print(f"Synced {len(proxies)} proxies")


if __name__ == "__main__":
    main()
