# gui.py

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import List
from utils import rename_files_in_directory, RenameResult
from tmdb import TMDBClient


class EpisodeRenamerGUI:
    def __init__(self, master: tk.Tk, tmdb_api_client: TMDBClient):
        self.tree = None
        self.root = master
        self.tmdb_client = tmdb_api_client
        self.root.title("TV Episode Renamer")
        self.folder_var = tk.StringVar()
        self.format_template = "{show} - S{season}E{episode} - {title}.{ext}"
        self.setup_ui()

    def setup_ui(self):
        # Folder selection row
        folder_frame = tk.Frame(self.root)
        folder_frame.pack(padx=10, pady=(10, 5), fill=tk.X)

        tk.Label(folder_frame, text="Target Folder:").pack(side=tk.LEFT)
        tk.Entry(folder_frame, textvariable=self.folder_var, width=80).pack(side=tk.LEFT, padx=(5, 5), fill=tk.X,
                                                                            expand=True)
        tk.Button(folder_frame, text="Browse", command=self.browse_folder).pack(side=tk.LEFT)

        # Command buttons row
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=(5, 10))

        tk.Button(button_frame, text="Preview Rename", command=self.preview_rename).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Apply Rename", command=self.apply_rename).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Set Rename Template", command=self.set_template).pack(side=tk.LEFT, padx=5)

        # Treeview frame with scrollbars
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame, columns=(
            "tmdb_show", "orig_season_folder", "renamed_season_folder", "original", "newname",
        ), show="headings", selectmode="browse")

        self.tree.tag_configure("renamedrow", background="#ffdddd")  # Red
        self.tree.tag_configure("skippedrow", background="#ddffdd")  # Green
        self.tree.tag_configure("folderrow", background="#ddeeff")  # Blue

        # Add a legend
        legend_frame = tk.Frame(self.root)
        legend_frame.pack(pady=(5, 10))

        tk.Label(legend_frame, text="Legend:").pack(side="left")
        tk.Label(legend_frame, text="Renamed", bg="#ffdddd", width=10).pack(side="left", padx=5)
        tk.Label(legend_frame, text="Skipped", bg="#ddffdd", width=10).pack(side="left", padx=5)
        tk.Label(legend_frame, text="Folder Rename", bg="#ddeeff", width=15).pack(side="left", padx=5)

        self.tree.heading("tmdb_show", text="TMDB Show")
        self.tree.heading("orig_season_folder", text="Original Season Folder")
        self.tree.heading("renamed_season_folder", text="Renamed Season Folder")
        self.tree.heading("original", text="Original Filename")
        self.tree.heading("newname", text="Renamed Filename")

        self.tree.column("tmdb_show", anchor="w", width=200)
        self.tree.column("orig_season_folder", anchor="w", width=150)
        self.tree.column("renamed_season_folder", anchor="w", width=150)
        self.tree.column("original", anchor="w", width=300)
        self.tree.column("newname", anchor="w", width=300)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_var.set(folder_selected)
            self.preview_rename()

    def set_template(self):
        new_template = simpledialog.askstring(
            "Rename Template",
            "Enter rename template (e.g. {show} - S{season}E{episode} - {title}.{ext}):",
            initialvalue=self.format_template)
        if new_template:
            self.format_template = new_template
            self.preview_rename()

    def preview_rename(self):
        threading.Thread(target=self._run_rename, args=(True,), daemon=True).start()

    def apply_rename(self):
        threading.Thread(target=self._run_rename, args=(False,), daemon=True).start()

    def _run_rename(self, preview_only: bool):
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        renamed_files, renamed_folders = rename_files_in_directory(
            folder,
            self.tmdb_client,
            self.format_template,
            preview_only,
            root_folder=folder
        )

        self.root.after(0, self.update_treeview, renamed_files, renamed_folders)

        if not renamed_files and not renamed_folders and preview_only:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No matching files found."))

    def update_treeview(self, renamed_files: List[RenameResult]):
        self.tree.delete(*self.tree.get_children())

        # Insert file renames
        for result in renamed_files:
            tag = "skippedrow" if result.original_filename == result.renamed_filename else "renamedrow"
            self.tree.insert(
                "", "end",
                values=(
                    result.tmdb_show_name or "",
                    result.original_season_folder or "",
                    result.renamed_season_folder or "",
                    result.original_filename,
                    result.renamed_filename,
                ),
                tags=(tag,)
            )
