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
- API: Python Serverless (`web/api/*.py`) + `yt-dlp`
- Dönüştürme: `ffmpeg` (`imageio-ffmpeg` ile)

## Proje Yapısı

```text
web/
  app/                 # Arayüz
  api/                 # Vercel Python serverless endpoint'leri
    download.py
    download-batch.py
    info.py
    hero.py
  scripts/dev-api.py   # Yerel geliştirme API sunucusu
```

## Yerelde Çalıştırma

Yerel geliştirmede 2 servis çalışır:

1) Python API (`http://127.0.0.1:3002`)
2) Next.js UI (`http://localhost:3000`)

### 1) API

```bash
cd web
pip install -r requirements.txt
python -m uvicorn scripts.dev-api:app --reload --port 3002
```

### 2) UI

```bash
cd web
npm install
npm run dev
```

## Kullanım Akışı

1. YouTube linkini yapıştır.
2. `Bul` ile listeyi getir.
3. Parça seç:
   - Satırdaki `İndir` => tek dosya
   - `Seçilenleri indir` => `parcalar.zip`

## Vercel Deploy

1. Projeyi GitHub'a pushla.
2. Vercel'de yeni proje oluştur.
3. **Root Directory** olarak `web` seç.
4. Deploy et.

Not: Uygulama Vercel'de `web/api` altındaki Python endpoint'leriyle çalışır.

## YouTube "not a bot" (cookies) ayarı

YouTube bazı IP'lerde doğrulama isteyebilir. Bunu azaltmak için Vercel'de aşağıdaki env'lerden birini ekleyebilirsin:

- `YTDLP_COOKIES_B64` (önerilen): `cookies.txt` dosyasının Base64 hali
- `YTDLP_COOKIES_TXT`: `cookies.txt` içeriğinin düz metni

API endpoint'leri (`/api/info`, `/api/download`, `/api/download-batch`) bu env'leri otomatik kullanır.
