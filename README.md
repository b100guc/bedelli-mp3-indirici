# bedelli-mp3-indirici

YouTube video/playlist içeriğini **önce listeler**, sonra **tek tek** veya **seçilenleri ZIP** olarak indirir.

## Yerel Çalıştırma

İki terminal:

### 1) API (Python) – 3002

```bash
cd web
pip install -r requirements.txt
python -m uvicorn scripts.dev-api:app --reload --port 3002
```

### 2) UI (Next.js) – 3000

```bash
cd web
npm install
npm run dev
```

Tarayıcı: `http://localhost:3000`

## Akış

- **Bul**: linkteki video/playlist parçalarını listeler
- **İndir**: tek parça indirir (dosya adı parça adı)
- **Seçilenleri indir**: seçilenleri indirip **`parcalar.zip`** olarak verir
