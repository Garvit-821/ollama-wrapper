"""
VISION AI Assistant - Screenshot Module
Take screenshots and search Google Images.
"""
import os
import time
from datetime import datetime
from pathlib import Path
import config


SCREENSHOT_DIR = config.DATA_DIR / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)


def take_screenshot(search_google: bool = False) -> str:
    """Take a screenshot and optionally search Google Images."""
    try:
        import pyautogui
        from PIL import Image

        # Capture screen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = SCREENSHOT_DIR / filename

        screenshot = pyautogui.screenshot()
        screenshot.save(str(filepath))

        result = f"Screenshot saved: {filepath}"

        if search_google:
            # Open Google Lens for image search
            from modules.web_browser import open_website
            open_website("https://lens.google.com/")
            result += "\nOpened Google Lens -- upload the screenshot to search."
            result += f"\nScreenshot location: {filepath}"

        return result

    except ImportError:
        return "Error: pyautogui or Pillow not installed. Run: pip install pyautogui Pillow"
    except Exception as e:
        return f"Screenshot error: {str(e)}"


def list_screenshots() -> str:
    """List all saved screenshots."""
    screenshots = sorted(SCREENSHOT_DIR.glob("*.png"), reverse=True)
    if not screenshots:
        return "No screenshots saved yet."

    lines = ["[SCREENSHOTS] Saved screenshots:"]
    for ss in screenshots[:20]:
        size = ss.stat().st_size
        size_str = f"{size / 1024:.0f} KB"
        lines.append(f"  [IMG] {ss.name} ({size_str})")

    return "\n".join(lines)
