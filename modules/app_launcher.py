"""
VISION AI Assistant - Application Launcher Module
Open applications by name using a registry + smart search.
"""
import os
import subprocess
import glob
from pathlib import Path

# ─── Application Registry ───────────────────────────────
# Maps common names to executable paths or commands
APP_REGISTRY = {
    # Browsers
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",

    # Microsoft Office
    "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
    "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
    "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
    "outlook": r"C:\Program Files\Microsoft Office\root\Office16\OUTLOOK.EXE",

    # Development
    "vscode": r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "visual studio code": r"C:\Users\{user}\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "terminal": "wt.exe",
    "git bash": r"C:\Program Files\Git\git-bash.exe",

    # System Utilities
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "snipping tool": "SnippingTool.exe",
    "task manager": "taskmgr.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "control panel": "control.exe",
    "settings": "ms-settings:",

    # Media
    "vlc": r"C:\Program Files\VideoLAN\VLC\vlc.exe",
    "spotify": r"C:\Users\{user}\AppData\Roaming\Spotify\Spotify.exe",

    # Communication
    "discord": r"C:\Users\{user}\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "telegram": r"C:\Users\{user}\AppData\Roaming\Telegram Desktop\Telegram.exe",
    "whatsapp": r"C:\Users\{user}\AppData\Local\WhatsApp\WhatsApp.exe",

    # Gaming
    "steam": r"C:\Program Files (x86)\Steam\steam.exe",
}


def open_application(app_name: str) -> str:
    """Open an application by name."""
    app_name_lower = app_name.lower().strip()
    username = os.getenv("USERNAME", "")

    # 1. Check the registry
    for name, path in APP_REGISTRY.items():
        if app_name_lower in name or name in app_name_lower:
            resolved_path = path.replace("{user}", username)

            # Handle special URI schemes (like ms-settings:)
            if ":" in resolved_path and not resolved_path[1] == ":":
                try:
                    os.startfile(resolved_path)
                    return f"Opened {app_name}"
                except Exception:
                    pass

            # Handle commands with arguments
            if " " in resolved_path and "--" in resolved_path:
                try:
                    subprocess.Popen(resolved_path, shell=True)
                    return f"Opened {app_name}"
                except Exception:
                    pass

            # Try direct path
            if os.path.isfile(resolved_path):
                try:
                    os.startfile(resolved_path)
                    return f"Opened {app_name}"
                except Exception:
                    pass

            # Try as command
            try:
                subprocess.Popen(resolved_path, shell=True)
                return f"Opened {app_name}"
            except Exception:
                pass

    # 2. Search Start Menu shortcuts
    start_menu_paths = [
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs"),
    ]

    for sm_path in start_menu_paths:
        if not os.path.isdir(sm_path):
            continue
        for root, dirs, files in os.walk(sm_path):
            for file in files:
                if file.endswith('.lnk') and app_name_lower in file.lower():
                    shortcut_path = os.path.join(root, file)
                    try:
                        os.startfile(shortcut_path)
                        return f"Opened {app_name} (via Start Menu)"
                    except Exception:
                        continue

    # 3. Try direct command
    try:
        subprocess.Popen(app_name_lower, shell=True)
        return f"Attempted to open {app_name}"
    except Exception:
        pass

    return f"Could not find application: {app_name}. Try providing the full path."
