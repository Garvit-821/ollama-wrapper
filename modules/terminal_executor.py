"""
VISION AI Assistant - Terminal Executor Module
Allows VISION to safely run bash (Linux) or powershell/cmd (Windows) command lines.
"""
import subprocess
import sys
import os
import signal
import re

# Blacklist of commands that are potentially destructive.
BLACKLIST = [
    r"\brm\s+-[rRfF]*\s*/",          # rm -rf /
    r"\brmdir\s+-[rRfF]*\s*/",       # rmdir /
    r"\bmkfs\b",                     # format disk
    r"\bdd\s+if=",                   # low level write
    r"\bshutdown\b",                 # shutdown system
    r"\breboot\b",                   # reboot system
    r"\bpoweroff\b",                 # poweroff
    r"\binit\s+0\b",                 # shutdown Linux
    r"\binit\s+6\b",                 # reboot Linux
    r"\bkillall\b",                  # mass process killing
    r"\bpkill\b",                    # mass process killing
    r"\bchmod\s+-[rRfF]*\s*777\s*/", # chmod 777 /
    r"\bchown\b",                    # ownership change
    r"\bdel\s+/f\s*/s\s*/q\s*c:\\",   # Windows del c:\*
    r"\bformat\s+c:",                # format Windows C: drive
]

def execute_command(command: str) -> str:
    """
    Safely execute a shell command.
    Checks the command against a blacklist to prevent destructive actions.
    Uses process groups to cleanly handle timeouts and avoid orphaned child processes.
    """
    cmd_clean = command.strip()
    if not cmd_clean:
        return "Error: Command is empty."

    # Check blacklist
    for pattern in BLACKLIST:
        if re.search(pattern, cmd_clean, re.IGNORECASE):
            return f"Error: Command rejected. Destructive pattern detected: '{pattern}'"

    # Determine default shell / executable
    shell = True
    executable = None
    if sys.platform == "win32":
        executable = "powershell.exe"

    # Unix-specific process group creation to handle timeouts correctly
    kwargs = {}
    if sys.platform != "win32":
        kwargs["preexec_fn"] = os.setsid

    try:
        proc = subprocess.Popen(
            cmd_clean,
            shell=shell,
            executable=executable,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            **kwargs
        )
        
        try:
            stdout, stderr = proc.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            # Kill the process / process group
            if sys.platform == "win32":
                proc.terminate()
            else:
                try:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
                except Exception:
                    pass
            stdout, stderr = proc.communicate()
            return "Error: Command execution timed out (limit: 30 seconds)."

        stdout = (stdout or "").strip()
        stderr = (stderr or "").strip()
        
        output = []
        if stdout:
            output.append(f"STDOUT:\n{stdout}")
        if stderr:
            output.append(f"STDERR:\n{stderr}")
            
        final_output = "\n\n".join(output) if output else "Command executed successfully with no output."
        return f"[Exit Code: {proc.returncode}]\n{final_output}"
        
    except Exception as e:
        return f"Error executing command: {str(e)}"
