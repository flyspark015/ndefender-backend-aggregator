#!/usr/bin/env python3
"""End-to-end diagnostics runner for N-Defender backend."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


FIGMA_ORIGIN = "https://www.figma.com"


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
    missing_keys: List[str] = field(default_factory=list)
    present_keys: List[str] = field(default_factory=list)


@dataclass
class CorsResult:
    url: str
    status: str
    http_status: Optional[int]
    allow_origin: Optional[str]
    allow_methods: Optional[str]
    allow_headers: Optional[str]
    error: Optional[str]


@dataclass
class WsResult:
    url: str
    status: str
    messages_received: int
    envelope_ok: bool
    missing_keys: List[str]
    error: Optional[str]
    first_message: Optional[str]


@dataclass
class SystemdResult:
    unit: str
    active: Optional[str]
    error: Optional[str]


@dataclass
class JournalResult:
    unit: str
    ok: bool
    error: Optional[str]
    snippet: str


@dataclass
class DiagnosticsReport:
    base: str
    base_api: str
    base_root: str
    generated_at: str
    health_attempts: List[EndpointResult]
    endpoints: List[EndpointResult]
    cors: Optional[CorsResult]
    websocket: Optional[WsResult]
    systemd: List[SystemdResult]
    journals: List[JournalResult]
    ui_blank_causes: List[Dict[str, str]]


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


def _present_keys(payload: Any, expected: List[str]) -> Tuple[List[str], List[str]]:
    if not isinstance(payload, dict):
        return [], expected
    keys = set(payload.keys())
    present = [key for key in expected if key in keys]
    missing = [key for key in expected if key not in keys]
    return present, missing


def evaluate_status_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = [
        "timestamp_ms",
        "system",
        "power",
        "rf",
        "video",
        "services",
        "network",
        "audio",
        "contacts",
    ]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def evaluate_contacts_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = ["contacts"]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict) and "contacts" in present
    return ok, missing, present


def evaluate_system_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = [
        "uptime_s",
        "cpu_temp_c",
        "cpu_usage_percent",
        "load_1m",
        "load_5m",
        "load_15m",
        "ram_used_mb",
        "ram_total_mb",
        "disk_used_gb",
        "disk_total_gb",
        "throttled_flags",
        "status",
    ]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def evaluate_power_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = [
        "pack_voltage_v",
        "current_a",
        "input_vbus_v",
        "input_power_w",
        "soc_percent",
        "time_to_empty_s",
        "time_to_full_s",
        "per_cell_v",
        "state",
        "status",
    ]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def evaluate_rf_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = ["last_event_type", "last_event", "last_timestamp_ms", "status"]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def evaluate_video_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = ["selected", "status"]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def evaluate_services_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    if not isinstance(payload, list):
        return False, ["services[]"], []
    required = ["name", "active_state", "sub_state", "restart_count"]
    if not payload:
        return True, [], []
    missing = []
    present = []
    if isinstance(payload[0], dict):
        present, missing = _present_keys(payload[0], required)
    return True, missing, present


def evaluate_network_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = ["connected", "ssid", "ip_v4", "ip_v6", "status"]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def evaluate_audio_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = ["volume_percent", "muted", "status"]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def evaluate_health_fields(payload: Any) -> Tuple[bool, List[str], List[str]]:
    expected = ["status", "timestamp_ms"]
    present, missing = _present_keys(payload, expected)
    ok = isinstance(payload, dict)
    return ok, missing, present


def check_endpoint(name: str, url: str) -> EndpointResult:
    http_status, headers, body, error, latency_ms = http_request("GET", url)
    content_type = headers.get("Content-Type", "")
    snippet = snippet_from_body(body)
    json_ok, payload, json_error = try_parse_json(body)

    status = "PASS" if http_status and 200 <= http_status < 300 else "FAIL"
    missing_keys: List[str] = []
    present_keys: List[str] = []

    if status == "PASS" and json_ok:
        ok = True
        if name == "status":
            ok, missing_keys, present_keys = evaluate_status_fields(payload)
        elif name == "contacts":
            ok, missing_keys, present_keys = evaluate_contacts_fields(payload)
        elif name == "system":
            ok, missing_keys, present_keys = evaluate_system_fields(payload)
        elif name == "power":
            ok, missing_keys, present_keys = evaluate_power_fields(payload)
        elif name == "rf":
            ok, missing_keys, present_keys = evaluate_rf_fields(payload)
        elif name == "video":
            ok, missing_keys, present_keys = evaluate_video_fields(payload)
        elif name == "services":
            ok, missing_keys, present_keys = evaluate_services_fields(payload)
        elif name == "network":
            ok, missing_keys, present_keys = evaluate_network_fields(payload)
        elif name == "audio":
            ok, missing_keys, present_keys = evaluate_audio_fields(payload)
        elif name == "health":
            ok, missing_keys, present_keys = evaluate_health_fields(payload)
        if not ok or missing_keys:
            status = "DEGRADED" if status == "PASS" else status

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


def check_cors(base_api: str) -> CorsResult:
    url = f"{base_api}/status"
    headers = {
        "Origin": FIGMA_ORIGIN,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type",
    }
    http_status, resp_headers, _body, error, _latency = http_request("OPTIONS", url, headers=headers)
    allow_origin = resp_headers.get("Access-Control-Allow-Origin")
    allow_methods = resp_headers.get("Access-Control-Allow-Methods")
    allow_headers = resp_headers.get("Access-Control-Allow-Headers")

    ok = http_status in (200, 204) and (allow_origin in ("*", FIGMA_ORIGIN))
    status = "PASS" if ok else "FAIL"

    return CorsResult(
        url=url,
        status=status,
        http_status=http_status,
        allow_origin=allow_origin,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        error=error,
    )


def _ws_url_from_base(base_api: str) -> str:
    if base_api.startswith("https://"):
        return "wss://" + base_api[len("https://") :] + "/ws"
    if base_api.startswith("http://"):
        return "ws://" + base_api[len("http://") :] + "/ws"
    return base_api.rstrip("/") + "/ws"


def _ws_recv_websocket_client(ws_url: str, timeout_s: float) -> Tuple[int, List[str], Optional[str]]:
    try:
        import websocket  # type: ignore
    except Exception as err:
        return 0, [], f"websocket-client import failed: {err}"

    messages: List[str] = []
    try:
        ws = websocket.create_connection(
            ws_url,
            timeout=timeout_s,
            header=[f"Origin: {FIGMA_ORIGIN}"],
        )
        ws.settimeout(timeout_s)
        for _ in range(3):
            try:
                msg = ws.recv()
            except Exception:
                break
            if isinstance(msg, bytes):
                msg = msg.decode("utf-8", errors="replace")
            messages.append(str(msg))
        ws.close()
        return len(messages), messages, None
    except Exception as err:
        return 0, [], str(err)


def _ws_recv_websockets(ws_url: str, timeout_s: float) -> Tuple[int, List[str], Optional[str]]:
    try:
        import asyncio
        import websockets  # type: ignore
    except Exception as err:
        return 0, [], f"websockets import failed: {err}"

    messages: List[str] = []

    async def _run() -> None:
        nonlocal messages
        async with websockets.connect(ws_url, extra_headers={"Origin": FIGMA_ORIGIN}) as ws:  # type: ignore
            for _ in range(3):
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=timeout_s)
                except Exception:
                    break
                if isinstance(msg, bytes):
                    msg = msg.decode("utf-8", errors="replace")
                messages.append(str(msg))

    try:
        asyncio.run(_run())
        return len(messages), messages, None
    except Exception as err:
        return 0, [], str(err)


def check_websocket(base_api: str, timeout_s: float = 6.0) -> WsResult:
    ws_url = _ws_url_from_base(base_api)

    recv_count, messages, error = _ws_recv_websocket_client(ws_url, timeout_s)
    if error and "websocket-client" in (error or ""):
        recv_count, messages, error = _ws_recv_websockets(ws_url, timeout_s)

    envelope_ok = False
    missing_keys: List[str] = []
    first_message = messages[0] if messages else None

    if messages:
        try:
            payload = json.loads(messages[0])
            expected = ["type", "timestamp", "source", "data"]
            present, missing = _present_keys(payload, expected)
            missing_keys = missing
            envelope_ok = not missing
        except Exception as err:
            error = error or f"ws_json_error: {err}"

    status = "PASS" if recv_count > 0 and envelope_ok else "FAIL"

    return WsResult(
        url=ws_url,
        status=status,
        messages_received=recv_count,
        envelope_ok=envelope_ok,
        missing_keys=missing_keys,
        error=error,
        first_message=first_message,
    )


def _run_cmd(cmd: List[str], timeout_s: float = 6.0) -> Tuple[int, str, str, Optional[str]]:
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
        return proc.returncode, proc.stdout, proc.stderr, None
    except Exception as err:
        return 1, "", "", str(err)


def check_systemd(units: List[str]) -> List[SystemdResult]:
    results: List[SystemdResult] = []
    for unit in units:
        code, out, err, exc = _run_cmd(["systemctl", "is-active", unit])
        if exc:
            results.append(SystemdResult(unit=unit, active=None, error=exc))
            continue
        if code != 0:
            results.append(SystemdResult(unit=unit, active=(out.strip() or None), error=err.strip() or None))
            continue
        results.append(SystemdResult(unit=unit, active=out.strip() or None, error=None))
    return results


def check_journal(unit: str, lines: int = 120) -> JournalResult:
    cmd = ["journalctl", "-u", unit, "-n", str(lines), "--no-pager"]
    code, out, err, exc = _run_cmd(cmd, timeout_s=8.0)
    if exc:
        return JournalResult(unit=unit, ok=False, error=exc, snippet="")
    if code != 0:
        return JournalResult(unit=unit, ok=False, error=err.strip() or "journalctl_failed", snippet=out[:1200])
    return JournalResult(unit=unit, ok=True, error=None, snippet=out[-1200:])


def derive_ui_blank_causes(
    endpoints: List[EndpointResult],
    cors: Optional[CorsResult],
    ws: Optional[WsResult],
    systemd: List[SystemdResult],
    journals: List[JournalResult],
) -> List[Dict[str, str]]:
    causes: List[Tuple[int, str, str]] = []

    status_res = next((r for r in endpoints if r.name == "status"), None)
    if status_res and status_res.status == "FAIL":
        causes.append((100, "API /status failing", f"/status HTTP={status_res.http_status} err={status_res.error}"))
    elif status_res and status_res.status == "DEGRADED":
        causes.append((90, "API /status missing fields", f"missing={','.join(status_res.missing_keys)}"))

    health_res = next((r for r in endpoints if r.name == "health"), None)
    if health_res and health_res.status == "FAIL":
        causes.append((95, "API /health failing", f"/health HTTP={health_res.http_status} err={health_res.error}"))

    if ws:
        if ws.status != "PASS":
            causes.append((85, "WebSocket not delivering events", ws.error or "no messages or invalid envelope"))
        elif not ws.envelope_ok:
            causes.append((80, "WebSocket envelope invalid", f"missing={','.join(ws.missing_keys)}"))

    if cors and cors.status != "PASS":
        causes.append((75, "CORS preflight blocked", f"allow_origin={cors.allow_origin} http={cors.http_status}"))

    for unit in ["ndefender-backend", "cloudflared", "ndefender-kiosk"]:
        state = next((s for s in systemd if s.unit == unit), None)
        if state and state.active not in ("active", "activating"):
            causes.append((70, f"systemd {unit} not active", f"state={state.active} err={state.error}"))

    for journal in journals:
        if journal.ok and "ERR" in journal.snippet:
            causes.append((60, f"errors in {journal.unit} journal", "ERR found in last 120 lines"))
        if journal.ok and "Traceback" in journal.snippet:
            causes.append((60, f"exceptions in {journal.unit} journal", "Traceback found in last 120 lines"))

    if not causes:
        causes.append((10, "No obvious backend failures", "Backend responses look healthy; check UI assets/build."))

    causes.sort(key=lambda x: x[0], reverse=True)
    top = causes[:5]
    return [{"cause": c, "evidence": e} for _score, c, e in top]


def render_markdown(report: DiagnosticsReport, report_path: str) -> str:
    lines: List[str] = []
    lines.append("# N-Defender Diagnostics Report")
    lines.append("")
    lines.append(f"Base URL: `{report.base}`")
    lines.append(f"Generated: `{report.generated_at}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("| Endpoint | Status | HTTP | Latency (ms) |")
    lines.append("| --- | --- | --- | --- |")
    for res in report.endpoints:
        http_code = res.http_status if res.http_status is not None else "-"
        latency = res.latency_ms if res.latency_ms is not None else "-"
        lines.append(f"| `{res.name}` | {res.status} | {http_code} | {latency} |")

    lines.append("")
    lines.append("## Health Probe Attempts")
    for res in report.health_attempts:
        lines.append(f"- `{res.url}` -> {res.status} ({res.http_status})")

    lines.append("")
    lines.append("## CORS Preflight")
    if report.cors:
        lines.append(f"URL: `{report.cors.url}`")
        lines.append(f"Status: `{report.cors.status}` HTTP `{report.cors.http_status}`")
        lines.append(f"Allow-Origin: `{report.cors.allow_origin}`")
        lines.append(f"Allow-Methods: `{report.cors.allow_methods}`")
        lines.append(f"Allow-Headers: `{report.cors.allow_headers}`")
        if report.cors.error:
            lines.append(f"Error: `{report.cors.error}`")
    else:
        lines.append("CORS check not executed.")

    lines.append("")
    lines.append("## WebSocket")
    if report.websocket:
        lines.append(f"URL: `{report.websocket.url}`")
        lines.append(f"Status: `{report.websocket.status}`")
        lines.append(f"Messages received: `{report.websocket.messages_received}`")
        lines.append(f"Envelope ok: `{report.websocket.envelope_ok}`")
        if report.websocket.missing_keys:
            lines.append(f"Missing keys: `{', '.join(report.websocket.missing_keys)}`")
        if report.websocket.error:
            lines.append(f"Error: `{report.websocket.error}`")
        if report.websocket.first_message:
            lines.append("First message:")
            lines.append("```")
            lines.append(report.websocket.first_message)
            lines.append("```")
    else:
        lines.append("WebSocket check not executed.")

    lines.append("")
    lines.append("## Systemd Status")
    for state in report.systemd:
        lines.append(f"- `{state.unit}`: `{state.active}` error=`{state.error}`")

    lines.append("")
    lines.append("## Journal Snippets")
    for journal in report.journals:
        lines.append(f"### {journal.unit}")
        if journal.error:
            lines.append(f"Error: `{journal.error}`")
        lines.append("```")
        lines.append(journal.snippet)
        lines.append("```")

    lines.append("")
    lines.append("## Why UI Blank (Top 5 Causes)")
    for item in report.ui_blank_causes:
        lines.append(f"- {item['cause']} — evidence: `{item['evidence']}`")

    lines.append("")
    lines.append("## Endpoint Details")
    for res in report.endpoints:
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


def write_json_report(report: DiagnosticsReport, report_path: str) -> str:
    payload: Dict[str, Any] = {
        "base": report.base,
        "base_api": report.base_api,
        "base_root": report.base_root,
        "generated_at": report.generated_at,
        "health_attempts": [res.__dict__ for res in report.health_attempts],
        "endpoints": [res.__dict__ for res in report.endpoints],
        "cors": report.cors.__dict__ if report.cors else None,
        "websocket": report.websocket.__dict__ if report.websocket else None,
        "systemd": [res.__dict__ for res in report.systemd],
        "journals": [res.__dict__ for res in report.journals],
        "ui_blank_causes": report.ui_blank_causes,
    }
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return report_path


def label_for_base(base: str) -> str:
    host = urlparse(base).hostname or ""
    if host in ("127.0.0.1", "localhost"):
        return "local"
    return "public"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run N-Defender diagnostics")
    parser.add_argument("--base", required=True, help="Base API URL, e.g. http://127.0.0.1:8000/api/v1")
    args = parser.parse_args()

    base_api, base_root = normalize_base(args.base)
    timestamp = now_timestamp()
    label = label_for_base(base_api)

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

    cors_result = check_cors(base_api)
    ws_result = check_websocket(base_api)
    systemd_result = check_systemd(["ndefender-backend", "cloudflared", "ndefender-kiosk"])
    journals = [
        check_journal("ndefender-backend"),
        check_journal("cloudflared"),
    ]

    ui_causes = derive_ui_blank_causes(results, cors_result, ws_result, systemd_result, journals)

    report = DiagnosticsReport(
        base=args.base,
        base_api=base_api,
        base_root=base_root,
        generated_at=datetime.now(timezone.utc).isoformat(),
        health_attempts=health_attempts,
        endpoints=results,
        cors=cors_result,
        websocket=ws_result,
        systemd=systemd_result,
        journals=journals,
        ui_blank_causes=ui_causes,
    )

    md_path = os.path.join(reports_dir, f"diagnostics_{label}_{timestamp}.md")
    json_path = os.path.join(reports_dir, f"diagnostics_{label}_{timestamp}.json")

    render_markdown(report, md_path)
    write_json_report(report, json_path)

    print(f"report_md={md_path}")
    print(f"report_json={json_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
