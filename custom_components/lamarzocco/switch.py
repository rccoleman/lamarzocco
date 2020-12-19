import logging
from typing import Dict

from homeassistant.components.switch import SwitchEntity
from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_STATUS_MAP,
    ATTRIBUTION,
    DEFAULT_NAME,
    DEVICE_MAP,
    DOMAIN,
    STATUS_MACHINE_STATUS,
    TEMP_KEYS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a switch entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [LaMarzoccoEntity(coordinator, config_entry.data, hass.config.units.is_metric)]
    )


class LaMarzoccoEntity(CoordinatorEntity, SwitchEntity, RestoreEntity):
    """Implementation of a La Marzocco integration"""

    def __init__(self, coordinator, config, is_metric):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config
        self._temp_state = None
        self._is_metric = is_metric
        self._current_status = {}

        """Start with the machine in standby if we haven't received accurate data yet"""
        self._is_on = False
        self._current_status[STATUS_MACHINE_STATUS] = 0

        """Register the callback to receive updates"""
        coordinator.data.lmdirect.register_callback(self.update_callback)

    @callback
    def update_callback(self, status, state):
        _LOGGER.debug("Data updated: {}, state={}".format(status, state))
        self._current_status.update(status)

        self._is_on = True if self._current_status[STATUS_MACHINE_STATUS] else False
        if self._temp_state == self._is_on:
            self._temp_state = None

        self.schedule_update_ha_state(force_refresh=False)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        await self.coordinator.data.power(True)
        self._temp_state = True
        self.async_schedule_update_ha_state(force_refresh=False)

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        await self.coordinator.data.power(False)
        self._temp_state = False
        self.async_schedule_update_ha_state(force_refresh=False)

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self.coordinator.data.serial_number}"

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        return self._temp_state if self._temp_state is not None else self._is_on

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return False

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{DEFAULT_NAME}"

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
        return self.generate_attrs(self._current_status, ATTR_STATUS_MAP)

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
        prefix = self.coordinator.data.serial_number[:2]

        return {
            "identifiers": {(DOMAIN,)},
            "name": "La Marzocco",
            "manufacturer": "La Marzocco",
            "model": DEVICE_MAP[prefix] if prefix in DEVICE_MAP.keys() else "No Model",
            "default_name": "lamarzocco",
            "entry_type": "None",
        }
