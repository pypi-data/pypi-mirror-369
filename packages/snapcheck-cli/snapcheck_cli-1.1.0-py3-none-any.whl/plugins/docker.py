# plugins/docker.py
from __future__ import annotations
import os
import json
import time
import requests
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from utils.reporter import AuditResult, Severity
from core.paths import OUTDIR, ensure_outdir, write_json
from config import get_config_value  # from config/accessors.py

DOCKERHUB_BASE = "https://hub.docker.com/v2/repositories"

# ───────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ───────────────────────────────────────────────────────────────────────────────

def _http_get(url: str, timeout: int = 15) -> Tuple[int, Any, Dict[str, str]]:
    try:
        r = requests.get(url, timeout=timeout)
        ct = r.headers.get("content-type", "")
        body = r.json() if "application/json" in ct else r.text
        return r.status_code, body, dict(r.headers)
    except Exception as e:
        return 599, {"error": str(e)}, {}

def _parse_iso(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None

# ───────────────────────────────────────────────────────────────────────────────
# Docker Hub queries
# ───────────────────────────────────────────────────────────────────────────────

def _list_tags_paged(repo: str, page_size: int = 100, max_pages: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch tags for a repo with pagination.
    Returns a list of tag dicts from Docker Hub (may be large).
    """
    tags: List[Dict[str, Any]] = []
    url = f"{DOCKERHUB_BASE}/{repo}/tags?page_size={page_size}"
    pages = 0
    while url and pages < max_pages:
        code, data, _ = _http_get(url)
        if code != 200 or not isinstance(data, dict):
            break
        results = data.get("results") or []
        if not isinstance(results, list):
            break
        tags.extend(results)
        url = data.get("next")
        pages += 1
    return tags

def _get_tag(repo: str, tag: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Get a specific tag payload or (None, 'not_found'|'error text').
    """
    code, data, _ = _http_get(f"{DOCKERHUB_BASE}/{repo}/tags/{tag}")
    if code == 200 and isinstance(data, dict):
        return data, None
    if code == 404:
        return None, "not_found"
    return None, f"http {code}: {data if isinstance(data, str) else data.get('error') or data}"

# ───────────────────────────────────────────────────────────────────────────────
# CVE simulation (MVP honesty)
# ───────────────────────────────────────────────────────────────────────────────

def _simulate_cves(repo: str, tag: str) -> Dict[str, Any]:
    # deterministic-ish so runs are stable
    h = sum(bytearray(f"{repo}:{tag}", "utf-8")) % 7
    buckets = [
        {"critical": 0, "high": 0, "medium": 1, "low": 2},
        {"critical": 0, "high": 1, "medium": 3, "low": 5},
        {"critical": 1, "high": 2, "medium": 5, "low": 8},
        {"critical": 0, "high": 0, "medium": 0, "low": 0},
        {"critical": 0, "high": 2, "medium": 4, "low": 6},
        {"critical": 2, "high": 4, "medium": 8, "low": 12},
        {"critical": 1, "high": 0, "medium": 2, "low": 3},
    ]
    return {"simulated": True, "note": "CVEs are simulated for MVP", **buckets[h]}

# ───────────────────────────────────────────────────────────────────────────────
# Config collection
# ───────────────────────────────────────────────────────────────────────────────

def _collect_images_from_config(cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Accept either schema:
      docker:
        images:
          - { name: org/repo, tags: [t1, t2] }
        scan_mode: explicit|top|all
        top_n: 5
      docker_images:
        - { name: org/repo, tags: [t1, t2] }
    """
    images = get_config_value(cfg, ("docker", "images"), ("docker_images",), fallback=[])
    if not isinstance(images, list):
        images = []
    # Normalize
    norm: List[Dict[str, Any]] = []
    for item in images:
        if not isinstance(item, dict):
            continue
        name = item.get("name") or item.get("image") or item.get("repo")
        tags = item.get("tags")
        norm.append({"name": name, "tags": tags if isinstance(tags, list) else None})
    # Global defaults
    scan_mode = (get_config_value(cfg, ("docker", "scan_mode"), ("docker_scan_mode",), fallback="explicit") or "explicit").lower()
    top_n = int(get_config_value(cfg, ("docker", "top_n"), ("docker_top_n",), fallback=5) or 5)
    return [{"name": e["name"], "tags": e["tags"], "scan_mode": scan_mode, "top_n": top_n} for e in norm if e["name"]]

# ───────────────────────────────────────────────────────────────────────────────
# Core logic
# ───────────────────────────────────────────────────────────────────────────────

def _choose_tags_for_repo(repo: str, entry: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    """
    Decide which tags to scan for a repo entry.
    Returns (tags_to_scan, warnings).
    """
    warnings: List[str] = []
    tags_cfg = entry.get("tags")
    scan_mode = entry.get("scan_mode", "explicit")
    top_n = int(entry.get("top_n", 5) or 5)

    if tags_cfg and scan_mode == "explicit":
        return [str(t) for t in tags_cfg], warnings

    # Need to list tags to choose top/all
    all_tags = _list_tags_paged(repo, page_size=100, max_pages=50)
    if not all_tags:
        warnings.append(f"{repo}: no tags found or API error")
        return [], warnings

    # sort by last_updated desc; fallback to name
    def sort_key(t):
        dt = _parse_iso(t.get("last_updated") or "")
        return (dt or datetime.min, t.get("name", ""))
    all_tags_sorted = sorted(all_tags, key=sort_key, reverse=True)

    if scan_mode == "top":
        chosen = [t.get("name") for t in all_tags_sorted[:top_n]]
    else:  # scan_mode == "all"
        chosen = [t.get("name") for t in all_tags_sorted]

    return [c for c in chosen if isinstance(c, str)], warnings

def _size_mb_from_tag_payload(tag_payload: Dict[str, Any]) -> Optional[float]:
    imgs = tag_payload.get("images") or []
    sizes = []
    for img in imgs:
        try:
            sizes.append(float(img.get("size", 0)) / (1024 * 1024))
        except Exception:
            pass
    if sizes:
        return round(max(sizes), 2)
    # Fallback to top-level full_size if present
    try:
        fs = tag_payload.get("full_size")
        if isinstance(fs, (int, float)):
            return round(float(fs) / (1024 * 1024), 2)
    except Exception:
        pass
    return None

def run_check(config: Dict[str, Any]) -> AuditResult:
    """
    Scan multiple repos with explicit/top/all tag selection.
    Writes .snapcheck/docker.json with full details.
    """
    ensure_outdir()
    entries = _collect_images_from_config(config)

    if not entries:
        payload = {
            "module": "docker",
            "outdir": OUTDIR,
            "timestamp": int(time.time()),
            "images": [],
            "messages": ["No docker images configured. Add docker.images or docker_images in profile."],
        }
        write_json(payload, "docker.json")
        return AuditResult("Docker Audit", Severity.OK, payload["messages"])

    results: List[Dict[str, Any]] = []
    messages: List[str] = []
    errors_overall: List[str] = []
    not_found: List[str] = []

    for entry in entries:
        repo = entry["name"]
        tags_to_scan, warns = _choose_tags_for_repo(repo, entry)
        for w in warns:
            messages.append(f"ℹ️ {w}")

        # If explicit mode but no tags provided, default to top 5 for that repo
        if not tags_to_scan and (entry.get("scan_mode") == "explicit"):
            tags_to_scan, _ = _choose_tags_for_repo(repo, {**entry, "scan_mode": "top", "top_n": entry.get("top_n", 5)})

        # Iterate chosen tags
        for tag in tags_to_scan:
            payload, err = _get_tag(repo, tag)
            rec: Dict[str, Any] = {
                "repo": repo,
                "tag": tag,
                "found": payload is not None,
                "size_mb": _size_mb_from_tag_payload(payload) if payload else None,
                "last_updated": payload.get("last_updated") if payload else None,
                "errors": [],
                "vulnerabilities": _simulate_cves(repo, tag),
            }

            if err == "not_found":
                not_found.append(f"{repo}:{tag}")
                rec["errors"].append("tag not found")
                messages.append(f"{repo}:{tag} (tag not found)")
            elif err:
                errors_overall.append(f"{repo}:{tag} → {err}")
                rec["errors"].append(err)
                messages.append(f"{repo}:{tag} (error: {err})")
            else:
                size_str = f"{rec['size_mb']} MB" if rec["size_mb"] is not None else "size unknown"
                v = rec["vulnerabilities"]
                messages.append(
                    f"{repo}:{tag} → {size_str}; CVEs (SIMULATED) C:{v['critical']} H:{v['high']} M:{v['medium']} L:{v['low']}"
                )

            results.append(rec)

    # Severity policy (soft because CVEs are simulated):
    sev = Severity.OK
    if errors_overall:
        sev = Severity.MEDIUM
    elif not_found:
        sev = Severity.LOW

    header = f"{len(results)} image-tags checked across {len(entries)} repo(s); {len(not_found)} not found; {len(errors_overall)} errors"

    payload = {
        "module": "docker",
        "outdir": OUTDIR,
        "timestamp": int(time.time()),
        "images": results,
        "messages": [header] + messages,
        "errors": errors_overall,
        "not_found": not_found,
        "note": "CVEs are simulated for MVP; replace with a real scanner later.",
    }
    write_json(payload, "docker.json")

    return AuditResult("Docker Audit", sev, payload["messages"][:120])

