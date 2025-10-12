from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from ..const import FAMILY_JSON, FAMILY_V3


@dataclass(frozen=True)
class DeviceProfile:
    product_codes: tuple[str, ...]
    family: str
    profile_module: str


_REGISTRY: Dict[str, DeviceProfile] = {}


def register_defaults() -> None:
    # Existing families would be pre-registered elsewhere. Add River 3 Plus.
    _REGISTRY["RIVER_3_PLUS"] = DeviceProfile(
        product_codes=("R3P", "RIVER_3_PLUS"),
        family=FAMILY_V3,
        profile_module=".internal.river_3_plus",
    )


def find_profile_by_product(product_code: str) -> Optional[DeviceProfile]:
    for profile in _REGISTRY.values():
        if product_code in profile.product_codes:
            return profile
    return None

