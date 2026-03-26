# Vercel Python Serverless - TubeGrab Pro
# api/download.py

import os
import re
import tempfile
import base64
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import yt_dlp

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
except Exception:
    FFMPEG_PATH = "ffmpeg"


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


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        url = (params.get("url") or [""])[0].strip()
        fmt = (params.get("format") or ["mp3"])[0].lower()

        if not url:
            self._send_error(400, "URL gerekli")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            self._send_error(400, "Geçerli YouTube linki girin")
            return
        if fmt not in ("mp3", "mp4"):
            self._send_error(400, "Format mp3 veya mp4 olmalı")
            return

        tmp_dir = tempfile.mkdtemp()
        out_tmpl = os.path.join(tmp_dir, "%(title)s.%(ext)s")

        cookiefile = load_cookiefile_from_env()
        ydl_opts = {
            "outtmpl": out_tmpl,
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
            ydl_opts["cookiefile"] = cookiefile

        if fmt == "mp3":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }]
        else:
            # Bazi videolarda mp4+m4a kombinasyonu yok; daha toleransli secici kullan.
            ydl_opts["format"] = "bestvideo*+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    self._send_error(400, "Video bilgisi alınamadı")
                    return

            title = sanitize(info.get("title", "download"))
            ext = "mp3" if fmt == "mp3" else "mp4"
            files = list(Path(tmp_dir).glob(f"*.{ext}"))
            if not files:
                files = list(Path(tmp_dir).glob("*.*"))
            if not files:
                self._send_error(500, "Dosya bulunamadı")
                return

            file_path = files[0]
            filename = f"{title}.{ext}"

            with open(file_path, "rb") as f:
                data = f.read()

            for f in Path(tmp_dir).glob("*"):
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                os.rmdir(tmp_dir)
            except Exception:
                pass

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "Private video" in msg or "Video unavailable" in msg:
                msg = "Bu video gizli veya mevcut değil."
            elif "Invalid URL" in msg or "Unable to extract" in msg:
                msg = "Geçersiz link veya video bulunamadı."
            self._send_error(400, msg)
        except Exception as e:
            self._send_error(500, f"Sunucu hatası: {str(e)}")
        finally:
            if cookiefile and os.path.exists(cookiefile):
                try:
                    os.remove(cookiefile)
                except Exception:
                    pass

    def _send_error(self, code: int, msg: str):
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(msg.encode("utf-8"))
