import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from io import BytesIO
import re
import subprocess

try:
    import yt_dlp
    import requests
    from PIL import Image, ImageTk
except ImportError as e:
    print(f"Error: Missing library - {e}")
    print("Please install required packages: pip install yt-dlp requests pillow")
    sys.exit(1)

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video & MP3 Downloader")
        self.root.geometry("700x750")
        self.root.configure(bg="#1e1e1e")
        self.root.resizable(False, False)

        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        self.style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"), foreground="#ff4d4d")
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"), background="#333333", foreground="#ffffff")
        self.style.map("TButton", background=[("active", "#555555")])
        self.style.configure("TCombobox", fieldbackground="#333333", background="#333333", foreground="#ffffff")
        self.style.configure("TCheckbutton", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        self.style.map("TCheckbutton", background=[("active", "#1e1e1e")])
        self.style.configure("Horizontal.TProgressbar", thickness=20, troughcolor="#333333", background="#ff4d4d")
        self.style.configure('TLabelframe', background="#1e1e1e")
        self.style.configure('TLabelframe.Label', background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10, "bold"))

        self.video_info = None
        self.download_dir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        
        self.create_widgets()
        self.check_clipboard_for_url()

    def create_widgets(self):
        # Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=15, fill="x")
        ttk.Label(header_frame, text="▶ YouTube Video & MP3 Downloader", style="Header.TLabel").pack()

        # URL Input
        url_frame = ttk.Frame(self.root)
        url_frame.pack(pady=10, padx=20, fill="x")
        ttk.Label(url_frame, text="Video/Playlist URL:").pack(anchor="w")
        
        self.url_entry = tk.Entry(url_frame, font=("Segoe UI", 11), bg="#333333", fg="#ffffff", insertbackground="white", relief="flat")
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=5, padx=(0, 10))
        
        self.fetch_btn = ttk.Button(url_frame, text="Fetch Info", command=self.fetch_info_thread)
        self.fetch_btn.pack(side="right", ipady=2)

        # Video Info Display
        self.info_frame = ttk.Frame(self.root)
        self.info_frame.pack(pady=10, padx=20, fill="x")
        
        self.thumbnail_label = tk.Label(self.info_frame, bg="#1e1e1e", text="Thumbnail Preview", fg="#777777", width=45, height=12, relief="solid", bd=1)
        self.thumbnail_label.pack(pady=10)
        
        self.title_label = ttk.Label(self.info_frame, text="Title: N/A", wraplength=650, font=("Segoe UI", 11, "bold"))
        self.title_label.pack(anchor="w", pady=(0, 5))
        
        self.duration_label = ttk.Label(self.info_frame, text="Duration: N/A")
        self.duration_label.pack(anchor="w")

        # Options Frame
        options_frame = ttk.LabelFrame(self.root, text="Download Options")
        options_frame.pack(pady=10, padx=20, fill="x")

        # Quality Selection
        qual_frame = ttk.Frame(options_frame)
        qual_frame.pack(pady=10, padx=10, fill="x")
        ttk.Label(qual_frame, text="Select Quality:").pack(side="left", padx=(0, 10))
        
        self.quality_var = tk.StringVar()
        self.quality_combo = ttk.Combobox(qual_frame, textvariable=self.quality_var, state="readonly", width=30)
        self.quality_combo.pack(side="left")
        self.quality_combo.set("Awaiting video info...")

        # Extra Options (Checkboxes)
        cb_frame = ttk.Frame(options_frame)
        cb_frame.pack(pady=5, padx=10, fill="x")
        
        self.audio_only_var = tk.BooleanVar(value=False)
        self.audio_cb = ttk.Checkbutton(cb_frame, text="Audio Only (MP3)", variable=self.audio_only_var, command=self.toggle_audio_only)
        self.audio_cb.pack(side="left", padx=(0, 20))
        
        self.playlist_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(cb_frame, text="Download Playlist", variable=self.playlist_var).pack(side="left", padx=(0, 20))

        self.subtitles_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(cb_frame, text="Download Subtitles", variable=self.subtitles_var).pack(side="left")

        # Location Selection
        loc_frame = ttk.Frame(self.root)
        loc_frame.pack(pady=10, padx=20, fill="x")
        ttk.Label(loc_frame, text="Save To:").pack(anchor="w")
        
        self.loc_entry = tk.Entry(loc_frame, textvariable=self.download_dir, font=("Segoe UI", 10), bg="#333333", fg="#ffffff", state="readonly", relief="flat")
        self.loc_entry.pack(side="left", fill="x", expand=True, ipady=4, padx=(0, 10))
        
        ttk.Button(loc_frame, text="Browse", command=self.browse_location).pack(side="right")

        # Download Button
        self.download_btn = ttk.Button(self.root, text="⬇ DOWNLOAD", command=self.start_download_thread, state="disabled")
        self.download_btn.pack(pady=15, ipady=5, ipadx=20)

        # Progress and Status
        prog_frame = ttk.Frame(self.root)
        prog_frame.pack(pady=5, padx=20, fill="x")
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_var, maximum=100, mode='determinate')
        self.progress_bar.pack(fill="x", pady=5)
        
        self.status_label = ttk.Label(prog_frame, text="Ready", foreground="#aaaaaa")
        self.status_label.pack()
        
        # Open folder button (hidden initially)
        self.open_folder_btn = ttk.Button(self.root, text="📂 Open Folder", command=self.open_download_folder)

    def get_ffmpeg_path(self):
        """Determine the path to the bundled FFmpeg directory."""
        if getattr(sys, 'frozen', False):
            # Running as compiled PyInstaller executable
            base_path = sys._MEIPASS
        else:
            # Running as a standard Python script
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        ffmpeg_dir = os.path.join(base_path, 'ffmpeg')
        ffmpeg_exe = os.path.join(ffmpeg_dir, 'ffmpeg.exe')
        
        # yt-dlp expects the directory containing ffmpeg/ffprobe, or the exe itself
        if os.path.exists(ffmpeg_exe):
            return ffmpeg_dir
            
        return None  # Fallback to system PATH if not found

    def check_clipboard_for_url(self):
        """Auto-paste YouTube URL from clipboard if present."""
        try:
            clip_text = self.root.clipboard_get()
            if "youtube.com/" in clip_text or "youtu.be/" in clip_text:
                self.url_entry.insert(0, clip_text)
                self.status_label.config(text="Auto-pasted URL from clipboard.")
        except tk.TclError:
            pass # clipboard is empty or not text

    def browse_location(self):
        """Open dialog to select download directory."""
        folder = filedialog.askdirectory(initialdir=self.download_dir.get(), title="Select Download Folder")
        if folder:
            self.download_dir.set(folder)

    def open_download_folder(self):
        """Open the selected download directory in file explorer."""
        path = self.download_dir.get()
        if os.name == 'nt':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

    def toggle_audio_only(self):
        """Handle UI changes when Audio Only is toggled."""
        if self.audio_only_var.get():
            self.quality_combo.set("MP3 - High Quality (320kbps)")
            self.quality_combo.config(state="disabled")
        else:
            self.quality_combo.config(state="readonly")
            if self.video_info:
                self.populate_qualities()
            else:
                self.quality_combo.set("Awaiting video info...")

    def update_status(self, text, color="#ffffff"):
        """Update the status label safely."""
        self.status_label.config(text=text, foreground=color)
        self.root.update_idletasks()

    def fetch_info_thread(self):
        """Start thread to fetch video info without blocking UI."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Input Error", "Please enter a valid YouTube URL.")
            return
            
        self.fetch_btn.config(state="disabled")
        self.update_status("Fetching video information...", "#ffcc00")
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)
        
        threading.Thread(target=self.fetch_info, args=(url,), daemon=True).start()

    def fetch_info(self, url):
        """Use yt-dlp to extract video metadata."""
        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist' if not self.playlist_var.get() else False,
            'no_warnings': True
        }
        
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
            if 'entries' in info and not self.playlist_var.get():
                # It's a playlist but playlist download is not checked, grab first video
                info = info['entries'][0]
                
            self.video_info = info
            
            # Update UI on main thread
            self.root.after(0, self.display_video_info)
            
        except Exception as e:
            self.root.after(0, self.handle_error, f"Error fetching video info:\n{str(e)}")

    def display_video_info(self):
        """Update UI with fetched video details."""
        self.progress_bar.stop()
        self.progress_bar.config(mode="determinate")
        self.progress_var.set(0)
        self.fetch_btn.config(state="normal")
        self.update_status("Video info loaded successfully.", "#00cc44")
        
        # Set Title
        title = self.video_info.get('title', 'Unknown Title')
        self.title_label.config(text=f"Title: {title}")
        
        # Set Duration
        duration_sec = self.video_info.get('duration', 0)
        if duration_sec:
            mins, secs = divmod(duration_sec, 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                dur_str = f"{hours}:{mins:02d}:{secs:02d}"
            else:
                dur_str = f"{mins}:{secs:02d}"
            self.duration_label.config(text=f"Duration: {dur_str}")
        else:
            self.duration_label.config(text="Duration: N/A (Might be a playlist)")

        # Load Thumbnail
        thumbnail_url = self.video_info.get('thumbnail')
        if thumbnail_url:
            threading.Thread(target=self.load_thumbnail, args=(thumbnail_url,), daemon=True).start()

        # Populate Formats
        if not self.audio_only_var.get():
            self.populate_qualities()
            
        self.download_btn.config(state="normal")

    def load_thumbnail(self, url):
        """Download and display the thumbnail image."""
        try:
            response = requests.get(url, timeout=10)
            img_data = response.content
            img = Image.open(BytesIO(img_data))
            # Resize image to fit label (16:9 aspect ratio)
            img = img.resize((320, 180), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Update label on main thread
            def update_img():
                self.thumbnail_label.config(image=photo, text="", width=320, height=180, bd=0)
                self.thumbnail_label.image = photo
                
            self.root.after(0, update_img)
        except Exception as e:
            print("Failed to load thumbnail:", e)

    def populate_qualities(self):
        """Extract available resolutions and populate the combobox."""
        formats = self.video_info.get('formats', [])
        available_res = set()
        
        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height'):
                available_res.add(f.get('height'))
                
        res_list = sorted(list(available_res), reverse=True)
        options = ["Best Quality (Default)"] + [f"{res}p" for res in res_list]
        
        self.quality_combo['values'] = options
        if options:
            self.quality_combo.set(options[0])

    def start_download_thread(self):
        """Start thread to download video without blocking UI."""
        url = self.url_entry.get().strip()
        if not url:
            return
            
        self.download_btn.config(state="disabled")
        self.fetch_btn.config(state="disabled")
        self.open_folder_btn.pack_forget()
        self.progress_var.set(0)
        
        threading.Thread(target=self.download_video, args=(url,), daemon=True).start()

    def download_video(self, url):
        """Execute the download using yt-dlp with configured options."""
        out_tmpl = os.path.join(self.download_dir.get(), '%(title)s.%(ext)s')
        
        ydl_opts = {
            'outtmpl': out_tmpl,
            'progress_hooks': [self.progress_hook],
            'noplaylist': not self.playlist_var.get(),
            'quiet': True,
            'no_warnings': True
        }
        
        ffmpeg_path = self.get_ffmpeg_path()
        if ffmpeg_path:
            ydl_opts['ffmpeg_location'] = ffmpeg_path

        # Handle Subtitles
        if self.subtitles_var.get():
            ydl_opts['writesubtitles'] = True
            ydl_opts['allsubtitles'] = True

        # Handle Audio vs Video
        if self.audio_only_var.get():
            self.update_status("Starting Audio Download...", "#00cc44")
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }]
        else:
            self.update_status("Starting Video Download...", "#00cc44")
            qual = self.quality_var.get()
            if qual == "Best Quality (Default)" or not qual:
                ydl_opts['format'] = 'bestvideo+bestaudio/best'
            else:
                # Extract height number (e.g. "1080p" -> "1080")
                res = "".join(filter(str.isdigit, qual))
                ydl_opts['format'] = f'bestvideo[height<={res}]+bestaudio/best[height<={res}]'

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.root.after(0, self.download_complete)
        except Exception as e:
            self.root.after(0, self.handle_error, f"Download Error:\n{str(e)}")

    def progress_hook(self, d):
        """Callback to update progress bar and status text during download."""
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0.0%')
            # Remove ANSI color codes commonly output by yt-dlp
            p_str = re.sub(r'\x1b\[[0-9;]*m', '', p_str).strip()
            
            try:
                percent = float(p_str.replace('%', ''))
                self.root.after(0, lambda: self.progress_var.set(percent))
                
                speed = d.get('_speed_str', 'N/A')
                eta = d.get('_eta_str', 'N/A')
                speed = re.sub(r'\x1b\[[0-9;]*m', '', speed).strip()
                eta = re.sub(r'\x1b\[[0-9;]*m', '', eta).strip()
                
                status_text = f"Downloading... {p_str} | Speed: {speed} | ETA: {eta}"
                self.root.after(0, lambda: self.update_status(status_text, "#00cc44"))
            except ValueError:
                pass
                
        elif d['status'] == 'finished':
            self.root.after(0, lambda: self.update_status("Download finished! Processing/Converting... (Do not close)", "#ffcc00"))
            self.root.after(0, lambda: self.progress_var.set(100))

    def download_complete(self):
        """Reset UI after a successful download."""
        self.update_status("Download and Processing Complete!", "#00cc44")
        self.download_btn.config(state="normal")
        self.fetch_btn.config(state="normal")
        self.open_folder_btn.pack(pady=5)
        messagebox.showinfo("Success", "Download completed successfully!")

    def handle_error(self, error_msg):
        """Reset UI and show error message."""
        self.progress_bar.stop()
        self.progress_var.set(0)
        self.download_btn.config(state="normal")
        self.fetch_btn.config(state="normal")
        self.update_status("An error occurred.", "#ff4d4d")
        messagebox.showerror("Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()
