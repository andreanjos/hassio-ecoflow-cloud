from __future__ import annotations

from typing import Any, Dict

from ..const import FAMILY_JSON, FAMILY_V3
from . import codec_v3


def decode_envelope(family: str, envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Decode device payload based on model family into normalized dict used by profiles."""
    if family == FAMILY_V3:
        return codec_v3.decode_v3(envelope)
    # JSON family is already normalized upstream; pass-through
    if family == FAMILY_JSON:
        return envelope
    return {}

