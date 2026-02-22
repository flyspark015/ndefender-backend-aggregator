#!/usr/bin/env python3
"""End-to-end GREEN SIGNAL verification for N-Defender."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import websockets

REST_ENDPOINTS = [
    "health",
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

COMMAND_ENDPOINTS = [
    "vrx/tune",
    "scan/start",
    "scan/stop",
    "video/select",
]

GENERIC_COMMAND_ENDPOINTS = [
    "command",
    "cmd",
    "control",
]

COMMAND_PAYLOADS = {
    "vrx/tune": {"payload": {"vrx_id": 1, "freq_hz": 5740000000}},
    "scan/start": {"payload": {"dwell_ms": 200, "step_hz": 2000000, "start_hz": 5645000000, "stop_hz": 5665000000}},
    "scan/stop": {"payload": {}},
    "video/select": {"payload": {"ch": 1}},
}

REQUIRED_STATUS_KEYS = ["system", "power", "services", "rf", "network", "audio", "contacts"]

SERVICE_UNITS = [
    "ndefender-backend",
    "cloudflared",
    "ndefender-remoteid-engine",
    "ndefender-rfscan",
    "gpsd",
]

LOG_KEYWORDS = re.compile(r"error|exception|traceback|ws|403|cloudflare", re.IGNORECASE)


@dataclass
class RestResult:
    endpoint: str
    url: str
    http_status: Optional[int]
    latency_ms: Optional[int]
    content_type: str
    snippet: str
    json_ok: bool
    error: Optional[str]


@dataclass
class WsResult:
    url: str
    connect_ok: bool
    msgs_received: int
    first_type: Optional[str]
    first_200: Optional[str]
    first_message: Optional[str]
    envelope_valid: bool
    error: Optional[str]


@dataclass
class CorsResult:
    url: str
    origin: str
    http_status: Optional[int]
    allow_origin: Optional[str]
    allow_methods: Optional[str]
    allow_headers: Optional[str]
    error: Optional[str]


@dataclass
class ServiceResult:
    unit: str
    active: Optional[str]
    substate: Optional[str]
    main_pid: Optional[str]
    error: Optional[str]


@dataclass
class CommandResult:
    command: str
    url: str
    http_status: Optional[int]
    response_snippet: str
    accepted: Optional[bool]
    command_id: Optional[str]
    ack_received: bool
    ack_match: bool
    error: Optional[str]


@dataclass
class SubsystemResult:
    name: str
    status: str
    evidence: str


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def http_request(method: str, url: str, headers: Optional[Dict[str, str]] = None, body: Optional[bytes] = None, timeout_s: float = 10.0) -> Tuple[Optional[int], Dict[str, str], bytes, Optional[str], Optional[int]]:
    start = time.perf_counter()
    req = Request(url, method=method, headers=headers or {}, data=body)
    try:
        with urlopen(req, timeout=timeout_s) as resp:
            data = resp.read()
            latency = int((time.perf_counter() - start) * 1000)
            return resp.status, dict(resp.headers), data, None, latency
    except HTTPError as err:
        try:
            data = err.read()
        except Exception:
            data = b""
        latency = int((time.perf_counter() - start) * 1000)
        return err.code, dict(err.headers or {}), data, str(err), latency
    except URLError as err:
        latency = int((time.perf_counter() - start) * 1000)
        return None, {}, b"", str(err), latency
    except Exception as err:
        latency = int((time.perf_counter() - start) * 1000)
        return None, {}, b"", str(err), latency


def probe_rest(base: str, endpoint: str) -> RestResult:
    url = f"{base}/{endpoint}"
    status, headers, body, error, latency = http_request("GET", url)
    content_type = headers.get("Content-Type", "") if headers else ""
    snippet = body.decode("utf-8", errors="replace")[:300]
    json_ok = False
    if body:
        try:
            json.loads(body.decode("utf-8", errors="strict"))
            json_ok = True
        except Exception:
            json_ok = False
    return RestResult(endpoint, url, status, latency, content_type, snippet, json_ok, error)


async def probe_ws(url: str, origin: Optional[str] = None, max_messages: int = 10, timeout_s: float = 10.0) -> WsResult:
    headers = {"Origin": origin} if origin else None
    msgs: List[str] = []
    first_type = None
    envelope_valid = False
    try:
        async with websockets.connect(url, extra_headers=headers) as ws:
            start = time.time()
            while len(msgs) < max_messages and (time.time() - start) < timeout_s:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=timeout_s - (time.time() - start))
                    msgs.append(msg)
                except asyncio.TimeoutError:
                    break
            if msgs:
                first = msgs[0]
                try:
                    payload = json.loads(first)
                    first_type = payload.get("type")
                    envelope_valid = isinstance(first_type, str)
                except Exception:
                    envelope_valid = False
            return WsResult(url, True, len(msgs), first_type, msgs[0][:200] if msgs else None, msgs[0] if msgs else None, envelope_valid, None)
    except Exception as exc:
        return WsResult(url, False, 0, None, None, None, False, str(exc))


def probe_cors(url: str, origin: str) -> CorsResult:
    headers = {
        "Origin": origin,
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "Content-Type,X-API-Key,X-Role",
    }
    status, resp_headers, _body, error, _lat = http_request("OPTIONS", url, headers=headers)
    allow_origin = resp_headers.get("Access-Control-Allow-Origin") if resp_headers else None
    allow_methods = resp_headers.get("Access-Control-Allow-Methods") if resp_headers else None
    allow_headers = resp_headers.get("Access-Control-Allow-Headers") if resp_headers else None
    return CorsResult(url, origin, status, allow_origin, allow_methods, allow_headers, error)


def systemctl_show(unit: str) -> ServiceResult:
    try:
        show = subprocess.run(["systemctl", "show", unit, "-p", "ActiveState", "-p", "SubState", "-p", "MainPID"], capture_output=True, text=True, check=False)
        if show.returncode != 0:
            return ServiceResult(unit, None, None, None, show.stderr.strip() or show.stdout.strip())
        kv = dict(line.split("=", 1) for line in show.stdout.strip().splitlines() if "=" in line)
        return ServiceResult(unit, kv.get("ActiveState"), kv.get("SubState"), kv.get("MainPID"), None)
    except Exception as exc:
        return ServiceResult(unit, None, None, None, str(exc))


def journal_snippet(unit: str, lines: int = 200) -> Tuple[str, List[str]]:
    try:
        proc = subprocess.run(["journalctl", "-u", unit, "-n", str(lines), "--no-pager"], capture_output=True, text=True, check=False)
        text = proc.stdout.strip()
        highlights = [line for line in text.splitlines() if LOG_KEYWORDS.search(line)]
        return text[-2000:], highlights[:20]
    except Exception as exc:
        return f"error: {exc}", []


def pick_command_endpoint(base: str) -> Optional[str]:
    for endpoint in COMMAND_ENDPOINTS:
        url = f"{base}/{endpoint}"
        status, _headers, _body, _err, _lat = http_request("POST", url, headers={"Content-Type": "application/json"}, body=b"{}")
        if status is None:
            continue
        if status not in (404, 405):
            return endpoint
    return None


def run_command_tests(base: str, ws_url: str, api_key: Optional[str], api_role: Optional[str]) -> Tuple[List[CommandResult], Optional[str], Dict[str, Optional[int]]]:
    generic_status: Dict[str, Optional[int]] = {}
    for ep in GENERIC_COMMAND_ENDPOINTS:
        url = f"{base}/{ep}"
        status, _headers, _body, _err, _lat = http_request("POST", url, headers={"Content-Type": "application/json"}, body=b"{}")
        generic_status[ep] = status

    generic_endpoint = None
    for ep, status in generic_status.items():
        if status is not None and status not in (404, 405):
            generic_endpoint = ep
            break

    direct_endpoint = pick_command_endpoint(base)

    if generic_endpoint is None and direct_endpoint is None:
        return [], "No command endpoint found (generic: /command,/cmd,/control and direct: /vrx/tune,/scan/start,/scan/stop,/video/select)", generic_status

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["X-API-Key"] = api_key
    if api_role:
        headers["X-Role"] = api_role

    results: List[CommandResult] = []
    commands = ["ping", "scan/stop", "video/select"]

    async def send_and_listen() -> Dict[str, List[Dict[str, Any]]]:
        acks: Dict[str, List[Dict[str, Any]]] = {cmd: [] for cmd in commands}
        try:
            async with websockets.connect(ws_url) as ws:
                start = time.time()
                while (time.time() - start) < 10:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=10 - (time.time() - start))
                    except asyncio.TimeoutError:
                        break
                    try:
                        payload = json.loads(msg)
                    except Exception:
                        continue
                    if payload.get("type") == "COMMAND_ACK":
                        data = payload.get("data") or {}
                        cmd = data.get("command") or data.get("cmd")
                        if cmd in acks:
                            acks[cmd].append(data)
        except Exception:
            pass
        return acks

    for cmd in commands:
        if generic_endpoint:
            url = f"{base}/{generic_endpoint}"
            payload = {"command": cmd, "payload": COMMAND_PAYLOADS.get(cmd, {"payload": {}}).get("payload", {})}
        else:
            if cmd == "ping":
                results.append(CommandResult(cmd, f"{base}/(none)", None, "no generic endpoint; ping not supported", None, None, False, False, "no generic endpoint"))
                continue
            url = f"{base}/{cmd}"
            payload = COMMAND_PAYLOADS.get(cmd, {"payload": {}})
        body = json.dumps(payload).encode("utf-8")
        status, _headers, resp_body, error, _lat = http_request("POST", url, headers=headers, body=body)
        snippet = resp_body.decode("utf-8", errors="replace")[:200]
        accepted = None
        command_id = None
        if resp_body:
            try:
                parsed = json.loads(resp_body.decode("utf-8", errors="strict"))
                accepted = parsed.get("accepted")
                command_id = parsed.get("command_id")
            except Exception:
                pass

        acks = asyncio.run(send_and_listen())
        ack_received = len(acks.get(cmd, [])) > 0
        ack_match = ack_received

        results.append(CommandResult(cmd, url, status, snippet, accepted, command_id, ack_received, ack_match, error))

    return results, None, generic_status


def status_key_check(payload: Dict[str, Any]) -> List[str]:
    return [k for k in REQUIRED_STATUS_KEYS if k not in payload]


def fetch_status_payload(base: str) -> Dict[str, Any]:
    url = f"{base}/status"
    status, _headers, body, _error, _lat = http_request("GET", url)
    if status != 200 or not body:
        return {}
    try:
        return json.loads(body.decode("utf-8", errors="strict"))
    except Exception:
        return {}


def subsystem_checks(status_payload: Dict[str, Any], ws_messages: List[str], services: Dict[str, ServiceResult]) -> List[SubsystemResult]:
    results: List[SubsystemResult] = []

    system = status_payload.get("system")
    if isinstance(system, dict):
        results.append(SubsystemResult("system_metrics", "PASS", f"cpu_usage={system.get('cpu_usage_percent')}, temp={system.get('cpu_temp_c')}"))
    else:
        results.append(SubsystemResult("system_metrics", "FAIL", "missing system object"))

    services_obj = status_payload.get("services")
    if isinstance(services_obj, list):
        results.append(SubsystemResult("services_status", "PASS", f"services_count={len(services_obj)}"))
    else:
        results.append(SubsystemResult("services_status", "FAIL", "missing services list"))

    power = status_payload.get("power")
    if isinstance(power, dict):
        if all(power.get(k) is None for k in ["soc_percent", "pack_voltage_v", "current_a"]):
            results.append(SubsystemResult("power_ups", "DEGRADED", "power fields present but null"))
        else:
            results.append(SubsystemResult("power_ups", "PASS", "power fields populated"))
    else:
        results.append(SubsystemResult("power_ups", "FAIL", "missing power object"))

    network = status_payload.get("network")
    if isinstance(network, dict):
        results.append(SubsystemResult("network", "PASS", f"connected={network.get('connected')} ssid={network.get('ssid')}"))
    else:
        results.append(SubsystemResult("network", "FAIL", "missing network object"))

    rf = status_payload.get("rf")
    rf_sensor = status_payload.get("rf_sensor")
    if isinstance(rf, dict) or isinstance(rf_sensor, dict):
        results.append(SubsystemResult("rf_pipeline", "PASS", f"rf_last={rf.get('last_timestamp_ms') if isinstance(rf, dict) else None} rf_sensor_state={rf_sensor.get('state') if isinstance(rf_sensor, dict) else None}"))
    else:
        results.append(SubsystemResult("rf_pipeline", "FAIL", "missing rf/rf_sensor"))

    remote_id = status_payload.get("remote_id")
    if isinstance(remote_id, dict):
        state = remote_id.get("health", {}).get("state") if isinstance(remote_id.get("health"), dict) else remote_id.get("state")
        results.append(SubsystemResult("remoteid", "PASS" if state in ("ok", "OK", "active", None) else "DEGRADED", f"state={state} capture_active={remote_id.get('capture_active')}"))
    else:
        results.append(SubsystemResult("remoteid", "FAIL", "missing remote_id"))

    esp_dev = os.environ.get("NDEFENDER_CTRL_DEV", "/dev/ndefender-esp32")
    if os.path.exists(esp_dev):
        results.append(SubsystemResult("esp32_link", "PASS", f"device={esp_dev}"))
    else:
        results.append(SubsystemResult("esp32_link", "FAIL", f"device not found: {esp_dev}"))

    contact_events = 0
    for msg in ws_messages:
        try:
            payload = json.loads(msg)
            if isinstance(payload.get("type"), str) and payload["type"].startswith("CONTACT_"):
                contact_events += 1
        except Exception:
            continue
    if contact_events > 0:
        results.append(SubsystemResult("contacts_pipeline", "PASS", f"contact_events={contact_events}"))
    else:
        results.append(SubsystemResult("contacts_pipeline", "DEGRADED", "no CONTACT_* events observed in WS capture"))

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", default="http://127.0.0.1:8000/api/v1")
    parser.add_argument("--public", default="https://n.flyspark.in/api/v1")
    parser.add_argument("--out-md", default="reports/README_GREEN_SIGNAL.md")
    parser.add_argument("--out-json", default="reports/green_signal.json")
    args = parser.parse_args()

    base_local = args.local.rstrip("/")
    base_public = args.public.rstrip("/")

    local_rest = [probe_rest(base_local, ep) for ep in REST_ENDPOINTS]
    public_rest = [probe_rest(base_public, ep) for ep in REST_ENDPOINTS]

    local_ws_url = base_local.replace("http://", "ws://") + "/ws"
    public_ws_url = base_public.replace("https://", "wss://") + "/ws"

    local_ws = asyncio.run(probe_ws(local_ws_url))
    public_ws = asyncio.run(probe_ws(public_ws_url))

    cors_targets = [f"{base_public}/status", f"{base_public}/ws"]
    cors_results = []
    for target in cors_targets:
        for origin in ["https://www.figma.com", "http://127.0.0.1"]:
            cors_results.append(probe_cors(target, origin))

    services = {unit: systemctl_show(unit) for unit in SERVICE_UNITS}
    journals = {unit: journal_snippet(unit) for unit in SERVICE_UNITS}

    api_key = os.environ.get("NDEFENDER_API_KEY")
    api_role = os.environ.get("NDEFENDER_API_ROLE")

    command_results, command_error, generic_command_status = run_command_tests(base_local, local_ws_url, api_key, api_role)

    status_payload = fetch_status_payload(base_local)

    ws_messages = []
    if local_ws.first_message:
        ws_messages.append(local_ws.first_message)
    if public_ws.first_message:
        ws_messages.append(public_ws.first_message)

    subsystems = subsystem_checks(status_payload, ws_messages, services)

    missing_keys = []
    if isinstance(status_payload, dict):
        missing_keys = status_key_check(status_payload)

    def rest_summary(results: List[RestResult]) -> List[Dict[str, Any]]:
        out = []
        for r in results:
            out.append({
                "endpoint": r.endpoint,
                "status": r.http_status,
                "latency_ms": r.latency_ms,
                "json_ok": r.json_ok,
                "snippet": r.snippet,
            })
        return out

    result_obj = {
        "meta": {
            "generated_at": now_utc(),
            "hostname": socket.gethostname(),
            "local_base": base_local,
            "public_base": base_public,
        },
        "rest": {
            "local": rest_summary(local_rest),
            "public": rest_summary(public_rest),
        },
        "ws": {
            "local": asdict(local_ws),
            "public": asdict(public_ws),
        },
        "cors": [asdict(c) for c in cors_results],
        "services": {k: asdict(v) for k, v in services.items()},
        "commands": {
            "error": command_error,
            "generic_endpoint_status": generic_command_status,
            "results": [asdict(c) for c in command_results],
        },
        "subsystems": [asdict(s) for s in subsystems],
        "missing_status_keys": missing_keys,
        "diagnosis": {
            "public_rest_ok": all(r.http_status == 200 for r in public_rest),
            "local_rest_ok": all(r.http_status == 200 for r in local_rest),
            "public_ws_ok": public_ws.connect_ok and public_ws.msgs_received > 0,
            "local_ws_ok": local_ws.connect_ok and local_ws.msgs_received > 0,
        },
    }

    Path(os.path.dirname(args.out_md)).mkdir(parents=True, exist_ok=True)
    Path(os.path.dirname(args.out_json)).mkdir(parents=True, exist_ok=True)

    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(result_obj, f, indent=2)

    def format_rest_table(label: str, results: List[RestResult]) -> str:
        lines = [f"### {label}", "| Endpoint | HTTP | JSON | Snippet |", "| --- | --- | --- | --- |"]
        for r in results:
            snippet = r.snippet.replace("\n", " ")[:120]
            lines.append(f"| {r.endpoint} | {r.http_status} | {str(r.json_ok)} | {snippet} |")
        return "\n".join(lines)

    def format_ws(label: str, result: WsResult) -> str:
        return "\n".join([
            f"### {label}",
            f"- connect_ok: {result.connect_ok}",
            f"- msgs_received: {result.msgs_received}",
            f"- first_type: {result.first_type}",
            f"- first_200: {result.first_200}",
        ])

    summary_rows = []
    def comp_row(name: str, ok: bool, evidence: str) -> None:
        summary_rows.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {evidence} |")

    comp_row("Local REST", all(r.http_status == 200 for r in local_rest), "see REST tables")
    comp_row("Public REST", all(r.http_status == 200 for r in public_rest), "see REST tables")
    comp_row("Local WS", local_ws.connect_ok and local_ws.msgs_received > 0, f"msgs={local_ws.msgs_received}")
    comp_row("Public WS", public_ws.connect_ok and public_ws.msgs_received > 0, f"msgs={public_ws.msgs_received}")
    comp_row("CORS", all(c.http_status == 200 for c in cors_results), "OPTIONS /status,/ws")

    now = now_utc()
    lines = [
        "# N-Defender GREEN SIGNAL Report",
        f"Generated: {now}",
        f"Hostname: {socket.gethostname()}",
        "",
        "## Summary",
        "| Component | Status | Evidence |",
        "| --- | --- | --- |",
        *summary_rows,
        "",
        format_rest_table("Local REST", local_rest),
        "",
        format_rest_table("Public REST", public_rest),
        "",
        "## WebSocket",
        format_ws("Local WS", local_ws),
        "",
        format_ws("Public WS", public_ws),
        "",
        "## CORS",
    ]

    for c in cors_results:
        lines.append(f"- {c.url} origin={c.origin} status={c.http_status} allow-origin={c.allow_origin} allow-methods={c.allow_methods} allow-headers={c.allow_headers}")

    lines.append("")
    lines.append("## Command Tests")
    lines.append("Generic endpoint probe (POST):")
    lines.append(", ".join([f"/{k}={v}" for k, v in generic_command_status.items()]))
    if command_error:
        lines.append(f"- error: {command_error}")
    if command_results:
        lines.append("| Command | HTTP | Accepted | Ack | Snippet |")
        lines.append("| --- | --- | --- | --- | --- |")
        for c in command_results:
            snippet = c.response_snippet.replace("\n", " ")[:120]
            lines.append(f"| {c.command} | {c.http_status} | {c.accepted} | {c.ack_received} | {snippet} |")

    lines.append("")
    lines.append("## Services")
    lines.append("| Unit | Active | SubState | MainPID | Error |")
    lines.append("| --- | --- | --- | --- | --- |")
    for unit, res in services.items():
        lines.append(f"| {unit} | {res.active} | {res.substate} | {res.main_pid} | {res.error} |")

    lines.append("")
    lines.append("## Subsystems")
    lines.append("| Name | Status | Evidence |")
    lines.append("| --- | --- | --- |")
    for s in subsystems:
        lines.append(f"| {s.name} | {s.status} | {s.evidence} |")

    lines.append("")
    lines.append("## Missing /status Keys")
    lines.append(", ".join(missing_keys) if missing_keys else "none")

    lines.append("")
    lines.append("## Log Highlights")
    for unit, (_text, highlights) in journals.items():
        lines.append(f"### {unit}")
        if highlights:
            lines.append("```\n" + "\n".join(highlights) + "\n```")
        else:
            lines.append("(no matching error/exception/traceback/ws/403/cloudflare lines)")

    lines.append("")
    if result_obj["diagnosis"]["public_rest_ok"] and result_obj["diagnosis"]["public_ws_ok"] and all(c.http_status == 200 for c in cors_results):
        lines.append("## Conclusion\nGREEN SIGNAL")
    else:
        lines.append("## Conclusion\nRED SIGNAL")
        lines.append("\n## Root Cause If Not Green")
        causes = []
        if not result_obj["diagnosis"]["public_rest_ok"]:
            causes.append("Public REST failing (likely Cloudflare 403 for non-browser clients)")
        if not result_obj["diagnosis"]["public_ws_ok"]:
            causes.append("Public WS not receiving messages")
        if not all(c.http_status == 200 for c in cors_results):
            causes.append("CORS preflight failing")
        lines.extend([f"- {c}" for c in causes])
        lines.append("\n## Fix Plan")
        lines.append("1. Verify Cloudflare WAF Skip rule for /api/v1/* (Managed Rules, BIC, Bot Fight).")
        lines.append("2. Re-run diagnostics after rule is active.")

    out_md = Path(args.out_md)
    out_md.write_text("\n".join(lines), encoding="utf-8")

    print(out_md.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
