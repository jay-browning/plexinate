# 📺 Plexinate

**Plexinate** is a desktop utility that automatically renames TV episode files to Plex-compatible formats using metadata from [The Movie Database (TMDB)](https://www.themoviedb.org/). It’s designed to clean up disorganized TV show folders and ensure perfect recognition in Plex Media Server.

---

## ✨ Features

- 🔍 Searches TMDB for accurate episode titles
- 🧠 Automatically detects show, season, and episode numbers
- 📝 Customizable filename templates (e.g., `{show} - S{season}E{episode} - {title}.{ext}`)
- 🎨 GUI interface with preview and batch-rename
- 🧼 Skips files that don’t need renaming
- ✅ Compatible with Plex naming conventions

---

## 🖼 Example

Before:
```
Show.Name.S01E01.avi
Show.Name.S01E02.avi
```

After:
```
Show Name - S01E01 - Pilot.avi
Show Name - S01E02 - The Next Episode.avi
```

---

## 🚀 Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/plexinate.git
cd plexinate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python main.py
```

### 4. Enter Your TMDB API Key
- Sign up at [TMDB](https://www.themoviedb.org/) to get an API key.
- The key will be stored locally in your home directory (e.g., `~/.tmdb_api_key`).

You'll be prompted to enter your [TMDB API key](https://www.themoviedb.org/settings/api) the first time you run the app.

---

## 🔧 Customize Rename Template

Use placeholders in your rename format:

- `{show}` – Series name
- `{season}` – Season number (zero-padded)
- `{episode}` – Episode number (zero-padded)
- `{title}` – Episode title
- `{ext}` – File extension

Example:
```
{show} - S{season}E{episode} - {title}.{ext}
```

---

## 📂 Supported File Structure

The app assumes TV shows are in a folder structure like:

```
📁 TV Shows
  └── 📁 Show Name
      └── 📁 Season 1
          ├── episode1.avi
          └── episode2.avi
```

---

## 🛡 License

MIT License

---

## 💬 Feedback / Contributions

Suggestions and pull requests welcome!  
Just open an [issue](https://github.com/yourusername/plexinate/issues) or PR.

---

### 👤 Author

[redbeardarr] – [@redbeardarr]((https://github.com/jay-browning))
