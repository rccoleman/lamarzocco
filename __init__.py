"""The La Marzocco integration."""
import asyncio

import voluptuous as vol

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749.wrappers import OAuth2Token

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.core import HomeAssistant

from datetime import timedelta
import logging

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
)

from datetime import timedelta

SCAN_INTERVAL = timedelta(minutes=1)

_LOGGER = logging.getLogger(__name__)

from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    COMMAND_ON,
    COMMAND_STANDBY,
    DATA_TAG,
    DOMAIN,
    CONF_SERIAL_NUMBER,
    CONF_CLIENT_ID,
    CONF_CLIENT_SECRET,
    MACHINE_STATUS,
    STATUS_ON,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

PLATFORMS = ["switch"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the La Marzocco component."""
    _LOGGER.debug("La Marzocco Setup")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry):
    """Set up La Marzocco as config entry."""
    coordinator = LaMarzoccoDataUpdateCoordinator(hass, config_entry)
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class LaMarzoccoDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data."""

    def __init__(self, hass, config_entry):
        """Initialize global data updater."""
        self.machine_data = LMData(hass, config_entry.data)
        self.machine_data.init_data()

        super().__init__(
            hass, _LOGGER, name=DOMAIN, update_interval=timedelta(seconds=60)
        )

    async def _async_update_data(self):
        """Fetch data"""
        try:
            return await self.machine_data.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err


class LMData:
    """Keep data for La Marzocco entities."""

    def __init__(self, hass, config):
        """Initialise the weather entity data."""
        self.hass = hass
        self._config = config
        self.current_data = {}
        self.current_status = None
        self.new_status = None
        self.client = None
        self.config_endpoint = None
        self.status_endpoint = None
        self.token = None

    def init_data(self):
        """Machine data inialization"""
        serial_number = self._config[CONF_SERIAL_NUMBER]
        token_endpoint = "https://cms.lamarzocco.io/oauth/v2/token"
        self.config_endpoint = (
            f"https://gw.lamarzocco.io/v1/home/machines/{serial_number}/configuration"
        )
        self.status_endpoint = (
            f"https://gw.lamarzocco.io/v1/home/machines/{serial_number}/status"
        )
        self.client = OAuth2Session(
            self._config[CONF_CLIENT_ID],
            self._config[CONF_CLIENT_SECRET],
            token_endpoint=token_endpoint,
        )

    async def fetch_data(self):
        """Fetch data from API - (current weather and forecast)."""
        await self.hass.async_add_executor_job(self._fetch_data)
        return self

    def _fetch_data(self):
        if self.token is None:
            self.token = self.client.fetch_token(
                username=self._config[CONF_USERNAME],
                password=self._config[CONF_PASSWORD],
            )

        if self.new_status is not None and self.current_status != self.new_status:
            self._power(self.new_status)
            self.current_status = self.new_status
        else:
            self.current_status = self.client.get(self.status_endpoint)
            if self.current_status is not None:
                data = self.current_status.json().get(DATA_TAG)
                self.current_status = data.get(MACHINE_STATUS) == STATUS_ON
                self.new_status = self.current_status

        self.current_data = self.client.get(self.config_endpoint)
        if self.current_data is not None:
            self.current_data = self.current_data.json().get(DATA_TAG)

        print("Device is {}".format("On" if self.current_status else "Off"))

    def _power(self, power):
        command = COMMAND_ON if power else COMMAND_STANDBY
        self.client.post(self.status_endpoint, json=command)