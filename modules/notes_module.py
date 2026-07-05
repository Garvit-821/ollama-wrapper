"""
VISION AI Assistant - Notes Module
Create, read, search, and manage notes.
"""
import json
from datetime import datetime
import config


def _load_notes() -> list:
    """Load notes from file."""
    if config.NOTES_FILE.exists():
        try:
            with open(config.NOTES_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_notes(notes: list):
    """Save notes to file."""
    with open(config.NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def manage_notes(action: str, title: str = None, content: str = None, query: str = None) -> str:
    """Manage notes: create, read, list, delete, search."""
    notes = _load_notes()

    if action == "create":
        if not title:
            return "Please provide a title for the note."
        note = {
            "id": len(notes) + 1,
            "title": title,
            "content": content or "",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        notes.append(note)
        _save_notes(notes)
        return f"[NOTE] Note created: '{title}'"

    elif action == "read":
        if title:
            for note in notes:
                if title.lower() in note["title"].lower():
                    return (
                        f"[NOTE] {note['title']}\n"
                        f"   Created: {note['created']}\n"
                        f"   Updated: {note['updated']}\n"
                        f"   ---------------\n"
                        f"   {note['content']}"
                    )
            return f"Note '{title}' not found."
        else:
            return "Please specify a note title to read."

    elif action == "list":
        if not notes:
            return "No notes saved yet."
        lines = ["[NOTES] Saved notes:"]
        for note in notes:
            lines.append(f"  {note['id']}. {note['title']} ({note['created']})")
        return "\n".join(lines)

    elif action == "delete":
        if title:
            original_len = len(notes)
            notes = [n for n in notes if title.lower() not in n["title"].lower()]
            if len(notes) < original_len:
                # Re-index
                for i, note in enumerate(notes):
                    note["id"] = i + 1
                _save_notes(notes)
                return f"[DELETED] Note removed: '{title}'"
            return f"Note '{title}' not found."
        return "Please specify a note title to delete."

    elif action == "search":
        search_term = query or title or ""
        if not search_term:
            return "Please provide a search term."
        found = []
        for note in notes:
            if (search_term.lower() in note["title"].lower() or
                search_term.lower() in note.get("content", "").lower()):
                found.append(note)
        if found:
            lines = [f"[SEARCH] Found {len(found)} note(s) matching '{search_term}':"]
            for note in found:
                lines.append(f"  {note['id']}. {note['title']}")
            return "\n".join(lines)
        return f"No notes found matching '{search_term}'."

    return "Invalid note action. Use: create, read, list, delete, search."
