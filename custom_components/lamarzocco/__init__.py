"""The La Marzocco integration."""

import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .api import LaMarzocco
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the La Marzocco component."""
    _LOGGER.debug("La Marzocco Setup")
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry):
    """Set up La Marzocco as config entry."""
    lm = LaMarzocco(hass, config_entry.data)
    await lm.init_data(hass)

    hass.data[DOMAIN][config_entry.entry_id] = lm

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
        await hass.data[DOMAIN][config_entry.entry_id].close()
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
