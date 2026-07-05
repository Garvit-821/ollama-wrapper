"""
VISION AI Assistant - Windows Startup Registration
Add/remove VISION from Windows startup.
"""
import os
import sys
import winreg


APP_NAME = "VISION-AI"
PYTHON_PATH = sys.executable
MAIN_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "main.py")


def install_startup() -> str:
    """Add VISION to Windows startup via Registry."""
    try:
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
        return f"[ERROR] Error adding to startup: {str(e)}"


def uninstall_startup() -> str:
    """Remove VISION from Windows startup."""
    try:
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
        return f"[ERROR] Error removing from startup: {str(e)}"


def check_startup() -> bool:
    """Check if VISION is in Windows startup."""
    try:
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


if __name__ == "__main__":
    import sys
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
