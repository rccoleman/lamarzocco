"""The La Marzocco integration."""

from .const import DOMAIN
from .api import LaMarzocco

from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.core import HomeAssistant
from datetime import timedelta

import logging, asyncio

from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

SCAN_INTERVAL = timedelta(minutes=10)
_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the La Marzocco component."""
    _LOGGER.debug("La Marzocco Setup")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry):
    """Set up La Marzocco as config entry."""
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


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        await hass.data[DOMAIN][config_entry.entry_id]._device.close()
        hass.data[DOMAIN].pop(config_entry.entry_id)

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
