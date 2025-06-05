import os
import re
from typing import Optional, Tuple


def extract_info(
        filename: str,
        file_folder: str,
        root_folder: Optional[str] = None
) -> Optional[Tuple[str, str, str]]:
    # print(f"[DEBUG] filename={filename} | file_folder={file_folder} | root_folder={root_folder}")

    """
    Extract show, season, episode from filename or folder structure.

    Args:
        filename: The video file name.
        file_folder: The folder containing the file.
        root_folder: The root folder selected by the user (optional).

    Returns:
        Tuple of (show, season, episode) or None if not found.
    """
    patterns = [
        re.compile(r"(?P<show>.+?)[.\s_-]*[Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{2})"),
        re.compile(r"(?P<show>.+?)\s*-\s*\[(?P<season>\d{1,2})x(?P<episode>\d{2})]"),
        re.compile(r"(?P<show>.+?)\s*-\s*(?P<season>\d{1,2})x(?P<episode>\d{2})"),
        re.compile(r"(?P<show>.+?)[.\s_-]+(?P<season>\d{1,2})x(?P<episode>\d{2})"),
        re.compile(r"(?P<show>.+)[.\s_-]+[Ee](?P<episode>\d{2})(?!\d)"),
        re.compile(r"(?P<show>.*?)[.\s_-]*[Ee]p(?:isode)?\s*(?P<episode>\d{1,2})", re.IGNORECASE),
        re.compile(r"(?P<show>.+?)[.\s_-]*[Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{1,2})"),
        re.compile(r"[Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{2})\s*-\s*(?P<show>.+)"),
    ]

    for pattern in patterns:
        match = pattern.search(filename)
        if match:
            show = match.groupdict().get("show")
            season = match.groupdict().get("season")
            episode = match.group("episode")

            if show:
                show = show.replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
            else:
                show = os.path.basename(file_folder) or "Unknown"

            # Season fallback if missing
            if not season:
                folder_match = re.search(r"Season[\s_-]?(\d{1,2})", file_folder, re.IGNORECASE)
                season = folder_match.group(1) if folder_match else "01"

            return show, f"{int(season):02}", f"{int(episode):02}"

    # --- Fallbacks ---

    # Fallback: try sXXeXX manually
    lowered = filename.lower()
    for i in range(1, 100):
        for j in range(1, 100):
            tag = f"s{i:02}e{j:02}"
            if tag in lowered:
                idx = lowered.find(tag)
                show = filename[:idx].replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
                show = show or os.path.basename(file_folder) or "Unknown"
                return show, f"{i:02}", f"{j:02}"

    # Try to infer show name from root folder, and season from file_folder
    show = None
    season = None
    episode = None

    if root_folder:
        current_folder = os.path.abspath(file_folder)
        root_folder = os.path.abspath(root_folder)

        while current_folder != root_folder and os.path.commonpath([current_folder, root_folder]) == root_folder:
            parent = os.path.dirname(current_folder)
            if parent == root_folder:
                # Current folder is likely the show folder
                show = os.path.basename(current_folder).replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()
                break
            current_folder = parent

    # If still no show name, default to parent folder
    if not show:
        show = os.path.basename(file_folder).replace('.', ' ').replace('_', ' ').replace('-', ' ').strip()

    # Try to get season from folder name
    season_match = re.search(r"[Ss]eason[\s_-]?(\d{1,2})", os.path.basename(file_folder), re.IGNORECASE)
    if not season_match:
        # Try matching patterns like "S9E01" in filenames
        sxe_match = re.search(r"[Ss](\d{1,2})[Ee](\d{2})", filename)
        if sxe_match:
            season = sxe_match.group(1)
            episode = sxe_match.group(2)
        else:
            # Try folder name like "CSI - Season 9"
            season_match = re.search(r"\D?(\d{1,2})\s*$", os.path.basename(file_folder))

    season = f"{int(season_match.group(1)):02}" if season_match else "01"

    # Try to get episode number from filename (at end)
    ep_match = re.search(r'[^0-9](\d{1,2})(?:\.\w+)?$', filename)
    if ep_match:
        episode = f"{int(ep_match.group(1)):02}"

    if episode:
        return show, season, episode
    # print(f"[DEBUG fallback] guessed show={show} | season={season} | episode={episode}")

    return None
