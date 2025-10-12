from __future__ import annotations

import json
import logging
from dataclasses import dataclass
import time
from typing import Any, Callable, Dict, Optional

from .const import FAMILY_V3
from .ecoflow_mqtt import EcoflowMqttClient
from .mqtt import decode_envelope
from .mqtt import commands_v3


LOG = logging.getLogger(__name__)


@dataclass
class DeviceContext:
    serial: str
    family: str


class Coordinator:
    def __init__(self, mqtt_client: EcoflowMqttClient, device: DeviceContext) -> None:
        self._mqtt = mqtt_client
        self._device = device
        self._state: Dict[str, Any] = {}
        self._listeners: list[Callable[[Dict[str, Any]], None]] = []
        self._last_update_monotonic = 0.0

        self._mqtt.set_message_handler(self._handle_message)

    def start(self) -> None:
        topic = f"/app/device/property/{self._device.serial}"
        self._mqtt.subscribe(topic, qos=0)
        self._mqtt.connect_and_start()

    def stop(self) -> None:
        self._mqtt.stop()

    def on_state(self, cb: Callable[[Dict[str, Any]], None]) -> None:
        self._listeners.append(cb)

    # Commands (publish only when connected)
    def set_ac_output(self, enabled: bool) -> None:
        payload = commands_v3.set_ac_output(enabled)
        self._publish_command(payload)

    def set_dc_output(self, enabled: bool) -> None:
        payload = commands_v3.set_dc_output(enabled)
        self._publish_command(payload)

    def set_min_soc(self, percent: int) -> None:
        payload = commands_v3.set_min_soc(percent)
        self._publish_command(payload)

    def set_ac_charge_power(self, watts: int) -> None:
        payload = commands_v3.set_ac_charge_power(watts)
        self._publish_command(payload)

    def set_xboost(self, enabled: bool) -> None:
        payload = commands_v3.set_xboost(enabled)
        self._publish_command(payload)

    # Internal
    def _publish_command(self, payload_bytes: bytes) -> None:
        topic = f"/app/device/thing/property/set/{self._device.serial}"
        self._mqtt.publish_base64(topic, payload_bytes, qos=0, retain=False)

    def _handle_message(self, topic: str, data: Dict[str, Any]) -> None:
        try:
            raw = data.get("raw")
            if not raw:
                return
            envelope = json.loads(raw.decode("utf-8"))
            normalized = decode_envelope(self._device.family, envelope)
            if not normalized:
                return
            self._state.update(normalized)
            self._last_update_monotonic = time.monotonic()
            if self._listeners:
                snapshot = dict(self._state)
                for cb in list(self._listeners):
                    cb(snapshot)

    def seconds_since_update(self) -> int:
        if self._last_update_monotonic <= 0:
            return 1_000_000
        return int(max(0.0, time.monotonic() - self._last_update_monotonic))
        except Exception:
            LOG.exception("failed to process MQTT message on %s", topic)

