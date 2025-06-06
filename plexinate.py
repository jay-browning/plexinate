# plexinate.py

import tkinter as tk
from tkinter import messagebox
from tmdb import TMDBClient, get_tmdb_api_key_gui
from utils import load_api_key, save_api_key  # Make sure this import is present
from gui import EpisodeRenamerGUI


def main():
    root = tk.Tk()
    root.withdraw()  # Hide main window while checking/loading API key

    # Try to load the API key first
    api_key = load_api_key()

    # If not found, ask the user
    if not api_key:
        api_key = get_tmdb_api_key_gui(root)
        if api_key:
            save_api_key(api_key.strip())

    # If still no API key, show error and exit
    if not api_key:
        messagebox.showerror("API Key Required", "The application cannot run without a TMDB API key.")
        return

    # Now run the app
    tmdb_client = TMDBClient(api_key.strip())
    root.deiconify()
    EpisodeRenamerGUI(root, tmdb_client)
    root.mainloop()


if __name__ == "__main__":
    main()
