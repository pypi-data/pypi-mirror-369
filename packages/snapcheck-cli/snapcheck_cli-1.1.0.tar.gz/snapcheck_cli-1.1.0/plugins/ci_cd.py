# plugins/ci_cd.py
from __future__ import annotations

import os
import datetime
import statistics
from collections import defaultdict
from typing import Any, Dict, Optional, Tuple, List

import requests

from utils.reporter import AuditResult, Severity
from core.paths import write_json, ensure_outdir, OUTDIR
from config import resolve_ci_settings  # unified accessors (ENV > ci_cd.* > top-level)

GITHUB_API = "https://api.github.com"


# ──────────────────────────────────────────────────────────────────────────────
# HTTP helpers
# ──────────────────────────────────────────────────────────────────────────────
def _headers(token: Optional[str]) -> Dict[str, str]:
    """Build GitHub headers; token optional (public API works with limits)."""
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def _get(url: str, headers: Dict[str, str]) -> Dict[str, Any]:
    """GET JSON with a short error message if non-2xx."""
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code >= 400:
        # keep message compact to avoid noisy logs
        snippet = (r.text or "")[:200]
        raise RuntimeError(f"GET {url} -> {r.status_code}: {snippet}")
    try:
        return r.json() if r.text else {}
    except Exception:
        return {}


# ──────────────────────────────────────────────────────────────────────────────
# GitHub API wrappers
# ──────────────────────────────────────────────────────────────────────────────
def get_recent_workflow_runs(repo: str, headers: Dict[str, str], limit: int = 10) -> List[Dict[str, Any]]:
    data = _get(f"{GITHUB_API}/repos/{repo}/actions/runs?per_page={limit}", headers)
    runs = data.get("workflow_runs") or []
    return runs[:limit]


def get_jobs_for_run(repo: str, run_id: int, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    data = _get(f"{GITHUB_API}/repos/{repo}/actions/runs/{run_id}/jobs", headers)
    return data.get("jobs") or []


def get_artifacts(repo: str, headers: Dict[str, str]) -> List[Dict[str, Any]]:
    data = _get(f"{GITHUB_API}/repos/{repo}/actions/artifacts?per_page=100", headers)
    return data.get("artifacts") or []


def get_branch_protection(repo: str, headers: Dict[str, str], branch: str = "main") -> bool:
    """Return True if branch protection is enabled for `branch` (False if 404)."""
    url = f"{GITHUB_API}/repos/{repo}/branches/{branch}/protection"
    r = requests.get(url, headers=headers, timeout=20)
    if r.status_code == 200:
        return True
    if r.status_code == 404:
        return False
    raise RuntimeError(f"branch protection check failed: {r.status_code} {(r.text or '')[:120]}")


# ──────────────────────────────────────────────────────────────────────────────
# Analysis
# ──────────────────────────────────────────────────────────────────────────────
def analyze_runs(repo: str, runs: List[Dict[str, Any]], headers: Dict[str, str]) -> Dict[str, Any]:
    total_duration = 0.0
    longest_job = {"name": "", "duration": 0.0}
    contributors = defaultdict(int)
    flaky_runs = 0
    failed_runs = 0
    artifact_sizes: List[float] = []
    commit_latencies: List[float] = []
    artifact_trend: List[Tuple[str, float]] = []
    bot_triggers = 0

    for run in runs:
        # durations
        created_at = datetime.datetime.fromisoformat(run["created_at"].replace("Z", "+00:00"))
        updated_at = datetime.datetime.fromisoformat(run["updated_at"].replace("Z", "+00:00"))
        duration = (updated_at - created_at).total_seconds() / 60.0
        total_duration += duration

        conclusion = (run.get("conclusion") or "").lower()
        if conclusion == "failure":
            failed_runs += 1
        if duration > 30.0:
            flaky_runs += 1

        actor = (run.get("triggering_actor") or {}).get("login") or "unknown"
        contributors[actor] += 1
        if "bot" in actor.lower():
            bot_triggers += 1

        # longest job
        try:
            for job in get_jobs_for_run(repo, run["id"], headers):
                s = job.get("started_at")
                c = job.get("completed_at")
                if s and c:
                    sdt = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
                    cdt = datetime.datetime.fromisoformat(c.replace("Z", "+00:00"))
                    jd = (cdt - sdt).total_seconds() / 60.0
                    if jd > (longest_job["duration"] or 0):
                        longest_job = {"name": job.get("name") or "", "duration": round(jd, 2)}
        except Exception:
            pass

        # coarse latency; best-effort
        rs = run.get("run_started_at")
        if rs:
            t = datetime.datetime.fromisoformat(rs.replace("Z", "+00:00"))
            commit_latencies.append((updated_at - t).total_seconds() / 60.0)

    # artifacts
    try:
        for a in get_artifacts(repo, headers):
            size_mb = round((a.get("size_in_bytes", 0) or 0) / 1024.0 / 1024.0, 2)
            artifact_sizes.append(size_mb)
            if a.get("created_at"):
                artifact_trend.append((a["created_at"], size_mb))
    except Exception:
        pass

    avg_duration = round(total_duration / len(runs), 1) if runs else 0.0
    avg_latency = round(sum(commit_latencies) / len(commit_latencies), 1) if commit_latencies else 0.0
    artifact_stats = (
        f"{len(artifact_sizes)} artifacts, avg size: {round(statistics.mean(artifact_sizes), 2)} MB"
        if artifact_sizes else "No artifacts"
    )

    return {
        "total_runs": len(runs),
        "failed_runs": failed_runs,
        "longest_job": longest_job,
        "avg_duration_min": avg_duration,
        "avg_latency_min": avg_latency,
        "contributors": dict(contributors),
        "flaky_runs": flaky_runs,
        "artifact_summary": artifact_stats,
        "artifact_trend": artifact_trend,
        "bot_triggered_jobs": bot_triggers,
    }


def _severity_from_metrics(m: Dict[str, Any]) -> Severity:
    if (m.get("failed_runs") or 0) > 0:
        return Severity.CRITICAL
    if (m.get("flaky_runs") or 0) > 0:
        return Severity.MEDIUM
    return Severity.OK


# ──────────────────────────────────────────────────────────────────────────────
# Entry point
# ──────────────────────────────────────────────────────────────────────────────
def run_check(config: Dict[str, Any]) -> AuditResult:
    """
    Returns an AuditResult for CLI/table AND writes a rich .snapcheck/ci_cd.json
    that the HTML dashboard & correlator can read.
    """
    ensure_outdir()

    # Unified config: ENV > ci_cd.* > top-level (handled by your accessor)
    ci = resolve_ci_settings(config)
    platform = (ci.get("platform") or "github").lower()
    repo: Optional[str] = ci.get("repo")
    token: Optional[str] = ci.get("token")

    # No repo configured: persist a clear "Skipped" JSON and return LOW severity.
    if not repo:
        payload = {
            "module": "ci_cd",
            "title": "CI/CD",
            "platform": platform,
            "repo": repo,
            "timestamp": int(datetime.datetime.utcnow().timestamp()),
            "status": "Skipped",
            "errors": ["Missing repository (set ci_cd.repo or github_repo or SNAPCHECK_GITHUB_REPO)"],
            "summary": "Repo not configured",
            "metrics": {},
            "outdir": OUTDIR,
            "schema_version": 1,
        }
        write_json(payload, "ci_cd.json")
        return AuditResult(
            title="CI/CD",
            status=Severity.LOW,
            messages=["❌ GitHub repo missing in config"]
        )

    try:
        headers = _headers(token)
        runs = get_recent_workflow_runs(repo, headers, limit=10)
        metrics = analyze_runs(repo, runs, headers)

        # Branch protection: only try if we have a token (avoids noisy 401s)
        bp = False
        if token:
            try:
                bp = get_branch_protection(repo, headers)
            except Exception:
                bp = False

        # Normalize & enrich metrics
        failed = int(metrics.get("failed_runs") or 0)
        flaky = int(metrics.get("flaky_runs") or 0)
        avg = metrics.get("avg_duration_min") or 0
        longest_name = (metrics.get("longest_job") or {}).get("name") or "—"
        bots = int(metrics.get("bot_triggered_jobs") or 0)

        metrics["branch_protection"] = bool(bp)
        metrics["repo"] = repo
        metrics["platform"] = platform

        summary = (
            f"{failed} failures, {flaky} flaky, "
            f"{avg}m avg, longest: {longest_name}, "
            f"{bots} bot jobs, branch protection: {'✅' if bp else '❌'}"
        )

        payload = {
            "module": "ci_cd",
            "title": "CI/CD",
            "platform": platform,
            "repo": repo,
            "timestamp": int(datetime.datetime.utcnow().timestamp()),
            "status": "OK" if failed == 0 else "Failure",
            "errors": [],
            "summary": summary,
            "metrics": metrics,
            "outdir": OUTDIR,
            "schema_version": 1,
        }
        write_json(payload, "ci_cd.json")
        shas = sorted({ (r.get("head_sha") or "")[:7] for r in runs if r.get("head_sha") })
        extra = [f"CI commits: {' '.join([s for s in shas if s][:5])}"] if shas else []

        return AuditResult(
            title="CI/CD",
            status=_severity_from_metrics(metrics),
            messages=[summary]+ extra
        )

    except Exception as e:
        payload = {
            "module": "ci_cd",
            "title": "CI/CD",
            "platform": platform,
            "repo": repo,
            "timestamp": int(datetime.datetime.utcnow().timestamp()),
            "status": "Failure",
            "errors": [str(e)],
            "summary": "GitHub API error",
            "metrics": {},
            "outdir": OUTDIR,
            "schema_version": 1,
        }
        write_json(payload, "ci_cd.json")
        return AuditResult(
            title="CI/CD",
            status=Severity.CRITICAL,
            messages=[f"❌ GitHub API Error: {e}"]
        )

