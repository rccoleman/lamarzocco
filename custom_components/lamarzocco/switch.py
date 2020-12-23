import logging
from datetime import datetime
from typing import Dict

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_platform, service
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import *

_LOGGER = logging.getLogger(__name__)


class Service:
    def __init__(self, name, params):
        self._name = name
        self._params = params
        self._platform = entity_platform.current_platform.get()

    def register(self):
        self._platform.async_register_entity_service(
            self._name, self._params, self._name
        )


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a switch entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [LaMarzoccoEntity(coordinator, config_entry.data, hass.config.units.is_metric)]
    )

    SERVICES = [
        Service(SERVICE_SET_COFFEE_TEMP, {vol.Required("temperature"): cv.string}),
        Service(SERVICE_SET_STEAM_TEMP, {vol.Required("temperature"): cv.string}),
    ]

    for service in SERVICES:
        service.register()


class LaMarzoccoEntity(CoordinatorEntity, SwitchEntity, RestoreEntity):
    """Implementation of a La Marzocco integration"""

    def __init__(self, coordinator, config, is_metric):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config
        self._temp_state = None
        self._is_metric = is_metric

        self.coordinator._device.register_callback(self.update_callback)

    async def set_coffee_temp(self, temperature=None):
        """Service call to set coffee temp"""
        _LOGGER.debug(f"Setting coffee temp to {temperature}")
        await self.coordinator._device.set_coffee_temp(temperature)

    async def set_steam_temp(self, temperature=None):
        """Service call to set steam temp"""
        _LOGGER.debug(f"Setting steam temp to {temperature}")
        await self.coordinator._device.set_steam_temp(temperature)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        await self.coordinator._device.set_power(True)
        self._temp_state = True
        self.async_schedule_update_ha_state(force_refresh=False)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        await self.coordinator._device.set_power(False)
        self._temp_state = False
        self.async_schedule_update_ha_state(force_refresh=False)

    @callback
    def update_callback(self, status, state):
        """Update callback for switch entity"""
        _LOGGER.debug("update_callback for SWITCH called")
        self.schedule_update_ha_state(force_refresh=False)

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.coordinator._device.serial_number}"

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        if self._temp_state == self.coordinator._device._is_on:
            self._temp_state = None

        return (
            self._temp_state
            if self._temp_state is not None
            else self.coordinator._device._is_on
        )

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return False

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self.coordinator._device.machine_name}"

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return self.generate_attrs(
            self.coordinator._device._current_status, ATTR_STATUS_MAP
        )

    def generate_attrs(self, data, map) -> Dict:
        output = {}

        for key in data:
            if key in map.keys():
                value = data[key]

                """Convert boolean values to strings to improve display in Lovelace"""
                if isinstance(value, bool):
                    value = str(value)

                """Convert temps to fahrenheit if needed"""
                if not self._is_metric and any(val in key for val in TEMP_KEYS):
                    value = round((value * 9 / 5) + 32, 1)

                output[map[key]] = value

        return output

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return "mdi:coffee-maker"

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN, self.coordinator._device.serial_number)},
            "name": self.coordinator._device.machine_name,
            "manufacturer": "La Marzocco",
            "model": self.coordinator._device.model_name,
            "default_name": "La Marzocco " + self.coordinator._device.model_name,
            "entry_type": "None",
        }
