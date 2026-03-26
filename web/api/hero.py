import random
from http.server import BaseHTTPRequestHandler
from urllib.request import Request, urlopen

HERO_IMAGES = [
    f"https://www.kkk.tsk.tr/img/default/galeri/{i:03d}.jpg"
    for i in range(1, 83)
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
