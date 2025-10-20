import logging

_LOGGER = logging.getLogger(__name__)

plain_to_status: dict[str, str] = {
    "pd": "pdStatus",
    "mppt": "mpptStatus",
    "bms_emsStatus": "emsStatus",
    "bms_bmsStatus": "bmsStatus",
    "bms_bmsInfo": "bmsInfo",
    "inv": "invStatus",
    "bms_slave": "bmsSlaveStatus",
    "bms_slave_bmsSlaveStatus_1": "bmsSlaveStatus_1",
    "bms_slave_bmsSlaveStatus_2": "bmsSlaveStatus_2",
}

status_to_plain = dict((v, k) for (k, v) in plain_to_status.items())


def to_plain(raw_data: dict[str, any]) -> dict[str, any]:
    new_params = {}
    prefix = ""
    if "typeCode" in raw_data:
        prefix1 = status_to_plain.get(
            raw_data["typeCode"], "unknown_" + raw_data["typeCode"]
        )
        prefix += f"{prefix1}."
    elif "cmdFunc" in raw_data and "cmdId" in raw_data:
        prefix += f"{raw_data['cmdFunc']}_{raw_data['cmdId']}."
    else :
        prefix += ""

    if "param" in raw_data:
        for k, v in raw_data["param"].items():
            new_params[f"{prefix}{k}"] = v

    if "params" in raw_data:
        for k, v in raw_data["params"].items():
            new_params[f"{prefix}{k}"] = v

    for k, v in raw_data.items():
        if k != "param" and k != "params":
            new_params[f"{prefix}{k}"] = v

    new_params2 = {}
    for k, v in new_params.items():
        new_params2[k] = v
        if isinstance(v, dict):
            for k2, v2 in v.items():
                new_params2[f"{k}.{k2}"] = v2

    result: dict[str, any] = {"params": new_params2, "raw_data": raw_data}

    # Preserve the module serial number and any other metadata that the
    # data holder relies on to route payloads to the right device.
    #
    # For devices that expose child modules, Home Assistant initialises the
    # data holder with ``module_sn``.  During updates we only accept payloads
    # whose top-level ``moduleSn`` matches that value.  The original bridge
    # flattened the payload into ``params`` exclusively, which meant the
    # top-level ``moduleSn`` disappeared.  As a result the update logic would
    # ignore every message (and therefore never populate the entities),
    # because the guard `if "moduleSn" not in raw` short-circuited.
    #
    # By copying the serial number – and any other commonly used metadata –
    # back to the top level we allow the rest of the pipeline to recognise
    # and process the payload just like the unflattened version.
    if "moduleSn" in raw_data:
        result["moduleSn"] = raw_data["moduleSn"]
    if "sn" in raw_data:
        result["sn"] = raw_data["sn"]
    if "time" in raw_data:
        result["time"] = raw_data["time"]
    _LOGGER.debug(str(result))

    return result
