# 🌐 List of free proxy for Telegram (MTProto)

Auto-updated, auto-verified.

This repository is a **fork-focused mirror** of the original project [`SoliSpirit/mtproto`](https://github.com/SoliSpirit/mtproto), with one practical goal:

- keep the original raw proxy feed,
- and provide a more convenient **clickable Markdown list** for daily use.

> **Upstream source:** `SoliSpirit/mtproto`  
> **Sync interval:** every 12 hours

---

## 📦 What this fork provides

This fork keeps **both formats** in sync:

- [`all_proxies.txt`](all_proxies.txt) — original plain text list (one proxy per line)
- [`all_proxies.md`](all_proxies.md) — human-friendly clickable list with direct `tg://proxy` fallbacks

So you can choose:

- **automation / scripts** → use `all_proxies.txt`
- **manual usage** (phone/desktop) → use `all_proxies.md`

---

## 🔄 Auto-sync from original project

The repository automatically updates from the original upstream list in `SoliSpirit/mtproto` every 12 hours.

Automation is implemented in:

- `scripts/sync_mtproto.py`
- `.github/workflows/sync-from-solispirit.yml`

> `all_proxies.txt` is committed only when its content actually changes. If upstream data is unchanged, GitHub can show an older “last updated” date for this file.

---

## 💡 How to use

1. Open [`all_proxies.md`](all_proxies.md)
2. Click the server link to open the proxy through `t.me`
3. If `t.me` is blocked, copy the `direct: tg://proxy?...` value next to the server link and open it locally

The Markdown list keeps `https://t.me/proxy?...` as the clickable link because GitHub and some desktop Markdown viewers do not reliably allow clickable custom URL schemes such as `tg://`.
For countries where `t.me` is blocked, each proxy also includes a copyable direct `tg://proxy?...` fallback.

Possible caveats:

- `tg://` links require the Telegram app to be installed and registered as the handler for Telegram links.
- Some browsers, in-app webviews, Markdown viewers, or Git hosting interfaces may ask for confirmation before opening Telegram, or may block custom URL schemes.
- If both the clickable `t.me` link and the direct `tg://` fallback do not work, copy the proxy data manually from [`all_proxies.txt`](all_proxies.txt) and add it in Telegram settings.

---

## 🔗 Related repositories

- Original project: [`SoliSpirit/mtproto`](https://github.com/SoliSpirit/mtproto)
- This fork: current repository

---

## ⭐ Support

If this fork is useful, star both repositories:

- this fork
- original `SoliSpirit/mtproto`

- [English](README.md)
- [Русский](README_RU.md)
