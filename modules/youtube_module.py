"""
VISION AI Assistant - YouTube Module
Search YouTube, play videos, and control YT Music via Brave browser.
"""
import subprocess
import os
import json
import config
from modules.web_browser import _get_brave_path

# --- Playlist Configuration ---
PLAYLISTS_FILE = config.DATA_DIR / "playlists.json"

DEFAULT_PLAYLISTS = {
    "liked": "https://music.youtube.com/playlist?list=LM",
    "discover": "https://music.youtube.com/",
}


def _load_playlists() -> dict:
    """Load user playlists from config."""
    if PLAYLISTS_FILE.exists():
        try:
            with open(PLAYLISTS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_PLAYLISTS


def _save_playlists(playlists: dict):
    """Save playlists to config."""
    with open(PLAYLISTS_FILE, 'w') as f:
        json.dump(playlists, f, indent=2)


def search_youtube(query: str, action: str = "search") -> str:
    """Search YouTube or play a video."""
    brave_path = _get_brave_path()

    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    try:
        if brave_path:
            subprocess.Popen([brave_path, url])
        else:
            import webbrowser
            webbrowser.open(url)
        return f"Searching YouTube for: {query}"
    except Exception as e:
        return f"Error opening YouTube: {str(e)}"


def play_music(query: str = None, action: str = "play") -> str:
    """Play music on YouTube Music."""
    brave_path = _get_brave_path()

    if action == "playlist":
        # Show available playlists
        playlists = _load_playlists()
        if query:
            # Find matching playlist
            query_lower = query.lower()
            for name, url in playlists.items():
                if query_lower in name.lower():
                    try:
                        if brave_path:
                            subprocess.Popen([brave_path, url])
                        else:
                            import webbrowser
                            webbrowser.open(url)
                        return f"Playing playlist: {name}"
                    except Exception as e:
                        return f"Error opening playlist: {str(e)}"
            return f"Playlist '{query}' not found. Available: {', '.join(playlists.keys())}"
        else:
            playlist_list = "\n".join([f"  [PLAYLIST] {name}" for name in playlists.keys()])
            return f"Available playlists:\n{playlist_list}\n\nWhat would you like to hear?"

    elif action == "search" or action == "play":
        if query:
            url = f"https://music.youtube.com/search?q={query.replace(' ', '+')}"
        else:
            url = "https://music.youtube.com/"

        try:
            if brave_path:
                subprocess.Popen([brave_path, url])
            else:
                import webbrowser
                webbrowser.open(url)

            if query:
                return f"Searching YT Music for: {query}"
            else:
                return "Opened YouTube Music. What would you like to hear?"
        except Exception as e:
            return f"Error opening YT Music: {str(e)}"

    return "What would you like to listen to?"


def add_playlist(name: str, url: str) -> str:
    """Add a playlist to the saved playlists."""
    playlists = _load_playlists()
    playlists[name] = url
    _save_playlists(playlists)
    return f"Added playlist: {name}"
