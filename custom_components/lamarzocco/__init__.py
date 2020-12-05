"""The La Marzocco integration."""
import asyncio
from homeassistant.helpers import config_entry_oauth2_flow

from authlib.integrations.httpx_client import AsyncOAuth2Client
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

from homeassistant.components.light import LightEntity
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

SCAN_INTERVAL = timedelta(minutes=10)
_LOGGER = logging.getLogger(__name__)

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
    GW_URL,
    TOKEN_URL,
)

PLATFORMS = ["switch"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the La Marzocco component."""
    _LOGGER.debug("La Marzocco Setup")
    hass.data.setdefault(DOMAIN, {})

    config_flow.OAuth2FlowHandler.async_register_implementation(
        hass,
        config_entry_oauth2_flow.LocalOAuth2Implementation(
            hass,
            DOMAIN,
            config[DOMAIN][CONF_CLIENT_ID],
            config[DOMAIN][CONF_CLIENT_SECRET],
            config[DOMAIN][CONF_USERNAME],
            config[DOMAIN][CONF_PASSWORD],
        ),
    )
    return True


async def async_setup_entry(hass, config_entry):
    """Set up La Marzocco as config entry."""
    implementation = (
        await config_entry_oauth2_flow.async_get_config_entry_implementation(
            hass, config_entry
        )
    )

    session = config_entry_oauth2_flow.OAuth2Session(hass, config_entry, implementation)

    coordinator = LaMarzoccoDataUpdateCoordinator(hass, config_entry)
    await coordinator.init_data()
    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data[DOMAIN][config_entry.entry_id] = coordinator

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
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
        self._device = LaMarzocco(hass, config_entry.data)
        self.hass = hass

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=60),
            update_method=self.async_update_data,
        )

    async def init_data(self):
        """Initialize the UpdateCoordinator object"""
        try:
            await self._device.init_data()
        except Exception as err:
            raise UpdateFailed(f"Init failed: {err}") from err

    async def async_update_data(self):
        """Fetch data"""
        try:
            return await self._device.fetch_data()
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}") from err


class LaMarzocco:
    """Keep data for La Marzocco entities."""

    def __init__(self, hass, config):
        """Initialise the weather entity data."""
        self.hass = hass
        self._config = config
        self.current_data = {}
        self.client = None
        self.is_on = False

    async def init_data(self):
        """Machine data inialization"""
        serial_number = self._config[CONF_SERIAL_NUMBER]
        self.config_endpoint = f"{GW_URL}/{serial_number}/configuration"
        self.status_endpoint = f"{GW_URL}/{serial_number}/status"
        client_id = self._config[CONF_CLIENT_ID]
        client_secret = self._config[CONF_CLIENT_SECRET]

        self.client = AsyncOAuth2Client(
            client_id=client_id,
            client_secret=client_secret,
            token_endpoint=TOKEN_URL,
        )

        headers = {"client_id": client_id, "client_secret": client_secret}

        await self.client.fetch_token(
            url=TOKEN_URL,
            username=self._config[CONF_USERNAME],
            password=self._config[CONF_PASSWORD],
            headers=headers,
        )

    async def fetch_data(self):
        """Fetch data from API - (current weather and forecast)."""
        _LOGGER.debug("Fetching data")

        current_status = await self.client.get(self.status_endpoint)
        if current_status is not None:
            _LOGGER.debug(current_status.json())
            data = current_status.json()
            if data is not None:
                self.is_on = data[DATA_TAG][MACHINE_STATUS] == STATUS_ON

        current_data = await self.client.get(self.config_endpoint)
        if current_data is not None:
            _LOGGER.debug(current_data.json())
            self.current_data = current_data.json().get(DATA_TAG)

        _LOGGER.debug("Device is {}".format("On" if self.is_on else "Off"))
        _LOGGER.debug("Data is {}".format(self.current_data))
        return self

    async def power(self, power):
        command = COMMAND_ON if power else COMMAND_STANDBY
        await self.client.post(self.status_endpoint, json=command)