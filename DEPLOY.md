# TubeGrab Pro – Vercel’e Deploy

Tek proje, backend yok. Her şey Vercel’de çalışır.

## Deploy Adımları

1. **GitHub’a pushlayın** (tüm proje).

2. **[vercel.com](https://vercel.com)** → **New Project** → Repo’yu seçin.

3. **Root Directory:** `web` olarak ayarlayın.

4. **Deploy** ile yayına alın.

## Notlar

- **Python API:** `api/download.py` Vercel Python runtime ile çalışır.
- **FFmpeg:** `imageio-ffmpeg` paketi ile otomatik gelir.
- **Zaman aşımı:** Vercel Pro’da 60 saniye. Uzun videolarda timeout olabilir; kısa videolar sorunsuz çalışır.
