"""Filesystem and input validation safeguards."""
import os
import re
from pathlib import Path
from backend.core.errors import PathTraversalError, SecurityException
from backend.core.config import BASE_DIR

ALLOWED_BASE_DIRS = [
    BASE_DIR.resolve(),
    Path.cwd().resolve(),
    Path("/home/jmari/proyectosIA").resolve(),
    Path("/home/jmari/siam_worktrees").resolve(),
    Path("/tmp").resolve(),
]

def validate_safe_path(target_path: str | Path, base_dirs: list[Path] | None = None) -> Path:
    """
    Validates that a path does not escape allowed directories (path traversal protection).
    Resolves symlinks and normalizes relative components.
    """
    resolved = Path(target_path).resolve()
    bases = base_dirs or ALLOWED_BASE_DIRS
    
    is_allowed = any(
        resolved == base or base in resolved.parents
        for base in bases
    )
    if not is_allowed:
        raise PathTraversalError(
            f"Access denied: path '{resolved}' is outside permitted project directories.",
            {"attempted_path": str(target_path)}
        )
    return resolved

def sanitize_identifier(name: str) -> str:
    """Ensure identifier has no path traversal, control chars, or shell injection tokens."""
    if not re.match(r"^[a-zA-Z0-9_\-\. ]+$", name):
        raise SecurityException(f"Invalid identifier characters in '{name}'")
    return name.strip()
