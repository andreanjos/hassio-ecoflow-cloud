from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN
from .mqtt import codec_v3


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    storage = hass.data.get(DOMAIN, {})
    ctx = storage.get(entry.entry_id, {})
    coord = ctx.get("coordinator")
    mqtt_metrics = coord._mqtt.get_metrics() if coord else {}  # type: ignore[attr-defined]
    v3_metrics = codec_v3.get_metrics()
    return {
        "mqtt": mqtt_metrics,
        "v3": v3_metrics,
    }

