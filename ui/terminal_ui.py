"""
VISION AI Assistant - Terminal UI
Dense, cyber-themed terminal interface using Rich library.
"""
import os
import sys
import time
import threading
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from ui.ascii_face import ASCIIFace, generate_scanline


class TerminalUI:
    """Dense cyber-themed terminal UI for VISION."""

    BANNER = r"""[bright_green]
 ██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗
 ██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║
 ██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║
 ╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║
  ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║
   ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
[/bright_green][cyan]     ═══ Advanced AI Desktop Assistant ═══[/cyan]
[cyan]       ═══ Developed By Garvit Prakash ═══[/cyan]"""

    STATUS_ICONS = {
        "online": "[bright_green]● ONLINE[/bright_green]",
        "listening": "[bright_cyan]◉ LISTENING[/bright_cyan]",
        "thinking": "[bright_yellow]◌ THINKING[/bright_yellow]",
        "speaking": "[bright_magenta]◉ SPEAKING[/bright_magenta]",
        "sleeping": "[dim]◌ STANDBY[/dim]",
        "error": "[bright_red]✖ ERROR[/bright_red]",
    }

    # ─── Help text lines ─────────────────────────────────
    HELP_LINES = [
        "[bright_cyan]═══ COMMANDS ═══[/bright_cyan]",
        "[green]▸[/green] Open [app] / Launch [app]",
        "[green]▸[/green] Volume up/down/mute",
        "[green]▸[/green] Brightness up/down/set",
        "[green]▸[/green] Play/pause, Next/Prev song",
        "[green]▸[/green] Search [query] on YouTube",
        "[green]▸[/green] Play [song] (YT Music)",
        "[green]▸[/green] Find [file] on my PC",
        "[green]▸[/green] Open [website.com]",
        "[green]▸[/green] Take a note: [text]",
        "[green]▸[/green] Tell [contact] [msg] (WhatsApp)",
        "[green]▸[/green] Send email to [contact]",
        "[green]▸[/green] Take a screenshot",
        "[green]▸[/green] What's the weather?",
        "[green]▸[/green] Latest news on [topic]",
        "[green]▸[/green] Compare prices of [product]",
        "[green]▸[/green] Write code for [task]",
        "[green]▸[/green] Explain [concept]",
        "[green]▸[/green] Create study plan for [topic]",
        "[green]▸[/green] Type this: [text]",
        "[green]▸[/green] Run command: [command]",
        "",
        "[bright_cyan]═══ META ═══[/bright_cyan]",
        "[dim]voice[/dim]    — Voice input mode",
        "[dim]clear[/dim]    — Clear conversation",
        "[dim]help[/dim]     — Toggle this help",
        "[dim]quit[/dim]     — Exit VISION",
        "[dim]Ctrl+Alt+V[/dim] — Activate voice",
        "[dim]\"VISION online\"[/dim] — Wake word",
    ]

    def __init__(self):
        self.console = Console()
        self.face = ASCIIFace()
        self.conversation_log = []
        self.status = "online"
        self.mode = "TEXT"
        self._lock = threading.Lock()
        self.show_help = False  # Toggle for help sidebar

    def clear(self):
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def boot_sequence(self):
        """Animated boot-up sequence."""
        self.clear()

        # Scanline effect
        for i in range(4):
            line = generate_scanline(55)
            self.console.print(f" [dim green]{line}[/dim green]", end="\r")
            time.sleep(0.04)

        # Banner
        self.console.print(self.BANNER)
        time.sleep(0.2)

        # Boot messages
        boot_msgs = [
            ("Initializing neural networks", "bright_green"),
            ("Loading language model", "bright_green"),
            ("Calibrating voice systems", "cyan"),
            ("Mounting file system access", "cyan"),
            ("Establishing web connections", "bright_green"),
            ("Loading module registry", "bright_green"),
            ("Activating cyber interface", "magenta"),
            ("All systems nominal", "bright_green"),
        ]

        for msg, color in boot_msgs:
            self._typewriter(f" [{color}]▸ {msg}...[/{color}]")
            time.sleep(0.08)

        self.console.print(f" [bright_green]{'━' * 48}[/bright_green]")
        self.console.print(f" [bright_cyan] VISION v1.0 — Ready[/bright_cyan]  [dim]Ctrl+Alt+V │ 'help'[/dim]")
        self.console.print(f" [bright_green]{'━' * 48}[/bright_green]")
        time.sleep(0.2)

    def _typewriter(self, text: str, delay: float = 0.01):
        """Print text with typewriter effect."""
        import re
        clean = re.sub(r'\[.*?\]', '', text)
        for char in clean:
            sys.stdout.write(char)
            sys.stdout.flush()
            time.sleep(delay)
        sys.stdout.write('\r')
        self.console.print(text)

    def display_face_and_status(self):
        """Display full face centered, with status info below."""
        face_lines = self.face.get_frame()
        now = datetime.now().strftime("%H:%M:%S")
        status_icon = self.STATUS_ICONS.get(self.status, self.STATUS_ICONS["online"])
        mode_label = "[cyan]VOICE[/cyan]" if self.mode == "VOICE" else "[green]TEXT[/green]"

        face_text = "\n".join(face_lines)

        if self.show_help:
            info_text = " | ".join([line.replace("[bright_cyan]═══ COMMANDS ═══[/bright_cyan]", "").strip() for line in self.HELP_LINES if "▸" in line][:5]) + " ... (see more in text mode)"
        else:
            info_text = f"Status: {status_icon}  |  Mode: {mode_label}  |  Time: [dim]{now}[/dim]  |  [dim]Ctrl+Alt+V: Activate Voice[/dim]"

        # Face panel
        face_panel = Panel(
            Text.from_ansi(f"\033[32m{face_text}\033[0m", justify="center"),
            border_style="bright_green",
            title=f"[bright_cyan]◈ VISION ◈[/bright_cyan] {status_icon}",
            title_align="center",
            subtitle=info_text,
            subtitle_align="center",
        )
        self.console.print(face_panel)

    def display_conversation(self, max_lines: int = 10):
        """Display compact conversation history with timestamps."""
        if not self.conversation_log:
            return

        conv_text = Text()
        recent = self.conversation_log[-max_lines:]
        for entry in recent:
            role = entry["role"]
            content = entry["content"]
            ts = entry.get("time", "")

            # Truncate very long messages for display
            display_content = content
            if len(display_content) > 200:
                display_content = display_content[:197] + "..."

            if role == "user":
                conv_text.append(f" {ts} ", style="dim")
                conv_text.append("YOU ", style="bright_cyan bold")
                conv_text.append(f"│ {display_content}\n", style="bright_white")
            elif role == "vision":
                conv_text.append(f" {ts} ", style="dim")
                conv_text.append("AI  ", style="bright_green bold")
                conv_text.append(f"│ {display_content}\n", style="white")
            elif role == "system":
                conv_text.append(f" {ts} ", style="dim")
                conv_text.append("SYS ", style="yellow")
                conv_text.append(f"│ {display_content}\n", style="dim")
            elif role == "error":
                conv_text.append(f" {ts} ", style="dim")
                conv_text.append("ERR ", style="bright_red bold")
                conv_text.append(f"│ {display_content}\n", style="red")

        panel = Panel(
            conv_text,
            border_style="green",
            title="[dim cyan]◈ log ◈[/dim cyan]",
            title_align="left",
            padding=(0, 1),
        )
        self.console.print(panel)

    def add_message(self, role: str, content: str):
        """Add a message to the conversation log."""
        with self._lock:
            self.conversation_log.append({
                "role": role,
                "content": content,
                "time": datetime.now().strftime("%H:%M:%S")
            })

    def set_status(self, status: str):
        """Update status: online, listening, thinking, speaking, sleeping, error."""
        self.status = status
        state_map = {
            "listening": "listening",
            "thinking": "thinking",
            "speaking": "speaking",
            "sleeping": "sleeping",
        }
        self.face.set_state(state_map.get(status, "idle"))

    def display_resource_hud(self):
        """Display real-time system metrics (CPU, RAM, Disk, Temp) in a cyberpunk panel."""
        try:
            import psutil
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            
            try:
                disk = psutil.disk_usage('/').percent
            except Exception:
                disk = 0.0

            # Get CPU temperature safely
            temp_val = None
            if hasattr(psutil, "sensors_temperatures"):
                try:
                    temps = psutil.sensors_temperatures()
                    for key in ['coretemp', 'cpu_thermal', 'acpitz']:
                        if key in temps and temps[key]:
                            temp_val = temps[key][0].current
                            break
                    if temp_val is None and temps:
                        for val in temps.values():
                            if val:
                                temp_val = val[0].current
                                break
                except Exception:
                    pass

            def make_bar(pct: float, color: str) -> str:
                filled = int(pct / 10)
                empty = 10 - filled
                return f"[{color}]{'■' * filled}[/{color}][dim]{'□' * empty}[/dim]"

            cpu_bar = make_bar(cpu, "bright_green")
            ram_bar = make_bar(ram, "bright_cyan")
            disk_bar = make_bar(disk, "bright_magenta")
            
            temp_str = f"[bright_yellow]{temp_val:.1f}°C[/bright_yellow]" if temp_val is not None else "[dim]N/A[/dim]"
            
            hud_text = Text.from_markup(
                f" [green]CPU[/green] {cpu:4.1f}% {cpu_bar}   "
                f"[cyan]RAM[/cyan] {ram:4.1f}% {ram_bar}   "
                f"[magenta]DSK[/magenta] {disk:4.1f}% {disk_bar}   "
                f"[yellow]TMP[/yellow] {temp_str}"
            )
            
            panel = Panel(
                hud_text,
                border_style="green",
                title="[dim cyan]◈ system resources ◈[/dim cyan]",
                title_align="left",
                padding=(0, 1)
            )
            self.console.print(panel)
        except Exception as e:
            self.console.print(f"[dim red]System HUD Error: {e}[/dim red]")

    def refresh_display(self):
        """Refresh the full display."""
        self.clear()
        self.display_face_and_status()
        self.display_resource_hud()
        self.display_conversation()
        self._display_input_prompt()

    def _display_input_prompt(self):
        """Show the input prompt."""
        mode_label = "[cyan]VOICE[/cyan]" if self.mode == "VOICE" else "[green]TEXT[/green]"
        self.console.print(
            f" [bright_green]╔══[/bright_green] {mode_label} "
            f"[bright_green]{'═' * 40}╗[/bright_green]"
        )

    def get_input_prompt(self) -> str:
        """Get the input prompt string."""
        return " ║ ❯ "

    def show_processing(self, message: str = "Processing"):
        """Show a processing indicator."""
        self.console.print(f" [bright_yellow] ◌ {message}...[/bright_yellow]")

    def show_result(self, message: str):
        """Show a result message."""
        self.console.print(f" [bright_green] ✔ {message}[/bright_green]")

    def show_error(self, message: str):
        """Show an error message."""
        self.console.print(f" [bright_red] ✖ {message}[/bright_red]")

    def print_response(self, text: str):
        """Print VISION's response with styling."""
        self.console.print(
            Panel(
                f"[white]{text}[/white]",
                border_style="bright_green",
                title="[bright_green]◈ VISION[/bright_green]",
                title_align="left",
                padding=(0, 2),
            )
        )

    def print_divider(self):
        """Print a styled divider."""
        self.console.print(f" [dim green]{'─' * 55}[/dim green]")

    def display_help(self):
        """Display full help panel (standalone, stays visible until user presses Enter)."""
        help_lines = "\n".join(self.HELP_LINES)
        self.console.print(
            Panel(
                Text.from_markup(help_lines),
                border_style="bright_green",
                title="[bright_cyan]◈ VISION HELP ◈[/bright_cyan]",
                title_align="center",
                padding=(0, 2),
            )
        )
