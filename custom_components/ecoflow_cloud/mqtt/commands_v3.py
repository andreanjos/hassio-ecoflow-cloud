from __future__ import annotations

from typing import Any, Dict
from google.protobuf import descriptor_pool, message_factory, descriptor_pb2


def _bool(v: bool) -> int:
    return 1 if v else 0


def set_ac_output(enabled: bool) -> bytes:
    return _encode_command({"type": "AC_OUT_TOGGLE", "enable": _bool(enabled)})


def set_dc_output(enabled: bool) -> bytes:
    return _encode_command({"type": "DC_OUT_TOGGLE", "enable": _bool(enabled)})


def set_min_soc(percent: int) -> bytes:
    p = 0 if percent < 0 else 100 if percent > 100 else int(percent)
    return _encode_command({"type": "SET_MIN_SOC", "min_soc": p})


def set_ac_charge_power(watts: int) -> bytes:
    w = 0 if watts < 0 else int(watts)
    return _encode_command({"type": "SET_AC_LIMIT_W", "ac_limit_w": w})


def set_xboost(enabled: bool) -> bytes:
    return _encode_command({"type": "SET_XBOOST", "xboost": _bool(enabled)})


_POOL: descriptor_pool.DescriptorPool | None = None
_FACTORY: message_factory.MessageFactory | None = None


def bind_file_descriptor_set(descriptor_bytes: bytes) -> None:
    global _POOL, _FACTORY
    fds = descriptor_pb2.FileDescriptorSet()
    fds.MergeFromString(descriptor_bytes)
    pool = descriptor_pool.DescriptorPool()
    for fd_proto in fds.file:
        pool.Add(fd_proto)
    _POOL = pool
    _FACTORY = message_factory.MessageFactory(pool)


def build_message(full_message_name: str, fields: Dict[str, Any]) -> bytes:
    if _POOL is None or _FACTORY is None:
        # Fallback to JSON stub
        import json

        return json.dumps(fields, separators=(",", ":")).encode("utf-8")
    desc = _POOL.FindMessageTypeByName(full_message_name)
    cls = _FACTORY.GetPrototype(desc)
    msg = cls()
    for k, v in fields.items():
        setattr(msg, k, v)
    return msg.SerializeToString()


def _encode_command(payload: Dict[str, Any]) -> bytes:
    # Placeholder entrypoint; in real code, select correct full message name from payload["type"]
    return build_message("ecoflow.v3.Command", payload)

