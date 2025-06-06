# TV Episode Renamer 🎬

A Python desktop GUI tool to automatically rename TV show episode files in a format compatible with plex media server using data from [TMDB](https://www.themoviedb.org/). Designed for organized media libraries.

---

## Features

- Batch renames episode files using TMDB metadata.
- Automatically detects show, season, and episode numbers.
- Lets you preview changes before applying them.
- Customizable filename templates (e.g., `{show} - S{season}E{episode} - {title}.{ext}`).
- Renames season folders if applicable.
- Built with `tkinter` and `CustomTkinter`.

---

## Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/tv-episode-renamer.git
cd tv-episode-renamer
```

### 2. Install Requirements
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python main.py
```

### 4. Enter Your TMDB API Key
- Sign up at [TMDB](https://www.themoviedb.org/) to get an API key.
- The key will be stored locally in your home directory (e.g., `~/.tmdb_api_key`).

---

## Rename Template

The default rename format is:
```
{show} - S{season}E{episode} - {title}.{ext}
```

You can change it in the app using the **"Set Rename Template"** button.

---

## Folder Structure

The tool works best with folders structured like this:

```
Show Name/
├── Season 1/
│   ├── Show.Name.S01E01.mkv
│   ├── Show.Name.S01E02.mkv
```

It will detect and rename files and (optionally) season folders accordingly.

---

## Dependencies

- Python 3.9+
- `requests`
- `tkinter`

---

## License

MIT License

---

## Credits

- [TMDB API](https://developers.themoviedb.org/)
- Built with 💙 using Python + Tkinter

