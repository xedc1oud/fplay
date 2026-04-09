<div align="center">

```
███████╗██████╗ ██╗      █████╗ ██╗   ██╗
██╔════╝██╔══██╗██║     ██╔══██╗╚██╗ ██╔╝
█████╗  ██████╔╝██║     ███████║ ╚████╔╝ 
██╔══╝  ██╔═══╝ ██║     ██╔══██║  ╚██╔╝  
██║     ██║     ███████╗██║  ██║   ██║   
╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝   ╚═╝   
```

**A terminal-based video player for VK Video**

![Linux](https://img.shields.io/badge/Linux-only-FCC624?style=flat-square&logo=linux&logoColor=black)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat-square&logo=python&logoColor=white)
![uv](https://img.shields.io/badge/built_with-uv-DE5FE9?style=flat-square)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)

</div>

---

## What is fplay?

`fplay` is a command-line tool for searching and watching videos from VK Video directly in your terminal. No browser, no GUI — just search, select, and watch in `mpv`.

---

## Requirements

- **OS:** Linux (only)
- **Python:** 3.13+
- **Package manager:** [`uv`](https://github.com/astral-sh/uv)
- **Player:** [`mpv`](https://mpv.io/)

---

## Installation

### 1. Install `uv` (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> Restart your shell or run `source $HOME/.local/bin/env` after installation.

### 2. Clone the repository

```bash
git clone https://github.com/xedc1oud/fplay.git
cd fplay
```

### 3. Build and install

```bash
uv tool install .
```

---

## Updating

```bash
cd fplay
git pull
uv tool install . --reinstall
```

---

## Usage

### Search and watch

```bash
fplay <query>
```

Searches VK Video, shows up to 5 results in a curses menu, and opens the selected video in `mpv` fullscreen.

```bash
fplay зверополис
fplay "как приручить дракона"
fplay inception
```

### Interactive prompt

```bash
fplay
```

If no query is provided, `fplay` will prompt for one.

---

## Interface

```
 [>] fplay — use arrows to navigate, enter to play, q to quit
─────────────────────────────────────────────────────────────
 [>] 1. Зверополис | Zootopia (2016)               [1:48:12]
 [ ] 2. Зверополис (полный фильм)                  [1:47:51]
 [ ] 3. Зверополис — Русский трейлер               [0:02:13]
 [ ] 4. Зверополис 4K HDR                          [1:48:48]
 [ ] 5. Зверополис (2016) BDRip 1080p              [1:48:12]
─────────────────────────────────────────────────────────────
```

**Controls:**

| Key | Action |
|---|---|
| `↑` / `↓` | Navigate results |
| `Enter` | Play selected video in mpv |
| `q` | Quit |

---

## Notes

### VK rate limiting

Sometimes VK blocks the connection mid-search. This is normal — `fplay` will automatically retry until it gets through. You might see this in the terminal:

```
[?] Searching: inception
[!] Retrying...
[*] Found 5 results, fetching info...
```

`[!] Retrying...` means VK dropped the connection. Just wait a few seconds — `fplay` handles it automatically, no action needed on your end.

---

## Quick Reference

| Command | Description |
|---|---|
| `fplay` | Launch with interactive prompt |
| `fplay <query>` | Search and pick a video |
| `fplay --help` | Show help |

---

## Uninstall

```bash
uv tool uninstall fplay
```

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

<div align="center">
<sub>Made for Linux. Runs in a terminal. Does its job.</sub>
<br><br>
<sub>suck VK 🖕</sub>
</div>
