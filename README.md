# Bedelli MP3 İndirici

Askeri temalı YouTube video/playlist indirici. Linki yapıştır, parçaları listele, tek tek veya toplu ZIP olarak indir.

## Gereksinimler

- **Python 3.10+**
- **Node.js 18+**
- **FFmpeg** (MP3 dönüşümü ve video birleştirme için)
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Kurulum

```bash
git clone https://github.com/b100guc/bedelli-mp3-indirici.git
cd bedelli-mp3-indirici
```

### Python bağımlılıkları

```bash
cd web
pip install -r requirements.txt
```

### Node.js bağımlılıkları

```bash
cd web
npm install
```

## Çalıştırma

**İki ayrı terminal** açın, ikisi de `web` klasöründe:

### Terminal 1 — API sunucusu (Python)

```bash
cd web
python -m uvicorn scripts.dev-api:app --reload --port 3002
```

Çıktıda `Uvicorn running on http://127.0.0.1:3002` görmelisiniz.

### Terminal 2 — Arayüz (Next.js)

```bash
cd web
npm run dev
```

Çıktıda `Ready on http://localhost:3000` görmelisiniz.

### Tarayıcıda aç

```
http://localhost:3000
```

## Kullanım

1. **Link yapıştır** — YouTube video veya oynatma listesi URL'sini girin.
2. **Bul** — Parçalar listelenir (tek video ise 1 satır, playlist ise tümü).
3. **Format seç** — MP3 (320kbps ses) veya MP4 (video).
4. **İndir** — Satırdaki "İndir" ile tek parça, "Seçilenleri indir" ile seçilenleri ZIP olarak indirin.

## Proje Yapısı

```
web/
├── app/              # Next.js arayüzü (page.tsx, globals.css, ...)
├── api/              # Vercel Python serverless fonksiyonları
│   ├── download.py   # Tek parça indirme
│   ├── download-batch.py  # Toplu ZIP indirme
│   ├── info.py       # Video/playlist bilgi alma
│   └── hero.py       # Rastgele askeri görsel proxy
├── scripts/
│   └── dev-api.py    # Yerel geliştirme API sunucusu (FastAPI)
├── requirements.txt  # Python bağımlılıkları
└── package.json      # Node.js bağımlılıkları
```

## Vercel Deploy

1. GitHub'a pushlayın.
2. [vercel.com](https://vercel.com) → New Project → Repo seçin.
3. **Root Directory:** `web`
4. Deploy.

## Lisans

MIT
