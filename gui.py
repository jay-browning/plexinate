import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import List
from utils import rename_files_in_directory, RenameResult
from tmdb import TMDBClient


class EpisodeRenamerGUI:
    def __init__(self, root: ctk.CTk, tmdb_api_client: TMDBClient):
        self.tree = None
        self.root = root
        self.tmdb_client = tmdb_api_client
        self.root.title("Plexinate - TV Episode Renamer")
        self.folder_var = ctk.StringVar()
        self.format_template = "{show} - S{season}E{episode} - {title}.{ext}"

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Treeview Customisation (theme colors are selected)
        bg_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
        text_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
        selected_color = root._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])

        treestyle = ttk.Style()
        treestyle.theme_use('default')
        treestyle.configure("Treeview",
                            background=bg_color,
                            foreground='black',
                            fieldbackground=bg_color,
                            borderwidth=0
                            )
        treestyle.map('Treeview',
                      background=[('selected', bg_color)],
                      foreground=[('selected', selected_color)]
                      )
        treestyle.configure("Treeview.Heading",
                            background=bg_color,
                            foreground=text_color,
                            relief='flat'
                            )
        treestyle.map("Treeview.Heading",
                      background=[('selected', bg_color)],
                      foreground=[('selected', selected_color)]
                      )
        root.bind("<<TreeviewSelect>>", lambda event: root.focus_set())

        self.setup_ui()

    def setup_ui(self):
        # Folder selection row
        folder_frame = ctk.CTkFrame(self.root)
        folder_frame.pack(padx=10, pady=(10, 5), fill="x")

        ctk.CTkLabel(folder_frame, text="Target Folder:").pack(side="left")
        ctk.CTkEntry(folder_frame, textvariable=self.folder_var, width=700).pack(side="left", padx=5, expand=True)
        ctk.CTkButton(folder_frame, text="Browse", command=self.browse_folder).pack(side="left")

        # Command buttons row
        button_frame = ctk.CTkFrame(self.root)
        button_frame.pack(pady=(5, 10))

        ctk.CTkButton(button_frame, text="Preview Rename", command=self.preview_rename).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Apply Rename", command=self.apply_rename).pack(side="left", padx=5)
        ctk.CTkButton(button_frame, text="Set Rename Template", command=self.set_template).pack(side="left", padx=5)

        # Treeview frame
        tree_frame = ctk.CTkFrame(self.root)
        tree_frame.pack(padx=10, pady=5, fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=(
            "tmdb_show", "orig_season_folder", "renamed_season_folder", "original", "newname",
        ), show="headings", selectmode="browse")

        self.tree.heading("tmdb_show", text="TMDB Show")
        self.tree.heading("orig_season_folder", text="Original Folder")
        self.tree.heading("renamed_season_folder", text="Renamed Folder")
        self.tree.heading("original", text="Original Filename")
        self.tree.heading("newname", text="Renamed Filename")

        self.tree.column("tmdb_show", anchor="w", width=150)
        self.tree.column("orig_season_folder", anchor="w", width=150)
        self.tree.column("renamed_season_folder", anchor="w", width=100)
        self.tree.column("original", anchor="w", width=300)
        self.tree.column("newname", anchor="w", width=300)

        self.tree.tag_configure("renamedrow", background="#ffdddd")  # Red
        self.tree.tag_configure("skippedrow", background="#ddffdd")  # Green
        self.tree.tag_configure("folderrow", background="#ddeeff")  # Blue

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Legend
        legend_frame = ctk.CTkFrame(self.root)
        legend_frame.pack(pady=(5, 10))
        ctk.CTkLabel(legend_frame, text="Legend:").pack(side="left", padx=(0, 5))
        ctk.CTkLabel(legend_frame, text="Renamed", fg_color="#ffdddd", text_color="black", width=80).pack(side="left",
                                                                                                          padx=5)
        ctk.CTkLabel(legend_frame, text="Skipped", fg_color="#ddffdd", text_color="black", width=80).pack(side="left",
                                                                                                          padx=5)
        ctk.CTkLabel(legend_frame, text="Folder Rename", fg_color="#ddeeff", text_color="black", width=120).pack(
            side="left", padx=5)

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

        self.root.after(0, self.update_treeview, renamed_files)

        if not renamed_files and preview_only:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No matching files found."))

    def update_treeview(self, renamed_files: List[RenameResult]):
        self.tree.delete(*self.tree.get_children())

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
