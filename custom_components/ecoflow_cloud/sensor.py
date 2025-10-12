from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, AVAILABILITY_STALE_SECONDS


SENSOR_KEYS = {
    "sensor.battery": ("Battery", None),
    "sensor.time_remaining": ("Time Remaining", "s"),
    "sensor.input_power": ("Input Power", "W"),
    "sensor.output_power": ("Output Power", "W"),
    "sensor.ac_voltage": ("AC Voltage", "V"),
    "sensor.ac_output_power": ("AC Output Power", "W"),
    "sensor.battery_temperature": ("Battery Temperature", "°C"),
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    store = hass.data[DOMAIN][entry.entry_id]
    coord = store["coordinator"]

    entities = [
        _SimpleSensor(entry.entry_id, key, name, unit, coord) for key, (name, unit) in SENSOR_KEYS.items()
    ]

    def _on_state(state: dict[str, Any]) -> None:
        for ent in entities:
            ent.receive_state(state)

    coord.on_state(_on_state)
    async_add_entities(entities)


class _SimpleSensor(SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, entry_id: str, key: str, name: str, unit: str | None, coord) -> None:
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}-{key}"
        self._attr_native_unit_of_measurement = unit
        self._state: Any = None
        self._coord = coord

    @property
    def native_value(self) -> Any:
        return self._state

    def receive_state(self, state: dict[str, Any]) -> None:
        if self._key in state:
            self._state = state[self._key]
            self.async_write_ha_state()

    @property
    def available(self) -> bool:
        return self._coord.seconds_since_update() <= AVAILABILITY_STALE_SECONDS

