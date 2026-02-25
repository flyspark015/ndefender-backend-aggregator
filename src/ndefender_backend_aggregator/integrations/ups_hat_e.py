"""UPS HAT E reader for local power telemetry."""

from __future__ import annotations

import logging
import time
from typing import Any

try:  # Prefer smbus if available on Raspberry Pi images
    from smbus import SMBus
except Exception:  # pragma: no cover - fallback for alternative installs
    try:
        from smbus2 import SMBus  # type: ignore
    except Exception:  # pragma: no cover - no SMBus available
        SMBus = None  # type: ignore

LOGGER = logging.getLogger(__name__)


class UpsHatEReader:
    def __init__(self, i2c_bus: int = 1, i2c_addr: int = 0x2D, keepalive_interval_s: float = 30.0) -> None:
        self._i2c_bus = i2c_bus
        self._i2c_addr = i2c_addr
        self._keepalive_interval_s = keepalive_interval_s
        self._bus: SMBus | None = None
        self._last_keepalive_ts = 0.0
        self._last_error: str | None = None

    @property
    def last_error(self) -> str | None:
        return self._last_error

    def read_status(self) -> dict[str, Any] | None:
        if SMBus is None:
            self._last_error = "smbus_unavailable"
            return None
        try:
            bus = self._ensure_bus()
            if bus is None:
                return None
            self._keepalive_if_needed(bus)
            status = self._read_block(bus, 0x02, 0x01)[0]
            vbus = self._read_block(bus, 0x10, 0x06)
            battery = self._read_block(bus, 0x20, 0x0C)
            cells = self._read_block(bus, 0x30, 0x08)
            self._last_error = None
            return self._decode(status, vbus, battery, cells)
        except Exception as exc:  # pragma: no cover - hardware dependent
            self._last_error = str(exc)
            LOGGER.exception("UPS read failed")
            return None

    def _ensure_bus(self) -> SMBus | None:
        if self._bus is not None:
            return self._bus
        try:
            self._bus = SMBus(self._i2c_bus)
            return self._bus
        except Exception as exc:  # pragma: no cover - hardware dependent
            self._last_error = str(exc)
            LOGGER.exception("Failed to open I2C bus %s", self._i2c_bus)
            return None

    def _keepalive_if_needed(self, bus: SMBus) -> None:
        now = time.time()
        if now - self._last_keepalive_ts < self._keepalive_interval_s:
            return
        try:
            bus.write_byte_data(self._i2c_addr, 0x01, 0x55)
            self._last_keepalive_ts = now
        except Exception as exc:  # pragma: no cover - hardware dependent
            self._last_error = str(exc)
            LOGGER.exception("UPS keepalive write failed")

    def _read_block(self, bus: SMBus, register: int, length: int) -> list[int]:
        return bus.read_i2c_block_data(self._i2c_addr, register, length)

    def _decode(self, status_byte: int, vbus: list[int], battery: list[int], cells: list[int]) -> dict[str, Any]:
        state = self._decode_state(status_byte)
        vbus_mv = self._u16(vbus, 0)
        vbus_mw = self._u16(vbus, 4)

        batt_mv = self._u16(battery, 0)
        current_ma = self._s16(battery, 2)
        soc_percent = self._u16(battery, 4)
        tte_min = self._u16(battery, 8)
        ttf_min = self._u16(battery, 10)

        cell_vs = [
            self._u16(cells, 0),
            self._u16(cells, 2),
            self._u16(cells, 4),
            self._u16(cells, 6),
        ]

        time_to_empty_s = int(tte_min * 60) if current_ma < 0 else None
        time_to_full_s = int(ttf_min * 60) if current_ma >= 0 else None

        return {
            "pack_voltage_v": self._mv_to_v(batt_mv),
            "current_a": self._ma_to_a(current_ma),
            "input_vbus_v": self._mv_to_v(vbus_mv),
            "input_power_w": self._mw_to_w(vbus_mw),
            "soc_percent": self._clamp_percent(soc_percent),
            "time_to_empty_s": time_to_empty_s,
            "time_to_full_s": time_to_full_s,
            "per_cell_v": [self._mv_to_v(v) for v in cell_vs],
            "state": state,
        }

    @staticmethod
    def _decode_state(status_byte: int) -> str:
        if status_byte & 0x40:
            return "FAST_CHARGING"
        if status_byte & 0x80:
            return "CHARGING"
        if status_byte & 0x20:
            return "DISCHARGING"
        return "IDLE"

    @staticmethod
    def _u16(data: list[int], offset: int) -> int:
        return data[offset] | (data[offset + 1] << 8)

    @staticmethod
    def _s16(data: list[int], offset: int) -> int:
        value = UpsHatEReader._u16(data, offset)
        if value & 0x8000:
            value -= 0x10000
        return value

    @staticmethod
    def _mv_to_v(value_mv: int) -> float:
        return round(value_mv / 1000.0, 3)

    @staticmethod
    def _ma_to_a(value_ma: int) -> float:
        return round(value_ma / 1000.0, 3)

    @staticmethod
    def _mw_to_w(value_mw: int) -> float:
        return round(value_mw / 1000.0, 3)

    @staticmethod
    def _clamp_percent(value: int) -> int:
        if value < 0:
            return 0
        if value > 100:
            return 100
        return value
