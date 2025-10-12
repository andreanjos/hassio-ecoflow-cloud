from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN
from .coordinator import Coordinator, DeviceContext
from .ecoflow_mqtt import EcoflowMqttClient
from .mqtt.proto_loader import (
    bind_file_descriptor_set_from_path,
    register_dispatch_from_json,
)


PLATFORMS = [Platform.SENSOR, Platform.SWITCH, Platform.NUMBER]


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    data = entry.data
    client = EcoflowMqttClient(
        broker_host=data["broker_host"],
        broker_port=int(data["broker_port"]),
        client_id=data["client_id"],
        username=data["username"],
        password=data["password"],
    )
    device = DeviceContext(serial=data["serial"], family=data.get("family", "v3"))
    coord = Coordinator(client, device)

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coord,
        "device": device,
        "options": dict(entry.options),
    }

    # Bind v3 descriptors/dispatch if configured
    v3_fds = entry.options.get("v3_fds_path")
    v3_map = entry.options.get("v3_dispatch_path")
    try:
        if v3_fds:
            bind_file_descriptor_set_from_path(v3_fds)
        if v3_map:
            register_dispatch_from_json(v3_map)
    except Exception:
        # Non-fatal; decoding remains tolerant until descriptors provided
        pass

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    coord.start()
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    storage = hass.data.get(DOMAIN, {})
    ctx = storage.get(entry.entry_id)
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ctx:
        coord: Coordinator = ctx.get("coordinator")
        if coord:
            coord.stop()
    storage.pop(entry.entry_id, None)
    return unloaded


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    storage = hass.data.get(DOMAIN, {})
    ctx = storage.get(entry.entry_id)
    if ctx is not None:
        ctx["options"] = dict(entry.options)

