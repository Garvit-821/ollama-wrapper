"""
VISION AI Assistant - Text-to-Speech Engine
Offline TTS using pyttsx3 with threaded non-blocking speech.
"""
import threading
import pyttsx3
import config


class TTSEngine:
    """Text-to-Speech engine using pyttsx3."""

    def __init__(self):
        self._engine = pyttsx3.init()
        self._engine.setProperty('rate', config.TTS_RATE)
        self._engine.setProperty('volume', config.TTS_VOLUME)

        # Try to set a good voice
        voices = self._engine.getProperty('voices')
        for voice in voices:
            # Prefer a female or clear voice
            if 'zira' in voice.name.lower() or 'david' in voice.name.lower():
                self._engine.setProperty('voice', voice.id)
                break

        self._lock = threading.Lock()
        self._speaking = False

    def speak(self, text: str, blocking: bool = False):
        """Speak text. Non-blocking by default (runs in thread)."""
        if blocking:
            self._speak_sync(text)
        else:
            thread = threading.Thread(target=self._speak_sync, args=(text,), daemon=True)
            thread.start()

    def _speak_sync(self, text: str):
        """Synchronous speech."""
        with self._lock:
            self._speaking = True
            try:
                self._engine = pyttsx3.init()
                self._engine.setProperty('rate', config.TTS_RATE)
                self._engine.setProperty('volume', config.TTS_VOLUME)
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception:
                pass
            finally:
                self._speaking = False

    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def stop(self):
        """Stop current speech."""
        try:
            self._engine.stop()
        except Exception:
            pass
        self._speaking = False
