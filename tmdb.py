# tmdb.py

import requests
import tkinter as tk
from tkinter import simpledialog


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


def get_tmdb_api_key_gui(root: tk.Tk) -> str | None:
    """Prompt user with a dialog to enter their TMDB API key."""
    return simpledialog.askstring("TMDB API Key", "Enter your TMDB API key:", parent=root)
