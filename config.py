"""
VISION AI Assistant - Central Configuration
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

NOTES_FILE = DATA_DIR / "notes.json"
PLANS_FILE = DATA_DIR / "plans.json"
CONTACTS_FILE = DATA_DIR / "contacts.json"

# ─── Ollama ──────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")

# ─── Voice ───────────────────────────────────────────────
WAKE_WORD = "vision online"
HOTKEY = "ctrl+alt+v"
TTS_RATE = 180  # Words per minute
TTS_VOLUME = 0.9

# ─── Browser ─────────────────────────────────────────────
BRAVE_PATH = os.getenv(
    "BRAVE_PATH",
    r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
)

# ─── Email ───────────────────────────────────────────────
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_SMTP_SERVER = os.getenv("EMAIL_SMTP_SERVER", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(os.getenv("EMAIL_SMTP_PORT", "587"))

# ─── Weather ─────────────────────────────────────────────
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")
WEATHER_CITY = os.getenv("WEATHER_CITY", "")

# ─── UI Theme ────────────────────────────────────────────
THEME = {
    "primary": "green",
    "secondary": "cyan",
    "accent": "magenta",
    "error": "red",
    "warning": "yellow",
    "bg": "black",
    "text": "bright_white",
    "border": "bright_green",
}

# ─── System Prompt ───────────────────────────────────────
SYSTEM_PROMPT = """You are VISION, an advanced AI desktop assistant. You have a cyber/futuristic personality — confident, efficient, and slightly witty. You speak concisely but helpfully.

Your capabilities include:
- Normal conversation and answering questions
- File browsing and opening files/movies on the PC
- Taking and managing notes
- Searching YouTube and playing music via YT Music
- Opening applications on command
- Sending WhatsApp messages and emails
- Taking screenshots and searching Google Images
- Providing real-time info (weather, news)
- Comparing prices across e-commerce platforms
- Generating code
- Opening websites in the browser
- Typing text on behalf of the user
- Controlling system volume, brightness, and media playback
- Helping with planning, studies, and explaining concepts

When the user gives a command, decide which tool/function to call. If it's just conversation, respond naturally.
Keep responses concise unless asked for detail. Use a futuristic, slightly cool tone.
When greeting, say something like "VISION online. Systems nominal. How can I assist you?"
"""
