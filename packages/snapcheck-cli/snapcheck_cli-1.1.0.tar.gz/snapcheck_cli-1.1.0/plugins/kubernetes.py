from __future__ import annotations
import os
import json
import subprocess
import shlex
import datetime
from typing import List, Dict, Any, Optional

from kubernetes import client, config
from kubernetes.stream import stream
from kubernetes.client.exceptions import ApiException

from utils.reporter import AuditResult, Severity
from core.paths import OUTDIR, ensure_outdir, write_json

# ---------- helpers ----------

def _run(cmd: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a shell command and return the completed process (no raise)."""
    return subprocess.run(shlex.split(cmd), capture_output=True, text=True, timeout=timeout)

def _pick_running_pod(v1: client.CoreV1Api, namespace: str):
    pods = v1.list_namespaced_pod(namespace=namespace).items
    for p in pods:
        if (p.status and p.status.phase == "Running"):
            return p
    return pods[0] if pods else None

def _first_container_name(pod) -> Optional[str]:
    if not pod or not pod.spec or not pod.spec.containers:
        return None
    return pod.spec.containers[0].name

def _endpoint_has_addresses(v1: client.CoreV1Api, namespace: str, svc_name: str) -> bool:
    try:
        ep = v1.read_namespaced_endpoints(svc_name, namespace)
        if not ep or not ep.subsets:
            return False
        for subset in ep.subsets:
            if subset.addresses:
                return True
    except ApiException:
        return False
    return False

# ---------- main check ----------

def run_check(config_data: Dict[str, Any]):
    """
    Returns a single AuditResult (unchanged interface).
    Also writes OUTDIR/kubernetes.json with structured results for correlation/debugging.
    """
    ensure_outdir()
    test_mode = config_data.get("test_mode", False)
    if test_mode:
        payload = {
            "module": "kubernetes",
            "when": datetime.datetime.utcnow().isoformat() + "Z",
            "test_mode": True,
            "notes": ["Test mode enabled. Skipping live cluster diagnostics."],
        }
        write_json(payload, "kubernetes.json")
        return AuditResult(
            title="Kubernetes Cluster Audit",
            status=Severity.OK,
            messages=["Test mode enabled. Skipping live cluster diagnostics."]
        )

    # Connect
    try:
        config.load_kube_config(config_file=config_data.get("kubeconfig"))
    except Exception as e:
        payload = {
            "module": "kubernetes",
            "error": f"Failed to connect to cluster: {e}",
        }
        write_json(payload, "kubernetes.json")
        return AuditResult(
            title="Kubernetes Cluster Audit",
            status=Severity.CRITICAL,
            messages=[f"❌ Failed to connect to cluster: {e}"]
        )

    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()

    messages: List[str] = []
    severity = Severity.OK
    details = {}

    # --- Metrics API (fixes PL-K8S-1) ---
    top_cp = _run("kubectl top nodes")
    if top_cp.returncode == 0:
        messages.append("📈 Metrics API OK: `kubectl top nodes` succeeded.")
        details["metrics_api"] = {"status": "ok"}
    else:
        # Is metrics-server installed?
        installed = False
        try:
            apps_v1.read_namespaced_deployment("metrics-server", "kube-system")
            installed = True
        except ApiException:
            installed = False

        if not installed:
            messages.append(
                "📉 Metrics API unavailable. metrics-server not installed.\n"
                "Install with:\n"
                "  helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server &&\n"
                "  helm upgrade --install metrics-server metrics-server/metrics-server -n kube-system "
                "--set args={--kubelet-insecure-tls}"
            )
            severity = max(severity, Severity.MEDIUM)
            details["metrics_api"] = {"status": "missing_metrics_server", "kubectl_top_err": top_cp.stderr or top_cp.stdout}
        else:
            # Installed but maybe no endpoints yet
            if not _endpoint_has_addresses(v1, "kube-system", "metrics-server"):
                messages.append("⚠️ metrics-server Service exists but has NO endpoints yet (pods starting/not ready).")
                severity = max(severity, Severity.LOW)
                details["metrics_api"] = {"status": "no_endpoints", "kubectl_top_err": top_cp.stderr or top_cp.stdout}
            else:
                messages.append("⚠️ `kubectl top nodes` failed despite metrics-server present (check RBAC/certs).")
                severity = max(severity, Severity.MEDIUM)
                details["metrics_api"] = {"status": "present_but_top_failed", "kubectl_top_err": top_cp.stderr or top_cp.stdout}

    # --- Node readiness & pressure (unchanged) ---
    unready_nodes = []
    pressure_nodes = []
    for node in v1.list_node().items:
        for condition in node.status.conditions or []:
            if condition.type == "Ready" and condition.status != "True":
                unready_nodes.append(node.metadata.name)
            if condition.type in ["MemoryPressure", "DiskPressure"] and condition.status == "True":
                pressure_nodes.append(f"{node.metadata.name} - {condition.type}")
    if unready_nodes:
        messages.append(f"🚨 Unready nodes: {', '.join(unready_nodes)}")
        severity = max(severity, Severity.HIGH)
    if pressure_nodes:
        messages.append(f"⚠️ Node pressure detected: {', '.join(pressure_nodes)}")
        severity = max(severity, Severity.MEDIUM)

    # --- Pod status (unchanged) ---
    crashloop_pods = []
    restarted_pods = []
    failed_liveness = []
    for pod in v1.list_pod_for_all_namespaces().items:
        for status in (pod.status.container_statuses or []):
            if status.state and status.state.waiting and status.state.waiting.reason == "CrashLoopBackOff":
                crashloop_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
            if getattr(status, "restart_count", 0) and status.restart_count > 3:
                restarted_pods.append(f"{pod.metadata.namespace}/{pod.metadata.name} - restarts: {status.restart_count}")
            if status.ready is False and not status.state.running:
                failed_liveness.append(f"{pod.metadata.namespace}/{pod.metadata.name}")
    if crashloop_pods:
        messages.append(f"❌ CrashLoopBackOff pods: {', '.join(crashloop_pods)}")
        severity = max(severity, Severity.HIGH)
    if restarted_pods:
        messages.append(f"♻️ High pod restarts: {', '.join(restarted_pods)}")
        severity = max(severity, Severity.MEDIUM)
    if failed_liveness:
        messages.append(f"🔍 Readiness/Liveness failures: {', '.join(failed_liveness)}")
        severity = max(severity, Severity.MEDIUM)

    # --- PVC status (unchanged) ---
    pvc_issues = []
    for pvc in v1.list_persistent_volume_claim_for_all_namespaces().items:
        if pvc.status and pvc.status.phase != "Bound":
            pvc_issues.append(f"{pvc.metadata.namespace}/{pvc.metadata.name} - {pvc.status.phase}")
    if pvc_issues:
        messages.append(f"💾 Unbound PVCs: {', '.join(pvc_issues)}")
        severity = max(severity, Severity.MEDIUM)

    # --- DNS test (fixes PL-K8S-2) ---
    try:
        pod = _pick_running_pod(v1, "kube-system")
        if pod:
            container_name = _first_container_name(pod)
            if container_name:
                output = stream(
                    v1.connect_get_namespaced_pod_exec,
                    pod.metadata.name,
                    "kube-system",
                    command=["nslookup", "kubernetes.default"],
                    container=container_name,
                    stderr=True, stdin=False, stdout=True, tty=False
                )
                if "can't find" in (output or "").lower():
                    messages.append(f"❌ DNS resolution failed inside pod {pod.metadata.name} ({container_name})")
                    severity = max(severity, Severity.HIGH)
                else:
                    messages.append(f"🧪 DNS OK inside pod {pod.metadata.name} ({container_name})")
            else:
                messages.append("⚠️ DNS exec skipped: selected pod has no containers.")
                severity = max(severity, Severity.LOW)
        else:
            messages.append("⚠️ DNS exec skipped: no Running pods in kube-system.")
            severity = max(severity, Severity.LOW)
    except Exception as e:
        messages.append(f"⚠️ DNS test failed to execute: {e}")
        severity = max(severity, Severity.MEDIUM)

    # --- Services with no endpoints (clarify metrics-server) (fixes PL-K8S-3) ---
    no_endpoints = []
    for ep in v1.list_endpoints_for_all_namespaces().items:
        if not ep.subsets:
            no_endpoints.append(f"{ep.metadata.namespace}/{ep.metadata.name}")
    if no_endpoints:
        messages.append(f"🔌 Services with no endpoints: {', '.join(no_endpoints)}")
        if "kube-system/metrics-server" in no_endpoints:
            messages.append("ℹ️ metrics-server has no endpoints → metrics API will not work until pods are Ready.")
        severity = max(severity, Severity.MEDIUM)

    # --- Security checks (flag but annotate system pods) (fixes PL-K8S-4) ---
    privileged_containers = []
    hostpath_volumes = []
    expected_noise = ("aws-node", "kube-proxy")
    for pod in v1.list_pod_for_all_namespaces().items:
        # privileged
        for c in (pod.spec.containers or []):
            sc = getattr(c, "security_context", None)
            if sc and getattr(sc, "privileged", False):
                tag = " (expected system pod)" if any(x in pod.metadata.name for x in expected_noise) else ""
                privileged_containers.append(f"{pod.metadata.namespace}/{pod.metadata.name}{tag}")
        # hostPath
        for vol in (pod.spec.volumes or []):
            if getattr(vol, "host_path", None):
                tag = " (expected system pod)" if any(x in pod.metadata.name for x in expected_noise) else ""
                hostpath_volumes.append(f"{pod.metadata.namespace}/{pod.metadata.name} uses hostPath{tag}")

    if privileged_containers:
        messages.append(f"🔐 Privileged containers: {', '.join(privileged_containers)}")
        severity = max(severity, Severity.HIGH)
    if hostpath_volumes:
        messages.append(f"⚠️ HostPath volumes: {', '.join(hostpath_volumes)}")
        severity = max(severity, Severity.MEDIUM)

    if not messages:
        messages.append("✅ All checks passed. Cluster looks healthy.")

    # Persist JSON snapshot for correlation/debugging
    payload = {
        "module": "kubernetes",
        "outdir": OUTDIR,
        "when": datetime.datetime.utcnow().isoformat() + "Z",
        "results": messages,
        "status": severity.name if hasattr(severity, "name") else str(severity),
    }
    write_json(payload, "kubernetes.json")

    return AuditResult(
        title="Kubernetes Cluster Audit",
        status=severity,
        messages=messages
    )

