# core/correlator.py

import os
import json
import requests
import datetime
import socket
import ssl
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
import glob
import re

# boto3 is optional; we degrade gracefully when unavailable
try:
    import boto3
    from botocore.exceptions import ClientError
    HAS_BOTO3 = True
except Exception:
    HAS_BOTO3 = False

from utils.reporter import AuditResult, Severity
from core.paths import OUTDIR, ensure_outdir, outpath, write_json

HEX7PLUS = re.compile(r"^[0-9a-f]{7,40}$", re.IGNORECASE)

# -------------------------------------------------------------------
# Helpers (JSON IO + Terraform state discovery/download)
# -------------------------------------------------------------------

def _read_json(p):
    try:
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def _iter_dicts(data):
    if isinstance(data, dict):
        yield data
    elif isinstance(data, list):
        for x in data:
            if isinstance(x, dict):
                yield x

def _discover_tfstate_path():
    p = outpath("terraform.tfstate")
    if os.path.exists(p):
        return p
    cands = sorted(glob.glob(outpath("*.tfstate")), key=os.path.getmtime, reverse=True)
    if cands:
        return cands[0]
    tj = _read_json(outpath("terraform.json")) or {}
    for k in ("tfstate_path", "terraform_state", "state_path"):
        if isinstance(tj.get(k), str) and tj[k]:
            return tj[k]
    s3h = tj.get("state_s3") or tj.get("s3_backend") or {}
    if isinstance(s3h, dict) and s3h.get("bucket") and s3h.get("key"):
        return f"s3://{s3h['bucket']}/{s3h['key']}"
    envp = os.environ.get("SNAPCHECK_TFSTATE")
    if envp:
        return envp
    return None

def _download_tfstate_if_needed(src, aws_region="us-east-2"):
    ensure_outdir()
    dst = outpath("terraform.tfstate")
    if isinstance(src, str) and (src.startswith("http://") or src.startswith("https://")):
        try:
            r = requests.get(src, timeout=15)
            r.raise_for_status()
            with open(dst, "w", encoding="utf-8") as f:
                f.write(r.text)
            return dst
        except Exception:
            return None
    if isinstance(src, str) and src.startswith("s3://"):
        if not HAS_BOTO3:
            return None
        try:
            _, _, rest = src.partition("s3://")
            bucket, _, key = rest.partition("/")
            s3 = boto3.client("s3", region_name=aws_region)  # type: ignore
            obj = s3.get_object(Bucket=bucket, Key=key)
            content = obj["Body"].read().decode("utf-8")
            with open(dst, "w", encoding="utf-8") as f:
                f.write(content)
            return dst
        except Exception:
            return None
    return src if (isinstance(src, str) and os.path.exists(src)) else None

# -------------------------------------------------------------------
# Main correlation entrypoint
# -------------------------------------------------------------------

def correlate(results):
    ensure_outdir()
    additional = []

    # --- Core Correlation ---
    core_result = correlate_root_cause(results)
    additional.append(core_result)

    # --- Infra Drift (auto-discover tfstate / tolerate missing creds) ---
    drift = detect_infra_drift(None)
    if drift:
        additional.append(drift)

    # --- Change Velocity ---
    change = summarize_change_velocity(results)
    if change:
        additional.append(change)

    # --- Snapshot Diff ---
    snapshot = detect_snapshot_drift()
    if snapshot:
        additional.append(snapshot)

    # --- Ownership Tags ---
    ownership = detect_ownership(results)
    if ownership:
        additional.append(ownership)

    # --- Incident Integration ---
    incidents = correlate_incidents()
    if incidents:
        additional.append(incidents)

    # --- Prometheus Rule Gaps ---
    alert_gap = analyze_alert_rules()
    if alert_gap:
        additional.append(alert_gap)

    # --- Endpoint Uptime (disabled by default to avoid noise) ---
    uptime = check_endpoints()
    if uptime:
        additional.append(uptime)

    # --- Test Coverage ---
    coverage = summarize_test_coverage()
    if coverage:
        additional.append(coverage)

    # --- Cost Spike Anomaly ---
    cost_spike = detect_cost_spikes()
    if cost_spike:
        additional.append(cost_spike)

    return additional

# -------------------------------------------------------------------
# Disk JSON loaders to enable correlation even if memory types differ
# -------------------------------------------------------------------

def _extract_sha_from_messages(msgs):
    """Try to pull a commit/revision SHA from free-form message strings."""
    if not isinstance(msgs, list):
        return None
    # Prefer explicit "Revision:" style
    for m in msgs:
        if not isinstance(m, str):
            continue
        mlow = m.lower()
        if "revision" in mlow or "commit" in mlow or "sha" in mlow:
            for tok in m.replace(":", " ").split():
                if HEX7PLUS.match(tok):
                    return tok[:7]
    # Fallback: any hex-ish token
    for m in msgs:
        if not isinstance(m, str):
            continue
        for tok in m.replace(":", " ").split():
            if HEX7PLUS.match(tok):
                return tok[:7]
    return None

def _load_latest_gitops():
    files = sorted(glob.glob(outpath("gitops*.json")), key=os.path.getmtime, reverse=True)
    for p in files:
        data = _read_json(p)
        if data is None:
            continue
        for item in _iter_dicts(data):
            rev = (item.get("revision") or item.get("targetRevision") or item.get("git_revision") or "").strip()
            app = (item.get("app") or item.get("application") or item.get("app_name") or "").strip()
            title = (item.get("title") or "")
            if not app and "App:" in title:
                app = title.split("App:")[-1].strip()
            # try parse from messages when keys aren't present
            if not rev:
                rev = _extract_sha_from_messages(item.get("messages", [])) or ""
            if not app:
                for m in item.get("messages", []) or []:
                    if isinstance(m, str) and "App:" in m:
                        app = m.split("App:")[-1].strip().split()[0]
                        break
            if rev:
                return {"revision": rev, "app": app or "unknown", "file": p}
    return None

def _load_docker_tags():
    data = _read_json(outpath("docker.json")) or {}
    images = data.get("images") if isinstance(data, dict) else data
    out = []
    if isinstance(images, list):
        for img in images:
            if isinstance(img, dict):
                repo = img.get("repo"); tag = img.get("tag")
                if repo and tag:
                    out.append({"repo": str(repo), "tag": str(tag)})
    return out

def _match_by_prefix(rev, tag):
    rev = (rev or "").strip()
    tag = (tag or "").strip()
    if not rev or not tag:
        return False
    if rev.startswith(tag) or tag.startswith(rev[:7]):
        return True
    for n in range(7, 13):
        if len(rev) >= n and tag.startswith(rev[:n]):
            return True
    return False

# -------------------------------------------------------------------
# Core correlation logic
# -------------------------------------------------------------------

def correlate_root_cause(results):
    ci_input = results.get("ci_cd")
    gitops_input = results.get("gitops")

    # Accept either list[AuditResult] or a single AuditResult
    ci_list = ci_input if isinstance(ci_input, list) else ([ci_input] if isinstance(ci_input, AuditResult) else [])
    gitops_list = gitops_input if isinstance(gitops_input, list) else ([gitops_input] if isinstance(gitops_input, AuditResult) else [])

    # Diagnostics: what JSONs exist on disk if results are missing/malformed?
    ci_files = sorted(glob.glob(os.path.join(OUTDIR, "ci_cd*.json")))
    gitops_files = sorted(glob.glob(os.path.join(OUTDIR, "gitops*.json")))

    # Disk-first correlation (works even if memory types are off)
    go = _load_latest_gitops()
    docker_tags = _load_docker_tags()
    if go and docker_tags:
        matches = [d for d in docker_tags if _match_by_prefix(go["revision"], d["tag"])]
        if matches:
            m = matches[0]
            msgs = [
                f"🔗 GitOps app {go['app']} at revision {go['revision']} matches Docker tag {m['repo']}:{m['tag']}.",
                ("ℹ️ CI data present on disk (ci_cd.json)." if ci_files else "ℹ️ CI snapshot not found on disk.")
            ]
            write_json(msgs, "correlations.json")
            return AuditResult("Root Cause Correlation", Severity.OK, msgs)

    # If memory is valid, attempt in-memory linkage too
    if ci_list and gitops_list:
        # Normalize HELM and K8s inputs (they might be single AuditResult or a list)
        helm_input = results.get("helm")
        helm_list = helm_input if isinstance(helm_input, list) else ([helm_input] if isinstance(helm_input, AuditResult) else [])

        k8s_input = results.get("kubernetes")
        k8s_list = k8s_input if isinstance(k8s_input, list) else ([k8s_input] if isinstance(k8s_input, AuditResult) else [])

        ci_commits   = extract_ci_commits(ci_list)
        helm_tags    = extract_helm_mappings(helm_list)
        gitops_state = extract_gitops_state(gitops_list)
        k8s_problems = extract_k8s_problems(k8s_list)

        correlations = []
        for sha in ci_commits:
            # Only enforce Helm match if any Helm tags were found
            if helm_tags and not helm_tags.get(sha):
                continue
            gm = gitops_state.get(sha)
            if not gm:
                continue
            affected_k8s = k8s_problems.get(gm.get("app"))
            message = f"🔗 Commit {sha} ➔ CI job ➔ {'Helm tag ➔ ' if helm_tags else ''}ArgoCD app {gm.get('app')}"
            if affected_k8s:
                message += f" ➔ K8s issue: {affected_k8s}"
            correlations.append(message)

        severity = Severity.CRITICAL if correlations else Severity.OK
        messages = correlations or ["No linked root cause issues found."]
        write_json(messages, "correlations.json")
        return AuditResult("Root Cause Correlation", severity, messages)

    # Informational skip (OK) if nothing linkable
    messages = [
        "Correlation skipped (missing or non-linkable CI/CD or GitOps signals).",
        f"Looked in memory types: ci_cd={type(ci_input).__name__}, gitops={type(gitops_input).__name__}",
        f"Also checked disk in OUTDIR={OUTDIR}",
        f"Found CI files: {', '.join(os.path.basename(f) for f in ci_files) or '(none)'}",
        f"Found GitOps files: {', '.join(os.path.basename(f) for f in gitops_files) or '(none)'}",
    ]
    write_json(messages, "correlations.json")
    return AuditResult("Root Cause Correlation", Severity.OK, messages)

# -------------------------------------------------------------------
# Infra drift (tolerant)
# -------------------------------------------------------------------

def detect_infra_drift(tfstate_path=None, aws_region="us-east-2"):
    """
    Accepts:
      - local file path (default OUTDIR/terraform.tfstate)
      - http(s):// URL
      - s3://bucket/key
    Writes a local copy to OUTDIR/terraform.tfstate when needed.
    """
    ensure_outdir()

    src = tfstate_path or _discover_tfstate_path()
    if not src:
        return AuditResult("Infra Drift Detection", Severity.OK, ["Terraform state not found (skipped drift check)."])

    local_tf_path = (
        _download_tfstate_if_needed(src, aws_region)
        if (isinstance(src, str) and (src.startswith("http") or src.startswith("s3://")))
        else (src if os.path.exists(src) else None)
    )
    if not local_tf_path or not os.path.exists(local_tf_path):
        return AuditResult("Infra Drift Detection", Severity.OK, [f"Terraform state path not accessible: {src} (skipped drift)."])

    try:
        with open(local_tf_path, encoding="utf-8") as f:
            tfstate = json.load(f)

        if not HAS_BOTO3:
            return AuditResult("Infra Drift Detection", Severity.OK, ["Terraform state present; live drift skipped (boto3 not available)."])

        try:
            boto3.client("sts").get_caller_identity()  # type: ignore
        except Exception:
            return AuditResult("Infra Drift Detection", Severity.OK, ["Terraform state present; live drift skipped (no AWS credentials)."])

        ec2 = boto3.client("ec2", region_name=aws_region)  # type: ignore
        s3 = boto3.client("s3", region_name=aws_region)    # type: ignore
        drifts = []

        expected_instances = set()
        actual_instances = set(i["InstanceId"] for r in ec2.describe_instances()["Reservations"] for i in r["Instances"])

        for res in tfstate.get("resources", []):
            if res.get("type") == "aws_instance":
                for inst in res.get("instances", []):
                    attrs = inst.get("attributes", {}) or {}
                    instance_id = attrs.get("id")
                    if instance_id:
                        expected_instances.add(instance_id)
                        try:
                            live = ec2.describe_instances(InstanceIds=[instance_id])
                            live_type = live["Reservations"][0]["Instances"][0]["InstanceType"]
                            tf_type = attrs.get("instance_type")
                            if tf_type and live_type and tf_type != live_type:
                                drifts.append(f"EC2 {instance_id} ➔ instance_type drift: TF={tf_type}, Live={live_type}")
                        except ClientError as ce:  # type: ignore
                            code = ce.response.get("Error", {}).get("Code")
                            if code == "InvalidInstanceID.NotFound":
                                drifts.append(f"❌ EC2 {instance_id} in TF state but missing in AWS")
                        except Exception:
                            pass

        missing = expected_instances - actual_instances
        extra = actual_instances - expected_instances
        for mid in missing:
            drifts.append(f"❌ EC2 {mid} in TF state but missing in AWS")
        for xid in extra:
            drifts.append(f"⚠️ EC2 {xid} in AWS but not managed by Terraform")

        tf_s3_buckets = []
        for r in tfstate.get("resources", []):
            if r.get("type") == "aws_s3_bucket":
                for inst in r.get("instances", []):
                    attrs = inst.get("attributes", {}) or {}
                    if "bucket" in attrs:
                        tf_s3_buckets.append(attrs["bucket"])

        live_s3_buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
        for bucket in tf_s3_buckets:
            if bucket not in live_s3_buckets:
                drifts.append(f"❌ S3 bucket {bucket} in TF state but missing in AWS")

        if drifts:
            return AuditResult("Infra Drift Detection", Severity.HIGH, drifts)
        return AuditResult("Infra Drift Detection", Severity.OK, ["No drift detected"])

    except Exception as e:
        return AuditResult("Infra Drift Detection", Severity.LOW, [f"Drift check error: {e}"])

# -------------------------------------------------------------------
# Misc analytics
# -------------------------------------------------------------------

def summarize_change_velocity(results):
    ci_cd = results.get("ci_cd")
    ci_list = ci_cd if isinstance(ci_cd, list) else ([ci_cd] if isinstance(ci_cd, AuditResult) else [])
    if not ci_list:
        return None
    deploys = 0
    for r in ci_list:
        if hasattr(r, "messages"):
            for msg in r.messages:
                if "avg_duration" in msg or "deploys" in msg:
                    deploys += 1
    return AuditResult("Change Velocity", Severity.OK, [f"Total recent deployments: {deploys}"])

def detect_snapshot_drift():
    current = outpath("ci_cd.json")
    prev = outpath("ci_cd_prev.json")
    if os.path.exists(current) and os.path.exists(prev):
        with open(current, encoding="utf-8") as f1, open(prev, encoding="utf-8") as f2:
            c1 = json.load(f1)
            c2 = json.load(f2)
            if c1 != c2:
                return AuditResult("Snapshot Drift", Severity.MEDIUM, ["Changes detected between last runs."])
    return None

def detect_ownership(results):
    owners = []
    for _, v in results.items():
        if isinstance(v, list):
            for r in v:
                if hasattr(r, "title") and "goutham" in getattr(r, "title", "").lower():
                    owners.append(f"{r.title} ➔ Owner: goutham")
    if owners:
        return AuditResult("Ownership Mapping", Severity.OK, owners)
    return None

def correlate_incidents():
    path = outpath("incidents.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return AuditResult("Incident Linkage", Severity.HIGH, [f"Incident: {i}" for i in data.get("alerts", [])])
    return None

def analyze_alert_rules():
    rule_path = "prometheus/alert.rules"
    if os.path.exists(rule_path):
        with open(rule_path, encoding="utf-8") as f:
            rules = f.read().lower()
            required = ["cpu", "memory", "disk", "pod", "kube"]
            missing = [r for r in required if r not in rules]
            if missing:
                return AuditResult("Alert Rule Gaps", Severity.MEDIUM, [f"Missing rules: {', '.join(missing)}"])
    return None

def check_endpoints():
    # Intentionally disabled by default; avoids noise in dashboards.
    urls = []
    issues = []
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                issues.append(f"{url} returned {r.status_code}")

            parsed = urlparse(url)
            ctx = ssl.create_default_context()
            with ctx.wrap_socket(socket.socket(), server_hostname=parsed.hostname) as s:
                s.settimeout(5)
                s.connect((parsed.hostname, 443))
                cert = s.getpeercert()
                expires = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
                days_left = (expires - datetime.datetime.utcnow()).days
                if days_left < 10:
                    issues.append(f"{url} SSL expires in {days_left} days")

        except Exception as e:
            issues.append(f"{url} error: {str(e)}")
    if issues:
        return AuditResult("Endpoint Uptime / SSL", Severity.MEDIUM, issues)
    return None

def summarize_test_coverage():
    if os.path.exists("coverage.xml"):
        try:
            tree = ET.parse("coverage.xml")
            root = tree.getroot()
            coverage = root.attrib.get("line-rate")
            pct = round(float(coverage) * 100, 2)
            return AuditResult("Test Coverage", Severity.OK, [f"Line coverage: {pct}%"])
        except Exception:
            return AuditResult("Test Coverage", Severity.LOW, ["Unable to parse coverage.xml"])
    return None

def detect_cost_spikes():
    path = outpath("cost_trend.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        spikes = []
        prev = 0.0
        for day, cost in data.items():
            try:
                costf = float(cost)
            except Exception:
                continue
            diff = costf - prev
            if prev and diff > 20:
                spikes.append(f"{day} ➔ ${costf} (Δ${round(diff, 2)})")
            prev = costf
        if spikes:
            return AuditResult("Cost Spike Anomaly", Severity.HIGH, spikes)
    except Exception:
        return None

# -------------------------------------------------------------------
# Extraction helpers for in-memory correlation path
# -------------------------------------------------------------------

def extract_ci_commits(ci_results):
    commits = set()
    for result in ci_results:
        msgs = getattr(result, "messages", []) or []
        for msg in msgs:
            lower = msg.lower()
            if "commit" in lower or "revision" in lower or "sha" in lower:
                for tok in msg.replace(":", " ").split():
                    if HEX7PLUS.match(tok):
                        commits.add(tok[:7])  # normalize to short SHA for join
    return commits

def extract_helm_mappings(helm_results):
    mappings = {}
    for result in helm_results:
        msgs = getattr(result, "messages", []) or []
        for msg in msgs:
            lower = msg.lower()
            if "chart version" in lower or "tag" in lower or "image" in lower:
                for part in msg.split():
                    if HEX7PLUS.match(part):
                        mappings[part[:7]] = True
    return mappings

def extract_gitops_state(gitops_results):
    state = {}
    for result in gitops_results:
        sha = None
        app = "unknown"
        msgs = getattr(result, "messages", []) or []
        for msg in msgs:
            lower = msg.lower()
            if "revision" in lower or "sha" in lower or "commit" in lower:
                for word in msg.replace(":", " ").split():
                    if HEX7PLUS.match(word):
                        sha = word[:7]
            if "app" in lower:
                parts = msg.split()
                if parts:
                    app = parts[-1]
        if sha:
            state[sha] = {"app": app}
    return state

def extract_k8s_problems(k8s_results):
    problems = {}
    for result in k8s_results:
        msgs = getattr(result, "messages", []) or []
        for msg in msgs:
            lower = msg.lower()
            if "crash" in lower or "failed" in lower or "crashloop" in lower:
                problems[getattr(result, "title", "unknown")] = msg
    return problems
