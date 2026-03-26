# Bedelli MP3 Downloader

> **[Türkçe versiyon →](README.md)**

Military-themed YouTube video/playlist downloader. The UI runs on the web, the download engine runs on your own computer.

## How It Works

| Layer | Where? | Technology |
|-------|--------|------------|
| **UI** | Vercel or localhost | Next.js (static) |
| **Download engine** | Your computer | Python, FastAPI, yt-dlp, FFmpeg |

Open the site → connect to your local server via the connection panel → downloads happen on your machine.

## Features

- Single video or playlist support
- MP3 (320kbps) and MP4 format selection
- Playlist tracks listed with thumbnails
- Single download or batch selected as ZIP
- Select all / clear selection
- Collapsible connection panel (connect, disconnect, address settings)
- Copyable startup command
- Military theme with random hero images

## Requirements

- **Python 3.10+**
- **FFmpeg**
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Quick Start

```bash
git clone https://github.com/b100guc/bedelli-mp3-indirici.git
cd bedelli-mp3-indirici/web
pip install -r requirements.txt
python -m uvicorn scripts.server:app --port 3002
```

You should see `Uvicorn running on http://127.0.0.1:3002` in the output.

Open the site in your browser → the connection panel at the top turns green → ready to use.

## Usage

1. **Connection check** — The top panel should show green "Bağlı" (Connected). You can expand it and click "Bağlan" (Connect).
2. **Paste link** — Enter a YouTube video or playlist URL.
3. **Find** — Tracks are listed with thumbnails.
4. **Select format** — MP3 or MP4.
5. **Download** — "İndir" for a single track, "Seçilenleri indir" for selected items as ZIP.

## Local Development (UI + API)

If you want to run both the frontend and backend locally:

**Additional requirement:** Node.js 18+

```bash
cd web
npm install
```

Open two terminals (both inside `web/`):

| Terminal | Command | Port |
|----------|---------|------|
| API | `python -m uvicorn scripts.server:app --reload --port 3002` | 3002 |
| UI | `npm run dev` | 3000 |

Open `http://localhost:3000` in your browser.

## API Settings

If the server is running on a different port, expand the connection panel on the site and change the API address. The setting is saved in the browser.

## Project Structure

```
web/
├── app/                # Next.js frontend
│   ├── page.tsx        # Main page component
│   ├── page.module.css # Styles
│   ├── globals.css     # Theme variables
│   └── layout.tsx      # Root layout
├── public/hero/        # Random hero images (10 total)
├── scripts/
│   └── server.py       # Python API server (FastAPI)
├── requirements.txt    # Python dependencies
├── package.json        # Node.js dependencies
└── next.config.js      # Next.js config (static export)
```

## Vercel Deploy (Frontend Only)

1. Push the repo to GitHub.
2. [vercel.com](https://vercel.com) → New Project → Select the repo.
3. **Root Directory:** `web`
4. Deploy.

Vercel only serves the UI. Downloads are handled by the Python server running on each user's own computer.

## License

MIT
