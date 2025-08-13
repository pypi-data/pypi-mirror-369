import os
import platform
import logging

logger = logging.getLogger(__name__)

def get_cursor_paths():
    """Get Cursor storage paths based on the operating system."""
    system = platform.system()
    home = os.path.expanduser("~")
    
    if system == "Windows":
        cursor_dir = os.path.join(home, "AppData", "Roaming", "Cursor", "User", "globalStorage")
    elif system == "Darwin":  # macOS
        cursor_dir = os.path.join(home, "Library", "Application Support", "Cursor", "User", "globalStorage")
    elif system == "Linux":
        cursor_dir = os.path.join(home, ".config", "Cursor", "User", "globalStorage")
    else:
        logger.error(f"Unsupported operating system: {system}")
        return None
    
    paths = {
        'storage_path': os.path.join(cursor_dir, "storage.json"),
        'sqlite_path': os.path.join(cursor_dir, "state.vscdb"),
    }
    
    # Check if at least one of the paths exists
    storage_exists = os.path.exists(paths['storage_path'])
    sqlite_exists = os.path.exists(paths['sqlite_path'])
    
    if storage_exists or sqlite_exists:
        logger.debug("Found Cursor data at standard location")
        return paths
    else:
        logger.error("Cursor data not found at standard location")
        logger.error("Please ensure Cursor is installed and you're logged in")
        return None
