import os
import re
import requests
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk

# TMDB API key storage (will be set on startup)
TMDB_API_KEY: str = ""


def fetch_show_data(show_name: str) -> tuple | None:
    global TMDB_API_KEY
    try:
        search_url = "https://api.themoviedb.org/3/search/tv"
        search_params = {
            "api_key": TMDB_API_KEY,
            "query": show_name
        }
        search_response = requests.get(search_url, params=search_params).json()
        if not search_response.get("results"):
            return None, None
        return search_response["results"][0]["id"], search_response["results"][0]["name"]
    except Exception as e:
        print(f"Error fetching show data: {e}")
        return None, None


def fetch_episode_title(show_id: int, season: str, episode: str) -> str:
    global TMDB_API_KEY
    try:
        episode_url = f"https://api.themoviedb.org/3/tv/{show_id}/season/{int(season)}/episode/{int(episode)}"
        episode_params = {"api_key": TMDB_API_KEY}
        episode_response = requests.get(episode_url, params=episode_params).json()
        return episode_response.get("name", "Unknown Title")
    except Exception as e:
        print(f"Error fetching episode title: {e}")
        return "Unknown Title"


def sanitize_filename(name: str) -> str:
    invalid = r'<>:"/\\|?*'
    for ch in invalid:
        if ch in ':/\\|?*':
            name = name.replace(ch, '-')
        else:
            name = name.replace(ch, '')
    return name.strip()


def extract_info(filename: str, folder_name: str = "") -> tuple | None:
    patterns = [
        re.compile(r"(?P<show>.+?)[.\s_-]*[Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{2})"),
        re.compile(r"(?P<show>.+?)\s*-\s*\[(?P<season>\d{1,2})x(?P<episode>\d{2})]"),
        re.compile(r"(?P<show>.+?)\s*-\s*(?P<season>\d{1,2})x(?P<episode>\d{2})"),
        re.compile(r"(?P<show>.+?)[.\s_-]+(?P<season>\d{1,2})x(?P<episode>\d{2})"),
        re.compile(r"(?P<show>.+)[.\s_-]+[Ee](?P<episode>\d{2})(?!\d)"),
        re.compile(r"(?P<show>.*?)[.\s_-]*[Ee]p(?:isode)?\s*(?P<episode>\d{1,2})", re.IGNORECASE),
    ]

    for pattern in patterns:
        match = pattern.search(filename)
        if match:
            show = match.groupdict().get("show") or folder_name or "Unknown"
            show = show.replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
            season = match.groupdict().get("season")
            episode = match.group("episode")

            if not season:
                # Try to detect from folder name like "Season 1"
                folder_match = re.search(r"Season[\s_-]?(\d{1,2})", folder_name, re.IGNORECASE)
                if folder_match:
                    season = folder_match.group(1)
                else:
                    season = "01"

            season = f"{int(season):02}"
            episode = f"{int(episode):02}"
            return show, season, episode

    # fallback string search
    lowered = filename.lower()
    for i in range(1, 100):
        for j in range(1, 100):
            tag = f"s{i:02}e{j:02}"
            if tag in lowered:
                idx = lowered.find(tag)
                show = filename[:idx].replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
                return show or folder_name, f"{i:02}", f"{j:02}"
    return None


class EpisodeRenamerGUI:
    def __init__(self, root: tk.Tk):
        self.tree = None
        self.root = root
        self.root.title("TV Episode Renamer")
        self.folder_var = tk.StringVar()
        self.format_template = "{show} - S{season}E{episode} - {title}.{ext}"
        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Target Folder:").pack(pady=(10, 0))
        tk.Entry(self.root, textvariable=self.folder_var, width=100).pack(padx=10)
        tk.Button(self.root, text="Browse", command=self.browse_folder).pack(pady=5)
        tk.Button(self.root, text="Preview Rename", command=self.preview_rename).pack(pady=2)
        tk.Button(self.root, text="Apply Rename", command=self.apply_rename).pack(pady=2)
        tk.Button(self.root, text="Set Rename Template", command=self.set_template).pack(pady=(2, 10))

        # Treeview frame with scrollbars
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(frame, columns=("original", "newname", "tmdb_show"), show="headings",
                                 selectmode="browse")
        self.tree.heading("original", text="Original Filename")
        self.tree.heading("newname", text="Renamed Filename")
        self.tree.heading("tmdb_show", text="TMDB Show")

        self.tree.column("original", anchor="w", width=300)
        self.tree.column("newname", anchor="w", width=300)
        self.tree.column("tmdb_show", anchor="w", width=200)

        vsb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        # Configure alternating row colors
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='#f0f0ff')

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_var.set(folder_selected)
            self.preview_rename()

    def set_template(self):
        new_template = simpledialog.askstring("Rename Template",
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

        renamed, canonical_name = self.detect_and_rename(folder, preview_only)
        # Update treeview in the main thread:
        self.root.after(0, self.update_treeview, renamed)

        if not renamed and preview_only:
            self.root.after(0, lambda: messagebox.showinfo("Info", "No matching files found."))

        if not preview_only and canonical_name:
            try:
                parent_dir = os.path.dirname(folder)
                new_root = os.path.join(parent_dir, canonical_name)
                if folder != new_root and not os.path.exists(new_root):
                    os.rename(folder, new_root)
            except Exception as e:
                print(f"Error renaming root folder: {e}")

    def update_treeview(self, renamed_files: list[tuple[str, str, str]]):
        self.tree.delete(*self.tree.get_children())
        for i, (old_name, new_name, tmdb_show) in enumerate(renamed_files):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=(old_name, new_name, tmdb_show), tags=(tag,))

    def detect_and_rename(self, folder_path: str, preview_only: bool = False) -> tuple[
        list[tuple[str, str, str]], str | None]:
        renamed_files = []
        canonical_show_name = None

        for root, dirs, files in os.walk(folder_path):
            for filename in files:
                name, ext = os.path.splitext(filename)
                season_folder = os.path.basename(root)
                info = extract_info(filename, folder_name=season_folder)
                if not info:
                    continue

                show, season, episode = info
                show_id, canonical_show = fetch_show_data(show)
                if show_id and not canonical_show_name:
                    canonical_show_name = canonical_show

                if not show_id:
                    canonical_show = show
                title = fetch_episode_title(show_id, season, episode) if show_id else "Unknown Title"

                # If unknown title, try searching TMDB with root folder show name
                if title == "Unknown Title":
                    root_folder_show = os.path.basename(folder_path).rsplit('(', 1)[0].strip()
                    fallback_id, fallback_show = fetch_show_data(root_folder_show)
                    if fallback_id:
                        title = fetch_episode_title(fallback_id, season, episode)
                        if fallback_show and not canonical_show_name:
                            canonical_show_name = fallback_show
                        canonical_show = fallback_show or canonical_show

                new_name = self.format_template.format(
                    show=canonical_show, season=season, episode=episode, title=title, ext=ext.lstrip('.')
                )
                new_name = sanitize_filename(new_name)

                counter = 1
                base_new_name = new_name
                while os.path.exists(os.path.join(root, new_name)):
                    new_name = f"{os.path.splitext(base_new_name)[0]} ({counter}){os.path.splitext(base_new_name)[1]}"
                    counter += 1

                if not preview_only:
                    try:
                        os.rename(os.path.join(root, filename), os.path.join(root, new_name))
                    except Exception as e:
                        print(f"Failed to rename {filename} to {new_name}: {e}")
                        continue

                renamed_files.append((filename, new_name, canonical_show or show))

            # rename season folders
            for dirname in dirs:
                if not re.match(r"(?i)season \d+", dirname):
                    season_match = re.search(r"\d+", dirname)
                    if season_match:
                        new_season_name = f"Season {season_match.group()}"
                        try:
                            os.rename(os.path.join(root, dirname), os.path.join(root, new_season_name))
                        except Exception as e:
                            print(f"Failed to rename folder {dirname}: {e}")

        return renamed_files, canonical_show_name


if __name__ == "__main__":
    root = tk.Tk()
    api_key = simpledialog.askstring("TMDB API Key", "Enter your TMDB API key:")
    if api_key:
        TMDB_API_KEY = api_key.strip()
        app = EpisodeRenamerGUI(root)
        root.mainloop()
    else:
        messagebox.showerror("API Key Required", "The application cannot run without a TMDB API key.")
