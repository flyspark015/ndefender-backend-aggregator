#!/usr/bin/env python3
"""End-to-end diagnostics runner for N-Defender backend."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class EndpointResult:
    name: str
    url: str
    status: str
    http_status: Optional[int]
    latency_ms: Optional[int]
    content_type: str
    snippet: str
    json_ok: bool
    error: Optional[str]
    missing_keys: List[str]
    present_keys: List[str]


def now_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def normalize_base(base: str) -> Tuple[str, str]:
    base = base.rstrip("/")
    if base.endswith("/api/v1"):
        return base, base[: -len("/api/v1")]
    return f"{base}/api/v1", base


def http_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    timeout_s: float = 10.0,
) -> Tuple[Optional[int], Dict[str, str], bytes, Optional[str], Optional[int]]:
    start = time.perf_counter()
    req = Request(url, method=method, headers=headers or {})
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            body = resp.read()
            latency = int((time.perf_counter() - start) * 1000)
            return resp.status, dict(resp.headers), body, None, latency
    except HTTPError as err:
        try:
            body = err.read()
        except Exception:
            body = b""
        latency = int((time.perf_counter() - start) * 1000)
        return err.code, dict(err.headers or {}), body, str(err), latency
    except URLError as err:
        latency = int((time.perf_counter() - start) * 1000)
        return None, {}, b"", str(err), latency
    except Exception as err:
        latency = int((time.perf_counter() - start) * 1000)
        return None, {}, b"", str(err), latency


def snippet_from_body(body: bytes, limit: int = 300) -> str:
    text = body.decode("utf-8", errors="replace")
    return text[:limit]


def try_parse_json(body: bytes) -> Tuple[bool, Any, Optional[str]]:
    try:
        parsed = json.loads(body.decode("utf-8", errors="strict"))
        return True, parsed, None
    except Exception as err:
        return False, None, str(err)


def evaluate_status_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = [
        "sys",
        "cpu",
        "ram",
        "disk",
        "ups",
        "services",
        "gps",
        "remote_id",
        "rf",
        "fpv",
    ]
    present: List[str] = []
    if not isinstance(payload, dict):
        return False, expected, present

    keys = set(payload.keys())
    if "system" in keys or "sys" in keys:
        present.append("sys")
    for key in expected:
        if key in keys and key not in present:
            present.append(key)

    missing = [key for key in expected if key not in present]
    return len(present) > 0, missing, present


def check_endpoint(name: str, url: str) -> EndpointResult:
    http_status, headers, body, error, latency_ms = http_request("GET", url)
    content_type = headers.get("Content-Type", "")
    snippet = snippet_from_body(body)
    json_ok, payload, json_error = try_parse_json(body)

    status = "PASS" if http_status and 200 <= http_status < 300 else "FAIL"
    missing_keys: List[str] = []
    present_keys: List[str] = []

    if name == "status" and status == "PASS":
        ok, missing_keys, present_keys = evaluate_status_fields(payload)
        if not ok:
            status = "DEGRADED"
        elif missing_keys:
            status = "DEGRADED"

    if status == "PASS" and not json_ok:
        status = "FAIL"
        error = json_error or "json_parse_failed"

    return EndpointResult(
        name=name,
        url=url,
        status=status,
        http_status=http_status,
        latency_ms=latency_ms,
        content_type=content_type,
        snippet=snippet,
        json_ok=json_ok,
        error=error,
        missing_keys=missing_keys,
        present_keys=present_keys,
    )


def probe_health(base_api: str, base_root: str) -> Tuple[EndpointResult, List[EndpointResult]]:
    urls = []
    primary = f"{base_api}/health"
    alt = f"{base_root}/health" if base_root else ""
    for url in [primary, alt]:
        if url and url not in urls:
            urls.append(url)

    attempts: List[EndpointResult] = []
    chosen: Optional[EndpointResult] = None
    for url in urls:
        res = check_endpoint("health", url)
        attempts.append(res)
        if res.http_status and 200 <= res.http_status < 300:
            chosen = res
            break
    if chosen is None:
        chosen = attempts[0]
    return chosen, attempts


def render_markdown(
    base: str,
    results: List[EndpointResult],
    health_attempts: List[EndpointResult],
    report_path: str,
) -> str:
    lines: List[str] = []
    lines.append("# N-Defender Diagnostics Report")
    lines.append("")
    lines.append(f"Base URL: `{base}`")
    lines.append(f"Generated: `{datetime.now(timezone.utc).isoformat()}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("| Endpoint | Status | HTTP | Latency (ms) |")
    lines.append("| --- | --- | --- | --- |")
    for res in results:
        http_code = res.http_status if res.http_status is not None else "-"
        latency = res.latency_ms if res.latency_ms is not None else "-"
        lines.append(f"| `{res.name}` | {res.status} | {http_code} | {latency} |")

    lines.append("")
    lines.append("## Health Probe Attempts")
    for res in health_attempts:
        lines.append(f"- `{res.url}` -> {res.status} ({res.http_status})")

    lines.append("")
    lines.append("## Endpoint Details")
    for res in results:
        lines.append(f"### {res.name}")
        lines.append(f"URL: `{res.url}`")
        lines.append(f"Status: `{res.status}`")
        lines.append(f"HTTP: `{res.http_status}`")
        lines.append(f"Latency: `{res.latency_ms}` ms")
        lines.append(f"Content-Type: `{res.content_type}`")
        if res.missing_keys:
            lines.append(f"Missing keys: `{', '.join(res.missing_keys)}`")
        if res.present_keys:
            lines.append(f"Present keys: `{', '.join(res.present_keys)}`")
        if res.error:
            lines.append(f"Error: `{res.error}`")
        lines.append("Snippet:")
        lines.append("```")
        lines.append(res.snippet)
        lines.append("```")

    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    return report_path


def write_json_report(
    base: str,
    results: List[EndpointResult],
    health_attempts: List[EndpointResult],
    report_path: str,
) -> str:
    payload: Dict[str, Any] = {
        "base": base,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "health_attempts": [res.__dict__ for res in health_attempts],
        "endpoints": [res.__dict__ for res in results],
    }
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run N-Defender diagnostics")
    parser.add_argument("--base", required=True, help="Base API URL, e.g. http://127.0.0.1:8000/api/v1")
    args = parser.parse_args()

    base_api, base_root = normalize_base(args.base)
    timestamp = now_timestamp()

    reports_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reports")
    os.makedirs(reports_dir, exist_ok=True)

    health_primary, health_attempts = probe_health(base_api, base_root)

    endpoints = [
        "status",
        "contacts",
        "system",
        "power",
        "rf",
        "video",
        "services",
        "network",
        "audio",
    ]

    results: List[EndpointResult] = [health_primary]
    for name in endpoints:
        url = f"{base_api}/{name}"
        results.append(check_endpoint(name, url))

    md_path = os.path.join(reports_dir, f"diagnostics_{timestamp}.md")
    json_path = os.path.join(reports_dir, f"diagnostics_{timestamp}.json")

    render_markdown(args.base, results, health_attempts, md_path)
    write_json_report(args.base, results, health_attempts, json_path)

    print(f"report_md={md_path}")
    print(f"report_json={json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
