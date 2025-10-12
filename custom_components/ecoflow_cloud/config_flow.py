from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_entry_oauth2_flow

from .const import DOMAIN


class EcoflowConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            return self.async_create_entry(title="EcoFlow Cloud", data=user_input)

        schema = vol.Schema(
            {
                vol.Required("broker_host"): str,
                vol.Required("broker_port", default=8883): int,
                vol.Required("client_id"): str,
                vol.Required("username"): str,
                vol.Required("password"): str,
                vol.Required("serial"): str,
                vol.Optional("family", default="v3"): str,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)


class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    "enable_controls_v3",
                    default=self.config_entry.options.get("enable_controls_v3", False),
                ): bool,
                vol.Optional(
                    "v3_fds_path",
                    default=self.config_entry.options.get("v3_fds_path", ""),
                ): str,
                vol.Optional(
                    "v3_dispatch_path",
                    default=self.config_entry.options.get("v3_dispatch_path", ""),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)


async def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    return OptionsFlowHandler(config_entry)

