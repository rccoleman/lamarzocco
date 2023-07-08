"""The La Marzocco integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .lm_client import LaMarzoccoClient
from .const import DOMAIN
from .coordinator import LmApiCoordinator
from .services import async_setup_services

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "binary_sensor", "sensor", "water_heater", "button"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the La Marzocco component."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass, config_entry):
    """Set up La Marzocco as config entry."""

    lm = LaMarzoccoClient(hass, config_entry.data)

    hass.data[DOMAIN][config_entry.entry_id] = coordinator = LmApiCoordinator(hass, lm)

    await coordinator.async_config_entry_first_refresh()

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

    unload_ok = await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok
