from __future__ import annotations

import base64
import logging
from typing import Any, Dict, Tuple, List

from google.protobuf.message import DecodeError
from google.protobuf import descriptor_pb2, descriptor_pool, message_factory

LOG = logging.getLogger(__name__)


class DynamicEnvelope:
    """Placeholder for dynamic Envelope parser bound at runtime from descriptors."""

    @staticmethod
    def parse_from_bytes(data: bytes):
        raise NotImplementedError


# Dispatch table will be populated when descriptors are loaded
_DISPATCH: Dict[Tuple[int, int], Any] = {}
_POOL: descriptor_pool.DescriptorPool | None = None
_FACTORY: message_factory.MessageFactory | None = None
_DISPATCH_CMD: Dict[Tuple[int, int], Any] = {}

# Metrics
_messages_decoded = 0
_decode_errors = 0


def bind_descriptors(envelope_cls, dispatch_table: Dict[Tuple[int, int], Any]) -> None:
    global DynamicEnvelope, _DISPATCH
    DynamicEnvelope = envelope_cls
    _DISPATCH = dict(dispatch_table)


def bind_file_descriptor_set(descriptor_bytes: bytes) -> None:
    """Bind a FileDescriptorSet so we can construct message classes by name later.

    This enables dynamic parsing without generated Python code.
    """
    global _POOL, _FACTORY
    fds = descriptor_pb2.FileDescriptorSet()
    fds.MergeFromString(descriptor_bytes)
    pool = descriptor_pool.DescriptorPool()
    for fd_proto in fds.file:
        pool.Add(fd_proto)
    _POOL = pool
    _FACTORY = message_factory.MessageFactory(pool)


def register_dispatch(module_type: int, cmd: int, full_message_name: str) -> None:
    """Register a (moduleType, cmd) → protobuf full message name mapping."""
    if _POOL is None or _FACTORY is None:
        raise RuntimeError("Descriptor pool not bound; call bind_file_descriptor_set first")
    desc = _POOL.FindMessageTypeByName(full_message_name)
    cls = _FACTORY.GetMessageClass(desc)
    _DISPATCH[(int(module_type), int(cmd))] = cls


def register_cmd_dispatch(cmd_func: int, cmd_id: int, full_message_name: str) -> None:
    """Register a (cmd_func, cmd_id) → protobuf full message name mapping for inner v3 messages."""
    if _POOL is None or _FACTORY is None:
        raise RuntimeError("Descriptor pool not bound; call bind_file_descriptor_set first")
    desc = _POOL.FindMessageTypeByName(full_message_name)
    cls = _FACTORY.GetMessageClass(desc)
    _DISPATCH_CMD[(int(cmd_func), int(cmd_id))] = cls


def _try_find_message(names: List[str]):
    if _POOL is None or _FACTORY is None:
        return None
    for name in names:
        try:
            desc = _POOL.FindMessageTypeByName(name)
            return _FACTORY.GetPrototype(desc)
        except Exception:
            continue
    return None


def _xor_in_place(buf: bytearray, key: int) -> None:
    if key <= 0:
        return
    key &= 0xFF
    for i in range(len(buf)):
        buf[i] ^= key


def _ensure_common_descriptors() -> None:
    """Ensure minimal Common (Header/Send_Header_Msg) descriptors are present.

    If the app-provided FDS is not bound, try to synthesize a minimal schema that
    allows parsing of Header.pdata, seq, cmd_func, cmd_id fields and Send_Header_Msg.msg.
    """
    global _POOL, _FACTORY
    if _POOL is not None and _FACTORY is not None:
        # Already have a pool; nothing to do
        return
    # Build a tiny FileDescriptorSet for Common.proto subset
    fds = descriptor_pb2.FileDescriptorSet()
    file_proto = fds.file.add()
    file_proto.name = "Common.proto"
    file_proto.package = "Common"

    # message Header { bytes pdata = 1; int32 src=2; int32 dest=3; int32 d_src=4; int32 d_dest=5; int32 enc_type=6; int32 check_type=7; int32 cmd_func=8; int32 cmd_id=9; int32 data_len=10; int32 need_ack=11; int32 is_ack=12; int32 seq=14; }
    header = file_proto.message_type.add()
    header.name = "Header"
    # pdata
    f = header.field.add(); f.name = "pdata"; f.number = 1; f.label = 1; f.type = 12  # TYPE_BYTES
    # src/dest
    for name, num in (("src", 2), ("dest", 3), ("d_src", 4), ("d_dest", 5), ("enc_type", 6), ("check_type", 7), ("cmd_func", 8), ("cmd_id", 9), ("data_len", 10), ("need_ack", 11), ("is_ack", 12), ("seq", 14)):
        f2 = header.field.add(); f2.name = name; f2.number = num; f2.label = 1; f2.type = 5  # TYPE_INT32

    # message Send_Header_Msg { repeated Header msg = 1; }
    send = file_proto.message_type.add()
    send.name = "Send_Header_Msg"
    fmsg = send.field.add(); fmsg.name = "msg"; fmsg.number = 1; fmsg.label = 3; fmsg.type = 11; fmsg.type_name = ".Common.Header"

    pool = descriptor_pool.DescriptorPool()
    pool.Add(file_proto)
    _POOL = pool
    _FACTORY = message_factory.MessageFactory(pool)


def _normalize(msg: Any) -> Dict[str, Any]:
    # Map parsed message fields to normalized keys expected by the profile
    out: Dict[str, Any] = {}
    # Implement minimal, tolerant field access; real mapping will be filled after descriptors
    # Examples shown; keys guarded via hasattr
    if hasattr(msg, "soc"):
        out["pd.soc"] = int(getattr(msg, "soc"))
    if hasattr(msg, "remain_minutes"):
        out["pd.remainTime"] = int(getattr(msg, "remain_minutes"))
    if hasattr(msg, "ac_out_watts"):
        out["ac.outWatts"] = int(getattr(msg, "ac_out_watts"))
    if hasattr(msg, "ac_out_volts"):
        out["ac.outVolts"] = float(getattr(msg, "ac_out_volts"))
    if hasattr(msg, "ac_enabled"):
        out["ac.enabled"] = bool(getattr(msg, "ac_enabled"))
    if hasattr(msg, "dc_out_watts"):
        out["dc.outWatts"] = int(getattr(msg, "dc_out_watts"))
    if hasattr(msg, "dc_enabled"):
        out["dc.enabled"] = bool(getattr(msg, "dc_enabled"))
    if hasattr(msg, "grid_present"):
        out["grid.present"] = bool(getattr(msg, "grid_present"))
    if hasattr(msg, "charging"):
        out["charge.charging"] = bool(getattr(msg, "charging"))
    if hasattr(msg, "temp_c"):
        out["bms.tempC"] = float(getattr(msg, "temp_c"))
    if hasattr(msg, "min_soc"):
        out["bms.minSoc"] = int(getattr(msg, "min_soc"))
    if hasattr(msg, "ac_limit_w"):
        out["charge.acLimitW"] = int(getattr(msg, "ac_limit_w"))
    if hasattr(msg, "xboost"):
        out["inverter.xBoost"] = bool(getattr(msg, "xboost"))
    # Aggregate totals if present
    if hasattr(msg, "watts_in_sum"):
        out["pd.wattsInSum"] = int(getattr(msg, "watts_in_sum"))
    if hasattr(msg, "watts_out_sum"):
        out["pd.wattsOutSum"] = int(getattr(msg, "watts_out_sum"))
    return out


def decode_v3(envelope: Dict[str, Any]) -> Dict[str, Any]:
    """Decode v3 protobuf payload carried in JSON envelope to normalized dict.

    envelope keys: moduleType (int), cmd (int), pData (base64 string), ts (optional)
    """
    global _messages_decoded, _decode_errors
    try:
        module_type = int(envelope.get("moduleType", -1))
        cmd = int(envelope.get("cmd", -1))
        p_data_b64 = envelope.get("pData")
        if not p_data_b64:
            return {}
        data = base64.b64decode(p_data_b64)

        # Attempt v3 Common envelope (Send_Header_Msg → repeated Header)
        # Build minimal Common descriptors on the fly if none were bound
        _ensure_common_descriptors()
        send_names = [
            "Send_Header_Msg",
            "Common.Send_Header_Msg",
            "com.ecoflow.corebiz.mqtt.proto.Send_Header_Msg",
            "com.ecoflow.corebiz.mqtt.proto.Common.Send_Header_Msg",
        ]
        header_names = [
            "Header",
            "Common.Header",
            "com.ecoflow.corebiz.mqtt.proto.Header",
            "com.ecoflow.corebiz.mqtt.proto.Common.Header",
        ]
        send_cls = _try_find_message(send_names)
        header_cls = _try_find_message(header_names)
        LOG.debug(f"Common envelope parsing: send_cls={send_cls}, header_cls={header_cls}")
        
        # Fallback: try to import the message classes directly if dynamic loading fails
        if send_cls is None or header_cls is None:
            try:
                from protos.Common_pb2 import Send_Header_Msg, Header
                send_cls = Send_Header_Msg
                header_cls = Header
                LOG.debug(f"Using direct imports: send_cls={send_cls}, header_cls={header_cls}")
            except ImportError:
                LOG.debug("Could not import Common_pb2 directly")
        
        if send_cls is not None and header_cls is not None:
            try:
                send_obj = send_cls.FromString(data) if hasattr(send_cls, "FromString") else send_cls.ParseFromString(data)
                headers = []
                if hasattr(send_obj, "msg"):
                    headers = list(getattr(send_obj, "msg"))
                else:
                    # Fallback: scan for first repeated Header field
                    if hasattr(send_obj, "ListFields"):
                        for fd, value in send_obj.ListFields():  # type: ignore[attr-defined]
                            try:
                                if isinstance(value, list) and value and isinstance(value[0], header_cls):
                                    headers = list(value)
                                    break
                            except Exception:
                                pass
                normalized_out: Dict[str, Any] = {}
                for h in headers:
                    enc_type = int(getattr(h, "enc_type", getattr(h, "encType", 0)))
                    seq = int(getattr(h, "seq", 0))
                    cmd_func = int(getattr(h, "cmd_func", getattr(h, "cmdFunc", 0)))
                    cmd_id = int(getattr(h, "cmd_id", getattr(h, "cmdId", 0)))
                    pdata = bytes(getattr(h, "pdata", b""))
                    if enc_type == 1 and pdata:
                        buf = bytearray(pdata)
                        _xor_in_place(buf, seq)
                        pdata = bytes(buf)
                    parser_inner = _DISPATCH_CMD.get((cmd_func, cmd_id))
                    if parser_inner is None:
                        LOG.debug("v3 inner message not bound: cmd_func=%s cmd_id=%s", cmd_func, cmd_id)
                        continue
                    inner = parser_inner.FromString(pdata) if hasattr(parser_inner, "FromString") else parser_inner.ParseFromString(pdata)
                    normalized_out.update(_normalize(inner))
                if normalized_out:
                    _messages_decoded += 1
                    return normalized_out
            except DecodeError:
                _decode_errors += 1
            except Exception:
                LOG.debug("v3 Common envelope parse failed; trying legacy module/cmd")

        # Legacy: dispatch by (moduleType, cmd)
        parser = _DISPATCH.get((module_type, cmd))
        if parser is None:
            LOG.debug("unknown v3 frame moduleType=%s cmd=%s (unbound)", module_type, cmd)
            return {}
        msg = parser.FromString(data) if hasattr(parser, "FromString") else parser.ParseFromString(data)
        normalized = _normalize(msg)
        if normalized:
            _messages_decoded += 1
        return normalized
    except DecodeError:
        _decode_errors += 1
        LOG.debug("decode error for v3 frame moduleType=%s cmd=%s", envelope.get("moduleType"), envelope.get("cmd"))
        return {}
    except Exception:
        _decode_errors += 1
        LOG.exception("unexpected error decoding v3 payload")
        return {}


def get_metrics() -> Dict[str, int]:
    return {"messages_decoded": _messages_decoded, "decode_errors": _decode_errors}


def reset_metrics() -> None:
    global _messages_decoded, _decode_errors
    _messages_decoded = 0
    _decode_errors = 0

