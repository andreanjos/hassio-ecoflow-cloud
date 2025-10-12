from __future__ import annotations

from typing import Any, Callable

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, AVAILABILITY_STALE_SECONDS


NUMBER_KEYS: dict[str, tuple[str, str, float, float, float]] = {
    # key: (name, setter_method, min, max, step)
    "number.ac_charge_power": ("AC Charge Power", "set_ac_charge_power", 0.0, 1200.0, 50.0),
    "number.min_soc": ("Minimum SoC", "set_min_soc", 0.0, 100.0, 1.0),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    coord = store["coordinator"]
    options = store.get("options", {})
    controls_enabled = bool(options.get("enable_controls_v3", False))

    entities = []
    for key, (name, method, vmin, vmax, step) in NUMBER_KEYS.items():
        setter = getattr(coord, method) if controls_enabled else None
        entities.append(_SimpleNumber(entry.entry_id, key, name, setter, vmin, vmax, step, coord))

    def _on_state(state: dict[str, Any]) -> None:
        for ent in entities:
            ent.receive_state(state)

    coord.on_state(_on_state)
    async_add_entities(entities)


class _SimpleNumber(NumberEntity):
    _attr_has_entity_name = True

    def __init__(self, entry_id: str, key: str, name: str, setter: Callable[[float], None] | None, vmin: float, vmax: float, step: float, coord) -> None:
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}-{key}"
        self._setter = setter
        self._attr_native_min_value = vmin
        self._attr_native_max_value = vmax
        self._attr_native_step = step
        self._state: float | None = None
        self._coord = coord

    @property
    def native_value(self) -> float | None:
        return self._state

    async def async_set_native_value(self, value: float) -> None:
        if self._setter:
            self._setter(value)

    def receive_state(self, state: dict[str, Any]) -> None:
        if self._key in state:
            self._state = state[self._key]
            self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return self._coord.seconds_since_update() <= AVAILABILITY_STALE_SECONDS

