"""
VISION AI Assistant - Speech-to-Text Engine
Voice input with wake word detection using speech_recognition.
"""
import speech_recognition as sr
import threading
import sys
import config


class STTEngine:
    """Speech-to-Text with wake word detection."""

    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 150  # Lowered from 300 to better catch quiet voices
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.wake_word = config.WAKE_WORD.lower()
        self.microphone = None
        self._listen_lock = threading.Lock()
        self._calibrated = False

    def _get_microphone(self):
        """Get or create microphone instance."""
        if self.microphone is None:
            self.microphone = sr.Microphone()
        return self.microphone

    def calibrate(self):
        """Calibrate for ambient noise."""
        if not self._listen_lock.acquire(timeout=2):
            return False
        try:
            with self._get_microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self._calibrated = True
            return True
        except Exception:
            return False
        finally:
            self._listen_lock.release()

    def listen_for_wake_word(self, timeout: int = None) -> bool:
        """
        Listen for the wake word "VISION online".
        Returns True if wake word detected, False otherwise.
        """
        if not self._listen_lock.acquire(timeout=0.2):
            return False
        try:
            with self._get_microphone() as source:
                if not self._calibrated:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self._calibrated = True
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=4
                )

            text = self._transcribe(audio)
            if text and self.wake_word in text.lower():
                return True
            return False

        except sr.WaitTimeoutError:
            return False
        except Exception:
            return False
        finally:
            self._listen_lock.release()

    def listen_for_command(self, timeout: int = 10, phrase_limit: int = 15) -> str:
        """
        Listen for a voice command after activation.
        Returns the transcribed text, or empty string on failure.
        """
        if not self._listen_lock.acquire(timeout=2):
            return ""
        try:
            with self._get_microphone() as source:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_limit
                )

            text = self._transcribe(audio)
            return text if text else ""

        except sr.WaitTimeoutError:
            return ""
        except Exception:
            return ""
        finally:
            self._listen_lock.release()

    def _transcribe(self, audio) -> str:
        """Transcribe audio using Google STT (free)."""
        try:
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            # Fallback: try offline if available
            try:
                text = self.recognizer.recognize_sphinx(audio)
                return text
            except Exception:
                return ""

    def list_microphones(self) -> list:
        """List available microphones."""
        return sr.Microphone.list_microphone_names()

    def diagnostics(self) -> dict:
        """Return basic voice diagnostics for troubleshooting."""
        try:
            names = self.list_microphones()
            try:
                import pyaudio
                pa = pyaudio.PyAudio()
                default_index = pa.get_default_input_device_info().get("index", None)
                pa.terminate()
            except Exception:
                default_index = None
            return {
                "ok": len(names) > 0,
                "mic_count": len(names),
                "default_index": default_index,
                "energy_threshold": self.recognizer.energy_threshold,
                "dynamic_energy": self.recognizer.dynamic_energy_threshold,
                "pause_threshold": self.recognizer.pause_threshold,
                "wake_word": self.wake_word,
                "microphones": names,
            }
        except Exception as e:
            hint = ""
            if "PyAudio" in str(e):
                hint = (
                    "PyAudio missing. On Windows, use Python 3.10/3.11 "
                    "or install Microsoft C++ Build Tools for Python 3.14."
                )
            return {
                "ok": False,
                "error": str(e),
                "hint": hint,
                "python_version": sys.version.split()[0],
                "wake_word": self.wake_word,
            }
