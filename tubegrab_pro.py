# pip install customtkinter yt-dlp
# TubeGrab Pro - YouTube Video/Ses İndirme Uygulaması

import customtkinter as ctk
import threading
import os
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("yt-dlp yüklü değil. Lütfen çalıştırın: pip install yt-dlp")
    exit(1)


class TubeGrabPro(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Pencere ayarları
        self.title("TubeGrab Pro")
        self.geometry("600x500")
        self.minsize(550, 450)
        
        # Tema ve renk şeması
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")
        
        # İndirme durumu için thread-safe değişkenler
        self.download_in_progress = False
        self.selected_folder = str(Path.home() / "Downloads")
        
        self._build_ui()
        
    def _build_ui(self):
        """Arayüz bileşenlerini oluşturur."""
        # Ana container - padding
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=30, pady=25)
        
        # Başlık
        title_label = ctk.CTkLabel(
            main_frame,
            text="TubeGrab Pro",
            font=ctk.CTkFont(family="Segoe UI", size=36, weight="bold"),
            text_color=("#1f6aa5", "#3b8ed0")
        )
        title_label.pack(pady=(0, 25))
        
        # Alt başlık
        subtitle_label = ctk.CTkLabel(
            main_frame,
            text="YouTube Video & Ses İndirici",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Link giriş alanı
        link_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        link_frame.pack(fill="x", pady=(0, 15))
        
        link_label = ctk.CTkLabel(
            link_frame,
            text="YouTube Linki:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        link_label.pack(anchor="w", pady=(0, 5))
        
        self.link_entry = ctk.CTkEntry(
            link_frame,
            placeholder_text="https://www.youtube.com/watch?v=... veya oynatma listesi linki",
            height=45,
            corner_radius=12,
            font=ctk.CTkFont(size=13),
            border_width=2
        )
        self.link_entry.pack(fill="x", pady=(0, 5))
        
        # Format seçimi
        format_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        format_frame.pack(fill="x", pady=(0, 15))
        
        format_label = ctk.CTkLabel(
            format_frame,
            text="Format:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        format_label.pack(anchor="w", pady=(0, 8))
        
        self.format_var = ctk.StringVar(value="mp3")
        format_options = ctk.CTkFrame(format_frame, fg_color="transparent")
        format_options.pack(fill="x")
        
        self.radio_mp3 = ctk.CTkRadioButton(
            format_options,
            text="MP3 (Ses) - 320kbps",
            variable=self.format_var,
            value="mp3",
            font=ctk.CTkFont(size=13)
        )
        self.radio_mp3.pack(side="left", padx=(0, 25))
        
        self.radio_mp4 = ctk.CTkRadioButton(
            format_options,
            text="MP4 (Video)",
            variable=self.format_var,
            value="mp4",
            font=ctk.CTkFont(size=13)
        )
        self.radio_mp4.pack(side="left")
        
        # Klasör seçimi
        folder_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        folder_frame.pack(fill="x", pady=(0, 20))
        
        folder_label = ctk.CTkLabel(
            folder_frame,
            text="Kayıt Konumu:",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        folder_label.pack(anchor="w", pady=(0, 5))
        
        folder_row = ctk.CTkFrame(folder_frame, fg_color="transparent")
        folder_row.pack(fill="x")
        
        self.folder_btn = ctk.CTkButton(
            folder_row,
            text="📁 Klasör Seç",
            width=120,
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=13),
            command=self._select_folder
        )
        self.folder_btn.pack(side="left", padx=(0, 15))
        
        self.folder_label = ctk.CTkLabel(
            folder_row,
            text=self.selected_folder,
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w"
        )
        self.folder_label.pack(side="left", fill="x", expand=True)
        
        # İndir butonu
        self.download_btn = ctk.CTkButton(
            main_frame,
            text="⬇ İndir",
            height=50,
            corner_radius=12,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color=("#1f6aa5", "#2b7fd4"),
            hover_color=("#144870", "#1a5a8a"),
            command=self._start_download
        )
        self.download_btn.pack(fill="x", pady=(10, 25))
        
        # İlerleme çubuğu
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            height=12,
            corner_radius=6,
            progress_color=("#1f6aa5", "#3b8ed0")
        )
        self.progress_bar.pack(fill="x", pady=(0, 10))
        self.progress_bar.set(0)
        
        # Durum etiketi
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Hazır",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 5))
        
    def _select_folder(self):
        """Klasör seçim dialogu açar."""
        from tkinter import filedialog
        folder = filedialog.askdirectory(
            title="İndirme Klasörü Seç",
            initialdir=self.selected_folder
        )
        if folder:
            self.selected_folder = folder
            # Uzun yolları kısalt
            display_path = folder
            if len(folder) > 50:
                display_path = "..." + folder[-47:]
            self.folder_label.configure(text=display_path)
            
    def _update_progress(self, percent: float, status: str):
        """Progress bar ve durum etiketini günceller (thread-safe)."""
        def update():
            self.progress_bar.set(percent / 100)
            self.status_label.configure(text=status)
        self.after(0, update)
        
    def _download_thread(self):
        """İndirme işlemini ayrı thread'de çalıştırır."""
        try:
            url = self.link_entry.get().strip()
            if not url:
                self.after(0, lambda: self._show_error("Lütfen bir YouTube linki girin."))
                return
                
            if "youtube.com" not in url and "youtu.be" not in url:
                self.after(0, lambda: self._show_error("Geçerli bir YouTube linki girin."))
                return
            
            format_type = self.format_var.get()
            
            # yt-dlp ayarları
            ydl_opts = {
                "outtmpl": os.path.join(self.selected_folder, "%(title)s.%(ext)s"),
                "noplaylist": False,  # Oynatma listesi desteği
                "progress_hooks": [self._progress_hook],
            }
            
            if format_type == "mp3":
                ydl_opts["format"] = "bestaudio/best"
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "320",
                }]
            else:  # mp4
                ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
                ydl_opts["merge_output_format"] = "mp4"
            
            self.after(0, lambda: self._update_progress(0, "İndiriliyor..."))
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.after(0, lambda: self._download_complete())
            
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if "Private video" in error_msg or "Video unavailable" in error_msg:
                error_msg = "Bu video gizli veya mevcut değil."
            elif "Invalid URL" in error_msg or "Unable to extract" in error_msg:
                error_msg = "Geçersiz link veya video bulunamadı."
            self.after(0, lambda: self._show_error(error_msg))
        except Exception as e:
            self.after(0, lambda: self._show_error(f"Beklenmeyen hata: {str(e)}"))
        finally:
            self.after(0, self._reset_ui)
            
    def _progress_hook(self, d):
        """yt-dlp progress hook - indirme ilerlemesini alır."""
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            if total and total > 0:
                percent = (downloaded / total) * 100
                status = f"İndiriliyor: %{percent:.1f}"
                self.after(0, lambda: self._update_progress(percent, status))
        elif d["status"] == "finished":
            self.after(0, lambda: self._update_progress(95, "Dönüştürülüyor..."))
            
    def _download_complete(self):
        """İndirme tamamlandığında çağrılır."""
        self._update_progress(100, "✓ Tamamlandı!")
        self.download_btn.configure(state="normal")
        
    def _show_error(self, message: str):
        """Hata mesajı gösterir."""
        self.status_label.configure(text=f"❌ Hata: {message}", text_color="#e74c3c")
        self.progress_bar.set(0)
        self.download_btn.configure(state="normal")
        
    def _reset_ui(self):
        """UI'ı sıfırlar."""
        self.download_in_progress = False
        self.download_btn.configure(state="normal")
        
    def _start_download(self):
        """İndirme işlemini başlatır."""
        if self.download_in_progress:
            return
            
        self.download_in_progress = True
        self.download_btn.configure(state="disabled")
        self.progress_bar.set(0)
        self.status_label.configure(text="Başlatılıyor...", text_color="gray")
        
        thread = threading.Thread(target=self._download_thread, daemon=True)
        thread.start()


def main():
    app = TubeGrabPro()
    app.mainloop()


if __name__ == "__main__":
    main()
