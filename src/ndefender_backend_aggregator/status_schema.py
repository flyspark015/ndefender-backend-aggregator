"""Canonical StatusSnapshot schema fill utilities."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any


def _default_system() -> dict[str, Any]:
    return {
        "cpu_temp_c": None,
        "cpu_usage_percent": None,
        "load_1m": None,
        "load_5m": None,
        "load_15m": None,
        "ram_used_mb": None,
        "ram_total_mb": None,
        "disk_used_gb": None,
        "disk_total_gb": None,
        "uptime_s": None,
        "throttled_flags": None,
        "status": "degraded",
    }


def _default_power() -> dict[str, Any]:
    return {
        "pack_voltage_v": None,
        "current_a": None,
        "input_vbus_v": None,
        "input_power_w": None,
        "soc_percent": None,
        "state": None,
        "time_to_empty_s": None,
        "time_to_full_s": None,
        "status": "degraded",
    }


def _default_rf() -> dict[str, Any]:
    return {
        "last_event": None,
        "last_event_type": None,
        "last_timestamp_ms": None,
        "scan_active": None,
        "status": "unknown",
        "last_error": None,
    }


def _default_remote_id() -> dict[str, Any]:
    return {
        "last_event": None,
        "last_event_type": None,
        "last_timestamp_ms": None,
        "state": None,
        "mode": "live",
        "capture_active": None,
        "contacts_active": None,
        "last_update_ms": None,
        "last_error": None,
    }


def _default_vrx() -> dict[str, Any]:
    return {
        "selected": None,
        "vrx": [],
        "led": {},
        "sys": {"status": "DISCONNECTED"},
        "scan_state": "idle",
    }


def _default_fpv() -> dict[str, Any]:
    return {
        "selected": None,
        "locked_channels": [],
        "rssi_raw": None,
        "scan_state": "idle",
        "freq_hz": None,
    }


def _default_video() -> dict[str, Any]:
    return {"selected": None, "status": "unknown"}


def _default_network() -> dict[str, Any]:
    return {
        "connected": None,
        "ip_v4": None,
        "ip_v6": None,
        "ssid": None,
        "wifi": None,
        "bluetooth": None,
    }


def _default_audio() -> dict[str, Any]:
    return {"muted": None, "volume_percent": None, "status": "unknown"}


def _default_gps() -> dict[str, Any]:
    return {
        "timestamp_ms": None,
        "fix": None,
        "satellites": None,
        "hdop": None,
        "vdop": None,
        "pdop": None,
        "latitude": None,
        "longitude": None,
        "altitude_m": None,
        "speed_m_s": None,
        "heading_deg": None,
        "last_update_ms": None,
        "age_ms": None,
        "source": None,
        "last_error": None,
    }


def _default_esp32() -> dict[str, Any]:
    return {
        "timestamp_ms": None,
        "connected": None,
        "last_seen_ms": None,
        "rtt_ms": None,
        "fw_version": None,
        "heartbeat": None,
        "capabilities": None,
        "last_error": None,
    }


def _default_antsdr() -> dict[str, Any]:
    return {
        "timestamp_ms": None,
        "connected": None,
        "uri": None,
        "temperature_c": None,
        "last_error": None,
    }


def _default_replay() -> dict[str, Any]:
    return {"active": False, "source": "none"}


def _merge_section(section: Any, defaults: dict[str, Any]) -> dict[str, Any]:
    base = section if isinstance(section, dict) else {}
    merged = dict(defaults)
    merged.update(base)
    return merged


def _infer_ok(section: dict[str, Any], fields: list[str]) -> bool:
    for key in fields:
        if section.get(key) is not None:
            return True
    return False


def _overall_ok(snapshot: dict[str, Any]) -> bool:
    for key in ("system", "power", "audio"):
        section = snapshot.get(key)
        if isinstance(section, dict):
            status = str(section.get("status") or "").lower()
            if status in {"degraded", "error", "stopped", "offline"}:
                return False
    remote = snapshot.get("remote_id")
    if isinstance(remote, dict):
        state = str(remote.get("state") or "").lower()
        if state in {"degraded", "error", "stopped", "offline"}:
            return False
    return True


def fill_status_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    filled = dict(snapshot)

    filled["system"] = _merge_section(filled.get("system"), _default_system())
    filled["power"] = _merge_section(filled.get("power"), _default_power())
    filled["rf"] = _merge_section(filled.get("rf"), _default_rf())
    filled["remote_id"] = _merge_section(filled.get("remote_id"), _default_remote_id())
    filled["gps"] = _merge_section(filled.get("gps"), _default_gps())
    filled["esp32"] = _merge_section(filled.get("esp32"), _default_esp32())
    filled["antsdr"] = _merge_section(filled.get("antsdr"), _default_antsdr())
    filled["vrx"] = _merge_section(filled.get("vrx"), _default_vrx())
    filled["fpv"] = _merge_section(filled.get("fpv"), _default_fpv())
    filled["video"] = _merge_section(filled.get("video"), _default_video())
    filled["network"] = _merge_section(filled.get("network"), _default_network())
    filled["audio"] = _merge_section(filled.get("audio"), _default_audio())

    if filled["system"].get("status") in (None, "unknown") and _infer_ok(
        filled["system"], ["cpu_temp_c", "cpu_usage_percent", "ram_used_mb", "disk_used_gb"]
    ):
        filled["system"]["status"] = "ok"

    if filled["power"].get("status") in (None, "unknown", "degraded") and _infer_ok(
        filled["power"], ["pack_voltage_v", "current_a", "soc_percent", "input_vbus_v"]
    ):
        filled["power"]["status"] = "ok"

    if filled["audio"].get("status") in (None, "unknown") and filled["audio"].get("muted") is not None:
        filled["audio"]["status"] = "ok"

    _mirror_vrx_to_fpv(filled)
    _apply_video_health(filled)

    if not isinstance(filled.get("services"), list):
        filled["services"] = []
    if not isinstance(filled.get("contacts"), list):
        filled["contacts"] = []

    filled["replay"] = _merge_section(filled.get("replay"), _default_replay())

    if "timestamp_ms" not in filled:
        filled["timestamp_ms"] = int(time.time() * 1000)

    filled["overall_ok"] = _overall_ok(filled)
    return filled


def _mirror_vrx_to_fpv(snapshot: dict[str, Any]) -> None:
    vrx = snapshot.get("vrx")
    fpv = snapshot.get("fpv")
    if not isinstance(vrx, dict) or not isinstance(fpv, dict):
        return
    selected = vrx.get("selected")
    if selected is None:
        return
    vrx_list = vrx.get("vrx") or []
    if not isinstance(vrx_list, list):
        return
    match = next((item for item in vrx_list if isinstance(item, dict) and item.get("id") == selected), None)
    if not match:
        return
    fpv["selected"] = selected
    fpv["freq_hz"] = match.get("freq_hz")
    fpv["rssi_raw"] = match.get("rssi_raw")
    if vrx.get("scan_state") is not None:
        fpv["scan_state"] = vrx.get("scan_state")


def _apply_video_health(snapshot: dict[str, Any]) -> None:
    video = snapshot.get("video")
    if not isinstance(video, dict):
        return
    if video.get("status") not in (None, "unknown"):
        return
    has_device = any(Path("/dev").glob("video*"))
    video["status"] = "ok" if has_device else "offline"
