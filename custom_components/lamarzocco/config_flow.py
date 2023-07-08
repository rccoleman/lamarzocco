"""Config flow for La Marzocco integration."""
import logging
from typing import Any, Dict

import voluptuous as vol
from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_USERNAME
from homeassistant.helpers import config_validation as cv
from lmcloud.exceptions import AuthFail, RequestNotSuccessful
from .lm_client import LaMarzoccoClient

from .const import (
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    CONF_SERIAL_NUMBER,
    DEFAULT_PORT,
    DOMAIN,
    MODEL_LMU
)

_LOGGER = logging.getLogger(__name__)

STEP_DISCOVERY_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_CLIENT_ID): cv.string,
        vol.Required(CONF_CLIENT_SECRET): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
    },
    extra=vol.PREVENT_EXTRA,
)

STEP_USER_DATA_SCHEMA = STEP_DISCOVERY_DATA_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
    },
    extra=vol.PREVENT_EXTRA,
)


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect."""

    try:
        lm = await LaMarzoccoClient.create(hass=hass, data=data)

        if not lm.machine_info:
            raise CannotConnect

    except AuthFail:
        _LOGGER.error("Server rejected login credentials")
        raise InvalidAuth
    except RequestNotSuccessful:
        _LOGGER.error("Failed to connect to server")
        raise CannotConnect

    # Return info that you want to store in the config entry.
    return {"title": lm.machine_name, **lm.machine_info}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for La Marzocco."""

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
            data = user_input.copy()
            data[CONF_PORT] = DEFAULT_PORT

            try:
                return await self._try_create_entry(data)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except CannotConnect:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    # async def async_step_zeroconf(self, discovery_info):
    #     """Handle a flow initialized by zeroconf discovery."""
    #     _LOGGER.debug(f"Discovered {discovery_info}")

    #     if isinstance(discovery_info, dict):
    #         raw = discovery_info["properties"]["_raw"]

    #         serial_number: str = raw["serial_number"].decode("utf-8")
    #         host: str = discovery_info[CONF_HOST]
    #         port: int = discovery_info[CONF_PORT]
    #     else:
    #         properties = discovery_info.properties

    #         serial_number = ""
    #         if "type" in properties:
    #             if properties["type"] == str.upper(MODEL_LMU):
    #                 serial_number = properties["sn"]
    #         if not serial_number:
    #             serial_number = properties["serial_number"]

    #         host: str = discovery_info.host
    #         port: int = discovery_info.port

    #     self._discovered = {
    #         CONF_HOST: host,
    #         CONF_PORT: port,
    #         CONF_SERIAL_NUMBER: serial_number,
    #     }
        
    #     _LOGGER.debug(f"Host={host}, Port={port}, SN={serial_number}")

    #     await self.async_set_unique_id(serial_number)
    #     self._abort_if_unique_id_configured({CONF_SERIAL_NUMBER: serial_number})

    #     self.context.update({"title_placeholders": self._discovered})

    #     return await self.async_step_confirm()

    # async def async_step_confirm(
    #     self, user_input: Dict[str, Any] = None
    # ) -> Dict[str, Any]:
    #     """Handle confirmation flow for discovered La Marzocco machine"""

    #     errors = {}

    #     if user_input is not None:
    #         try:
    #             data = user_input.copy()
    #             data.update(self._discovered)

    #             return await self._try_create_entry(data)
    #         except InvalidAuth:
    #             errors["base"] = "invalid_auth"
    #         except CannotConnect:
    #             errors["base"] = "cannot_connect"

    #     return self.async_show_form(
    #         step_id="confirm",
    #         data_schema=STEP_DISCOVERY_DATA_SCHEMA,
    #         errors=errors,
    #     )

    async def async_step_reauth(self, user_input=None):
        """Perform reauth upon an API authentication error."""
        self.reauth_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(self, user_input=None):
        """Dialog that informs the user that reauth is required."""
        if user_input is None:
            return self.async_show_form(
                step_id="reauth_confirm",
                data_schema=STEP_DISCOVERY_DATA_SCHEMA,
            )
        self.hass.config_entries.async_update_entry(
            self.reauth_entry, data=user_input
        )
        await self.hass.config_entries.async_reload(self.reauth_entry.entry_id)
        return self.async_abort(reason="reauth_successful")


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""
