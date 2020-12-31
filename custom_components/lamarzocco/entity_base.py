import logging

from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity

from .const import *

from .api import LaMarzocco

_LOGGER = logging.getLogger(__name__)


class EntityBase(RestoreEntity):
    """Common elements for all switches"""

    _is_metric = False
    _entity_id = None
    ENTITIES = []

    @property
    def entity_registry_enabled_default(self) -> bool:
        """Return if the entity should be enabled when first added to the entity registry."""
        return True

    @property
    def assumed_state(self) -> bool:
        """Return true if unable to access real state of entity."""
        return False

    @property
    def name(self):
        """Return the name of the switch."""
        return f"{self._lm.machine_name} " + self.ENTITIES[self._object_id][ENTITY_NAME]

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._lm.serial_number}_" + self._object_id

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend"""
        return self.ENTITIES[self._object_id][ENTITY_ICON]

    @callback
    def update_callback(self, **kwargs):
        """Update the state machine"""
        entity_type = kwargs.get("entity_type")
        if entity_type in [None, self._entity_type]:
            self.schedule_update_ha_state(force_refresh=False)

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN, self._lm.serial_number)},
            "name": self._lm.machine_name,
            "manufacturer": "La Marzocco",
            "model": self._lm.model_name,
            "default_name": "La Marzocco " + self._lm.model_name,
            "entry_type": "None",
        }

    @property
    def state_attributes(self):
        """Return the state attributes."""

        data = self._lm._current_status
        map = self.ENTITIES[self._object_id][ENTITY_MAP]

        def convert_values(k, v):
            """Convert boolean values to strings to improve display in Lovelace"""
            if isinstance(v, bool):
                v = str(v)

            """Convert temps to fahrenheit if needed"""
            if not self._is_metric and any(key in k for key in TEMP_KEYS):
                v = round((v * 9 / 5) + 32, 1)

            return v

        return {
            map[k]: convert_values(k, v) for (k, v) in data.items() if k in map.keys()
        }

    """Services"""

    async def call_service(self, func, **kwargs):
        _LOGGER.debug(f"Calling service {func}")
        await func(**kwargs)

    async def set_coffee_temp(self, temperature=None):
        """Service call to set coffee temp"""

        if not isinstance(temperature, float):
            temperature = float(temperature)

        """Machine expects Celcius"""
        if not self._is_metric:
            temperature = round((temperature - 32) / 9 * 5, 1)

        _LOGGER.debug(f"Setting coffee temp to {temperature}")
        await self.call_service(self._lm.set_coffee_temp, temp=temperature)

    async def set_steam_temp(self, temperature=None):
        """Service call to set steam temp"""

        if not isinstance(temperature, float):
            temperature = float(temperature)

        """Machine expects Celcius"""
        if not self._is_metric:
            temperature = round((temperature - 32) / 9 * 5, 1)

        _LOGGER.debug(f"Setting steam temp to {temperature}")
        await self.call_service(self._lm.set_steam_temp, temp=temperature)

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
            return False

        _LOGGER.debug(f"Enabling auto on/off for {day_of_week}")
        await self.call_service(self._lm.set_auto_on_off, day_of_week=key, enable=True)

    async def disable_auto_on_off(self, day_of_week=None):
        """Service call to set steam temp"""
        key = self.findkey(day_of_week, ATTR_STATUS_MAP_AUTO_ON_OFF)
        if not key:
            _LOGGER.error(f"Invalid day provided {day_of_week}")
            return False

        _LOGGER.debug(f"Disabling auto on/off for {day_of_week}")
        await self.call_service(self._lm.set_auto_on_off, day_of_week=key, enable=False)

    async def set_auto_on_off_hours(
        self, day_of_week=None, hour_on=None, hour_off=None
    ):
        """Service call to set steam temp"""
        key = self.findkey(day_of_week, ATTR_STATUS_MAP_AUTO_ON_OFF)
        if not key:
            _LOGGER.error(f"Invalid day provided {day_of_week}")
            return False

        if not isinstance(hour_on, int):
            hour_on = int(hour_on)
        if not isinstance(hour_off, int):
            hour_off = int(hour_off)

        """Validate input"""
        if not (24 > hour_on >= 0 and 24 > hour_off >= 0):
            _LOGGER.error(
                f"Hours out of range (0..23): hour_on:{hour_on} hour_off:{hour_off}"
            )
            return False

        _LOGGER.debug(
            f"Setting auto on/off hours for {day_of_week} from {hour_on} to {hour_off}"
        )
        await self.call_service(
            self._lm.set_auto_on_off_hours,
            day_of_week=key,
            hour_on=hour_on,
            hour_off=hour_off,
        )

    async def set_dose(self, key=None, pulses=None):
        """Service call to set dose"""

        if isinstance(key, str):
            key = int(key)

        if isinstance(pulses, str):
            pulses = int(pulses)

        """Validate input"""
        if not (1 <= pulses <= 1000 and 1 <= key <= 5):
            _LOGGER.error(f"Invalid values pulses:{pulses} key:{key}")
            return False

        _LOGGER.debug(f"Setting dose for key:{key} to pulses:{pulses}")
        await self.call_service(self._lm.set_dose, key=key, pulses=pulses)

    async def set_dose_tea(self, seconds=None):
        """Service call to set tea dose"""

        if isinstance(seconds, str):
            seconds = int(seconds)

        """Validate input"""
        if not (1 <= seconds <= 30):
            _LOGGER.error(f"Invalid values seconds:{seconds}")
            return False

        _LOGGER.debug(f"Setting tea dose to seconds:{seconds}")
        await self.call_service(self._lm.set_dose_tea, seconds=seconds)

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
            return False

        _LOGGER.debug(
            f"Setting prebrew on time for key:{key} to time_on:{time_on} and off_time:{time_off}"
        )
        await self.call_service(
            self._lm.set_prebrew_times, key=key, time_on=time_on, time_off=time_off
        )
