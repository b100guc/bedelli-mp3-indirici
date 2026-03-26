"use client";

import { useEffect, useMemo, useState } from "react";
import styles from "./page.module.css";

type Format = "mp3" | "mp4";
type Status = "idle" | "loading" | "downloading" | "success" | "error";

type VideoItem = {
  id: string;
  title: string;
  url: string;
  index?: number;
};

type InfoResponse = {
  type: "single" | "playlist";
  title: string;
  item_count: number;
  items: VideoItem[];
};

const DEFAULT_API = "http://localhost:3002";

export default function Home() {
  const [url, setUrl] = useState("");
  const [format, setFormat] = useState<Format>("mp3");
  const [status, setStatus] = useState<Status>("idle");
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const [items, setItems] = useState<VideoItem[]>([]);
  const [infoType, setInfoType] = useState<InfoResponse["type"] | null>(null);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [infoLoading, setInfoLoading] = useState(false);
  const [helpOpen, setHelpOpen] = useState(false);

  const [apiBase, setApiBase] = useState(DEFAULT_API);
  const [apiInput, setApiInput] = useState(DEFAULT_API);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [showApiSettings, setShowApiSettings] = useState(false);
  const [copied, setCopied] = useState(false);

  const heroImage = useMemo(
    () => `/hero/hero-${Math.floor(Math.random() * 10) + 1}.jpg`,
    []
  );

  useEffect(() => {
    try {
      const saved = localStorage.getItem("bedelliApiBase");
      if (saved) {
        setApiBase(saved);
        setApiInput(saved);
      }
    } catch {}
  }, []);

  useEffect(() => {
    let cancelled = false;
    const check = async () => {
      try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 3000);
        const res = await fetch(`${apiBase}/health`, {
          signal: controller.signal,
        });
        clearTimeout(timeout);
        if (!cancelled) setConnected(res.ok);
      } catch {
        if (!cancelled) setConnected(false);
      }
    };
    check();
    const id = setInterval(check, 10000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [apiBase]);

  useEffect(() => {
    if (!helpOpen) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setHelpOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [helpOpen]);

  const saveApiUrl = () => {
    const trimmed = apiInput.trim().replace(/\/+$/, "");
    if (trimmed) {
      setApiBase(trimmed);
      try {
        localStorage.setItem("bedelliApiBase", trimmed);
      } catch {}
    }
    setShowApiSettings(false);
  };

  const validateUrl = () => {
    const trimmed = url.trim();
    if (!trimmed) {
      setError("Lütfen bir YouTube linki girin.");
      setStatus("error");
      return null;
    }
    if (!trimmed.includes("youtube.com") && !trimmed.includes("youtu.be")) {
      setError("Geçerli bir YouTube linki girin.");
      setStatus("error");
      return null;
    }
    setError("");
    return trimmed;
  };

  const handleFetchInfo = async () => {
    const trimmed = validateUrl();
    if (!trimmed) return;

    setInfoLoading(true);
    setMessage("Liste alınıyor...");
    setStatus("idle");

    try {
      const res = await fetch(
        `${apiBase}/info?url=${encodeURIComponent(trimmed)}`
      );
      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || `Hata: ${res.status}`);
      }

      const data = (await res.json()) as InfoResponse;
      setItems(data.items);
      setInfoType(data.type);
      setSelectedIds(data.items.map((i) => i.id));
      setMessage(
        data.type === "playlist"
          ? `${data.item_count} parça bulundu.`
          : "Tek video bulundu."
      );
    } catch (e) {
      setItems([]);
      setInfoType(null);
      setSelectedIds([]);
      setStatus("error");
      setMessage("");
      setError(e instanceof Error ? e.message : "Liste alınamadı.");
    } finally {
      setInfoLoading(false);
    }
  };

  const downloadOne = async (targetUrl: string, customName?: string) => {
    const trimmed = targetUrl.trim();
    if (!trimmed) return;

    setStatus("downloading");
    setProgress(0);
    setMessage(customName ? `İndiriliyor: ${customName}` : "İndiriliyor...");

    const res = await fetch(
      `${apiBase}/download?url=${encodeURIComponent(trimmed)}&format=${format}`,
      { method: "GET" }
    );

    if (!res.ok) {
      const errText = await res.text();
      throw new Error(errText || `Hata: ${res.status}`);
    }

    const contentType = res.headers.get("content-disposition");
    const filenameMatch = contentType?.match(/filename="?([^";]+)"?/);
    const fallbackName = format === "mp3" ? "audio.mp3" : "video.mp4";
    const filename = filenameMatch ? filenameMatch[1] : fallbackName;

    const blob = await res.blob();
    const downloadUrl = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = downloadUrl;
    a.download = decodeURIComponent(filename);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(downloadUrl);
  };

  const handleDownloadClick = async () => {
    if (!items.length) {
      setStatus("error");
      setError("Önce 'Bul' butonuna basıp listeyi alın.");
      return;
    }
    if (!selectedIds.length) {
      setStatus("error");
      setError("Lütfen en az bir parça seçin.");
      return;
    }

    const selected = items.filter((i) => selectedIds.includes(i.id));
    setStatus("downloading");
    setProgress(0);
    setMessage("Parçalar indirilip ZIP hazırlanıyor...");

    try {
      const res = await fetch(`${apiBase}/download-batch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          items: selected.map((i) => ({ url: i.url, title: i.title })),
          format,
        }),
      });

      if (!res.ok) {
        const errText = await res.text();
        throw new Error(errText || `Hata: ${res.status}`);
      }

      const blob = await res.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = "parcalar.zip";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(downloadUrl);

      setStatus("success");
      setProgress(100);
      setMessage("ZIP indirildi!");
    } catch (e) {
      setStatus("error");
      setProgress(0);
      setMessage("");
      setError(e instanceof Error ? e.message : "İndirme başarısız.");
    }
  };

  const hostLabel = (() => {
    try {
      return new URL(apiBase).host;
    } catch {
      return apiBase;
    }
  })();

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <div
          className={styles.connectionBar}
          data-connected={
            connected === true
              ? "true"
              : connected === false
              ? "false"
              : "checking"
          }
        >
          <div className={styles.connectionLeft}>
            <span
              className={styles.connectionDot}
              data-connected={
                connected === true
                  ? "true"
                  : connected === false
                  ? "false"
                  : "checking"
              }
            />
            <span className={styles.connectionText}>
              {connected === null
                ? "Bağlantı kontrol ediliyor..."
                : connected
                ? `Bağlı — ${hostLabel}`
                : "Bağlantı yok — Yerel sunucuyu başlatın"}
            </span>
          </div>
          <button
            type="button"
            className={styles.connectionToggle}
            onClick={() => setShowApiSettings(!showApiSettings)}
            title="API ayarları"
          >
            ⚙
          </button>
        </div>

        {showApiSettings && (
          <div className={styles.apiSettings}>
            <label className={styles.apiSettingsLabel}>API Adresi:</label>
            <div className={styles.apiSettingsRow}>
              <input
                type="text"
                className={styles.apiSettingsInput}
                value={apiInput}
                onChange={(e) => setApiInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && saveApiUrl()}
                placeholder="http://localhost:3002"
              />
              <button
                type="button"
                className={styles.apiSettingsBtn}
                onClick={saveApiUrl}
              >
                Kaydet
              </button>
            </div>
          </div>
        )}

        {connected === false && (
          <div className={styles.cmdBox}>
            <div className={styles.cmdHeader}>
              <span className={styles.cmdLabel}>Sunucuyu başlatmak için terminale yapıştır:</span>
              <button
                type="button"
                className={styles.cmdCopy}
                onClick={() => {
                  navigator.clipboard.writeText(
                    "cd web && python -m uvicorn scripts.server:app --port 3002"
                  );
                  setCopied(true);
                  setTimeout(() => setCopied(false), 2000);
                }}
              >
                {copied ? "Kopyalandı!" : "Kopyala"}
              </button>
            </div>
            <pre className={styles.cmdPre}>
              <code>cd web &amp;&amp; python -m uvicorn scripts.server:app --port 3002</code>
            </pre>
          </div>
        )}

        <div className={styles.hero}>
          <img
            src={heroImage}
            alt="TSK fotoğraf galerisi"
            className={styles.heroImage}
          />
        </div>

        <div className={styles.headerRow}>
          <h1 className={styles.title}>Bedelli MP3 İndirici</h1>
          <button
            type="button"
            className={styles.helpButton}
            onClick={() => setHelpOpen(true)}
            aria-haspopup="dialog"
            aria-expanded={helpOpen}
          >
            Yardım
          </button>
        </div>

        <label className={styles.label}>YouTube Linki</label>
        <input
          type="url"
          className={styles.input}
          placeholder="https://www.youtube.com/watch?v=... veya oynatma listesi"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={
            !connected || status === "loading" || status === "downloading"
          }
        />

        <label className={styles.label}>Format</label>
        <div className={styles.radioGroup}>
          <label className={styles.radio}>
            <input
              type="radio"
              name="format"
              value="mp3"
              checked={format === "mp3"}
              onChange={() => setFormat("mp3")}
              disabled={
                !connected || status === "loading" || status === "downloading"
              }
            />
            <span>MP3 (Ses) – 320kbps</span>
          </label>
          <label className={styles.radio}>
            <input
              type="radio"
              name="format"
              value="mp4"
              checked={format === "mp4"}
              onChange={() => setFormat("mp4")}
              disabled={
                !connected || status === "loading" || status === "downloading"
              }
            />
            <span>MP4 (Video)</span>
          </label>
        </div>

        <div className={styles.buttonRow}>
          <button
            type="button"
            className={styles.buttonSecondary}
            onClick={handleFetchInfo}
            disabled={!connected || infoLoading || status === "downloading"}
          >
            {infoLoading ? "Liste alınıyor…" : "Bul"}
          </button>
          <button
            type="button"
            className={styles.button}
            onClick={handleDownloadClick}
            disabled={!connected || status === "downloading" || !items.length}
          >
            {status === "downloading" ? "İndiriliyor…" : "Seçilenleri indir"}
          </button>
        </div>

        {(status === "downloading" || status === "success") && (
          <div className={styles.progressWrap}>
            <div className={styles.progressBar}>
              <div
                className={styles.progressFill}
                style={{ width: `${progress}%` }}
              />
            </div>
            <p className={styles.status}>{message}</p>
          </div>
        )}

        {status === "error" && error && (
          <p className={styles.error}>Hata: {error}</p>
        )}

        {items.length > 0 && (
          <div className={styles.list}>
            <div className={styles.listHeader}>
              <span className={styles.listTitle}>
                {infoType === "playlist"
                  ? `${items.length} parçalık oynatma listesi`
                  : "Tek video"}
              </span>
              {items.length > 1 && (
                <div className={styles.listActions}>
                  <button
                    type="button"
                    className={styles.listToggle}
                    onClick={() => setSelectedIds(items.map((i) => i.id))}
                  >
                    Tümünü seç
                  </button>
                  <button
                    type="button"
                    className={styles.listToggle}
                    onClick={() => setSelectedIds([])}
                  >
                    Seçimi temizle
                  </button>
                </div>
              )}
            </div>

            <ul className={styles.listItems}>
              {items.map((item) => (
                <li key={item.id} className={styles.listItem}>
                  <label className={styles.listLabel}>
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(item.id)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedIds((prev) => [...prev, item.id]);
                        } else {
                          setSelectedIds((prev) =>
                            prev.filter((id) => id !== item.id)
                          );
                        }
                      }}
                    />
                    <span>
                      {item.index ? `${item.index}. ` : ""}
                      {item.title}
                    </span>
                  </label>
                  <button
                    type="button"
                    className={styles.listItemButton}
                    onClick={async () => {
                      try {
                        await downloadOne(item.url, item.title);
                        setStatus("success");
                        setProgress(100);
                        setMessage("İndirme tamamlandı!");
                      } catch (e) {
                        setStatus("error");
                        setProgress(0);
                        setMessage("");
                        setError(
                          e instanceof Error
                            ? e.message
                            : "İndirme başarısız."
                        );
                      }
                    }}
                  >
                    İndir
                  </button>
                </li>
              ))}
            </ul>
          </div>
        )}

        <footer className={styles.footer}>
          <div className={styles.footerEmblems}>
            <img
              className={styles.footerEmblem}
              src="https://upload.wikimedia.org/wikipedia/tr/f/f3/T%C3%BCrk_Kara_Kuvvetleri_amblemi.png"
              alt="Türk Kara Kuvvetleri arması"
              loading="lazy"
            />
            <img
              className={styles.footerEmblem}
              src="https://upload.wikimedia.org/wikipedia/tr/7/70/T%C3%BCrk_Hava_Kuvvetleri_armas%C4%B1.png?_=20130718142212"
              alt="Türk Hava Kuvvetleri arması"
              loading="lazy"
            />
            <img
              className={styles.footerEmblem}
              src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Seal_of_the_Turkish_Navy.svg/1280px-Seal_of_the_Turkish_Navy.svg.png"
              alt="Türk Deniz Kuvvetleri arması"
              loading="lazy"
            />
          </div>
          <a
            href="https://github.com/b100guc"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.footerCredit}
          >
            designed by 100GUC
          </a>
        </footer>
      </div>

      {helpOpen && (
        <div
          className={styles.helpOverlay}
          onClick={() => setHelpOpen(false)}
          role="presentation"
        >
          <aside
            className={styles.helpDrawer}
            role="dialog"
            aria-modal="true"
            aria-label="Kullanım Rehberi"
            onClick={(e) => e.stopPropagation()}
          >
            <div className={styles.helpTop}>
              <div>
                <div className={styles.helpTitle}>Kullanım Rehberi</div>
                <div className={styles.helpSubtitle}>
                  Yerel sunucu ile hızlı indirme
                </div>
              </div>
              <button
                type="button"
                className={styles.helpClose}
                onClick={() => setHelpOpen(false)}
                aria-label="Kapat"
              >
                ✕
              </button>
            </div>

            <div className={styles.helpBody}>
              <ol className={styles.helpList}>
                <li>
                  <b>Sunucuyu başlat</b>
                  <div className={styles.helpText}>
                    Bilgisayarınızda Python API sunucusunu çalıştırın:
                    <pre className={styles.helpPre}>
                      <code>cd web &amp;&amp; python -m uvicorn scripts.server:app --port 3002</code>
                    </pre>
                    Üstteki bağlantı çubuğu yeşile dönecektir.
                  </div>
                </li>
                <li>
                  <b>Linki yapıştır</b>
                  <div className={styles.helpText}>
                    Video veya oynatma listesi linkini üstteki alana gir.
                  </div>
                </li>
                <li>
                  <b>Bul</b>
                  <div className={styles.helpText}>
                    Sistem tek parça mı playlist mi anlar ve aşağıda listeyi
                    çıkarır.
                  </div>
                </li>
                <li>
                  <b>İndir</b>
                  <div className={styles.helpText}>
                    Tek parça için satırdaki <b>İndir</b>. Çoklu seçim için{" "}
                    <b>Seçilenleri indir</b> → <b>ZIP</b>.
                  </div>
                </li>
              </ol>

              <div className={styles.helpTipBox}>
                <div className={styles.helpTipTitle}>İpuçları</div>
                <ul className={styles.helpTips}>
                  <li>Formatı (MP3/MP4) indirmeden önce seç.</li>
                  <li>Playlist'te checkbox ile seçim yapabilirsin.</li>
                  <li>⚙ simgesi ile API adresini değiştirebilirsin.</li>
                  <li>Paneli kapatmak için ESC'ye basabilirsin.</li>
                </ul>
              </div>
            </div>
          </aside>
        </div>
      )}
    </main>
  );
}
