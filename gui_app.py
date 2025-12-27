"""
GUI application for PHAI Media Organizer - Modern CustomTkinter Version.
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import os
from pathlib import Path
from datetime import datetime
import tkinter.scrolledtext as scrolledtext

from media_organizer import organize_media, IMAGE_EXTENSIONS, VIDEO_EXTENSIONS
from ai_analyzer import MediaAnalyzer
from search_index import MediaSearchIndex

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # "light" or "dark"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"


class PHAIApp:
    """Main GUI application."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎬 PHAI - Personal Media AI Organizer")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.analyzer = None
        self.search_index = None
        self.index_path = "./data/index"
        self.organized_media_path = "./organized_media"
        
        # Thread control flags
        self.organize_stop_flag = threading.Event()
        self.index_stop_flag = threading.Event()
        self.add_to_index_stop_flag = threading.Event()
        
        # Progress animation flags
        self.organize_progress_animating = False
        self.index_progress_animating = False
        
        # Create UI
        self.create_widgets()
        
        # Try to load existing index
        self.load_index()
    
    def create_widgets(self):
        """Create the GUI widgets."""
        # Header
        header = ctk.CTkFrame(self.root, height=80, corner_radius=0)
        header.pack(fill="x", padx=0, pady=0)
        header.pack_propagate(False)
        
        title = ctk.CTkLabel(header, text="🎬 PHAI - Personal Media AI Organizer", 
                            font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(pady=25)
        
        # Create tabview
        self.tabview = ctk.CTkTabview(self.root, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create tabs
        self.tabview.add("📁 Organize")
        self.tabview.add("🔍 Index")
        self.tabview.add("🔎 Search")
        self.tabview.add("⚙️ About")
        
        # Create tab content
        self.create_organize_tab()
        self.create_index_tab()
        self.create_search_tab()
        self.create_settings_tab()
    
    def create_organize_tab(self):
        """Create the organize media tab."""
        tab = self.tabview.tab("📁 Organize")
        
        # Main container with scroll
        main_frame = ctk.CTkScrollableFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title = ctk.CTkLabel(main_frame, text="Organize Media Files", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))
        
        # Source folder
        source_frame = ctk.CTkFrame(main_frame)
        source_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(source_frame, text="Source Folder:", 
                    font=ctk.CTkFont(size=14, weight="bold"), width=150).pack(side="left", padx=10, pady=10)
        self.source_folder_var = ctk.StringVar(value="")
        source_entry = ctk.CTkEntry(source_frame, textvariable=self.source_folder_var, 
                                    width=400, font=ctk.CTkFont(size=12))
        source_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        ctk.CTkButton(source_frame, text="Browse...", command=self.select_source_folder, 
                     width=100).pack(side="left", padx=5, pady=10)
        
        # Destination folder
        dest_frame = ctk.CTkFrame(main_frame)
        dest_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(dest_frame, text="Destination Folder:", 
                    font=ctk.CTkFont(size=14, weight="bold"), width=150).pack(side="left", padx=10, pady=10)
        self.dest_folder_var = ctk.StringVar(value=self.organized_media_path)
        dest_entry = ctk.CTkEntry(dest_frame, textvariable=self.dest_folder_var, 
                                 width=400, font=ctk.CTkFont(size=12))
        dest_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        ctk.CTkButton(dest_frame, text="Browse...", command=self.select_dest_folder, 
                     width=100).pack(side="left", padx=5, pady=10)
        
        # Options
        self.move_files_var = ctk.BooleanVar(value=False)
        self.auto_index_var = ctk.BooleanVar(value=True)
        
        options_frame = ctk.CTkFrame(main_frame)
        options_frame.pack(fill="x", pady=10)
        
        ctk.CTkCheckBox(options_frame, text="Move files instead of copying", 
                       variable=self.move_files_var).pack(side="left", padx=20, pady=10)
        ctk.CTkCheckBox(options_frame, text="Automatically index after organizing", 
                       variable=self.auto_index_var).pack(side="left", padx=20, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=20)
        
        self.organize_btn = ctk.CTkButton(btn_frame, text="▶ Start Organizing", 
                                         command=self.organize_media,
                                         font=ctk.CTkFont(size=14, weight="bold"),
                                         height=40, fg_color="#1f77b4", hover_color="#1565a0")
        self.organize_btn.pack(side="left", padx=10)
        
        self.organize_stop_btn = ctk.CTkButton(btn_frame, text="⏹ Stop", 
                                               command=self.stop_organize,
                                               height=40, fg_color="#d32f2f", hover_color="#b71c1c",
                                               state="disabled")
        self.organize_stop_btn.pack(side="left", padx=10)
        
        # Progress
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(progress_frame, text="Progress:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.organize_progress = ctk.CTkProgressBar(progress_frame, width=500)
        self.organize_progress.pack(fill="x", padx=10, pady=5)
        self.organize_progress.set(0)
        
        # Log
        ctk.CTkLabel(main_frame, text="Activity Log:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.organize_log = scrolledtext.ScrolledText(main_frame, height=15, width=80, 
                                                      font=('Courier', 10), wrap="word",
                                                      bg="#1e1e1e", fg="#d4d4d4", 
                                                      insertbackground="#ffffff")
        self.organize_log.pack(fill="both", expand=True, pady=5)
    
    def create_index_tab(self):
        """Create the index media tab."""
        tab = self.tabview.tab("🔍 Index")
        
        main_frame = ctk.CTkScrollableFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(main_frame, text="Index Media for Search", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))
        
        # Media folder
        media_frame = ctk.CTkFrame(main_frame)
        media_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(media_frame, text="Media Folder:", 
                    font=ctk.CTkFont(size=14, weight="bold"), width=150).pack(side="left", padx=10, pady=10)
        self.index_folder_var = ctk.StringVar(value=self.organized_media_path)
        media_entry = ctk.CTkEntry(media_frame, textvariable=self.index_folder_var, 
                                   width=400, font=ctk.CTkFont(size=12))
        media_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        ctk.CTkButton(media_frame, text="Browse...", command=self.select_index_folder, 
                     width=100).pack(side="left", padx=5, pady=10)
        
        # Index path
        index_path_frame = ctk.CTkFrame(main_frame)
        index_path_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(index_path_frame, text="Index Location:", 
                    font=ctk.CTkFont(size=14, weight="bold"), width=150).pack(side="left", padx=10, pady=10)
        self.index_path_var = ctk.StringVar(value=self.index_path)
        index_entry = ctk.CTkEntry(index_path_frame, textvariable=self.index_path_var, 
                                  width=400, font=ctk.CTkFont(size=12))
        index_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        ctk.CTkButton(index_path_frame, text="Browse...", command=self.select_index_path, 
                     width=100).pack(side="left", padx=5, pady=10)
        
        # Buttons
        btn_frame = ctk.CTkFrame(main_frame)
        btn_frame.pack(fill="x", pady=20)
        
        self.index_btn = ctk.CTkButton(btn_frame, text="▶ Index All Media", 
                                      command=self.index_media,
                                      font=ctk.CTkFont(size=14, weight="bold"),
                                      height=40, fg_color="#1f77b4", hover_color="#1565a0")
        self.index_btn.pack(side="left", padx=10)
        
        self.index_stop_btn = ctk.CTkButton(btn_frame, text="⏹ Stop", 
                                            command=self.stop_index,
                                            height=40, fg_color="#d32f2f", hover_color="#b71c1c",
                                            state="disabled")
        self.index_stop_btn.pack(side="left", padx=10)
        
        self.add_to_index_btn = ctk.CTkButton(btn_frame, text="➕ Add New Files", 
                                             command=self.add_to_index,
                                             height=40)
        self.add_to_index_btn.pack(side="left", padx=10)
        
        self.add_stop_btn = ctk.CTkButton(btn_frame, text="⏹ Stop", 
                                         command=self.stop_add_to_index,
                                         height=40, fg_color="#d32f2f", hover_color="#b71c1c",
                                         state="disabled")
        self.add_stop_btn.pack(side="left", padx=10)
        
        # Progress
        progress_frame = ctk.CTkFrame(main_frame)
        progress_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(progress_frame, text="Progress:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.index_progress = ctk.CTkProgressBar(progress_frame, width=500)
        self.index_progress.pack(fill="x", padx=10, pady=5)
        self.index_progress.set(0)
        
        # Log
        ctk.CTkLabel(main_frame, text="Activity Log:", 
                    font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 5))
        self.index_log = scrolledtext.ScrolledText(main_frame, height=12, width=80, 
                                                   font=('Courier', 10), wrap="word",
                                                   bg="#1e1e1e", fg="#d4d4d4",
                                                   insertbackground="#ffffff")
        self.index_log.pack(fill="both", expand=True, pady=5)
        
        # Stats
        self.stats_label = ctk.CTkLabel(main_frame, text="", 
                                       font=ctk.CTkFont(size=12))
        self.stats_label.pack(pady=10)
    
    def create_search_tab(self):
        """Create the search tab."""
        tab = self.tabview.tab("🔎 Search")
        
        main_frame = ctk.CTkFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(main_frame, text="Search Your Media", 
                            font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(anchor="w", pady=(0, 20))
        
        # Search frame
        search_frame = ctk.CTkFrame(main_frame)
        search_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(search_frame, text="Search Query:", 
                    font=ctk.CTkFont(size=14, weight="bold"), width=120).pack(side="left", padx=10, pady=10)
        self.search_query_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_query_var, 
                                   width=400, font=ctk.CTkFont(size=14), height=40)
        search_entry.pack(side="left", fill="x", expand=True, padx=5, pady=10)
        search_entry.bind('<Return>', lambda e: self.search_media())
        
        ctk.CTkButton(search_frame, text="🔍 Search", command=self.search_media,
                     font=ctk.CTkFont(size=14, weight="bold"),
                     height=40, fg_color="#1f77b4", hover_color="#1565a0").pack(side="left", padx=5, pady=10)
        
        # Results frame
        results_frame = ctk.CTkFrame(main_frame)
        results_frame.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkLabel(results_frame, text="Search Results", 
                    font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=10, pady=10)
        
        # Results listbox with scroll
        listbox_frame = ctk.CTkFrame(results_frame)
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Use CTkScrollableFrame for results
        self.results_scroll = ctk.CTkScrollableFrame(listbox_frame, height=400)
        self.results_scroll.pack(fill="both", expand=True)
        self.results_items = []  # Store result widgets
        
        # Results info
        self.results_info = ctk.CTkLabel(main_frame, 
                                        text="💡 Enter a search query to find your media (e.g., 'videos where I'm drawing')", 
                                        font=ctk.CTkFont(size=12))
        self.results_info.pack(pady=10)
    
    def create_settings_tab(self):
        """Create the settings/about tab."""
        tab = self.tabview.tab("⚙️ About")
        
        main_frame = ctk.CTkScrollableFrame(tab)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # About card
        about_frame = ctk.CTkFrame(main_frame)
        about_frame.pack(fill="both", expand=True, pady=10)
        
        title = ctk.CTkLabel(about_frame, text="🎬 PHAI - Personal Media AI Organizer", 
                           font=ctk.CTkFont(size=20, weight="bold"))
        title.pack(pady=20)
        
        about_text = """Version: 1.0.0

Features:
• 📅 Organize media into date-based folders (YYYYMMDD)
• 🤖 AI-powered categorization using CLIP
• 🔍 Semantic search using natural language
• 🖥️ Modern GUI interface with dark mode
• ⏹️ Stop operations anytime
• 🔄 Automatic indexing after organizing

How to Use:
1. Go to "Organize" tab
2. Select your source folder and destination folder
3. Click "Start Organizing" - it will organize AND index automatically
4. Go to "Search" tab to find your media using natural language

For help, see the README.md file."""
        
        about_label = ctk.CTkLabel(about_frame, text=about_text.strip(), 
                                  font=ctk.CTkFont(size=12), justify="left")
        about_label.pack(padx=20, pady=20, anchor="w")
    
    # Folder selection methods
    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Select Source Folder")
        if folder:
            self.source_folder_var.set(folder)
    
    def select_dest_folder(self):
        folder = filedialog.askdirectory(title="Select Destination Folder")
        if folder:
            self.dest_folder_var.set(folder)
    
    def select_index_folder(self):
        folder = filedialog.askdirectory(title="Select Media Folder to Index")
        if folder:
            self.index_folder_var.set(folder)
    
    def select_index_path(self):
        folder = filedialog.askdirectory(title="Select Index Location")
        if folder:
            self.index_path_var.set(folder)
    
    # Stop methods
    def stop_organize(self):
        """Stop organizing operation."""
        self.organize_stop_flag.set()
        self.organize_log.insert("end", "\n⚠ Operation stopped by user.\n")
        self.organize_log.see("end")
    
    def stop_index(self):
        """Stop indexing operation."""
        self.index_stop_flag.set()
        self.index_log.insert("end", "\n⚠ Operation stopped by user.\n")
        self.index_log.see("end")
    
    def stop_add_to_index(self):
        """Stop add to index operation."""
        self.add_to_index_stop_flag.set()
        self.index_log.insert("end", "\n⚠ Operation stopped by user.\n")
        self.index_log.see("end")
    
    # Action methods
    def organize_media(self):
        """Organize media files."""
        source = self.source_folder_var.get()
        dest = self.dest_folder_var.get()
        
        if not source or not os.path.exists(source):
            messagebox.showerror("Error", "Please select a valid source folder")
            return
        
        if not dest:
            messagebox.showerror("Error", "Please select a destination folder")
            return
        
        # Reset stop flag
        self.organize_stop_flag.clear()
        
        self.organize_btn.configure(state="disabled")
        self.organize_stop_btn.configure(state="normal")
        self.organize_progress.set(0)
        self.start_progress_animation("organize")
        self.organize_log.delete(1.0, "end")
        self.organize_log.insert("end", f"🚀 Starting organization...\n")
        self.organize_log.insert("end", f"📂 Source: {source}\n")
        self.organize_log.insert("end", f"📁 Destination: {dest}\n\n")
        
        def organize_thread():
            try:
                organized = organize_media(
                    source_dir=source,
                    dest_dir=dest,
                    copy_files=not self.move_files_var.get()
                )
                
                if not self.organize_stop_flag.is_set():
                    self.root.after(0, lambda: self.organize_log.insert(
                        "end", f"\n✅ Successfully organized {len(organized)} files!\n"
                    ))
                    
                    # Auto-index if enabled
                    if self.auto_index_var.get() and len(organized) > 0:
                        self.root.after(0, lambda: self.organize_log.insert(
                            "end", f"\n🔍 Starting automatic indexing...\n"
                        ))
                        self.root.after(0, lambda: self.auto_index_after_organize(dest))
            except Exception as e:
                if not self.organize_stop_flag.is_set():
                    self.root.after(0, lambda: self.organize_log.insert(
                        "end", f"\n❌ Error: {str(e)}\n"
                    ))
            finally:
                if not self.auto_index_var.get() or self.organize_stop_flag.is_set():
                    self.root.after(0, lambda: (
                        self.stop_progress_animation("organize"),
                        self.organize_btn.configure(state="normal"),
                        self.organize_stop_btn.configure(state="disabled")
                    ))
        
        threading.Thread(target=organize_thread, daemon=True).start()
    
    def auto_index_after_organize(self, media_dir):
        """Automatically index files after organizing."""
        index_path = self.index_path_var.get()
        self.index_folder_var.set(media_dir)
        self.index_stop_flag.clear()
        
        self.organize_log.insert("end", f"📂 Indexing folder: {media_dir}\n")
        self.organize_log.see("end")
        
        def auto_index_thread():
            try:
                if self.analyzer is None:
                    self.root.after(0, lambda: self.organize_log.insert(
                        "end", "⏳ Loading AI models (this may take a moment)...\n"
                    ))
                    self.analyzer = MediaAnalyzer()
                
                if self.index_stop_flag.is_set():
                    return
                
                self.search_index = MediaSearchIndex(index_path=index_path)
                media_path = Path(media_dir)
                all_extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
                
                media_files = []
                for ext in all_extensions:
                    media_files.extend(media_path.rglob(f'*{ext}'))
                    media_files.extend(media_path.rglob(f'*{ext.upper()}'))
                
                self.root.after(0, lambda: self.organize_log.insert(
                    "end", f"📊 Found {len(media_files)} media files to index...\n\n"
                ))
                
                indexed = 0
                skipped = 0
                
                for i, media_file in enumerate(media_files):
                    if self.index_stop_flag.is_set():
                        self.root.after(0, lambda: self.organize_log.insert(
                            "end", f"\n⚠ Indexing stopped at file {i+1}/{len(media_files)}\n"
                        ))
                        break
                    
                    try:
                        file_path = str(media_file)
                        file_ext = media_file.suffix.lower()
                        
                        if file_ext in IMAGE_EXTENSIONS:
                            embedding = self.analyzer.extract_image_embedding(file_path)
                            file_type = "image"
                        elif file_ext in VIDEO_EXTENSIONS:
                            embedding = self.analyzer.extract_video_embedding(file_path)
                            file_type = "video"
                        else:
                            continue
                        
                        self.search_index.add_media(file_path, embedding, file_type)
                        indexed += 1
                        
                        if (i + 1) % 10 == 0:
                            self.root.after(0, lambda idx=indexed, total=len(media_files): 
                                          self.organize_log.insert("end", 
                                          f"📈 Indexing progress: {idx}/{total} files...\n"))
                            self.root.after(0, lambda: self.organize_log.see("end"))
                    except Exception as e:
                        skipped += 1
                
                if not self.index_stop_flag.is_set():
                    self.search_index.save()
                    stats = self.search_index.get_stats()
                    
                    self.root.after(0, lambda: (
                        self.organize_log.insert("end", f"\n✅ Indexing complete!\n"),
                        self.organize_log.insert("end", f"✅ Indexed: {indexed} files\n"),
                        self.organize_log.insert("end", f"⚠ Skipped: {skipped} files\n"),
                        self.organize_log.insert("end", f"📊 Total in index: {stats['total_entries']} files (📷 {stats['images']}, 🎬 {stats['videos']})\n"),
                        self.organize_log.see("end")
                    ))
                    
                    if hasattr(self, 'stats_label'):
                        stats_text = f"📊 Total: {stats['total_entries']} | 📷 Images: {stats['images']} | 🎬 Videos: {stats['videos']}"
                        self.stats_label.configure(text=stats_text)
            except Exception as e:
                if not self.index_stop_flag.is_set():
                    self.root.after(0, lambda: self.organize_log.insert(
                        "end", f"\n❌ Indexing error: {str(e)}\n"
                    ))
            finally:
                self.root.after(0, lambda: (
                    self.stop_progress_animation("organize"),
                    self.organize_btn.configure(state="normal"),
                    self.organize_stop_btn.configure(state="disabled")
                ))
        
        threading.Thread(target=auto_index_thread, daemon=True).start()
    
    def index_media(self):
        """Index media files."""
        media_dir = self.index_folder_var.get()
        index_path = self.index_path_var.get()
        
        if not media_dir or not os.path.exists(media_dir):
            messagebox.showerror("Error", "Please select a valid media folder")
            return
        
        self.index_stop_flag.clear()
        self.index_btn.configure(state="disabled")
        self.add_to_index_btn.configure(state="disabled")
        self.index_stop_btn.configure(state="normal")
        self.index_progress.set(0)
        self.start_progress_animation("index")
        self.index_log.delete(1.0, "end")
        self.index_log.insert("end", f"🤖 Initializing AI models...\n")
        
        def index_thread():
            try:
                if self.analyzer is None:
                    self.root.after(0, lambda: self.index_log.insert(
                        "end", "⏳ Loading AI models (this may take a moment)...\n"
                    ))
                    self.analyzer = MediaAnalyzer()
                
                if self.index_stop_flag.is_set():
                    return
                
                self.search_index = MediaSearchIndex(index_path=index_path)
                media_path = Path(media_dir)
                all_extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
                
                media_files = []
                for ext in all_extensions:
                    media_files.extend(media_path.rglob(f'*{ext}'))
                    media_files.extend(media_path.rglob(f'*{ext.upper()}'))
                
                self.root.after(0, lambda: self.index_log.insert(
                    "end", f"📊 Found {len(media_files)} media files to index...\n\n"
                ))
                
                indexed = 0
                skipped = 0
                
                for i, media_file in enumerate(media_files):
                    if self.index_stop_flag.is_set():
                        self.root.after(0, lambda: self.index_log.insert(
                            "end", f"\n⚠ Stopped at file {i+1}/{len(media_files)}\n"
                        ))
                        break
                    
                    try:
                        file_path = str(media_file)
                        file_ext = media_file.suffix.lower()
                        
                        if file_ext in IMAGE_EXTENSIONS:
                            embedding = self.analyzer.extract_image_embedding(file_path)
                            file_type = "image"
                        elif file_ext in VIDEO_EXTENSIONS:
                            embedding = self.analyzer.extract_video_embedding(file_path)
                            file_type = "video"
                        else:
                            continue
                        
                        self.search_index.add_media(file_path, embedding, file_type)
                        indexed += 1
                        
                        if (i + 1) % 10 == 0:
                            self.root.after(0, lambda idx=indexed, total=len(media_files): 
                                          self.index_log.insert("end", 
                                          f"📈 Progress: {idx}/{total} files indexed...\n"))
                    except Exception as e:
                        skipped += 1
                
                if not self.index_stop_flag.is_set():
                    self.search_index.save()
                    stats = self.search_index.get_stats()
                    stats_text = f"📊 Total: {stats['total_entries']} | 📷 Images: {stats['images']} | 🎬 Videos: {stats['videos']}"
                    
                    self.root.after(0, lambda: (
                        self.index_log.insert("end", f"\n✅ Indexing complete!\n"),
                        self.index_log.insert("end", f"✅ Indexed: {indexed} files\n"),
                        self.index_log.insert("end", f"⚠ Skipped: {skipped} files\n"),
                        self.stats_label.configure(text=stats_text)
                    ))
            except Exception as e:
                if not self.index_stop_flag.is_set():
                    self.root.after(0, lambda: self.index_log.insert(
                        "end", f"\n❌ Error: {str(e)}\n"
                    ))
            finally:
                self.root.after(0, lambda: (
                    self.stop_progress_animation("index"),
                    self.index_btn.configure(state="normal"),
                    self.add_to_index_btn.configure(state="normal"),
                    self.index_stop_btn.configure(state="disabled")
                ))
        
        threading.Thread(target=index_thread, daemon=True).start()
    
    def add_to_index(self):
        """Add new files to existing index."""
        media_dir = self.index_folder_var.get()
        index_path = self.index_path_var.get()
        
        if not media_dir or not os.path.exists(media_dir):
            messagebox.showerror("Error", "Please select a valid media folder")
            return
        
        if not os.path.exists(os.path.join(index_path, "metadata.json")):
            messagebox.showwarning("Warning", "No existing index found. Please create an index first.")
            return
        
        self.add_to_index_stop_flag.clear()
        self.add_to_index_btn.configure(state="disabled")
        self.index_btn.configure(state="disabled")
        self.add_stop_btn.configure(state="normal")
        self.index_progress.set(0)
        self.start_progress_animation("index")
        self.index_log.delete(1.0, "end")
        self.index_log.insert("end", f"📂 Loading existing index...\n")
        
        def add_thread():
            try:
                if self.analyzer is None:
                    self.root.after(0, lambda: self.index_log.insert(
                        "end", "⏳ Loading AI models (this may take a moment)...\n"
                    ))
                    self.analyzer = MediaAnalyzer()
                
                if self.add_to_index_stop_flag.is_set():
                    return
                
                self.search_index = MediaSearchIndex(index_path=index_path)
                existing_paths = {m['file_path'] for m in self.search_index.metadata}
                
                media_path = Path(media_dir)
                all_extensions = IMAGE_EXTENSIONS | VIDEO_EXTENSIONS
                
                media_files = []
                for ext in all_extensions:
                    media_files.extend(media_path.rglob(f'*{ext}'))
                    media_files.extend(media_path.rglob(f'*{ext.upper()}'))
                
                new_files = [f for f in media_files if str(f) not in existing_paths]
                
                self.root.after(0, lambda: self.index_log.insert(
                    "end", f"📊 Found {len(new_files)} new files to index (out of {len(media_files)} total)...\n\n"
                ))
                
                if not new_files:
                    self.root.after(0, lambda: (
                        self.index_log.insert("end", "ℹ️ No new files to index!\n"),
                        self.stop_progress_animation("index"),
                        self.add_to_index_btn.configure(state="normal"),
                        self.index_btn.configure(state="normal"),
                        self.add_stop_btn.configure(state="disabled")
                    ))
                    return
                
                indexed = 0
                skipped = 0
                
                for i, media_file in enumerate(new_files):
                    if self.add_to_index_stop_flag.is_set():
                        self.root.after(0, lambda: self.index_log.insert(
                            "end", f"\n⚠ Stopped at file {i+1}/{len(new_files)}\n"
                        ))
                        break
                    
                    try:
                        file_path = str(media_file)
                        file_ext = media_file.suffix.lower()
                        
                        if file_ext in IMAGE_EXTENSIONS:
                            embedding = self.analyzer.extract_image_embedding(file_path)
                            file_type = "image"
                        elif file_ext in VIDEO_EXTENSIONS:
                            embedding = self.analyzer.extract_video_embedding(file_path)
                            file_type = "video"
                        else:
                            continue
                        
                        self.search_index.add_media(file_path, embedding, file_type)
                        indexed += 1
                        
                        if (i + 1) % 10 == 0:
                            self.root.after(0, lambda idx=indexed, total=len(new_files): 
                                          self.index_log.insert("end", 
                                          f"📈 Progress: {idx}/{total} new files indexed...\n"))
                    except Exception as e:
                        skipped += 1
                
                if not self.add_to_index_stop_flag.is_set():
                    self.search_index.save()
                    stats = self.search_index.get_stats()
                    stats_text = f"📊 Total: {stats['total_entries']} | 📷 Images: {stats['images']} | 🎬 Videos: {stats['videos']}"
                    
                    self.root.after(0, lambda: (
                        self.index_log.insert("end", f"\n✅ Added {indexed} new files to index!\n"),
                        self.index_log.insert("end", f"⚠ Skipped: {skipped} files\n"),
                        self.stats_label.configure(text=stats_text)
                    ))
            except Exception as e:
                if not self.add_to_index_stop_flag.is_set():
                    self.root.after(0, lambda: self.index_log.insert(
                        "end", f"\n❌ Error: {str(e)}\n"
                    ))
            finally:
                self.root.after(0, lambda: (
                    self.stop_progress_animation("index"),
                    self.add_to_index_btn.configure(state="normal"),
                    self.index_btn.configure(state="normal"),
                    self.add_stop_btn.configure(state="disabled")
                ))
        
        threading.Thread(target=add_thread, daemon=True).start()
    
    def search_media(self):
        """Search for media."""
        query = self.search_query_var.get().strip()
        
        if not query:
            messagebox.showwarning("Warning", "Please enter a search query")
            return
        
        if self.analyzer is None:
            messagebox.showinfo("Info", "Loading AI models... This may take a moment.")
            self.analyzer = MediaAnalyzer()
        
        if self.search_index is None:
            self.load_index()
        
        if self.search_index is None or self.search_index.faiss_index.ntotal == 0:
            messagebox.showwarning("Warning", "No index found. Please index your media first.")
            return
        
        # Clear previous results
        for widget in self.results_items:
            widget.destroy()
        self.results_items = []
        self.results_info.configure(text="🔍 Searching...")
        
        def search_thread():
            try:
                query_embedding = self.analyzer.encode_text_query(query)
                results = self.search_index.search(query_embedding, k=20)
                self.root.after(0, lambda: self.display_results(results, query))
            except Exception as e:
                self.root.after(0, lambda: (
                    self.results_info.configure(text=f"❌ Error: {str(e)}"),
                    messagebox.showerror("Error", f"Search failed: {str(e)}")
                ))
        
        threading.Thread(target=search_thread, daemon=True).start()
    
    def display_results(self, results, query):
        """Display search results."""
        for widget in self.results_items:
            widget.destroy()
        self.results_items = []
        self._last_results = results
        
        if not results:
            self.results_info.configure(text="❌ No results found")
            return
        
        for result in results:
            file_path = result['file_path']
            file_type = result['file_type']
            similarity = result['similarity']
            
            type_emoji = "📷" if file_type == "image" else "🎬"
            display_text = f"{type_emoji} [{file_type.upper()}] {os.path.basename(file_path)} ({similarity*100:.1f}% match)"
            
            result_frame = ctk.CTkFrame(self.results_scroll)
            result_frame.pack(fill="x", padx=5, pady=5)
            
            label = ctk.CTkLabel(result_frame, text=display_text, 
                                font=ctk.CTkFont(size=12), anchor="w", justify="left")
            label.pack(side="left", padx=10, pady=10, fill="x", expand=True)
            
            open_btn = ctk.CTkButton(result_frame, text="Open", command=lambda p=file_path: self.open_file(p),
                                    width=80)
            open_btn.pack(side="right", padx=10, pady=10)
            
            self.results_items.append(result_frame)
            if not hasattr(self, '_result_paths'):
                self._result_paths = {}
            self._result_paths[len(self.results_items) - 1] = file_path
        
        self.results_info.configure(text=f"✅ Found {len(results)} results for '{query}'")
    
    def open_file(self, file_path):
        """Open file in default application."""
        if os.path.exists(file_path):
            import subprocess
            import platform
            try:
                if platform.system() == 'Darwin':
                    subprocess.run(['open', file_path])
                elif platform.system() == 'Windows':
                    os.startfile(file_path)
                else:
                    subprocess.run(['xdg-open', file_path])
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def start_progress_animation(self, progress_type):
        """Start animated progress bar."""
        if progress_type == "organize":
            self.organize_progress_animating = True
            self._animate_progress("organize", 0)
        elif progress_type == "index":
            self.index_progress_animating = True
            self._animate_progress("index", 0)
    
    def stop_progress_animation(self, progress_type):
        """Stop animated progress bar."""
        if progress_type == "organize":
            self.organize_progress_animating = False
            self.organize_progress.set(1.0)
        elif progress_type == "index":
            self.index_progress_animating = False
            self.index_progress.set(1.0)
    
    def _animate_progress(self, progress_type, value):
        """Animate progress bar."""
        if progress_type == "organize" and self.organize_progress_animating:
            value = (value + 0.02) % 1.0
            self.organize_progress.set(value)
            self.root.after(50, lambda: self._animate_progress("organize", value))
        elif progress_type == "index" and self.index_progress_animating:
            value = (value + 0.02) % 1.0
            self.index_progress.set(value)
            self.root.after(50, lambda: self._animate_progress("index", value))
    
    def load_index(self):
        """Load existing index."""
        try:
            index_path = self.index_path_var.get() if hasattr(self, 'index_path_var') else self.index_path
            self.search_index = MediaSearchIndex(index_path=index_path)
            
            if self.search_index.faiss_index.ntotal > 0:
                stats = self.search_index.get_stats()
                if hasattr(self, 'stats_label'):
                    stats_text = f"📊 Index loaded: {stats['total_entries']} files (📷 {stats['images']}, 🎬 {stats['videos']})"
                    self.stats_label.configure(text=stats_text)
        except Exception:
            pass


def main():
    """Run the GUI application."""
    root = ctk.CTk()
    app = PHAIApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
