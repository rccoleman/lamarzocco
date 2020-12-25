import logging
from typing import Dict

from homeassistant.core import callback

from .const import *

_LOGGER = logging.getLogger(__name__)


class EntityCommon:
    """Common elements for all switches"""

    _is_metric = False
    _entity = None

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

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
    def update_callback(self, **kwargs):
        """Update the state machine"""
        entity = kwargs.get("entity")
        if entity in [None, self._entity]:
            _LOGGER.debug(f"Calling callback for {self._entity}")
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

    async def set_coffee_temp(self, temperature=None):
        """Service call to set coffee temp"""

        if not isinstance(temperature, float):
            temperature = float(temperature)

        """Machine expects Celcius"""
        if not self._is_metric:
            temperature = round((temperature - 32) / 9 * 5, 1)

        _LOGGER.debug(f"Setting coffee temp to {temperature}")
        await self.coordinator._device.set_coffee_temp(temperature)

    async def set_steam_temp(self, temperature=None):
        """Service call to set steam temp"""

        if not isinstance(temperature, float):
            temperature = float(temperature)

        """Machine expects Celcius"""
        if not self._is_metric:
            temperature = round((temperature - 32) / 9 * 5, 1)

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

    async def disable_auto_on_off(self, day_of_week=None):
        """Service call to set steam temp"""
        key = self.findkey(day_of_week, ATTR_STATUS_MAP_AUTO_ON_OFF)
        if not key:
            _LOGGER.error(f"Invalid day provided {day_of_week}")
            return

        _LOGGER.debug(f"Disabling auto on/off for {day_of_week}")
        await self.coordinator._device.set_auto_on_off(key, False)

    async def set_auto_on_off_hours(
        self, day_of_week=None, hour_on=None, hour_off=None
    ):
        """Service call to set steam temp"""
        key = self.findkey(day_of_week, ATTR_STATUS_MAP_AUTO_ON_OFF)
        if not key:
            _LOGGER.error(f"Invalid day provided {day_of_week}")
            return

        if not isinstance(hour_on, int):
            hour_on = int(hour_on)
        if not isinstance(hour_off, int):
            hour_off = int(hour_off)

        """Validate input"""
        if not (24 > hour_on >= 0 and 24 > hour_off >= 0):
            _LOGGER.error(
                f"Hours out of range (0..23): hour_on:{hour_on} hour_off:{hour_off}"
            )
            return

        _LOGGER.debug(
            f"Setting auto on/off hours for {day_of_week} from {hour_on} to {hour_off}"
        )
        await self.coordinator._device.set_auto_on_off_hours(key, hour_on, hour_off)

    async def set_dose(self, key=None, pulses=None):
        """Service call to set dose"""

        if isinstance(key, str):
            key = int(key)

        if isinstance(pulses, str):
            pulses = int(pulses)

        """Validate input"""
        if not (1 <= pulses <= 1000 and 1 <= key <= 5):
            _LOGGER.error(f"Invalid values pulses:{pulses} key:{key}")
            return

        _LOGGER.debug(f"Setting dose for key:{key} to pulses:{pulses}")
        await self.coordinator._device.set_dose(key, pulses)

    async def set_dose_tea(self, seconds=None):
        """Service call to set tea dose"""

        if isinstance(seconds, str):
            seconds = int(seconds)

        """Validate input"""
        if not (1 <= seconds <= 30):
            _LOGGER.error(f"Invalid values seconds:{seconds}")
            return

        _LOGGER.debug(f"Setting tea dose to seconds:{seconds}")
        await self.coordinator._device.set_dose_tea(seconds)

    async def set_prebrew_times(self, key=None, time_on=None, time_off=None):
        """Service call to set prebrew on time"""

        if isinstance(key, str):
            key = int(key)

        if isinstance(time_on, str):
            time_on = float(time_on)

        if isinstance(time_off, str):
            time_off = float(time_off)

        """Validate input"""
        if not (0 <= time_on <= 5.9 and 0 <= time_off <= 5.9 and 1 <= key <= 4):
            _LOGGER.error(
                f"Invalid values time_on:{time_on} off_time:{time_off} key:{key}"
            )
            return

        _LOGGER.debug(
            f"Setting prebrew on time for key:{key} to time_on:{time_on} and off_time:{time_off}"
        )
        await self.coordinator._device.set_prebrew_times(key, time_on, time_off)
