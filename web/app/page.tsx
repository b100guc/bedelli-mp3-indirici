"use client";

import { useMemo, useState } from "react";
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

const HERO_IMAGES: string[] = [
  "https://www.kkk.tsk.tr/img/default/galeri/001.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/005.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/010.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/015.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/020.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/025.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/030.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/035.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/040.jpg",
  "https://www.kkk.tsk.tr/img/default/galeri/045.jpg",
];

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

  const heroImage = useMemo(
    () => HERO_IMAGES[Math.floor(Math.random() * HERO_IMAGES.length)],
    []
  );

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
      const res = await fetch(`/api/info?url=${encodeURIComponent(trimmed)}`);
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
      `/api/download?url=${encodeURIComponent(trimmed)}&format=${format}`,
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
      const res = await fetch("/api/download-batch", {
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

  return (
    <main className={styles.main}>
      <div className={styles.card}>
        <div className={styles.hero}>
          <img
            src={heroImage}
            alt="TSK fotoğraf galerisi"
            className={styles.heroImage}
            loading="lazy"
          />
        </div>
        <h1 className={styles.title}>Bedelli MP3 İndirici</h1>
        <p className={styles.subtitle}>Askeri temalı YouTube ses indirici</p>

        <label className={styles.label}>YouTube Linki</label>
        <input
          type="url"
          className={styles.input}
          placeholder="https://www.youtube.com/watch?v=... veya oynatma listesi"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={status === "loading" || status === "downloading"}
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
              disabled={status === "loading" || status === "downloading"}
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
              disabled={status === "loading" || status === "downloading"}
            />
            <span>MP4 (Video)</span>
          </label>
        </div>

        <div className={styles.buttonRow}>
          <button
            type="button"
            className={styles.buttonSecondary}
            onClick={handleFetchInfo}
            disabled={infoLoading || status === "downloading"}
          >
            {infoLoading ? "Liste alınıyor…" : "Bul"}
          </button>
          <button
            type="button"
            className={styles.button}
            onClick={handleDownloadClick}
            disabled={status === "downloading" || !items.length}
          >
            {status === "downloading" ? "İndiriliyor…" : "Seçilenleri indir"}
          </button>
        </div>

        {(status === "downloading" || status === "success") && (
          <div className={styles.progressWrap}>
            <div className={styles.progressBar}>
              <div className={styles.progressFill} style={{ width: `${progress}%` }} />
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
                <button
                  type="button"
                  className={styles.listToggle}
                  onClick={() => {
                    if (selectedIds.length === items.length) {
                      setSelectedIds([]);
                    } else {
                      setSelectedIds(items.map((i) => i.id));
                    }
                  }}
                >
                  {selectedIds.length === items.length ? "Seçimi temizle" : "Tümünü seç"}
                </button>
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
                          setSelectedIds((prev) => prev.filter((id) => id !== item.id));
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
                          e instanceof Error ? e.message : "İndirme başarısız."
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
      </div>
    </main>
  );
}
