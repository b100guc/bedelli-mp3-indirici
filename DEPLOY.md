# Bedelli MP3 İndirici – Deploy

## Mimari

- **Frontend (Vercel):** Statik Next.js sitesi. Sadece arayüzü sunar.
- **Backend (Yerel):** Her kullanıcı kendi bilgisayarında Python sunucusu çalıştırır.

## Vercel Deploy (Frontend)

1. GitHub'a pushlayın.
2. [vercel.com](https://vercel.com) → New Project → Repo seçin.
3. **Root Directory:** `web`
4. Deploy.

## Kullanıcılar Ne Yapar?

1. Vercel'deki siteyi açar.
2. Bilgisayarında Python sunucuyu başlatır:
   ```bash
   pip install yt-dlp fastapi uvicorn imageio-ffmpeg
   python -m uvicorn scripts.server:app --port 3002
   ```
3. Sitedeki bağlantı çubuğu yeşile döner → indirme hazır.
