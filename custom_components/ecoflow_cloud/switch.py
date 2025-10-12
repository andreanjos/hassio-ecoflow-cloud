from __future__ import annotations

from typing import Any, Callable

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, AVAILABILITY_STALE_SECONDS


SWITCH_KEYS: dict[str, tuple[str, str]] = {
    "switch.ac_output": ("AC Output", "set_ac_output"),
    "switch.dc_output": ("DC Output", "set_dc_output"),
    "switch.x_boost": ("X-Boost", "set_xboost"),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    coord = store["coordinator"]
    options = store.get("options", {})
    controls_enabled = bool(options.get("enable_controls_v3", False))

    entities = []
    for key, (name, method) in SWITCH_KEYS.items():
        setter = getattr(coord, method) if controls_enabled else None
        entities.append(_SimpleSwitch(entry.entry_id, key, name, setter, coord))

    def _on_state(state: dict[str, Any]) -> None:
        for ent in entities:
            ent.receive_state(state)

    coord.on_state(_on_state)
    async_add_entities(entities)


class _SimpleSwitch(SwitchEntity):
    _attr_has_entity_name = True

    def __init__(self, entry_id: str, key: str, name: str, setter: Callable[[bool], None] | None, coord) -> None:
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}-{key}"
        self._is_on = False
        self._setter = setter
        self._coord = coord

    @property
    def is_on(self) -> bool:
        return self._is_on

    def turn_on(self, **kwargs) -> None:
        if self._setter:
            self._setter(True)

    def turn_off(self, **kwargs) -> None:
        if self._setter:
            self._setter(False)

    def receive_state(self, state: dict[str, Any]) -> None:
        if self._key in state:
            self._is_on = bool(state[self._key])
            self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return self._coord.seconds_since_update() <= AVAILABILITY_STALE_SECONDS

