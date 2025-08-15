# utils/publisher.py
from __future__ import annotations

import os
import re
import glob
import shutil
from datetime import datetime
from typing import List

from git import Repo
from config.config_loader import load_config
from utils.logger import logger

# Jinja2 is optional; we fall back to a simple generator if the template is missing.
try:
    from jinja2 import Environment, FileSystemLoader  # type: ignore
    HAS_JINJA = True
except Exception:
    HAS_JINJA = False


# ───────────────────────────────────────────────────────────────────────────────
# Redaction
# ───────────────────────────────────────────────────────────────────────────────

# Slightly broader coverage (AWS keys, GitHub, Bearer/JWT, Stripe)
REDACT_PATTERNS = [
    r'AKIA[0-9A-Z]{16}',                              # AWS Access Key ID
    r'ASIA[0-9A-Z]{16}',                              # AWS Temp Key ID
    r'(?:ghp_|github_pat_[A-Za-z0-9_]{0,10})[A-Za-z0-9]{20,}',  # GitHub tokens
    r'sk_live_[A-Za-z0-9]{24,}',                      # Stripe live keys
    r'(?i)(?:Bearer|token)\s+[A-Za-z0-9\.\-_]{20,}',  # Bearer tokens
    r'\beyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\b',  # JWT-like
    r'(?i)secret[^a-z0-9]?["\']?[\w\d]{10,}',         # generic "secret..."
]

def redact_secrets(content: str) -> str:
    redacted = content
    for pat in REDACT_PATTERNS:
        redacted = re.sub(pat, '***REDACTED***', redacted)
    return redacted

def rewrite_html_paths(content: str) -> str:
    # Make absolute "/static/…" links relative "static/…" so GH Pages serves them
    return (content
            .replace('src="/static/', 'src="static/')
            .replace('href="/static/', 'href="static/'))


# ───────────────────────────────────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────────────────────────────────

def _human_time(path: str) -> str:
    try:
        ts = os.path.getmtime(path)
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ""

def _list_local_reports(directory: str) -> List[str]:
    """
    Return a sorted list (newest first) of report HTML files in `directory`.
    Includes both `report.html` and `report-*.html`.
    """
    pats = [os.path.join(directory, "report.html"),
            os.path.join(directory, "report-*.html")]
    files: List[str] = []
    for pat in pats:
        files.extend(glob.glob(pat))
    # de-dupe & sort by mtime desc
    files = sorted(set(files), key=lambda p: os.path.getmtime(p), reverse=True)
    return files


# ───────────────────────────────────────────────────────────────────────────────
# Local backup (unchanged behaviour)
# ───────────────────────────────────────────────────────────────────────────────

def backup_report_locally(report_path: str):
    backup_dir = os.path.join("reports")
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(backup_dir, f"report-{timestamp}.html")

    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    redacted = redact_secrets(content)
    with open(backup_path, "w", encoding="utf-8") as f:
        f.write(redacted)

    logger.info(f"📦 Report backup saved to: {backup_path}")
    return backup_path


# ───────────────────────────────────────────────────────────────────────────────
# Index generation (local or gh-pages)
# ───────────────────────────────────────────────────────────────────────────────

def _render_index_simple(directory: str, title: str = "SnapCheck Reports") -> str:
    files = _list_local_reports(directory)
    if not files:
        items = '<li><em>No reports found yet.</em></li>'
    else:
        rows = []
        for p in files:
            name = os.path.basename(p)
            ts = _human_time(p)
            rows.append(f'<li><a href="{name}">{name}</a> <small>({ts})</small></li>')
        items = "\n    ".join(rows)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 2rem; }}
  h1 {{ margin-bottom: .5rem; }}
  ul {{ line-height: 1.7; padding-left: 1.25rem; }}
  small {{ color: #666; }}
</style>
</head>
<body>
  <h1>{title}</h1>
  <ul>
    {items}
  </ul>
</body>
</html>"""


def generate_report_index(output_dir: str = ".snapcheck"):
    """
    Generate/overwrite index.html in `output_dir`, linking report.html + report-*.html.
    Uses Jinja2 template if available at output/templates/report_index.html, otherwise falls back.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)
        index_path = os.path.join(output_dir, "index.html")

        if HAS_JINJA and os.path.exists("output/templates/report_index.html"):
            env = Environment(loader=FileSystemLoader("output/templates"))
            template = env.get_template("report_index.html")

            report_files = [os.path.basename(p) for p in _list_local_reports(output_dir)]
            html = template.render(reports=report_files)  # template should iterate over 'reports'
        else:
            # Fallback simple index (no dependency on templates)
            html = _render_index_simple(output_dir)

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html)

        logger.info(f"📄 Generated index.html in {output_dir}")
    except Exception as e:
        logger.error(f"❌ Failed to generate index.html: {e}")


# ───────────────────────────────────────────────────────────────────────────────
# Publish to GitHub Pages
# ───────────────────────────────────────────────────────────────────────────────

def publish_report(profile_path: str):
    """
    Copies all .snapcheck/*.html (including index.html) into gh-pages branch
    and regenerates index there so older runs stay discoverable.
    """
    try:
        config = load_config(profile_path)

        github_repo = config.get("github_repo")
        github_token = os.environ.get("GITHUB_TOKEN")
        if not github_repo or not github_token:
            raise ValueError("Missing github_repo in config or GITHUB_TOKEN in environment")

        local_repo_path = os.getcwd()
        gh_pages_path = os.path.join(local_repo_path, "gh-pages-temp")

        # Clean temp folder
        if os.path.exists(gh_pages_path):
            shutil.rmtree(gh_pages_path)

        # Clone gh-pages branch (create if missing)
        repo_url = f"https://{github_token}@github.com/{github_repo}.git"
        repo = Repo.clone_from(repo_url, gh_pages_path)
        try:
            repo.git.checkout("gh-pages")
        except Exception:
            repo.git.checkout("-b", "gh-pages")

        # Always (re)generate local index so it gets published too
        snapcheck_dir = os.path.join(local_repo_path, ".snapcheck")
        generate_report_index(snapcheck_dir)

        # Clean any existing *.html in gh-pages to avoid stale files lingering
        for f in os.listdir(gh_pages_path):
            if f.endswith(".html"):
                try:
                    os.remove(os.path.join(gh_pages_path, f))
                except Exception:
                    pass

        # Copy & redact all .html from .snapcheck
        html_files = [f for f in os.listdir(snapcheck_dir) if f.endswith(".html")]
        if not html_files:
            raise FileNotFoundError("No HTML reports found in .snapcheck")

        for file in html_files:
            src_path = os.path.join(snapcheck_dir, file)
            with open(src_path, "r", encoding="utf-8") as f:
                content = f.read()
            redacted = rewrite_html_paths(redact_secrets(content))
            with open(os.path.join(gh_pages_path, file), "w", encoding="utf-8") as f:
                f.write(redacted)

        # Also copy JSON data so the dashboard can load module results
        json_files = [f for f in os.listdir(snapcheck_dir) if f.endswith(".json")]
        for file in json_files:
            src_path = os.path.join(snapcheck_dir, file)
            try:
                with open(src_path, "r", encoding="utf-8") as f:
                    content = f.read()
                redacted = redact_secrets(content)
                with open(os.path.join(gh_pages_path, file), "w", encoding="utf-8") as f:
                    f.write(redacted)
            except Exception:
                # if binary or unreadable, just copy raw
                shutil.copy2(src_path, os.path.join(gh_pages_path, file))

        # Copy static assets (charts/js/css) if present
        static_src = None
        for cand in ("output/static", "output/templates/static"):
            cand_path = os.path.join(local_repo_path, cand)
            if os.path.isdir(cand_path):
                static_src = cand_path
                break
        if static_src:
            dst = os.path.join(gh_pages_path, "static")
            if os.path.exists(dst):
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(static_src, dst)

        # IMPORTANT: regenerate index IN gh-pages dir to include *all* historical HTMLs there
        generate_report_index(gh_pages_path)

        # Commit and push
        to_add = [f for f in os.listdir(gh_pages_path) if f.endswith(".html")]
        repo.index.add(to_add)
        # include json + static
        json_add = [f for f in os.listdir(gh_pages_path) if f.endswith(".json")]
        if json_add:
            repo.index.add(json_add)
        if os.path.isdir(os.path.join(gh_pages_path, "static")):
            repo.git.add("static")
        repo.index.commit("📊 Publish SnapCheck report(s)")
        repo.remote().push(refspec="gh-pages:gh-pages")

        url = f"https://{github_repo.split('/')[0]}.github.io/{github_repo.split('/')[1]}/index.html"
        logger.info(f"✅ Published to GitHub Pages: {url}")

        # Backup latest locally (best-effort)
        fallback_path = os.path.join(snapcheck_dir, "report.html")
        if os.path.exists(fallback_path):
            backup_report_locally(fallback_path)

    except Exception as e:
        logger.error(f"❌ Failed to publish to GitHub Pages: {e}")
        try:
            fallback_path = os.path.join(".snapcheck", "report.html")
            if os.path.exists(fallback_path):
                backup_report_locally(fallback_path)
        except Exception as be:
            logger.error(f"❌ Even backup failed: {be}")
