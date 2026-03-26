import io
import json
import os
import re
import tempfile
import base64
import zipfile
from http.server import BaseHTTPRequestHandler
from pathlib import Path

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
    def do_POST(self):
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(content_length) if content_length > 0 else b"{}"
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            self._send_text(400, "Geçersiz JSON")
            return

        items = payload.get("items") or []
        fmt = (payload.get("format") or "mp3").lower()
        # Geçici olarak MP4 kapalı: toplu indirmeyi MP3'e zorla.
        fmt = "mp3"
        if not items:
            self._send_text(400, "En az bir parça seçin")
            return
        if fmt not in ("mp3", "mp4"):
            self._send_text(400, "Format mp3 veya mp4 olmalı")
            return

        ext = "mp3" if fmt == "mp3" else "mp4"
        cookiefile = load_cookiefile_from_env()
        ydl_opts = {
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
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }
            ]
        else:
            # Bazi videolarda mp4+m4a kombinasyonu yok; daha toleransli secici kullan.
            ydl_opts["format"] = "bestvideo*+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"

        zip_buffer = io.BytesIO()
        used_names = set()

        def unique_filename(base: str) -> str:
            safe = sanitize(base)
            candidate = f"{safe}.{ext}"
            if candidate not in used_names:
                used_names.add(candidate)
                return candidate
            i = 1
            while f"{safe} ({i}).{ext}" in used_names:
                i += 1
            candidate = f"{safe} ({i}).{ext}"
            used_names.add(candidate)
            return candidate

        try:
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
                for item in items:
                    url = str(item.get("url") or "").strip()
                    title = str(item.get("title") or "parca")
                    if not url:
                        continue

                    tmp_dir = tempfile.mkdtemp()
                    out_tmpl = os.path.join(tmp_dir, "%(title)s.%(ext)s")
                    ydl_opts["outtmpl"] = out_tmpl

                    try:
                        format_fallbacks = []
                        if fmt == "mp4":
                            format_fallbacks = [
                                "bestvideo*+bestaudio/best",
                                "best[ext=mp4]/best",
                                "best",
                            ]
                        else:
                            format_fallbacks = [
                                "bestaudio/best",
                                "best",
                            ]

                        success = False
                        last_err = None
                        for f in format_fallbacks:
                            try:
                                attempt_opts = dict(ydl_opts)
                                attempt_opts["format"] = f
                                with yt_dlp.YoutubeDL(attempt_opts) as ydl:
                                    ydl.download([url])
                                success = True
                                break
                            except yt_dlp.utils.DownloadError as e:
                                last_err = e
                                if "Requested format is not available" in str(e):
                                    continue
                                raise

                        if not success and last_err:
                            raise last_err

                        files = list(Path(tmp_dir).glob(f"*.{ext}")) or list(Path(tmp_dir).glob("*.*"))
                        if files:
                            zf.write(files[0], arcname=unique_filename(title))
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
            data = zip_buffer.getvalue()
            self.send_response(200)
            self.send_header("Content-Type", "application/zip")
            self.send_header("Content-Disposition", 'attachment; filename="parcalar.zip"')
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except yt_dlp.utils.DownloadError as e:
            self._send_text(400, str(e))
        except Exception as e:
            self._send_text(500, f"Sunucu hatası: {str(e)}")
        finally:
            if cookiefile and os.path.exists(cookiefile):
                try:
                    os.remove(cookiefile)
                except Exception:
                    pass

    def _send_text(self, code: int, text: str):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
