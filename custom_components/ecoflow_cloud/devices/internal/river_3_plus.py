from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class NormalizedState:
    data: Dict[str, Any]

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)


def build_entities(state: NormalizedState) -> Dict[str, Any]:
    # Minimal placeholders illustrating expected mapping; actual HA entities built elsewhere
    entities: Dict[str, Any] = {
        "sensor.battery": state.get("pd.soc"),
        "sensor.time_remaining": int(state.get("pd.remainTime", 0)) * 60,
        "sensor.input_power": state.get("pd.wattsInSum"),
        "sensor.output_power": state.get("pd.wattsOutSum"),
        "sensor.ac_voltage": state.get("ac.outVolts"),
        "sensor.ac_output_power": state.get("ac.outWatts"),
        "sensor.battery_temperature": state.get("bms.tempC"),
        "attr.grid_present": state.get("grid.present"),
        "attr.charging": state.get("charge.charging"),
        "switch.ac_output": state.get("ac.enabled"),
        "switch.dc_output": state.get("dc.enabled"),
        "switch.x_boost": state.get("inverter.xBoost"),
        "number.ac_charge_power": state.get("charge.acLimitW"),
        "number.min_soc": state.get("bms.minSoc"),
    }
    return entities

