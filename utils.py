# utils.py

import os
from dataclasses import dataclass
from typing import List, Optional, Tuple
from extract import extract_info
from tmdb import TMDBClient

API_KEY_FILE = os.path.expanduser("~/.tmdb_api_key")


@dataclass
class RenameResult:
    original_filename: str
    renamed_filename: str
    tmdb_show_name: Optional[str]
    original_season_folder: Optional[str]
    renamed_season_folder: Optional[str]


@dataclass
class RenameFolderResult:
    original_folder: str
    renamed_folder: str


def save_api_key(key: str) -> None:
    """Save the TMDB API key to a hidden file in the user's home directory."""
    try:
        with open(API_KEY_FILE, "w") as f:
            f.write(key.strip())
    except Exception as e:
        print(f"Error saving API key: {e}")


def load_api_key() -> str:
    """Load the TMDB API key from the hidden file."""
    try:
        if os.path.exists(API_KEY_FILE):
            with open(API_KEY_FILE, "r") as f:
                return f.read().strip()
    except Exception as e:
        print(f"Error loading API key: {e}")
    return ""


def sanitize_filename(name: str) -> str:
    """Remove illegal characters from filenames and replace them with safe ones."""
    invalid = r'<>:"/\\|?*'
    for ch in invalid:
        if ch in ':/\\|?*':
            name = name.replace(ch, '-')
        else:
            name = name.replace(ch, '')
    return name.strip()


def rename_files_in_directory(
        folder_path: str,
        tmdb_client: TMDBClient,
        format_template: str,
        preview_only: bool = True,
        root_folder: str = None
) -> Tuple[List[RenameResult], List[RenameFolderResult]]:
    renamed_files = []
    renamed_folders = []
    processed_folders = set()

    for root, _, files in os.walk(folder_path):
        original_root = root  # Save the original root before any renaming

        for filename in files:
            name, ext = os.path.splitext(filename)
            original_season_folder = os.path.basename(original_root)

            info = extract_info(filename, root, root_folder=root_folder)
            if not info:
                continue

            show, season, episode = info
            show_id, canonical_show = tmdb_client.search_show(show)

            if not show_id:
                canonical_show = show
                title = "Unknown Title"
            else:
                title = tmdb_client.get_episode_title(show_id, season, episode)
                if not title:
                    title = "Unknown Title"

            # Fallback if still unknown
            if title == "Unknown Title":
                fallback_show = os.path.basename(folder_path).rsplit("(", 1)[0].strip()
                fallback_id, fallback_canonical = tmdb_client.search_show(fallback_show)
                if fallback_id:
                    title = tmdb_client.get_episode_title(fallback_id, season, episode)
                    canonical_show = fallback_canonical or canonical_show

            new_name = format_template.format(
                show=canonical_show,
                season=season,
                episode=episode,
                title=title,
                ext=ext.lstrip(".")
            )
            new_name = sanitize_filename(new_name)

            # Determine new season folder name
            season_folder_name = f"Season {int(season):02d}"
            parent_dir = os.path.dirname(root)
            new_folder_path = os.path.join(parent_dir, season_folder_name)

            # Rename season folder once per folder (only if different name)
            if original_root not in processed_folders:
                if root != new_folder_path:
                    if not preview_only:
                        try:
                            os.rename(root, new_folder_path)
                        except OSError as e:
                            print(f"Failed to rename folder {root} to {new_folder_path}: {e}")
                            continue
                    renamed_folders.append(RenameFolderResult(
                        original_folder=os.path.relpath(root, folder_path),
                        renamed_folder=os.path.relpath(new_folder_path, folder_path)
                    ))
                    processed_folders.add(root)
                    root = new_folder_path  # update root for further file renames

            # --- Skip file rename if already correctly named ---
            if filename == new_name:
                renamed_files.append(RenameResult(
                    original_filename=filename,
                    renamed_filename=new_name,
                    tmdb_show_name=canonical_show,
                    original_season_folder=original_season_folder,
                    renamed_season_folder=season_folder_name
                ))
                continue
            # ---------------------------------------------------

            # Avoid filename conflict
            counter = 1
            base_new_name = new_name
            while os.path.exists(os.path.join(root, new_name)):
                new_name = f"{os.path.splitext(base_new_name)[0]} ({counter}){ext}"
                counter += 1

            if not preview_only:
                try:
                    os.rename(os.path.join(root, filename), os.path.join(root, new_name))
                except OSError as e:
                    print(f"Failed to rename {filename} to {new_name}: {e}")
                    continue

            renamed_files.append(RenameResult(
                original_filename=filename,
                renamed_filename=new_name,
                tmdb_show_name=canonical_show,
                original_season_folder=original_season_folder,
                renamed_season_folder=season_folder_name
            ))

    return renamed_files, renamed_folders
