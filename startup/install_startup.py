"""
VISION AI Assistant - Startup Registration (Windows & Linux)
Add/remove VISION from system startup.
"""
import os
import sys

APP_NAME = "VISION-AI"
PYTHON_PATH = sys.executable
MAIN_SCRIPT = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py"))


def install_startup() -> str:
    """Add VISION to system startup."""
    if sys.platform == "win32":
        return _install_startup_windows()
    else:
        return _install_startup_linux()


def uninstall_startup() -> str:
    """Remove VISION from system startup."""
    if sys.platform == "win32":
        return _uninstall_startup_windows()
    else:
        return _uninstall_startup_linux()


def check_startup() -> bool:
    """Check if VISION is in system startup."""
    if sys.platform == "win32":
        return _check_startup_windows()
    else:
        return _check_startup_linux()


# ─── Windows Startup Registry Helpers ───────────────────
def _install_startup_windows() -> str:
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        command = f'"{PYTHON_PATH}" "{MAIN_SCRIPT}"'
        winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        return f"[OK] VISION added to Windows startup.\nCommand: {command}"
    except Exception as e:
        return f"[ERROR] Error adding to Windows startup: {str(e)}"


def _uninstall_startup_windows() -> str:
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.DeleteValue(key, APP_NAME)
        winreg.CloseKey(key)
        return "[OK] VISION removed from Windows startup."
    except FileNotFoundError:
        return "VISION was not in startup."
    except Exception as e:
        return f"[ERROR] Error removing from Windows startup: {str(e)}"


def _check_startup_windows() -> bool:
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_READ
        )
        winreg.QueryValueEx(key, APP_NAME)
        winreg.CloseKey(key)
        return True
    except (FileNotFoundError, OSError):
        return False


# ─── Linux Startup Autostart Helpers ────────────────────
def _get_linux_autostart_path() -> str:
    autostart_dir = os.path.expanduser("~/.config/autostart")
    os.makedirs(autostart_dir, exist_ok=True)
    return os.path.join(autostart_dir, f"{APP_NAME.lower()}.desktop")


def _install_startup_linux() -> str:
    try:
        filepath = _get_linux_autostart_path()
        command = f'"{PYTHON_PATH}" "{MAIN_SCRIPT}" --no-voice' # Default to no-voice in background autostart
        content = f"""[Desktop Entry]
Type=Application
Name={APP_NAME}
Comment=VISION AI Desktop Assistant
Exec={command}
Terminal=true
X-GNOME-Autostart-enabled=true
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"[OK] VISION added to Linux Autostart (~/.config/autostart).\nEntry created at: {filepath}"
    except Exception as e:
        return f"[ERROR] Error adding to Linux autostart: {str(e)}"


def _uninstall_startup_linux() -> str:
    try:
        filepath = _get_linux_autostart_path()
        if os.path.exists(filepath):
            os.remove(filepath)
            return "[OK] VISION removed from Linux Autostart."
        return "VISION was not in Linux startup."
    except Exception as e:
        return f"[ERROR] Error removing from Linux autostart: {str(e)}"


def _check_startup_linux() -> bool:
    try:
        filepath = _get_linux_autostart_path()
        return os.path.exists(filepath)
    except Exception:
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "install":
            print(install_startup())
        elif sys.argv[1] == "uninstall":
            print(uninstall_startup())
        elif sys.argv[1] == "check":
            status = "installed" if check_startup() else "not installed"
            print(f"Startup status: {status}")
    else:
        print("Usage: python install_startup.py [install|uninstall|check]")
