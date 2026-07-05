"""
VISION AI Assistant - System Control Module
Volume, brightness, and media playback controls with Windows & Linux cross-platform fallbacks.
"""
import subprocess
import sys
import re

def control_volume(action: str, level: int = None) -> str:
    """Control system volume. Uses pycaw on Windows and amixer on Linux."""
    if sys.platform != "win32":
        return _linux_control_volume(action, level)

    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))

        current = volume.GetMasterVolumeLevelScalar()
        current_pct = int(current * 100)

        if action == "up":
            new_vol = min(1.0, current + 0.1)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return f"Volume increased to {int(new_vol * 100)}%"

        elif action == "down":
            new_vol = max(0.0, current - 0.1)
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return f"Volume decreased to {int(new_vol * 100)}%"

        elif action == "mute":
            volume.SetMute(True, None)
            return "Volume muted"

        elif action == "unmute":
            volume.SetMute(False, None)
            return "Volume unmuted"

        elif action == "set" and level is not None:
            new_vol = max(0.0, min(1.0, level / 100))
            volume.SetMasterVolumeLevelScalar(new_vol, None)
            return f"Volume set to {level}%"

        else:
            return f"Current volume: {current_pct}%"

    except ImportError:
        return "Error: pycaw not installed. Run: pip install pycaw comtypes"
    except Exception as e:
        return f"Volume control error: {str(e)}"


def _linux_control_volume(action: str, level: int = None) -> str:
    try:
        if action == "up":
            subprocess.run(["amixer", "sset", "Master", "10%+"], capture_output=True, check=True)
            return "Volume increased on Linux via amixer"
        elif action == "down":
            subprocess.run(["amixer", "sset", "Master", "10%-"], capture_output=True, check=True)
            return "Volume decreased on Linux via amixer"
        elif action == "mute":
            subprocess.run(["amixer", "sset", "Master", "toggle"], capture_output=True, check=True)
            return "Volume toggled (mute) on Linux via amixer"
        elif action == "unmute":
            subprocess.run(["amixer", "sset", "Master", "unmute"], capture_output=True, check=True)
            return "Volume unmuted on Linux via amixer"
        elif action == "set" and level is not None:
            level = max(0, min(100, level))
            subprocess.run(["amixer", "sset", "Master", f"{level}%"], capture_output=True, check=True)
            return f"Volume set to {level}% on Linux via amixer"

        # default: query volume
        res = subprocess.run(["amixer", "sget", "Master"], capture_output=True, text=True)
        if res.returncode == 0:
            pcts = re.findall(r"\[(\d+)%\]", res.stdout)
            muted = "[off]" in res.stdout
            status = "muted" if muted else "active"
            if pcts:
                return f"Current volume: {pcts[0]}% ({status}) [Linux]"
        return "Failed to query volume via amixer"
    except Exception as e:
        return f"Linux volume control failed (ensure alsa-utils is installed): {e}"


def control_brightness(action: str, level: int = None) -> str:
    """Control screen brightness."""
    if sys.platform != "win32":
        res = _linux_control_brightness(action, level)
        if res:
            return res

    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness()[0]

        if action == "up":
            new_level = min(100, current + 10)
            sbc.set_brightness(new_level)
            return f"Brightness increased to {new_level}%"

        elif action == "down":
            new_level = max(0, current - 10)
            sbc.set_brightness(new_level)
            return f"Brightness decreased to {new_level}%"

        elif action == "set" and level is not None:
            sbc.set_brightness(max(0, min(100, level)))
            return f"Brightness set to {level}%"

        else:
            return f"Current brightness: {current}%"

    except ImportError:
        return "Error: screen-brightness-control not installed."
    except Exception as e:
        return f"Brightness control error: {str(e)}"


def _linux_control_brightness(action: str, level: int = None) -> str:
    # Try brightnessctl first
    try:
        if action == "up":
            subprocess.run(["brightnessctl", "set", "+10%"], capture_output=True, check=True)
            return "Brightness increased via brightnessctl"
        elif action == "down":
            subprocess.run(["brightnessctl", "set", "10%-"], capture_output=True, check=True)
            return "Brightness decreased via brightnessctl"
        elif action == "set" and level is not None:
            subprocess.run(["brightnessctl", "set", f"{level}%"], capture_output=True, check=True)
            return f"Brightness set to {level}% via brightnessctl"
    except Exception:
        pass

    # Try xbacklight next
    try:
        if action == "up":
            subprocess.run(["xbacklight", "-inc", "10"], capture_output=True, check=True)
            return "Brightness increased via xbacklight"
        elif action == "down":
            subprocess.run(["xbacklight", "-dec", "10"], capture_output=True, check=True)
            return "Brightness decreased via xbacklight"
        elif action == "set" and level is not None:
            subprocess.run(["xbacklight", "-set", str(level)], capture_output=True, check=True)
            return f"Brightness set to {level}% via xbacklight"
    except Exception:
        pass
    return None


def media_control(action: str) -> str:
    """Control media playback using keyboard simulation (Windows) or playerctl/dbus (Linux)."""
    if sys.platform != "win32":
        return _linux_media_control(action)

    try:
        import keyboard

        key_map = {
            "play_pause": "play/pause media",
            "next": "next track",
            "previous": "previous track",
            "stop": "stop media",
        }

        key = key_map.get(action)
        if key:
            keyboard.send(key)
            action_names = {
                "play_pause": "Toggled play/pause",
                "next": "Skipped to next track",
                "previous": "Went to previous track",
                "stop": "Stopped media playback",
            }
            return action_names.get(action, f"Media action: {action}")
        else:
            return f"Unknown media action: {action}"

    except ImportError:
        return "Error: keyboard not installed. Run: pip install keyboard"
    except Exception as e:
        return f"Media control error: {str(e)}"


def _linux_media_control(action: str) -> str:
    playerctl_map = {
        "play_pause": "play-pause",
        "next": "next",
        "previous": "previous",
        "stop": "stop"
    }
    act = playerctl_map.get(action)
    try:
        if act:
            res = subprocess.run(["playerctl", act], capture_output=True)
            if res.returncode == 0:
                return f"Media action '{action}' executed via playerctl"
    except Exception:
        pass

    # Fallback to DBus command
    dbus_actions = {
        "play_pause": "PlayPause",
        "next": "Next",
        "previous": "Previous",
        "stop": "Stop"
    }
    dbus_act = dbus_actions.get(action)
    try:
        if dbus_act:
            cmd = [
                "dbus-send", "--print-reply", "--dest=org.mpris.MediaPlayer2.Player",
                "/org/mpris/MediaPlayer2", f"org.mpris.MediaPlayer2.Player.{dbus_act}"
            ]
            subprocess.run(cmd, capture_output=True)
            return f"Media action '{action}' attempted via DBus"
    except Exception:
        pass

    return f"Failed to execute media control on Linux (install playerctl or run as root to simulate keys)."
