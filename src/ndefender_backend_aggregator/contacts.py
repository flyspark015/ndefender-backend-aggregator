"""Contact unification and sorting."""

from __future__ import annotations

import asyncio
import time
from typing import Any

from .state import StateStore


class ContactStore:
    def __init__(self, state_store: StateStore) -> None:
        self._state_store = state_store
        self._lock = asyncio.Lock()
        self._remoteid: dict[str, dict[str, Any]] = {}
        self._rf: dict[str, dict[str, Any]] = {}
        self._fpv: dict[str, dict[str, Any]] = {}
        self._replay: dict[str, Any] = {"active": False, "source": "none"}
        self._remoteid_ttl_ms = 15000

    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.5

    async def update_remoteid(
        self,
        event_type: str,
        data: dict[str, Any],
        timestamp_ms: int,
    ) -> None:
        contact_id = data.get("id")
        if not contact_id:
            return
        now_ms = int(time.time() * 1000)
        last_seen_ts = self._normalize_ts(data.get("last_seen_ts") or timestamp_ms)
        async with self._lock:
            replay_active = bool(self._replay.get("active"))
        if not replay_active:
            if self._is_test_contact(data):
                return
            if now_ms - last_seen_ts > self._remoteid_ttl_ms:
                async with self._lock:
                    self._remoteid.pop(contact_id, None)
                    contacts = self._merged_contacts()
                    replay = dict(self._replay)
                await self._state_store.update_section("contacts", contacts)
                await self._state_store.update_section("replay", replay)
                return
        async with self._lock:
            if event_type == "CONTACT_LOST":
                self._remoteid.pop(contact_id, None)
            else:
                contact = self._build_contact(
                    data,
                    contact_id,
                    contact_type="REMOTE_ID",
                    source="remoteid",
                    last_seen_ts=last_seen_ts,
                    severity="unknown",
                )
                self._remoteid[contact_id] = contact
            contacts = self._merged_contacts()
            replay = dict(self._replay)
        await self._state_store.update_section("contacts", contacts)
        await self._state_store.update_section("replay", replay)

    async def update_rf(self, event_type: str, data: dict[str, Any], timestamp_ms: int) -> None:
        contact_id = data.get("id") or f"rf:{data.get('freq_hz', 'unknown')}"
        async with self._lock:
            if event_type == "RF_CONTACT_LOST":
                self._rf.pop(contact_id, None)
            else:
                severity = self._severity_from_confidence(data.get("confidence"))
                contact = self._build_contact(
                    data,
                    contact_id,
                    contact_type="RF",
                    source="antsdr",
                    last_seen_ts=timestamp_ms,
                    severity=severity,
                )
                self._rf[contact_id] = contact
            contacts = self._merged_contacts()
            replay = dict(self._replay)
        await self._state_store.update_section("contacts", contacts)
        await self._state_store.update_section("replay", replay)

    async def update_fpv(self, telemetry: dict[str, Any], timestamp_ms: int) -> None:
        vrx_list = telemetry.get("vrx") or []
        now_ms = int(time.time() * 1000)
        last_seen_ts = timestamp_ms
        last_seen_uptime_ms = None
        if timestamp_ms < 100000000000:
            last_seen_uptime_ms = timestamp_ms
            last_seen_ts = now_ms
        async with self._lock:
            if not vrx_list:
                self._fpv.clear()
            else:
                strongest = max(vrx_list, key=lambda item: item.get("rssi_raw") or 0)
                vrx_id = strongest.get("id", "unknown")
                contact_id = f"fpv:{vrx_id}"
                contact = {
                    "id": contact_id,
                    "type": "FPV",
                    "source": "esp32",
                    "last_seen_ts": last_seen_ts,
                    "severity": "unknown",
                    "vrx_id": vrx_id,
                    "freq_hz": strongest.get("freq_hz"),
                    "rssi_raw": strongest.get("rssi_raw"),
                    "selected": telemetry.get("sel"),
                }
                if last_seen_uptime_ms is not None:
                    contact["last_seen_uptime_ms"] = last_seen_uptime_ms
                self._fpv = {contact_id: contact}
            contacts = self._merged_contacts()
            replay = dict(self._replay)
        await self._state_store.update_section("contacts", contacts)
        await self._state_store.update_section("replay", replay)

    async def update_replay(self, data: dict[str, Any]) -> None:
        state = str(data.get("state") or "").lower()
        active = state not in {"", "stopped", "idle", "disabled", "off"}
        async with self._lock:
            self._replay = {"active": active, "source": "remoteid" if active else "none"}
            contacts = self._merged_contacts()
            replay = dict(self._replay)
        await self._state_store.update_section("contacts", contacts)
        await self._state_store.update_section("replay", replay)

    async def replay_active(self) -> bool:
        async with self._lock:
            return bool(self._replay.get("active"))

    async def remoteid_count(self) -> int:
        async with self._lock:
            return len(self._remoteid)

    def _merged_contacts(self) -> list[dict[str, Any]]:
        merged = [*self._remoteid.values(), *self._rf.values(), *self._fpv.values()]
        if not self._replay.get("active"):
            merged = [c for c in merged if not self._is_test_contact(c)]
            now_ms = int(time.time() * 1000)
            merged = [
                c
                for c in merged
                if c.get("type") != "REMOTE_ID"
                or now_ms - self._normalize_ts(c.get("last_seen_ts") or 0) <= self._remoteid_ttl_ms
            ]
        merged.sort(key=self._sort_key)
        return merged

    @staticmethod
    def _build_contact(
        data: dict[str, Any],
        contact_id: str,
        contact_type: str,
        source: str,
        last_seen_ts: int,
        severity: str,
    ) -> dict[str, Any]:
        filtered = {k: v for k, v in data.items() if k not in {"type", "last_seen_ts"}}
        filtered.update(
            {
                "id": contact_id,
                "type": contact_type,
                "source": source,
                "last_seen_ts": last_seen_ts,
                "severity": severity,
            }
        )
        return filtered

    @staticmethod
    def _severity_from_confidence(confidence: Any) -> str:
        if confidence is None:
            return "unknown"
        try:
            value = float(confidence)
        except (TypeError, ValueError):
            return "unknown"
        if value >= ContactStore.HIGH_CONFIDENCE:
            return "high"
        if value >= ContactStore.MEDIUM_CONFIDENCE:
            return "medium"
        return "low"

    @staticmethod
    def _normalize_ts(value: Any) -> int:
        try:
            ts = int(value)
        except (TypeError, ValueError):
            return int(time.time() * 1000)
        if ts < 100000000000:  # seconds -> ms
            return ts * 1000
        return ts

    @staticmethod
    def _is_test_contact(data: dict[str, Any]) -> bool:
        markers = ("testdrone", "warmstart")
        for value in data.values():
            if isinstance(value, str):
                lowered = value.lower()
                if any(marker in lowered for marker in markers):
                    return True
        return False

    @staticmethod
    def _sort_key(contact: dict[str, Any]) -> tuple[int, float, int]:
        severity_rank = {"critical": 3, "high": 2, "medium": 1, "low": 0, "unknown": -1}
        severity_weight = severity_rank.get(str(contact.get("severity", "unknown")).lower(), -1)
        distance = contact.get("distance_m")
        distance_value = float(distance) if distance is not None else float("inf")
        last_seen = int(contact.get("last_seen_ts") or 0)
        return (-severity_weight, distance_value, -last_seen)
