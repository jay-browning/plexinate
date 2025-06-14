# tmdb.py

import requests
import customtkinter as ctk


class TMDBClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search_show(self, show_name: str) -> tuple[int | None, str | None]:
        """Search TMDB for a TV show by name, return (show_id, canonical_name) or (None, None) if not found."""
        try:
            url = "https://api.themoviedb.org/3/search/tv"
            params = {"api_key": self.api_key, "query": show_name}
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            if results:
                return results[0]["id"], results[0]["name"]
            return None, None
        except requests.RequestException as e:
            print(f"TMDB search_show error: {e}")
            return None, None

    def get_episode_title(self, show_id: int, season: int | str, episode: int | str) -> str:
        """Fetch episode title for given show ID, season, and episode number."""
        try:
            season_num = int(season)
            episode_num = int(episode)
            url = f"https://api.themoviedb.org/3/tv/{show_id}/season/{season_num}/episode/{episode_num}"
            params = {"api_key": self.api_key}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("name", "Unknown Title")
        except (requests.RequestException, ValueError) as e:
            print(f"TMDB get_episode_title error: {e}")
            return "Unknown Title"


class TMDBApiKeyDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enter TMDB API Key")
        self.geometry("400x160")
        self.api_key = None
        self.grab_set()

        self.label = ctk.CTkLabel(self, text="Please enter your TMDB API Key:")
        self.label.pack(pady=(20, 10), padx=20)

        self.entry = ctk.CTkEntry(self, width=300)
        self.entry.pack(pady=(0, 10), padx=20)
        self.entry.focus()

        self.button = ctk.CTkButton(self, text="Submit", command=self.on_submit)
        self.button.pack(pady=(0, 20))

        self.bind("<Return>", lambda event: self.on_submit())

    def on_submit(self):
        self.api_key = self.entry.get().strip()
        self.destroy()


def get_tmdb_api_key_gui(parent):
    dialog = TMDBApiKeyDialog(parent)
    parent.wait_window(dialog)
    return dialog.api_key
