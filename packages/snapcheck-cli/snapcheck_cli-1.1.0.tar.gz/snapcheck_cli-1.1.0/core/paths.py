from __future__ import annotations
import os
import json
from typing import Any, Optional

# Single source of truth for the outdir.
# Default: ./.snapcheck (repo-local)
# Override: export SNAPCHECK_OUTDIR=/some/path
OUTDIR = os.path.abspath(os.getenv("SNAPCHECK_OUTDIR", ".snapcheck"))

def ensure_outdir(path: Optional[str] = None) -> str:
    """Ensure the output directory exists; return absolute path."""
    d = os.path.abspath(path or OUTDIR)
    os.makedirs(d, exist_ok=True)
    return d

def outpath(*parts: str, base: Optional[str] = None) -> str:
    """
    Join OUTDIR with provided parts.
    Example: outpath('ci_cd.json') -> /abs/repo/.snapcheck/ci_cd.json
    """
    d = ensure_outdir(base)
    return os.path.join(d, *parts)

def write_json(obj: Any, filename: str, base: Optional[str] = None) -> str:
    """
    Write JSON to OUTDIR/filename with pretty indent; return full path.
    """
    path = outpath(filename, base=base)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    return path

def describe_outdir() -> str:
    """A short string for startup banners/logs."""
    return f"[SnapCheck] Output directory: {ensure_outdir()}"
