"""
╔═══════════════════════════════════════════════════════════╗
║                    VISION AI ASSISTANT                    ║
║           Advanced AI Desktop Assistant v1.0              ║
║                                                           ║
║  Voice + Keyboard activated | Ollama phi3:mini brain       ║
║  Cyber-themed ASCII interface | 20+ capabilities          ║
╚═══════════════════════════════════════════════════════════╝

Usage:
    python main.py              # Start VISION
    python main.py --no-voice   # Start without voice (text only)
    python main.py --startup    # Install to Windows startup
"""

import sys
import os
import io
import threading
import time
import signal
import json

# Force UTF-8 output on Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from core.llm_engine import LLMEngine
from core.tts_engine import TTSEngine
from ui.terminal_ui import TerminalUI

# ─── Module Imports ──────────────────────────────────────
from modules.system_control import control_volume, control_brightness, media_control
from modules.file_browser import search_files, open_file, list_directory
from modules.app_launcher import open_application
from modules.typing_module import type_text
from modules.web_browser import open_website, google_search
from modules.youtube_module import search_youtube, play_music
from modules.messaging import send_whatsapp, send_email
from modules.web_search import get_weather, get_news, compare_prices, web_search, read_webpage
from modules.screenshot_module import take_screenshot
from modules.notes_module import manage_notes
from modules.code_generator import generate_code
from modules.planner import manage_plan
from modules.knowledge import explain_concept


class VisionAssistant:
    """Main VISION assistant orchestrator."""

    def __init__(self, voice_enabled: bool = True):
        self.ui = TerminalUI()
        self.llm = LLMEngine()
        self.tts = TTSEngine()
        self.voice_enabled = voice_enabled
        self.stt = None
        self.running = True
        self.active = True  # Whether VISION is actively listening
        self.hotkey_registered = False
        self._voice_session_lock = threading.Lock()
        self._voice_active = False
        self._voice_unavailable_reason = ""

        # Initialize STT if voice is enabled
        if self.voice_enabled:
            try:
                from core.stt_engine import STTEngine
                self.stt = STTEngine()
            except Exception as e:
                self.voice_enabled = False
                self._voice_unavailable_reason = str(e)
                self.ui.add_message("system", f"Voice disabled: {e}")

    def start(self):
        """Start VISION."""
        # Boot sequence
        self.ui.boot_sequence()

        # Register global hotkey
        self._register_hotkey()

        # Greeting
        greeting = "VISION online. All systems nominal. How can I assist you?"
        self.ui.add_message("vision", greeting)
        self.tts.speak(greeting)

        # Main loop
        self._main_loop()

    def _register_hotkey(self):
        """Register the global activation hotkey."""
        try:
            import keyboard
            keyboard.add_hotkey(config.HOTKEY, self._on_hotkey)
            self.hotkey_registered = True
        except ImportError:
            self.ui.add_message("system", "Hotkey disabled: keyboard library not found")
        except Exception as e:
            self.ui.add_message("system", f"Hotkey error: {e}")

    def _on_hotkey(self):
        """Handle hotkey press."""
        if not self.voice_enabled or not self.stt:
            msg = "Voice is unavailable. Run 'voice diagnostics' after installing PyAudio."
            self.ui.add_message("system", msg)
            return
        if self.voice_enabled and self.stt:
            if self._voice_active:
                return
            self.ui.set_status("listening")
            self.ui.add_message("system", "Hotkey activated -- listening...")
            self.ui.refresh_display()
            self._voice_input()

    def _main_loop(self):
        """Main interaction loop."""
        while self.running:
            try:
                self.ui.set_status("online")
                self.ui.refresh_display()

                # Get input (text mode)
                prompt = self.ui.get_input_prompt()
                try:
                    user_input = input(prompt).strip()
                except (EOFError, KeyboardInterrupt):
                    self._shutdown()
                    break

                if not user_input:
                    continue

                # Handle special commands
                if self._handle_special_command(user_input):
                    continue

                # Process through LLM
                self.ui.add_message("user", user_input)
                self._process_input(user_input)

            except KeyboardInterrupt:
                self._shutdown()
                break
            except Exception as e:
                self.ui.add_message("error", str(e))

    def _handle_special_command(self, cmd: str) -> bool:
        """Handle special meta-commands. Returns True if handled."""
        cmd_lower = cmd.lower().strip()

        if cmd_lower in ("quit", "exit", "shutdown", "bye"):
            self._shutdown()
            return True

        elif cmd_lower == "voice":
            if self.voice_enabled and self.stt:
                self.ui.mode = "VOICE"
                self.ui.add_message("system", "Voice mode activated. Listening...")
                self.ui.set_status("listening")
                self.ui.refresh_display()
                self._voice_input()
                self.ui.mode = "TEXT"
            else:
                self.ui.add_message("system", "Voice not available. Check microphone.")
            return True

        elif cmd_lower in ("voice test", "mic test", "voice diagnostics"):
            if self.voice_enabled and self.stt:
                report = self.stt.diagnostics()
                pretty = json.dumps(report, indent=2)
                self.ui.add_message("system", f"Voice diagnostics:\n{pretty}")
                if report.get("ok"):
                    self.tts.speak("Microphone diagnostics complete.")
                else:
                    self.tts.speak("Voice diagnostics failed. Please check microphone setup.")
            else:
                self.ui.add_message("system", "Voice engine is not initialized.")
            return True

        elif cmd_lower == "clear":
            self.ui.conversation_log.clear()
            self.llm.clear_history()
            self.ui.add_message("system", "Conversation cleared.")
            return True

        elif cmd_lower == "startup install":
            from startup.install_startup import install_startup
            result = install_startup()
            self.ui.add_message("system", result)
            return True

        elif cmd_lower == "startup uninstall":
            from startup.install_startup import uninstall_startup
            result = uninstall_startup()
            self.ui.add_message("system", result)
            return True

        elif cmd_lower == "help":
            self._show_help()
            return True

        return False

    def _voice_input(self):
        """Handle voice input mode."""
        if not self.stt:
            return
        if not self._voice_session_lock.acquire(blocking=False):
            return

        self._voice_active = True
        try:
            self.ui.set_status("listening")
            self.ui.refresh_display()

            # Calibrate mic
            calibrated = self.stt.calibrate()
            if not calibrated:
                self.voice_enabled = False
                self._voice_unavailable_reason = "Microphone unavailable (likely PyAudio missing)."
                self.ui.add_message(
                    "system",
                    "Microphone calibration failed. Voice has been disabled. "
                    "Install PyAudio (recommended: Python 3.11 venv) and restart VISION."
                )
                return

            # Listen for command
            command = self.stt.listen_for_command(timeout=10, phrase_limit=15)

            if command:
                self.ui.add_message("user", f"[VOICE] {command}")
                self._process_input(command)
            else:
                self.ui.add_message("system", "Didn't catch that. Try again.")
                self.tts.speak("I didn't catch that.")
        finally:
            self._voice_active = False
            self._voice_session_lock.release()

    def _process_input(self, user_input: str):
        """Process user input through the LLM and execute actions."""
        self.ui.set_status("thinking")
        self.ui.refresh_display()
        self.ui.show_processing("Analyzing command")

        # Send to LLM
        response = self.llm.chat(user_input)

        if response["type"] == "function_call":
            # Execute the function
            result = self._execute_function(
                response["function_name"],
                response["function_args"]
            )

            # Report result back to LLM for natural response
            final_response = self.llm.report_function_result(
                response["tool_call_id"],
                response["function_name"],
                result
            )

            # Handle chained function calls (up to 3 deep)
            depth = 0
            while final_response["type"] == "function_call" and depth < 3:
                result = self._execute_function(
                    final_response["function_name"],
                    final_response["function_args"]
                )
                final_response = self.llm.report_function_result(
                    final_response["tool_call_id"],
                    final_response["function_name"],
                    result
                )
                depth += 1

            # Display LLM's natural language response
            if final_response["content"]:
                self._respond(final_response["content"])
            else:
                self._respond(result)

        elif response["type"] == "text":
            self._respond(response["content"])

    def _execute_function(self, name: str, args: dict) -> str:
        """Execute a module function by name."""
        self.ui.show_processing(f"Executing: {name}")

        try:
            # ─── System Control ──────────────────────────
            if name == "control_volume":
                return control_volume(**args)

            elif name == "control_brightness":
                return control_brightness(**args)

            elif name == "media_control":
                return media_control(**args)

            # ─── File System ─────────────────────────────
            elif name == "search_files":
                return search_files(**args)

            elif name == "open_file":
                return open_file(**args)

            # ─── Applications ────────────────────────────
            elif name == "open_application":
                return open_application(**args)

            # ─── Web & Browser ───────────────────────────
            elif name == "open_website":
                return open_website(**args)

            elif name == "web_search":
                return web_search(**args)

            elif name == "read_webpage":
                return read_webpage(**args)

            # ─── YouTube & Music ─────────────────────────
            elif name == "search_youtube":
                return search_youtube(**args)

            elif name == "play_music":
                return play_music(**args)

            # ─── Messaging ───────────────────────────────
            elif name == "send_whatsapp":
                return send_whatsapp(**args)

            elif name == "send_email":
                return send_email(**args)

            # ─── Screenshots ─────────────────────────────
            elif name == "take_screenshot":
                return take_screenshot(**args)

            # ─── Information ─────────────────────────────
            elif name == "get_weather":
                return get_weather(**args)

            elif name == "get_news":
                return get_news(**args)

            elif name == "compare_prices":
                return compare_prices(**args)

            # ─── Notes ───────────────────────────────────
            elif name == "manage_notes":
                return manage_notes(**args)

            # ─── Code Generation ─────────────────────────
            elif name == "generate_code":
                return generate_code(llm_engine=self.llm, **args)

            # ─── Planning ────────────────────────────────
            elif name == "manage_plan":
                return manage_plan(**args)

            # ─── Knowledge ───────────────────────────────
            elif name == "explain_concept":
                return explain_concept(llm_engine=self.llm, **args)

            # ─── Typing ──────────────────────────────────
            elif name == "type_text":
                return type_text(**args)

            else:
                return f"Unknown function: {name}"

        except Exception as e:
            return f"Error executing {name}: {str(e)}"

    def _respond(self, text: str):
        """Display and speak VISION's response."""
        self.ui.set_status("speaking")
        self.ui.add_message("vision", text)
        self.ui.print_response(text)

        # Speak the response only if we are in voice mode
        if getattr(self, '_voice_active', False) or self.ui.mode == "VOICE":
            tts_text = text[:500] if len(text) > 500 else text
            # Clean TTS text of special characters / markers
            import re
            tts_clean = re.sub(r'\[\w+\]', '', tts_text)  # Remove [TAGS]
            tts_clean = tts_clean.replace(">", "").replace("--", ",")
            self.tts.speak(tts_clean)

        self.ui.set_status("online")

    def _show_help(self):
        """Display help — toggles sidebar and shows full help panel."""
        self.ui.show_help = not self.ui.show_help
        self.ui.clear()
        self.ui.display_face_and_status()
        self.ui.display_help()
        self.ui.add_message("system", "Help toggled. Type 'help' again to hide.")
        try:
            input("  [Press Enter to continue...] ")
        except (EOFError, KeyboardInterrupt):
            pass

    def _shutdown(self):
        """Graceful shutdown."""
        self.running = False
        self.ui.set_status("sleeping")

        farewell = "VISION shutting down. Until next time."
        self.ui.add_message("vision", farewell)
        self.ui.print_response(farewell)
        self.tts.speak(farewell, blocking=True)

        # Cleanup hotkey
        if self.hotkey_registered:
            try:
                import keyboard
                keyboard.unhook_all()
            except Exception:
                pass

        self.ui.console.print("\n  [dim green]═══ VISION v1.0 — Session ended ═══[/dim green]\n")


# ─── Wake Word Background Listener ──────────────────────
def start_wake_word_listener(assistant: VisionAssistant):
    """Background thread that listens for the wake word."""
    if not assistant.stt:
        return

    def listener():
        while assistant.running:
            try:
                if assistant._voice_active:
                    time.sleep(0.3)
                    continue
                if assistant.stt.listen_for_wake_word(timeout=3):
                    assistant.ui.add_message("system", "Wake word detected!")
                    assistant.tts.speak("Yes, I'm listening.")
                    assistant._voice_input()
            except Exception:
                time.sleep(1)

    thread = threading.Thread(target=listener, daemon=True)
    thread.start()


# ─── Entry Point ─────────────────────────────────────────
def main():
    """Main entry point."""
    # Parse arguments
    voice_enabled = "--no-voice" not in sys.argv

    # Handle startup commands
    if "--startup" in sys.argv:
        from startup.install_startup import install_startup
        print(install_startup())
        return

    if "--uninstall-startup" in sys.argv:
        from startup.install_startup import uninstall_startup
        print(uninstall_startup())
        return

    # Check Ollama availability
    try:
        import requests
        resp = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        models = [m.get("name", "") for m in resp.json().get("models", [])]
    except Exception:
        print("\n" + "=" * 55)
        print("  [!] VISION could not connect to Ollama!")
        print("=" * 55)
        print("  1. Install and start Ollama from: https://ollama.com/download")
        print("  2. Run: ollama pull phi3:mini")
        print("  3. Ensure Ollama is running at:", config.OLLAMA_BASE_URL)
        print("=" * 55 + "\n")
        return

    if not any(name.startswith(config.OLLAMA_MODEL) for name in models):
        print("\n" + "=" * 55)
        print(f"  [!] Ollama model not found: {config.OLLAMA_MODEL}")
        print("=" * 55)
        print(f"  Run: ollama pull {config.OLLAMA_MODEL}")
        print("=" * 55 + "\n")
        return

    # Create and start assistant
    assistant = VisionAssistant(voice_enabled=voice_enabled)

    # Start wake word listener in background (if voice enabled)
    if voice_enabled and assistant.stt:
        start_wake_word_listener(assistant)

    # Start main loop
    assistant.start()


if __name__ == "__main__":
    main()
