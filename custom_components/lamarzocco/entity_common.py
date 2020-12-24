from homeassistant.core import callback
from .const import *

from typing import Dict
import logging

_LOGGER = logging.getLogger(__name__)


class EntityCommon:
    """Common elements for all switches"""

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return False

    @property
    def name_base(self):
        """Return the name of the switch."""
        return f"{self.coordinator._device.machine_name} "

    @property
    def unique_id_base(self):
        """Return unique ID."""
        return f"{self.coordinator._device.serial_number}_"

    @callback
    def update_callback(self, status, state):
        """Update callback for switch entity"""
        self.schedule_update_ha_state(force_refresh=False)

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

    """Services"""

    async def set_coffee_temp(self, entity_id=None, temperature=None):
        """Service call to set coffee temp"""
        _LOGGER.debug(f"Setting coffee temp to {temperature}")
        await self.coordinator._device.set_coffee_temp(temperature)

    async def set_steam_temp(self, entity_id=None, temperature=None):
        """Service call to set steam temp"""
        _LOGGER.debug(f"Setting steam temp to {temperature}")
        await self.coordinator._device.set_steam_temp(temperature)

    def findkey(self, find_value, dict):
        """Find a key from the value in a dict"""
        return next(
            (key for key, value in dict.items() if value == find_value),
            None,
        )

    async def enable_auto_on_off(self, day_of_week=None):
        """Service call to set coffee temp"""
        key = self.findkey(day_of_week, ATTR_STATUS_MAP_AUTO_ON_OFF)
        if not key:
            _LOGGER.error(f"Invalid day provided {day_of_week}")
            return

        _LOGGER.debug(f"Enabling auto on/off for {day_of_week}")
        await self.coordinator._device.set_auto_on_off(key, True)
        self.async_schedule_update_ha_state(force_refresh=False)

    async def disable_auto_on_off(self, day_of_week=None):
        """Service call to set steam temp"""
        key = self.findkey(day_of_week, ATTR_STATUS_MAP_AUTO_ON_OFF)
        if not key:
            _LOGGER.error(f"Invalid day provided {day_of_week}")
            return

        _LOGGER.debug(f"Disabling auto on/off for {day_of_week}")
        await self.coordinator._device.set_auto_on_off(key, False)
        self.async_schedule_update_ha_state(force_refresh=False)

    async def set_auto_on_off_hours(
        self, day_of_week=None, hour_on=None, hour_off=None
    ):
        """Service call to set steam temp"""
        key = self.findkey(day_of_week, ATTR_STATUS_MAP_AUTO_ON_OFF)
        if not key:
            _LOGGER.error(f"Invalid day provided {day_of_week}")
            return

        try:
            hour_on = int(hour_on)
            hour_off = int(hour_off)

            if 24 > hour_on >= 0 and 24 > hour_off >= 0:
                _LOGGER.debug(f"Disabling auto on/off for {day_of_week}")
                await self.coordinator._device.set_auto_on_off_hours(
                    key, hour_on, hour_off
                )
            else:
                _LOGGER.error(
                    f"Hours out of range (0..23): hour_on:{hour_on} hour_off:{hour_off}"
                )
        except Exception as err:
            _LOGGER.error(
                f"Invalid input: day_of_week:{day_of_week} hour_on:{hour_on} hour_off:{hour_off}"
            )
            return
        self.async_schedule_update_ha_state(force_refresh=False)
