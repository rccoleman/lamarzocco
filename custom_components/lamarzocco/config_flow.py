"""Config flow for La Marzocco integration."""
import logging
from typing import Any, Dict, Optional

import voluptuous as vol
from authlib.integrations.base_client.errors import OAuthError
from homeassistant import config_entries, core, exceptions
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TYPE,
    CONF_USERNAME,
)
from homeassistant.helpers import config_validation as cv

from .api import LaMarzocco
from .const import CONF_CLIENT_ID, CONF_CLIENT_SECRET, CONF_SERIAL_NUMBER, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)

STEP_DISCOVERY_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    }
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""

    try:
        lm = LaMarzocco(hass, data)
        machine_info = await lm.connect()
        await lm.close()

        if not machine_info:
            raise CannotConnect

    except OAuthError:
        raise InvalidAuth
    except Exception:
        _LOGGER.exception("Unexpected exception")
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": lm.machine_name, **machine_info}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for La Marzocco."""

    # TODO pick one of the available connection classes in homeassistant/config_entries.py
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def _try_create_entry(self, data):
        machine_info = await validate_input(self.hass, data)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title=machine_info["title"], data={**data, **machine_info}
        )

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            # Config entry already exists, only one allowed.
            return self.async_abort(reason="single_instance_allowed")

        errors = {}

        if user_input is not None:
            try:
                return await self._try_create_entry(user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_zeroconf(
        self, discovery_info: Optional[Dict[str, Any]] = None
    ):
        """Handle the initial step."""

        """Handle a flow initialized by zeroconf discovery."""
        raw = discovery_info["properties"]["_raw"]

        type: str = raw["type"].decode("utf-8")
        serial_number: str = raw["serial_number"].decode("utf-8")
        host: str = discovery_info[CONF_HOST]

        self._discovered = {
            CONF_HOST: host,
            CONF_TYPE: type,
            CONF_SERIAL_NUMBER: serial_number,
            CONF_NAME: host,
        }

        _LOGGER.debug(
            "LaMarzocco: Host={}, Name={}, SN={}".format(host, type, serial_number)
        )

        await self.async_set_unique_id(serial_number)
        self._abort_if_unique_id_configured({CONF_SERIAL_NUMBER: serial_number})

        return await self.async_step_confirm()

    async def async_step_confirm(
        self, user_input: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Handle confirmation flow for discovered La Marzocco machine"""

        errors = {}

        if user_input is not None:
            try:
                data = user_input.copy()
                data[CONF_HOST] = self._discovered[CONF_HOST]

                return await self._try_create_entry(data)
            except InvalidAuth:
                errors["base"] = "invalid_auth"

        return self.async_show_form(
            step_id="confirm",
            data_schema=STEP_DISCOVERY_DATA_SCHEMA,
            errors=errors,
            description_placeholders=self._discovered,
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
