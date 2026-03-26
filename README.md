# Bedelli MP3 İndirici

Askeri temalı YouTube video/playlist indirici. Arayüz web'de, indirme motoru kendi bilgisayarında çalışır.

## Nasıl Çalışır?

| Katman | Nerede? | Teknoloji |
|--------|---------|-----------|
| **Arayüz** | Vercel veya localhost | Next.js (statik) |
| **İndirme motoru** | Senin bilgisayarın | Python, FastAPI, yt-dlp, FFmpeg |

Siteyi açarsın → bağlantı panelinden yerel sunucuya bağlanırsın → indirme kendi makinende gerçekleşir.

## Özellikler

- Tek video veya oynatma listesi desteği
- MP3 (320kbps) ve MP4 format seçimi
- Playlist parçalarını thumbnail ile listeleme
- Tekli indirme veya seçilenleri toplu ZIP
- Tümünü seç / seçimi temizle
- Açılır-kapanır bağlantı paneli (bağlan, kes, adres ayarı)
- Kopyalanabilir başlatma komutu
- Askeri tema, rastgele hero görselleri

## Gereksinimler

- **Python 3.10+**
- **FFmpeg**
  - Windows: `winget install ffmpeg`
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Hızlı Başlangıç

```bash
git clone https://github.com/b100guc/bedelli-mp3-indirici.git
cd bedelli-mp3-indirici/web
pip install -r requirements.txt
python -m uvicorn scripts.server:app --port 3002
```

Çıktıda `Uvicorn running on http://127.0.0.1:3002` görmelisiniz.

Tarayıcıda siteyi açın → üstteki bağlantı paneli yeşile döner → kullanıma hazır.

## Kullanım

1. **Bağlantı kontrolü** — Üstteki panel yeşil "Bağlı" göstermeli. Paneli açıp "Bağlan" butonuna basabilirsiniz.
2. **Link yapıştır** — YouTube video veya oynatma listesi URL'si girin.
3. **Bul** — Parçalar thumbnail ile listelenir.
4. **Format seç** — MP3 veya MP4.
5. **İndir** — Tek parça için satırdaki "İndir", çoklu seçim için "Seçilenleri indir" (ZIP).

## Yerel Geliştirme (UI + API)

Frontend'i de kendi bilgisayarınızda çalıştırmak isterseniz:

**Ek gereksinim:** Node.js 18+

```bash
cd web
npm install
```

İki terminal açın (ikisi de `web/` içinde):

| Terminal | Komut | Port |
|----------|-------|------|
| API | `python -m uvicorn scripts.server:app --reload --port 3002` | 3002 |
| UI | `npm run dev` | 3000 |

Tarayıcıda `http://localhost:3000` açın.

## API Ayarları

Sunucu farklı bir portta çalışıyorsa, sitedeki bağlantı panelini açıp API adresini değiştirebilirsiniz. Ayar tarayıcıda saklanır.

## Proje Yapısı

```
web/
├── app/                # Next.js arayüzü
│   ├── page.tsx        # Ana sayfa bileşeni
│   ├── page.module.css # Stiller
│   ├── globals.css     # Tema değişkenleri
│   └── layout.tsx      # Root layout
├── public/hero/        # Rastgele hero görselleri (10 adet)
├── scripts/
│   └── server.py       # Python API sunucusu (FastAPI)
├── requirements.txt    # Python bağımlılıkları
├── package.json        # Node.js bağımlılıkları
└── next.config.js      # Next.js yapılandırması (statik export)
```

## Vercel Deploy (Sadece Frontend)

1. Repoyu GitHub'a pushlayın.
2. [vercel.com](https://vercel.com) → New Project → Repo seçin.
3. **Root Directory:** `web`
4. Deploy.

Vercel sadece arayüzü sunar. İndirme işlemleri kullanıcının kendi bilgisayarındaki Python sunucusu üzerinden gerçekleşir.

## Lisans

MIT
