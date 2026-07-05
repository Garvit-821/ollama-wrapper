"""
VISION AI Assistant - Application Launcher Module
Open applications by name using a registry + smart search (Windows & Linux).
"""
import os
import sys
import subprocess
import glob
import shutil
from pathlib import Path

# ─── Windows Application Registry ───────────────────────
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

# ─── Linux Application Mapping ─────────────────────────
LINUX_APP_MAP = {
    "chrome": "google-chrome",
    "google chrome": "google-chrome",
    "firefox": "firefox",
    "brave": "brave-browser",
    "vscode": "code",
    "visual studio code": "code",
    "notepad": "gedit",
    "text editor": "gedit",
    "calculator": "gnome-calculator",
    "paint": "gimp",
    "file explorer": "nautilus",
    "explorer": "nautilus",
    "terminal": "gnome-terminal",
    "spotify": "spotify",
    "discord": "discord",
    "telegram": "telegram-desktop",
    "whatsapp": "whatsapp-for-linux",
    "vlc": "vlc",
    "steam": "steam",
}


def open_application(app_name: str) -> str:
    """Open an application by name (Windows & Linux)."""
    app_name_lower = app_name.lower().strip()

    if sys.platform != "win32":
        return _open_application_linux(app_name_lower)

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


def _open_application_linux(app_name_lower: str) -> str:
    # 1. Check in our mapping
    cmd = LINUX_APP_MAP.get(app_name_lower, app_name_lower)

    # 2. Check if the binary is in PATH
    if shutil.which(cmd):
        try:
            subprocess.Popen([cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return f"Opened {cmd} on Linux"
        except Exception as e:
            return f"Failed to launch {cmd}: {e}"

    # 3. Search .desktop entries
    desktop_search_paths = [
        "/usr/share/applications/**/*.desktop",
        os.path.expanduser("~/.local/share/applications/**/*.desktop")
    ]
    
    for pattern in desktop_search_paths:
        for df in glob.glob(pattern, recursive=True):
            filename = os.path.basename(df).lower()
            if app_name_lower in filename:
                # Try gtk-launch first
                app_id = os.path.basename(df).replace(".desktop", "")
                try:
                    subprocess.Popen(["gtk-launch", app_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opened {app_name_lower} via gtk-launch"
                except Exception:
                    pass

                # Fallback to xdg-open
                try:
                    subprocess.Popen(["xdg-open", df], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Opened {app_name_lower} via xdg-open"
                except Exception:
                    pass

    # 4. Try running it as shell command directly
    try:
        subprocess.Popen(app_name_lower, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Attempted to run '{app_name_lower}' in shell"
    except Exception as e:
        return f"Could not find or open application '{app_name_lower}' on Linux: {e}"
