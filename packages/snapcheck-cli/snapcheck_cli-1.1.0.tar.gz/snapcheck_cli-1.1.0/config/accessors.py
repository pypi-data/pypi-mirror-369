# config/accessors.py
from __future__ import annotations
import os
from typing import Any, Iterable, Sequence, List, Optional

KeyPath = Sequence[str]

def _deep_get(d: Any, path: KeyPath) -> Any:
    """Return value at nested dict path, or None."""
    cur = d
    for k in path:
        if isinstance(cur, dict) and k in cur:
            cur = cur[k]
        else:
            return None
    return cur

def get_config_value(config: dict, *paths: KeyPath, fallback: Any = None) -> Any:
    """
    Return the first existing value among provided key paths.
    Example:
      get_config_value(cfg, ('ci_cd','repo'), ('github_repo',))
    """
    for p in paths:
        val = _deep_get(config, p)
        if val is not None:
            return val
    return fallback

def pick(
    config: dict,
    env: Optional[Iterable[str]] = None,
    paths: Iterable[KeyPath] = (),
    fallback: Any = None,
) -> Any:
    """
    Precedence: first non-empty ENV from 'env', then first value among 'paths', else fallback.
    Empty values ('', 'null', 'None') are ignored.
    """
    # ENV precedence
    if env:
        for name in env:
            if name:
                v = os.environ.get(name)
                if v not in (None, "", "null", "None"):
                    return v
    # Config paths
    if paths:
        v = get_config_value(config, *paths, fallback=None)
        if v not in (None, "", "null", "None"):
            return v
    return fallback

def resolve_ci_settings(config: dict) -> dict:
    """
    Normalize CI/CD inputs for plugins:
      platform: github/gitlab/...
      repo:     owner/name
      token:    CI API token (prefer ENV:GITHUB_TOKEN)
    """
    platform = pick(
        config,
        env=['SNAPCHECK_CI_PLATFORM'],
        paths=[('ci_cd', 'platform'), ('ci_platform',)],
        fallback='github',
    )
    repo = pick(
        config,
        env=['SNAPCHECK_GITHUB_REPO'],
        paths=[('ci_cd', 'repo'), ('github_repo',)],
    )
    token = pick(
        config,
        env=['GITHUB_TOKEN', 'SNAPCHECK_GITHUB_TOKEN'],
        paths=[('ci_cd', 'token'), ('github_token',)],
    )
    return {'platform': platform, 'repo': repo, 'token': token}

def resolve_gitops_settings(config: dict) -> dict:
    """
    Normalize Argo CD inputs for plugins.
    """
    server = pick(
        config,
        env=['ARGOCD_SERVER'],
        paths=[('gitops', 'server'), ('argocd', 'server')],
    )
    token = pick(
        config,
        env=['ARGOCD_TOKEN'],
        paths=[('gitops', 'token'), ('argocd', 'token')],
    )
    insecure = bool(
        pick(
            config,
            env=['ARGOCD_INSECURE'],
            paths=[('gitops', 'insecure'), ('argocd', 'insecure')],
            fallback=False,
        )
    )
    return {'server': server, 'token': token, 'insecure': insecure}

def resolve_aws_settings(config: dict) -> dict:
    """
    Normalize AWS settings (region, etc.).
    """
    region = pick(
        config,
        env=['AWS_REGION', 'AWS_DEFAULT_REGION'],
        paths=[('aws_region',), ('aws', 'region')],
        fallback='us-east-1',
    )
    return {'region': region}

def validate_config(config: dict) -> List[str]:
    """
    Return warnings about common pitfalls (non-fatal).
    """
    warnings: List[str] = []

    # Secrets in YAML: discourage this; prefer ENV.
    gh_yaml = get_config_value(config, ('ci_cd', 'token'), ('github_token',))
    if gh_yaml and not os.environ.get('GITHUB_TOKEN'):
        warnings.append('GitHub token appears in YAML. Prefer env GITHUB_TOKEN.')

    # Mixed schema heads-up
    if get_config_value(config, ('ci_cd', 'repo')) and get_config_value(config, ('github_repo',)):
        warnings.append('Both ci_cd.repo and github_repo set; precedence is ENV > ci_cd.repo > github_repo.')

    return warnings
