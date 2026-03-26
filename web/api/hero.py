import random
from http.server import BaseHTTPRequestHandler
from urllib.request import Request, urlopen

HERO_IMAGES = [
    "https://www.kkk.tsk.tr/img/default/galeri/001.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/005.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/010.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/015.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/020.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/025.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/030.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/035.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/040.jpg",
    "https://www.kkk.tsk.tr/img/default/galeri/045.jpg",
]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            img_url = random.choice(HERO_IMAGES)
            req = Request(
                img_url,
                headers={
                    "User-Agent": "Mozilla/5.0 BedelliMP3Indirici/1.0",
                    "Referer": "https://www.kkk.tsk.tr/default/galeri.aspx",
                },
            )
            with urlopen(req, timeout=20) as resp:
                data = resp.read()
                content_type = resp.headers.get_content_type() or "image/jpeg"

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            body = f"Hero alınamadı: {str(e)}".encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
