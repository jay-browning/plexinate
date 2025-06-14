# plexinate.py

import customtkinter as ctk
from tkinter import messagebox
from tmdb import TMDBClient, get_tmdb_api_key_gui  # from new CTk-based dialog
from utils import load_api_key, save_api_key
from gui import EpisodeRenamerGUI


def main():
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("Plexinate")
    root.geometry("1000x600")

    api_key = load_api_key()
    if not api_key:
        api_key = get_tmdb_api_key_gui(root)
        if api_key:
            save_api_key(api_key)

    if not api_key:
        messagebox.showerror("API Key Required", "The application cannot run without a TMDB API key.")
        root.destroy()
        return

    tmdb_client = TMDBClient(api_key)
    app = EpisodeRenamerGUI(root, tmdb_client)
    root.mainloop()


if __name__ == "__main__":
    main()
