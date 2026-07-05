"""
VISION AI Assistant - Animated ASCII Face
Compact robot face derived from ui/ascii-art.txt with animated states.
"""
import random
import time
import os
from pathlib import Path


# ─── Load base art from file ───────────────────────────────
_ART_FILE = Path(__file__).parent / "ascii-art.txt"


def _load_art_lines() -> list:
    """Load the raw ASCII art and return as list of strings."""
    try:
        with open(_ART_FILE, "r", encoding="utf-8") as f:
            return [line.rstrip() for line in f.readlines()]
    except Exception:
        return []


def _load_full_art() -> list:
    """Load the raw ASCII art, uncompressed, and center it."""
    try:
        with open(_ART_FILE, "r", encoding="utf-8") as f:
            lines = [line.rstrip() for line in f.readlines()]
    except Exception:
        return _FALLBACK_FACE

    # Remove empty lines at start and end
    while lines and not lines[0].strip():
        lines = lines[1:]
    while lines and not lines[-1].strip():
        lines = lines[:-1]
    
    if not lines:
        return _FALLBACK_FACE

    # Find bounding box
    min_left = float('inf')
    max_right = 0
    for line in lines:
        stripped = line.rstrip()
        if stripped:
            left = len(stripped) - len(stripped.lstrip())
            right = len(stripped)
            min_left = min(min_left, left)
            max_right = max(max_right, right)

    if min_left == float('inf'):
        return lines

    # Center crop/pad to a generous terminal width like 100
    target_width = 100
    content_width = max_right - min_left
    center = (min_left + max_right) // 2
    crop_start = center - (target_width // 2)
    crop_end = crop_start + target_width

    result = []
    for line in lines:
        padded = line.ljust(crop_end)
        # Handle cases where crop_start is negative
        if crop_start < 0:
            result.append((" " * -crop_start) + padded[:crop_end])
        else:
            result.append(padded[crop_start:crop_end])
    return result

# Load the full uncompressed art at import time
_COMPACT_ART = _load_full_art()

# ─── Compact face fallback (if file missing) ────────────────
_FALLBACK_FACE = [
    "        ╔═══════════════════╗",
    "        ║  ╔══╗      ╔══╗  ║",
    "        ║  ║▓▓║      ║▓▓║  ║",
    "        ║  ╚══╝      ╚══╝  ║",
    "        ║                   ║",
    "        ║     ┌──────┐     ║",
    "        ║     │______│     ║",
    "        ╚═══════════════════╝",
]


class ASCIIFace:
    """Animated ASCII face with states: idle, listening, thinking, speaking, sleeping."""

    def __init__(self):
        self.state = "idle"
        self._frame_counter = 0
        self._blink_timer = 0
        self._blink_interval = random.randint(20, 40)
        self._last_update = time.time()
        # Load art
        self._base_art = _COMPACT_ART if _COMPACT_ART else _FALLBACK_FACE

    def set_state(self, state: str):
        """Set face state: idle, listening, thinking, speaking, sleeping, boot."""
        self.state = state
        self._frame_counter = 0

    def get_frame(self) -> list:
        """Get the current animation frame as a list of strings."""
        self._frame_counter += 1
        self._last_update = time.time()

        if self.state == "idle":
            return self._idle_frame()
        elif self.state == "listening":
            return self._listening_frame()
        elif self.state == "thinking":
            return self._thinking_frame()
        elif self.state == "speaking":
            return self._speaking_frame()
        elif self.state == "sleeping":
            return self._sleeping_frame()
        elif self.state == "boot":
            return self._boot_frame()
        return self._idle_frame()

    def _get_art_copy(self) -> list:
        """Return a copy of the base art lines."""
        return list(self._base_art)

    def _idle_frame(self) -> list:
        """Idle: occasional blink effect (dim random lines)."""
        art = self._get_art_copy()
        self._blink_timer += 1
        if self._blink_timer >= self._blink_interval:
            if self._blink_timer >= self._blink_interval + 2:
                self._blink_timer = 0
                self._blink_interval = random.randint(20, 40)
            # Blink: dim the eye region (lines ~3-8)
            for i in range(min(3, len(art)), min(8, len(art))):
                art[i] = art[i].replace("A", "░")
        return art

    def _listening_frame(self) -> list:
        """Listening: pulsing highlight effect."""
        art = self._get_art_copy()
        cycle = self._frame_counter % 6
        if cycle < 3:
            # Bright phase — replace A with █
            for i in range(len(art)):
                art[i] = art[i].replace("A", "█")
        else:
            # Dim phase — replace A with ▓
            for i in range(len(art)):
                art[i] = art[i].replace("A", "▓")
        return art

    def _thinking_frame(self) -> list:
        """Thinking: wave scan from top to bottom."""
        art = self._get_art_copy()
        scan_pos = self._frame_counter % (len(art) + 4)
        for i in range(len(art)):
            if i == scan_pos or i == scan_pos - 1:
                art[i] = art[i].replace("A", "█")
            elif i == scan_pos - 2 or i == scan_pos + 1:
                art[i] = art[i].replace("A", "▓")
            else:
                art[i] = art[i].replace("A", "░")
        return art

    def _speaking_frame(self) -> list:
        """Speaking: animated mouth region (bottom lines flicker)."""
        art = self._get_art_copy()
        cycle = self._frame_counter % 4
        mouth_chars = ["█", "▓", "░", "▒"]
        mouth_char = mouth_chars[cycle]
        # Top part stays solid
        for i in range(len(art)):
            if i < len(art) - 6:
                art[i] = art[i].replace("A", "▓")
            else:
                # Mouth region — animate
                art[i] = art[i].replace("A", mouth_char)
        return art

    def _sleeping_frame(self) -> list:
        """Sleeping: very dim with floating z's."""
        art = self._get_art_copy()
        for i in range(len(art)):
            art[i] = art[i].replace("A", "░")
        # Add z's at top
        z_count = (self._frame_counter // 4) % 4 + 1
        zzz = " z" * z_count
        if art:
            art[0] = art[0].rstrip() + zzz
        return art

    def _boot_frame(self) -> list:
        """Boot: progressive line reveal."""
        art = self._get_art_copy()
        reveal = min(self._frame_counter, len(art))
        for i in range(len(art)):
            if i < reveal:
                art[i] = art[i].replace("A", "▓")
            else:
                art[i] = " " * len(art[i])
        return art


# ─── Scan Line Effect ────────────────────────────────────
def generate_scanline(width: int = 50) -> str:
    """Generate a randomized scan line for cyber effect."""
    chars = "░▒▓█▀▄▌▐─═"
    return "".join(random.choice(chars) for _ in range(width))


def generate_glitch_line(text: str) -> str:
    """Add random glitch characters to a text line."""
    glitch_chars = "▓░▒█▄▀"
    result = list(text)
    num_glitches = random.randint(0, max(1, len(text) // 15))
    for _ in range(num_glitches):
        pos = random.randint(0, len(result) - 1)
        result[pos] = random.choice(glitch_chars)
    return "".join(result)
