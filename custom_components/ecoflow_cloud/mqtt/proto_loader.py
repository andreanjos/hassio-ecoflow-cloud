from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

from . import codec_v3


def bind_file_descriptor_set_from_path(fds_path: str) -> None:
    data = Path(fds_path).read_bytes()
    codec_v3.bind_file_descriptor_set(data)


def register_dispatch_from_json(mapping_path: str) -> None:
    """Load dispatch mapping {"moduleType,cmd": "full.message.Name"} from JSON."""
    mapping: Dict[str, str] = json.loads(Path(mapping_path).read_text())
    for k, v in mapping.items():
        module_type_str, cmd_str = k.split(",", 1)
        codec_v3.register_dispatch(int(module_type_str.strip()), int(cmd_str.strip()), v)


def register_cmd_dispatch_from_json(mapping_path: str) -> None:
    """Load inner dispatch mapping {"cmdFunc,cmdId": "full.message.Name"} from JSON."""
    mapping: Dict[str, str] = json.loads(Path(mapping_path).read_text())
    for k, v in mapping.items():
        func_str, id_str = k.split(",", 1)
        codec_v3.register_cmd_dispatch(int(func_str.strip()), int(id_str.strip()), v)

