"""
VISION AI Assistant - Typing Module
Type text on behalf of the user at the current cursor position.
"""
import time
import pyperclip


def type_text(text: str) -> str:
    """Type text at the current cursor position."""
    try:
        import pyautogui

        # Give user a moment to focus the target window
        time.sleep(1.5)

        # For ASCII-safe text, use typewrite (more reliable)
        # For unicode text, use clipboard paste
        try:
            text.encode('ascii')
            pyautogui.typewrite(text, interval=0.02)
        except UnicodeEncodeError:
            # Use clipboard for non-ASCII text
            _clipboard_paste(text)

        return f"Typed {len(text)} characters"

    except ImportError:
        return "Error: pyautogui not installed. Run: pip install pyautogui"
    except Exception as e:
        return f"Typing error: {str(e)}"


def _clipboard_paste(text: str):
    """Paste text from clipboard (handles unicode)."""
    import pyautogui

    try:
        # Save current clipboard
        old_clipboard = pyperclip.paste()
    except Exception:
        old_clipboard = ""

    try:
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
    finally:
        # Restore clipboard
        try:
            pyperclip.copy(old_clipboard)
        except Exception:
            pass
