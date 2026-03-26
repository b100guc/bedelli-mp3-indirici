# Bedelli MP3 İndirici

Askeri temalı YouTube video/playlist indirici. Arayüz Vercel'de, indirme motoru senin bilgisayarında çalışır.

## Nasıl Çalışır?

| Katman | Nerede çalışır? | Teknoloji |
|--------|-----------------|-----------|
| **Arayüz (UI)** | Vercel (web) | Next.js |
| **İndirme motoru (API)** | Senin bilgisayarın | Python + yt-dlp + FFmpeg |

Vercel'deki siteyi açarsın → bilgisayarında çalışan Python sunucuya bağlanır → indirme işlemlerini kendi makinende yapar.

## Gereksinimler

- **Python 3.10+**
- **FFmpeg** (MP3 dönüşümü ve video birleştirme için)
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Kurulum (Sadece Backend)

```bash
git clone https://github.com/b100guc/bedelli-mp3-indirici.git
cd bedelli-mp3-indirici/web
pip install -r requirements.txt
```

## Sunucuyu Başlat

```bash
cd web
python -m uvicorn scripts.server:app --port 3002
```

Çıktıda `Uvicorn running on http://127.0.0.1:3002` görmelisiniz.

## Kullanım

1. **Siteyi aç** — Vercel'deki adresi veya `http://localhost:3000`'i tarayıcıda aç.
2. **Bağlantı kontrolü** — Üstteki çubuk yeşil "Bağlı" yazmalı. Değilse sunucuyu başlat.
3. **Link yapıştır** — YouTube video veya oynatma listesi URL'sini girin.
4. **Bul** — Parçalar listelenir (tek video ise 1 satır, playlist ise tümü).
5. **Format seç** — MP3 (320kbps ses) veya MP4 (video).
6. **İndir** — Satırdaki "İndir" ile tek parça, "Seçilenleri indir" ile seçilenleri ZIP olarak indirin.

## Yerel Geliştirme (UI + API birlikte)

Hem frontend'i hem backend'i kendi bilgisayarınızda çalıştırmak isterseniz:

### Ek gereksinimler

- **Node.js 18+**

### Kurulum

```bash
cd web
npm install
```

### İki terminal açın

**Terminal 1 — API:**

```bash
cd web
python -m uvicorn scripts.server:app --reload --port 3002
```

**Terminal 2 — UI:**

```bash
cd web
npm run dev
```

Tarayıcıda `http://localhost:3000` açın.

## API Ayarları

Sunucu farklı bir portta veya makinede çalışıyorsa, arayüzdeki ⚙ butonuna tıklayıp API adresini değiştirebilirsiniz. Ayar tarayıcıda saklanır.

## Proje Yapısı

```
web/
├── app/              # Next.js arayüzü (page.tsx, globals.css, ...)
├── scripts/
│   └── server.py     # Python API sunucusu (FastAPI)
├── requirements.txt  # Python bağımlılıkları
└── package.json      # Node.js bağımlılıkları
```

## Vercel Deploy (Sadece Frontend)

1. GitHub'a pushlayın.
2. [vercel.com](https://vercel.com) → New Project → Repo seçin.
3. **Root Directory:** `web`
4. Deploy.

> Not: Vercel sadece arayüzü sunar. İndirme işlemleri her kullanıcının kendi bilgisayarında çalışan Python sunucusu üzerinden gerçekleşir.

## Lisans

MIT
