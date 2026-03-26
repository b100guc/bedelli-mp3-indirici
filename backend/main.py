import base64
import io
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import List, Literal, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel

import yt_dlp

try:
    import imageio_ffmpeg

    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = "ffmpeg"

app = FastAPI(title="Bedelli MP3 API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def sanitize(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name)[:200].strip() or "download"


def load_cookiefile_from_env() -> str | None:
    cookies_b64 = os.getenv("YTDLP_COOKIES_B64", "").strip()
    cookies_txt = os.getenv("YTDLP_COOKIES_TXT", "").strip()
    if not cookies_b64 and not cookies_txt:
        return None

    raw = b""
    try:
        if cookies_b64:
            raw = base64.b64decode(cookies_b64)
        else:
            raw = cookies_txt.encode("utf-8")
    except Exception:
        return None

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".txt")
    tmp.write(raw)
    tmp.flush()
    tmp.close()
    return tmp.name


def base_ydl_opts() -> dict:
    cookiefile = load_cookiefile_from_env()
    opts = {
        "noplaylist": True,
        "quiet": True,
        "ffmpeg_location": FFMPEG_PATH,
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
        },
        "extractor_args": {
            "youtube": {"player_client": ["web", "android", "ios"]},
        },
    }
    if cookiefile:
        opts["cookiefile"] = cookiefile
    return opts


class VideoItem(BaseModel):
    id: str
    title: str
    url: str
    index: Optional[int] = None


class InfoResponse(BaseModel):
    type: Literal["single", "playlist"]
    title: str
    item_count: int
    items: List[VideoItem]


class BatchItem(BaseModel):
    url: str
    title: str


class BatchDownloadRequest(BaseModel):
    items: List[BatchItem]
    format: Literal["mp3", "mp4"] = "mp3"


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/info", response_model=InfoResponse)
def info(url: str = Query(...)):
    if not url.strip():
        raise HTTPException(400, "URL gerekli")
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(400, "Geçerli YouTube linki girin")

    opts = base_ydl_opts()
    opts["skip_download"] = True

    cookiefile = opts.get("cookiefile")
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            data = ydl.extract_info(url, download=False)

        items: List[VideoItem] = []
        if data.get("_type") == "playlist" and data.get("entries"):
            entries = data.get("entries") or []
            for idx, entry in enumerate(entries, start=1):
                if not entry:
                    continue
                vid_id = entry.get("id") or entry.get("url") or ""
                title = entry.get("title") or entry.get("fulltitle") or f"Parça {idx}"
                video_url = entry.get("webpage_url") or f"https://www.youtube.com/watch?v={vid_id}"
                items.append(VideoItem(id=vid_id, title=title, url=video_url, index=idx))
            return InfoResponse(
                type="playlist",
                title=data.get("title") or "Oynatma Listesi",
                item_count=len(items),
                items=items,
            )

        title = data.get("fulltitle") or data.get("title") or "Video"
        return InfoResponse(
            type="single",
            title=title,
            item_count=1,
            items=[VideoItem(id=data.get("id") or "", title=title, url=data.get("webpage_url") or url, index=1)],
        )
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(400, str(e))
    finally:
        if cookiefile and os.path.exists(cookiefile):
            try:
                os.remove(cookiefile)
            except Exception:
                pass


def download_with_fallback(url: str, fmt: str, outtmpl: str, opts: dict):
    attempt_opts = dict(opts)
    attempt_opts["outtmpl"] = outtmpl

    if fmt == "mp3":
        fallbacks = ["bestaudio/best", "best"]
        attempt_opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}
        ]
    else:
        fallbacks = ["bestvideo*+bestaudio/best", "best[ext=mp4]/best", "best"]
        attempt_opts["merge_output_format"] = "mp4"

    last_err = None
    for f in fallbacks:
        try:
            one = dict(attempt_opts)
            one["format"] = f
            with yt_dlp.YoutubeDL(one) as ydl:
                info = ydl.extract_info(url, download=True)
            return info
        except yt_dlp.utils.DownloadError as e:
            last_err = e
            if "Requested format is not available" in str(e):
                continue
            raise
    if last_err:
        raise last_err
    raise HTTPException(400, "Video indirilemedi")


@app.get("/download")
def download(url: str = Query(...), format: Literal["mp3", "mp4"] = "mp3"):
    if not url.strip():
        raise HTTPException(400, "URL gerekli")
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(400, "Geçerli YouTube linki girin")

    tmp_dir = tempfile.mkdtemp()
    out_tmpl = os.path.join(tmp_dir, "%(title)s.%(ext)s")
    opts = base_ydl_opts()
    cookiefile = opts.get("cookiefile")

    try:
        info = download_with_fallback(url, format, out_tmpl, opts)
        title = sanitize((info or {}).get("title") or "download")
        ext = "mp3" if format == "mp3" else "mp4"
        files = list(Path(tmp_dir).glob(f"*.{ext}")) or list(Path(tmp_dir).glob("*.*"))
        if not files:
            raise HTTPException(500, "Dosya bulunamadı")
        return FileResponse(files[0], filename=f"{title}.{ext}", media_type="application/octet-stream")
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(400, str(e))
    finally:
        for f in Path(tmp_dir).glob("*"):
            try:
                f.unlink()
            except Exception:
                pass
        try:
            os.rmdir(tmp_dir)
        except Exception:
            pass
        if cookiefile and os.path.exists(cookiefile):
            try:
                os.remove(cookiefile)
            except Exception:
                pass


@app.post("/download-batch")
def download_batch(req: BatchDownloadRequest):
    if not req.items:
        raise HTTPException(400, "En az bir parça seçin")

    fmt = req.format
    ext = "mp3" if fmt == "mp3" else "mp4"
    opts = base_ydl_opts()
    cookiefile = opts.get("cookiefile")
    zip_buffer = io.BytesIO()
    used_names = set()

    def unique_filename(base: str) -> str:
        safe = sanitize(base)
        c = f"{safe}.{ext}"
        if c not in used_names:
            used_names.add(c)
            return c
        i = 1
        while f"{safe} ({i}).{ext}" in used_names:
            i += 1
        c = f"{safe} ({i}).{ext}"
        used_names.add(c)
        return c

    try:
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for item in req.items:
                url = item.url.strip()
                if not url:
                    continue
                tmp_dir = tempfile.mkdtemp()
                out_tmpl = os.path.join(tmp_dir, "%(title)s.%(ext)s")
                try:
                    download_with_fallback(url, fmt, out_tmpl, opts)
                    files = list(Path(tmp_dir).glob(f"*.{ext}")) or list(Path(tmp_dir).glob("*.*"))
                    if files:
                        zf.write(files[0], arcname=unique_filename(item.title))
                finally:
                    for f in Path(tmp_dir).glob("*"):
                        try:
                            f.unlink()
                        except Exception:
                            pass
                    try:
                        os.rmdir(tmp_dir)
                    except Exception:
                        pass

        zip_buffer.seek(0)
        return Response(
            content=zip_buffer.getvalue(),
            media_type="application/zip",
            headers={"Content-Disposition": 'attachment; filename="parcalar.zip"'},
        )
    except yt_dlp.utils.DownloadError as e:
        raise HTTPException(400, str(e))
    finally:
        if cookiefile and os.path.exists(cookiefile):
            try:
                os.remove(cookiefile)
            except Exception:
                pass
