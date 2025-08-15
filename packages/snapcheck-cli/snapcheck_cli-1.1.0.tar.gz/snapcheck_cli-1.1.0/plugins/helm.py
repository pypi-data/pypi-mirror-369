# plugins/helm.py
from __future__ import annotations
import subprocess
import shlex
import json
from typing import Any, Dict, List, Optional, Tuple

from utils.reporter import AuditResult, Severity
from core.paths import OUTDIR, ensure_outdir, write_json

def _run(cmd: str, timeout: int = 25) -> subprocess.CompletedProcess:
    return subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=timeout)

def _helm_json(args: str, timeout: int = 25) -> Optional[Any]:
    """Run a helm command that prints JSON and parse it."""
    cp = _run(f"helm {args}", timeout=timeout)
    if cp.returncode != 0:
        return None
    try:
        return json.loads(cp.stdout or "null")
    except Exception:
        return None

def _helm_version_short() -> str:
    cp = _run("helm version --short")
    return cp.stdout.strip() if cp.returncode == 0 else "unknown"

def _parse_chart_field(chart_field: str) -> Tuple[str, str]:
    """
    helm ls returns chart like 'metrics-server-3.12.2' or 'my-chart-1.0.0'.
    Split once from the right to get (name, version). If ambiguous, version = ''.
    """
    if "-" not in chart_field:
        return chart_field, ""
    name, ver = chart_field.rsplit("-", 1)
    return name, ver

def _semver_tuple(v: str) -> Tuple[int, ...]:
    parts: List[int] = []
    for p in v.split("."):
        try:
            parts.append(int(p))
        except Exception:
            digits = "".join(ch for ch in p if ch.isdigit())
            parts.append(int(digits) if digits.isdigit() else 0)
    return tuple(parts)

def _latest_chart_version(chart_name: str) -> Optional[str]:
    """
    Best-effort: search known repos for the chart and return the highest version.
    """
    rows = _helm_json(f"search repo {shlex.quote(chart_name)} -o json")
    if not rows:
        return None
    # prefer exact name matches first
    candidates = [r.get("version") for r in rows
                  if isinstance(r, dict) and r.get("name", "").split("/")[-1] == chart_name]
    if not candidates:
        candidates = [r.get("version") for r in rows if isinstance(r, dict) and r.get("version")]
    candidates = [c for c in candidates if isinstance(c, str)]
    if not candidates:
        return None
    return max(candidates, key=_semver_tuple)

def _list_releases_all() -> List[Dict[str, Any]]:
    """List Helm releases across all namespaces."""
    releases = _helm_json("ls -A -o json") or []
    if not isinstance(releases, list):
        return []
    return releases

def _compare_values_vs_live(name: str, ns: str) -> bool:
    """
    Optional drift check for values.yaml (kept from your original logic).
    Compares live values to repo file helm/<name>/values.yaml if present.
    """
    try:
        cp = _run(f"helm get values {shlex.quote(name)} -n {shlex.quote(ns)} -o json")
        if cp.returncode != 0:
            return False
        live = json.loads(cp.stdout or "{}")
        path = f"helm/{name}/values.yaml"
        if not _file_exists(path):
            return False
        # Cheap compare via re-render to JSON using yq not required; we just compare strings to avoid deps.
        # Since we fetched JSON from helm, stringify both sides minimally.
        repo_text = _read_text(path)
        return (json.dumps(live, sort_keys=True) != json.dumps({"_raw": repo_text.strip()}, sort_keys=True))
    except Exception:
        return False

def _file_exists(p: str) -> bool:
    try:
        import os
        return os.path.exists(p)
    except Exception:
        return False

def _read_text(p: str) -> str:
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def _summarize_releases(helm_namespaces: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Build a summary with per-release details and outdated status.
    """
    ensure_outdir()
    ver = _helm_version_short()
    # Refresh repos to make latest version comparisons meaningful (best-effort).
    _run("helm repo update")

    all_releases = _list_releases_all()
    # Optional filter to a subset of namespaces for the overview, but we still list -A.
    if helm_namespaces:
        releases = [r for r in all_releases if r.get("namespace") in helm_namespaces]
    else:
        releases = all_releases

    per_release_msgs: List[str] = []
    outdated_count = 0
    failed_count = 0
    drifted: List[str] = []

    for rel in releases:
        name = rel.get("name", "")
        ns = rel.get("namespace", "")
        status = (rel.get("status") or "").lower()
        chart_field = rel.get("chart") or ""
        app_ver = rel.get("app_version") or ""

        chart_name, chart_ver = _parse_chart_field(chart_field)
        latest: Optional[str] = None
        is_outdated = False

        if chart_name and chart_ver:
            latest = _latest_chart_version(chart_name)
            if latest:
                try:
                    is_outdated = _semver_tuple(latest) > _semver_tuple(chart_ver)
                except Exception:
                    is_outdated = False

        if status in ("failed", "pending-install", "pending-upgrade", "unknown"):
            failed_count += 1

        # Values drift (best-effort; non-fatal)
        try:
            if _compare_values_vs_live(name, ns):
                drifted.append(f"{ns}/{name}")
        except Exception:
            pass

        msg = f"{ns}/{name}: chart {chart_name} version {chart_ver} (status {status or 'unknown'})"
        if latest:
            if is_outdated:
                msg += f" → latest {latest} (OUTDATED)"
                outdated_count += 1
            else:
                msg += f" → latest {latest} (up-to-date)"
        else:
            msg += " → latest unknown"

        if app_ver:
            msg += f"; appVersion {app_ver}"

        per_release_msgs.append(msg)

    total = len(releases)
    parts = [f"{total} releases"]
    if failed_count:
        parts.append(f"{failed_count} unhealthy")
    if outdated_count:
        parts.append(f"{outdated_count} outdated")
    summary_line = f"{', '.join(parts)} (Helm {ver})"

    # Severity policy:
    # - Any failed → HIGH
    # - Else any outdated → MEDIUM
    # - Else OK
    if failed_count:
        sev = Severity.HIGH
    elif outdated_count:
        sev = Severity.MEDIUM
    else:
        sev = Severity.OK

    # Add drift note at the end (doesn't change severity by itself)
    if drifted:
        per_release_msgs.append(f"values.yaml drift detected for: {', '.join(drifted)}")

    payload = {
        "helm_version": ver,
        "releases": releases,
        "messages": [summary_line] + per_release_msgs,
        "outdated_count": outdated_count,
        "failed_count": failed_count,
        "total": total,
        "status": sev.name,
    }
    return payload

def run_check(config: Dict[str, Any]):
    """
    Returns a single AuditResult (keeps your original interface),
    and writes OUTDIR/helm.json for correlator & debugging.
    """
    # Sanity: ensure Helm exists
    hv = _helm_version_short()
    if hv == "unknown":
        return AuditResult(
            title="Helm Audit",
            status=Severity.CRITICAL,
            messages=["❌ Helm not installed or not in PATH."]
        )

    helm_namespaces = config.get("helm_namespaces")  # optional filter
    payload = _summarize_releases(helm_namespaces=helm_namespaces)

    ensure_outdir()
    write_json({
        "module": "helm",
        "outdir": OUTDIR,
        "helm_version": payload["helm_version"],
        "status": payload["status"],
        "releases": payload["releases"],
        "messages": payload["messages"],
        "outdated_count": payload["outdated_count"],
        "failed_count": payload["failed_count"],
        "total": payload["total"],
    }, "helm.json")

    # Compose a single AuditResult with a concise summary + a few details.
    # (Your runner likely wraps this into a list downstream.)
    messages = payload["messages"]
    summary = messages[0]
    details = messages[1:101]  # cap to avoid noisy terminals

    return AuditResult(
        title="Helm Audit",
        status=Severity[payload["status"]],
        messages=[summary] + details
    )


