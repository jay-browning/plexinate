import os
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext

# TMDB API key
TMDB_API_KEY = "2826bd0dc6f5df32746aff037a85d0dc"

def fetch_episode_title(show_name, season, episode):
    try:
        search_url = "https://api.themoviedb.org/3/search/tv"
        search_params = {
            "api_key": TMDB_API_KEY,
            "query": show_name
        }
        search_response = requests.get(search_url, params=search_params).json()
        if not search_response.get("results"):
            return "Unknown Title"

        show_id = search_response["results"][0]["id"]
        episode_url = f"https://api.themoviedb.org/3/tv/{show_id}/season/{int(season)}/episode/{int(episode)}"
        episode_params = {"api_key": TMDB_API_KEY}
        episode_response = requests.get(episode_url, params=episode_params).json()
        return episode_response.get("name", "Unknown Title")
    except Exception as e:
        print(f"Error fetching episode title: {e}")
        return "Unknown Title"

def sanitize_filename(name):
    return ''.join(c for c in name if c not in r'<>:"/\|?*')

class EpisodeRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TV Episode Renamer")

        self.folder_var = tk.StringVar()
        self.format_template = "{show} - S{season}E{episode} - {title}.{ext}"

        self.setup_ui()

    def setup_ui(self):
        tk.Label(self.root, text="Target Folder:").pack(pady=(10, 0))
        tk.Entry(self.root, textvariable=self.folder_var, width=100).pack(padx=10)
        tk.Button(self.root, text="Browse", command=self.browse_folder).pack(pady=5)

        tk.Label(self.root, text="Preview:").pack()
        self.preview_box = scrolledtext.ScrolledText(self.root, width=100, height=20, wrap=tk.WORD)
        self.preview_box.pack(padx=10, pady=5)

        tk.Button(self.root, text="Preview Rename", command=self.preview_rename).pack(pady=2)
        tk.Button(self.root, text="Apply Rename", command=self.apply_rename).pack(pady=2)
        tk.Button(self.root, text="Set Rename Template", command=self.set_template).pack(pady=(2, 10))

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

    def extract_info(self, filename):
        lowered = filename.lower()
        idx = lowered.find("s01e01")
        if idx == -1:
            for i in range(1, 100):
                for j in range(1, 100):
                    tag = f"s{i:02}e{j:02}"
                    if tag in lowered:
                        idx = lowered.find(tag)
                        season = f"{i:02}"
                        episode = f"{j:02}"
                        show = filename[:idx].replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
                        return show, season, episode
            return None
        else:
            show = filename[:idx].replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
            return show, "01", "01"

    def detect_and_rename(self, folder_path, preview_only=False):
        renamed_files = []
        original_files = []

        for filename in os.listdir(folder_path):
            name, ext = os.path.splitext(filename)
            info = self.extract_info(filename)
            if not info:
                continue

            show, season, episode = info
            title = fetch_episode_title(show, season, episode)
            title = sanitize_filename(title)

            new_name = self.format_template.format(
                show=show, season=season, episode=episode, title=title, ext=ext.lstrip('.')
            )

            counter = 1
            base_new_name = new_name
            while os.path.exists(os.path.join(folder_path, new_name)):
                new_name = f"{os.path.splitext(base_new_name)[0]} ({counter}){os.path.splitext(base_new_name)[1]}"
                counter += 1

            if not preview_only:
                os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_name))

            renamed_files.append((filename, new_name))
            original_files.append((new_name, filename))

        if not preview_only:
            with open(os.path.join(folder_path, "rename_log.txt"), "w") as log_file:
                for new_name, original_name in original_files:
                    log_file.write(f"{new_name} -> {original_name}\n")

        return renamed_files

    def preview_rename(self):
        folder = self.folder_var.get()
        if not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        preview = self.detect_and_rename(folder, preview_only=True)
        self.preview_box.delete(1.0, tk.END)
        if preview:
            preview_lines = [f"{old} → {new}" for old, new in preview]
            self.preview_box.insert(tk.END, "\n".join(preview_lines))
        else:
            self.preview_box.insert(tk.END, "No matching files found.")

    def apply_rename(self):
        folder = self.folder_var.get()
        renamed = self.detect_and_rename(folder)
        if renamed:
            messagebox.showinfo("Done", f"Renamed {len(renamed)} files.")
            self.preview_box.delete(1.0, tk.END)
        else:
            messagebox.showinfo("Info", "No files matched the pattern.")


# Run the GUI app
if __name__ == "__main__":
    root = tk.Tk()
    app = EpisodeRenamerGUI(root)
    root.mainloop()
