"""Small shared helpers for the Script Runner."""

import re


def safe_name(name: str) -> str:
    """Replace characters that are unsafe in file and directory names."""
    name = re.sub(r'[<>:"/\\\\|?*]', "_", name.strip())
    return name.strip(" .")
