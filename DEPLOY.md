# Bedelli MP3 Indirici - Vercel + Railway Deploy

YouTube bot/captcha engelleri nedeniyle en stabil kurulum:
- `web/` = Vercel (frontend)
- `backend/` = Railway (yt-dlp API)

## 1) Railway (Backend)

1. [railway.app](https://railway.app) -> **New Project** -> **Deploy from GitHub repo**
2. Repo sec (`b100guc/bedelli-mp3-indirici`)
3. **Root Directory:** `backend`
4. Build method: Dockerfile (otomatik algilanir)
5. Deploy bitince domain olustur (`https://...up.railway.app`)
6. Gerekirse env ekle:
   - `YTDLP_COOKIES_B64` veya `YTDLP_COOKIES_TXT`

## 2) Vercel (Frontend)

1. [vercel.com](https://vercel.com) -> **New Project**
2. Repo sec (`b100guc/bedelli-mp3-indirici`)
3. **Root Directory:** `web`
4. Environment Variable ekle:
   - `NEXT_PUBLIC_API_BASE = https://railway-domainin.up.railway.app`
5. Deploy / Redeploy

## 3) Local test

- Backend:
  - `cd backend`
  - `pip install -r requirements.txt`
  - `uvicorn main:app --reload --port 8000`
- Frontend:
  - `cd web`
  - `npm install`
  - `npm run dev`

`NEXT_PUBLIC_API_BASE` verilmezse frontend local `/api/*` endpointlerini kullanir.
