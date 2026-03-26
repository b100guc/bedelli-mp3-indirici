import json
import os
import base64
import tempfile
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import yt_dlp

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

        if not url:
            self._send_text(400, "URL gerekli")
            return
        if "youtube.com" not in url and "youtu.be" not in url:
            self._send_text(400, "Geçerli YouTube linki girin")
            return

        cookiefile = load_cookiefile_from_env()
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
            },
            "extractor_args": {
                "youtube": {"player_client": ["web", "android", "ios"]},
            },
        }
        if cookiefile:
            ydl_opts["cookiefile"] = cookiefile

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                data = ydl.extract_info(url, download=False)

            items = []
            if data.get("_type") == "playlist" and data.get("entries"):
                entries = data.get("entries") or []
                for idx, entry in enumerate(entries, start=1):
                    if not entry:
                        continue
                    vid_id = entry.get("id") or entry.get("url") or ""
                    title = entry.get("title") or entry.get("fulltitle") or f"Parça {idx}"
                    video_url = entry.get("webpage_url") or f"https://www.youtube.com/watch?v={vid_id}"
                    items.append(
                        {
                            "id": vid_id,
                            "title": title,
                            "url": video_url,
                            "index": idx,
                        }
                    )

                resp = {
                    "type": "playlist",
                    "title": data.get("title") or "Oynatma Listesi",
                    "item_count": len(items),
                    "items": items,
                }
            else:
                title = data.get("fulltitle") or data.get("title") or "Video"
                resp = {
                    "type": "single",
                    "title": title,
                    "item_count": 1,
                    "items": [
                        {
                            "id": data.get("id") or "",
                            "title": title,
                            "url": data.get("webpage_url") or url,
                            "index": 1,
                        }
                    ],
                }

            body = json.dumps(resp, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except yt_dlp.utils.DownloadError as e:
            msg = str(e)
            if "Private video" in msg or "Video unavailable" in msg:
                msg = "Bu video gizli veya mevcut değil."
            elif "Invalid URL" in msg or "Unable to extract" in msg:
                msg = "Geçersiz link veya video bulunamadı."
            self._send_text(400, msg)
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
