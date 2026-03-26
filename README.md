# Bedelli MP3 İndirici

Askeri temalı arayüzle YouTube linklerini analiz eden, parçaları listeleyen ve tekli/çoklu indirme yapan web uygulaması.

## Özellikler

- YouTube video veya oynatma listesi linkini analiz etme (`Bul`)
- Parçaları tek tek indirme
- Seçilen parçaları tek dosyada indirme (`parcalar.zip`)
- MP3 / MP4 format seçimi
- Sağ panelde kullanım rehberi (yardım popup)
- Üst bölümde her girişte rastgele askeri görsel

## Teknolojiler

- Frontend: Next.js (App Router)
- Backend: FastAPI + `yt-dlp` (Railway)
- Donusturme: ffmpeg

## Proje Yapısı

```text
web/                   # Next.js frontend (Vercel)
backend/               # FastAPI backend (Railway)
```

## Yerelde Çalıştırma

Yerelde 2 servis:

1) Backend (`http://127.0.0.1:8000`)
2) UI (`http://localhost:3000`)

### 1) Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2) UI

```bash
cd web
npm install
set NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
npm run dev
```

## Kullanım Akışı

1. YouTube linkini yapıştır.
2. `Bul` ile listeyi getir.
3. Parça seç:
   - Satırdaki `İndir` => tek dosya
   - `Seçilenleri indir` => `parcalar.zip`

## Deploy (Vercel + Railway)

1. Railway'de backend deploy et (`backend` root).
2. Domain al (`https://....up.railway.app`).
3. Vercel'de frontend deploy et (`web` root).
4. Vercel env:
   - `NEXT_PUBLIC_API_BASE=https://....up.railway.app`

## YouTube "not a bot" (cookies) ayarı

YouTube bazı IP'lerde doğrulama isteyebilir. Bunu azaltmak için Railway backend env'e aşağıdaki değişkenlerden birini ekleyebilirsin:

- `YTDLP_COOKIES_B64` (önerilen): `cookies.txt` dosyasının Base64 hali
- `YTDLP_COOKIES_TXT`: `cookies.txt` içeriğinin düz metni

Backend endpoint'leri (`/info`, `/download`, `/download-batch`) bu env'leri otomatik kullanır.
