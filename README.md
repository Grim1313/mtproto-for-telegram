# 🌐 List of free proxy for Telegram (MTProto)

Auto-updated, auto-verified.

This repository is a **fork-focused mirror** of the original project [`SoliSpirit/mtproto`](https://github.com/SoliSpirit/mtproto), with one practical goal:

- keep the original raw proxy feed,
- and provide a more convenient **clickable Markdown list** for daily use.

> **Upstream source:** `SoliSpirit/mtproto`  
> **Sync interval:** every 12 hours

---

## 📦 What this fork provides

This fork keeps **three formats** in sync:

- [`all_proxies.txt`](all_proxies.txt) — original plain text list (one proxy per line)
- [`all_proxies.md`](all_proxies.md) — human-friendly clickable Markdown list using `t.me` links
- [`all_proxies.html`](https://grim1313.github.io/mtproto-for-telegram/all_proxies.html) — browser page with direct `tg://proxy` buttons

So you can choose:

- **automation / scripts** → use `all_proxies.txt`
- **manual usage where `t.me` works** → use `all_proxies.md`
- **manual usage where `t.me` is blocked** → use the HTML page: [`all_proxies.html`](https://grim1313.github.io/mtproto-for-telegram/all_proxies.html)

---

## 🔄 Auto-sync from original project

The repository automatically updates from the original upstream list in `SoliSpirit/mtproto` every 12 hours.

Automation is implemented in:

- `scripts/sync_mtproto.py`
- `.github/workflows/sync-from-solispirit.yml`

> `all_proxies.txt` is committed only when its content actually changes. If upstream data is unchanged, GitHub can show an older “last updated” date for this file.

---

## 💡 How to use

If `t.me` opens in your country:

1. Open [`all_proxies.md`](all_proxies.md)
2. Click any proxy link
3. Telegram will open and suggest enabling that proxy

If `t.me` is blocked:

1. Open the HTML page: [`all_proxies.html`](https://grim1313.github.io/mtproto-for-telegram/all_proxies.html)
2. Click **Open** next to any proxy to use a direct `tg://proxy?...` link
3. Use **Copy** if your browser asks you to paste the link manually

The Markdown list uses `https://t.me/proxy?...` links because GitHub and some desktop Markdown viewers do not reliably allow clickable custom URL schemes such as `tg://`.
The HTML page is intended for direct `tg://proxy?...` links.

Possible caveats:

- `tg://` links require the Telegram app to be installed and registered as the handler for Telegram links.
- Some browsers or in-app webviews may ask for confirmation before opening Telegram, or may block custom URL schemes.
- If both the HTML page and the Markdown list do not work, copy the proxy data manually from [`all_proxies.txt`](all_proxies.txt) and add it in Telegram settings.

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
