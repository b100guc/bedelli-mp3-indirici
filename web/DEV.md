# Yerel Geliştirme

İki terminal açın:

**Terminal 1 – API sunucusu:**
```bash
cd web
pip install -r requirements.txt
python -m uvicorn scripts.server:app --reload --port 3002
```

**Terminal 2 – Next.js:**
```bash
cd web
npm install
npm run dev
```

Tarayıcıda: http://localhost:3000
