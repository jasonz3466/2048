"""Load and save the best score and motion preferences"""

import json
import os
from pathlib import Path
import sys


def data_path():
    """Reuse the previous version's save location and preference keys"""
    if os.environ.get("GAME2048_DATA_DIR"):
        return Path(os.environ["GAME2048_DATA_DIR"]) / "settings.json"
    if sys.platform == "win32":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData/Local"))
    elif sys.platform == "darwin":
        root = Path.home() / "Library/Application Support"
    else:
        root = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))

    return root / "Polished2048/settings.json"


def load(path):
    """Load the best score and motion preferences from a JSON file"""

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        best, quiet = data.get("best", 0), data.get("reduced_motion", False)
        return {
            "best": best if type(best) is int and best >= 0 else 0,
            "reduced_motion": quiet if type(quiet) is bool else False,
        }
    except (OSError, ValueError, AttributeError):
        return {"best": 0, "reduced_motion": False}


def save(path, preferences):
    """Save the best score and motion preferences to a JSON file"""

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        temporary.write_text(json.dumps(preferences, indent=2), encoding="utf-8")
        temporary.replace(path)
        return True

    except OSError:
        return False
