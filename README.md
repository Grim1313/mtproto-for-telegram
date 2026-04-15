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
- [`all_proxies.md`](all_proxies.md) — human-friendly clickable list with direct `tg://proxy` links

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
2. Click any proxy link
3. Telegram will open and suggest enabling that proxy

The Markdown list uses `tg://proxy?...` links instead of `https://t.me/proxy?...`.
This avoids relying on the `t.me` domain, which may be blocked in some countries.

Possible caveats:

- `tg://` links require the Telegram app to be installed and registered as the handler for Telegram links.
- Some browsers, in-app webviews, Markdown viewers, or Git hosting interfaces may ask for confirmation before opening Telegram, or may block custom URL schemes.
- If clicking a link does not work, copy the proxy data manually from [`all_proxies.txt`](all_proxies.txt) and add it in Telegram settings.

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
