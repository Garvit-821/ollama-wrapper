"""
VISION AI Assistant - System Control Module
Volume, brightness, and media playback controls.
"""
import subprocess


def control_volume(action: str, level: int = None) -> str:
    """Control system volume using pycaw."""
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


def control_brightness(action: str, level: int = None) -> str:
    """Control screen brightness."""
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
        return "Error: screen-brightness-control not installed. Run: pip install screen-brightness-control"
    except Exception as e:
        return f"Brightness control error: {str(e)}"


def media_control(action: str) -> str:
    """Control media playback using keyboard simulation."""
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
