# Yerel geliştirme için indirme API sunucusu
# Kullanım: python scripts/dev-api.py
# http://localhost:3002/download?url=...&format=mp3

import io
import os
import random
import re
import tempfile
import zipfile
from pathlib import Path
from typing import List, Literal, Optional
from urllib.request import Request, urlopen

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import yt_dlp

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = "ffmpeg"

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

HERO_IMAGES: list[str] = [
    f"https://www.kkk.tsk.tr/img/default/galeri/{i:03d}.jpg"
    for i in range(1, 83)
]


@app.get("/hero")
def hero(r: int = Query(0, description="Cache-bust")):
    # Görseli backend üzerinden çekip tarayıcıya servis ediyoruz (hotlink/CORS sorunlarını aşmak için)
    img_url = random.choice(HERO_IMAGES)
    req = Request(
        img_url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) BedelliMP3Indirici/1.0",
            "Referer": "https://www.kkk.tsk.tr/default/galeri.aspx",
        },
    )
    with urlopen(req, timeout=20) as resp:
        data = resp.read()
        content_type = resp.headers.get_content_type() or "image/jpeg"

    return Response(
        content=data,
        media_type=content_type,
        headers={
            "Cache-Control": "no-store",
        },
    )


def sanitize(name: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", name)[:200].strip() or "download"


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


@app.get("/download")
def download(url: str = Query(...), format: str = Query("mp3")):
    if not url.strip():
        raise HTTPException(400, "URL gerekli")
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(400, "Geçerli YouTube linki girin")
    if format not in ("mp3", "mp4"):
        raise HTTPException(400, "Format mp3 veya mp4 olmalı")

    tmp_dir = tempfile.mkdtemp()
    out_tmpl = os.path.join(tmp_dir, "%(title)s.%(ext)s")

    ydl_opts = {
        "outtmpl": out_tmpl,
        "noplaylist": True,
        "quiet": True,
        "ffmpeg_location": FFMPEG_PATH,
    }
    if format == "mp3":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}]
    else:
        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        ydl_opts["merge_output_format"] = "mp4"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
        if not info:
            raise HTTPException(400, "Video bilgisi alınamadı")

        title = sanitize(info.get("title", "download"))
        ext = "mp3" if format == "mp3" else "mp4"
        files = list(Path(tmp_dir).glob(f"*.{ext}")) or list(Path(tmp_dir).glob("*.*"))
        if not files:
            raise HTTPException(500, "Dosya bulunamadı")

        return FileResponse(files[0], filename=f"{title}.{ext}", media_type="application/octet-stream")
    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "Private video" in msg or "Video unavailable" in msg:
            msg = "Bu video gizli veya mevcut değil."
        elif "Invalid URL" in msg or "Unable to extract" in msg:
            msg = "Geçersiz link veya video bulunamadı."
        raise HTTPException(400, msg)


class BatchItem(BaseModel):
    url: str
    title: str


class BatchDownloadRequest(BaseModel):
    items: List[BatchItem]
    format: Literal["mp3", "mp4"] = "mp3"


@app.post("/download-batch")
def download_batch(req: BatchDownloadRequest):
    if not req.items:
        raise HTTPException(400, "En az bir parça seçin")

    ext = "mp3" if req.format == "mp3" else "mp4"
    ydl_opts = {
        "noplaylist": True,
        "quiet": True,
        "ffmpeg_location": FFMPEG_PATH,
    }
    if req.format == "mp3":
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "320"}]
    else:
        ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        ydl_opts["merge_output_format"] = "mp4"

    zip_buffer = io.BytesIO()
    used_names: set[str] = set()

    def unique_filename(base: str) -> str:
        name = f"{sanitize(base)}.{ext}"
        if name in used_names:
            i = 1
            while f"{sanitize(base)} ({i}).{ext}" in used_names:
                i += 1
            name = f"{sanitize(base)} ({i}).{ext}"
        used_names.add(name)
        return name

    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in req.items:
            if not item.url.strip() or "youtube.com" not in item.url and "youtu.be" not in item.url:
                continue
            tmp_dir = tempfile.mkdtemp()
            out_tmpl = os.path.join(tmp_dir, "%(title)s.%(ext)s")
            ydl_opts["outtmpl"] = out_tmpl
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([item.url])
                files = list(Path(tmp_dir).glob(f"*.{ext}")) or list(Path(tmp_dir).glob("*.*"))
                if files:
                    arcname = unique_filename(item.title)
                    zf.write(files[0], arcname=arcname)
            except Exception:
                pass
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


@app.get("/info", response_model=InfoResponse)
def info(url: str = Query(..., description="YouTube video veya oynatma listesi URL'si")):
    if not url.strip():
        raise HTTPException(400, "URL gerekli")
    if "youtube.com" not in url and "youtu.be" not in url:
        raise HTTPException(400, "Geçerli YouTube linki girin")

    # Sadece bilgi al, indirme yok (extract_flat yok = tam başlıklar)
    ydl_opts = {
        "quiet": True,
        "skip_download": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        items: List[VideoItem] = []

        if info.get("_type") == "playlist" and "entries" in info:
            entries = info.get("entries") or []
            for idx, entry in enumerate(entries, start=1):
                if not entry:
                    continue
                vid_id = entry.get("id") or entry.get("url") or ""
                title = entry.get("title") or entry.get("fulltitle") or f"Parça {idx}"
                # Tam video linkini oluştur
                video_url = entry.get("webpage_url") or f"https://www.youtube.com/watch?v={vid_id}"
                items.append(
                    VideoItem(
                        id=vid_id,
                        title=title,
                        url=video_url,
                        index=idx,
                    )
                )

            playlist_title = info.get("title") or "Oynatma Listesi"
            return InfoResponse(
                type="playlist",
                title=playlist_title,
                item_count=len(items),
                items=items,
            )

        # Tek video
        vid_id = info.get("id") or ""
        title = info.get("fulltitle") or info.get("title") or "Video"
        video_url = info.get("webpage_url") or url
        items.append(VideoItem(id=vid_id, title=title, url=video_url, index=1))

        return InfoResponse(
            type="single",
            title=title,
            item_count=1,
            items=items,
        )

    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        if "Private video" in msg or "Video unavailable" in msg:
            msg = "Bu video gizli veya mevcut değil."
        elif "Invalid URL" in msg or "Unable to extract" in msg:
            msg = "Geçersiz link veya video bulunamadı."
        raise HTTPException(400, msg)
    except Exception as e:
        raise HTTPException(500, f"Sunucu hatası: {str(e)}")
