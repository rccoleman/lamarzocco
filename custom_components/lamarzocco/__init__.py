"""The La Marzocco integration."""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .api import LaMarzocco
from .const import DOMAIN
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "binary_sensor", "sensor", "water_heater"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the La Marzocco component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry):
    """Set up La Marzocco as config entry."""
    lm = LaMarzocco(hass, config_entry=config_entry)
    await lm.init_data(hass)

    hass.data[DOMAIN][config_entry.entry_id] = lm

    for platform in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    """Set up global services."""
    await async_setup_services(hass, config_entry)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    services = list(hass.services.async_services().get(DOMAIN).keys())
    [hass.services.async_remove(DOMAIN, service) for service in services]

    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in PLATFORMS
            ]
        )
    )
    if unload_ok:
        await hass.data[DOMAIN][config_entry.entry_id].close()
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
