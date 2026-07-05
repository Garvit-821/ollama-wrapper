"""
VISION AI Assistant - Web Browser Module
Open websites and perform web searches in Brave browser.
"""
import os
import subprocess
import webbrowser
import config


def _get_brave_path() -> str:
    """Get Brave browser path."""
    if os.path.isfile(config.BRAVE_PATH):
        return config.BRAVE_PATH
    # Fallback paths
    fallbacks = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\Application\brave.exe"),
    ]
    for path in fallbacks:
        if os.path.isfile(path):
            return path
    return None


def open_website(url: str) -> str:
    """Open a URL in Brave browser (falls back to default browser)."""
    # Normalize URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    brave_path = _get_brave_path()

    try:
        if brave_path:
            subprocess.Popen([brave_path, url])
            return f"Opened {url} in Brave"
        else:
            webbrowser.open(url)
            return f"Opened {url} in default browser"
    except Exception as e:
        # Final fallback
        try:
            webbrowser.open(url)
            return f"Opened {url} in default browser"
        except Exception:
            return f"Error opening website: {str(e)}"


def google_search(query: str) -> str:
    """Search Google in the browser."""
    search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    return open_website(search_url)


def web_search(query: str) -> str:
    """Generic web search - opens Google search results."""
    return google_search(query)
