"""
VISION AI Assistant - File Browser Module
Search for files, browse directories, and open files.
"""
import os
import glob
from pathlib import Path


# Common file type extensions
FILE_TYPES = {
    "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
    "audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
    "document": [".pdf", ".doc", ".docx", ".txt", ".pptx", ".xlsx", ".csv", ".rtf"],
    "image": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
    "code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".ts", ".go", ".rs"],
}

# Default search locations
DEFAULT_SEARCH_DIRS = [
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    os.path.expanduser("~\\Videos"),
    os.path.expanduser("~\\Music"),
    os.path.expanduser("~\\Pictures"),
]


def search_files(query: str, directory: str = None, file_type: str = None, max_results: int = 20) -> str:
    """
    Search for files by name. Optionally filter by type and directory.
    """
    results = []

    # Determine extensions to filter
    extensions = None
    if file_type:
        if file_type.startswith("."):
            extensions = [file_type.lower()]
        else:
            extensions = FILE_TYPES.get(file_type.lower())

    # Determine directories to search
    if directory:
        search_dirs = [directory]
    else:
        search_dirs = DEFAULT_SEARCH_DIRS

    query_lower = query.lower()

    for search_dir in search_dirs:
        if not os.path.isdir(search_dir):
            continue
        try:
            for root, dirs, files in os.walk(search_dir):
                # Skip hidden and system directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]

                for file in files:
                    if query_lower in file.lower():
                        filepath = os.path.join(root, file)
                        ext = Path(file).suffix.lower()

                        if extensions and ext not in extensions:
                            continue

                        size = os.path.getsize(filepath)
                        size_str = _format_size(size)
                        results.append(f"  [FILE] {file} ({size_str})\n     [DIR] {filepath}")

                        if len(results) >= max_results:
                            break
                if len(results) >= max_results:
                    break
        except PermissionError:
            continue

    if results:
        header = f"Found {len(results)} file(s) matching '{query}':\n"
        return header + "\n".join(results)
    else:
        return f"No files found matching '{query}' in the searched directories."


def open_file(path: str) -> str:
    """Open a file or folder with the default application."""
    try:
        path = os.path.expandvars(os.path.expanduser(path))
        if os.path.exists(path):
            os.startfile(path)
            name = os.path.basename(path)
            return f"Opened: {name}"
        else:
            return f"Path not found: {path}"
    except Exception as e:
        return f"Error opening file: {str(e)}"


def list_directory(path: str) -> str:
    """List contents of a directory."""
    try:
        path = os.path.expandvars(os.path.expanduser(path))
        if not os.path.isdir(path):
            return f"Not a directory: {path}"

        items = []
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                items.append(f"  [DIR] {item}/")
            else:
                size = _format_size(os.path.getsize(full_path))
                items.append(f"  [FILE] {item} ({size})")

        if items:
            return f"Contents of {path}:\n" + "\n".join(items[:50])
        else:
            return f"Directory is empty: {path}"
    except PermissionError:
        return f"Access denied: {path}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
