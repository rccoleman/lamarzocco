"""Base class for the La Marzocco entities."""

import logging

from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity
from lmdirect import InvalidInput

from .const import DOMAIN, ENTITY_ICON, ENTITY_MAP, ENTITY_NAME, TEMP_KEY

_LOGGER = logging.getLogger(__name__)


class EntityBase(RestoreEntity):
    """Common elements for all switches."""

    _device_version = None
    _is_metric = False
    _entity_id = None
    _entities = []

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
        return (
            f"{self._lm.machine_name} " + self._entities[self._object_id][ENTITY_NAME]
        )

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._lm.serial_number}_" + self._object_id

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return self._entities[self._object_id][ENTITY_ICON]

    @callback
    def update_callback(self, **kwargs):
        """Update the state machine when new data arrives."""
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
            "model": self._lm.true_model_name,
            "default_name": "La Marzocco " + self._lm.true_model_name,
            "entry_type": "None",
            "sw_version": self._lm.firmware_version,
        }

    @property
    def state_attributes(self):
        """Return the state attributes."""

        def convert_value(k, v):
            """Convert boolean values to strings to improve display in Lovelace."""
            if isinstance(v, bool):
                v = str(v)

            """Convert temps to Fahrenheit if needed."""
            if not self._is_metric and TEMP_KEY in k:
                v = round((v * 9 / 5) + 32, 1)

            return v

        data = self._lm._current_status
        map = self._entities[self._object_id][ENTITY_MAP][self._lm.model_name]

        return {k: convert_value(k, v) for (k, v) in data.items() if k in map}

    # Services

    async def call_service(self, func, *args, **kwargs):
        try:
            await func(*args, **kwargs)
        except InvalidInput as err:
            _LOGGER.error(f"{err}, returning FALSE")
            return False

    async def set_coffee_temp(self, temperature=None):
        """Service call to set coffee temp."""

        """Machine expects Celcius, so convert if needed."""
        if not self._is_metric:
            temperature = round((temperature - 32) / 9 * 5, 1)

        _LOGGER.debug(f"Setting coffee temp to {temperature}")
        await self.call_service(self._lm.set_coffee_temp, temp=temperature)
        return True

    async def set_steam_temp(self, temperature=None):
        """Service call to set steam temp."""

        """Machine expects Celcius, so convert if needed."""
        if not self._is_metric:
            temperature = round((temperature - 32) / 9 * 5, 1)

        _LOGGER.debug(f"Setting steam temp to {temperature}")
        await self.call_service(self._lm.set_steam_temp, temp=temperature)
        return True

    async def enable_auto_on_off(self, day_of_week=None):
        """Service call to enable auto on/off."""

        _LOGGER.debug(f"Enabling auto on/off for {day_of_week}")
        await self.call_service(
            self._lm.set_auto_on_off, day_of_week=day_of_week, enable=True
        )
        return True

    async def disable_auto_on_off(self, day_of_week=None):
        """Service call to disable auto on/off."""

        _LOGGER.debug(f"Disabling auto on/off for {day_of_week}")
        await self.call_service(
            self._lm.set_auto_on_off, day_of_week=day_of_week, enable=False
        )
        return True

    async def set_auto_on_off_hours(
        self, day_of_week=None, hour_on=None, hour_off=None
    ):
        """Service call to configure auto on/off hours for a day."""

        _LOGGER.debug(
            f"Setting auto on/off hours for {day_of_week} from {hour_on} to {hour_off}"
        )
        await self.call_service(
            self._lm.set_auto_on_off_hours,
            day_of_week=day_of_week,
            hour_on=hour_on,
            hour_off=hour_off,
        )
        return True

    async def set_dose(self, key=None, pulses=None):
        """Service call to set the dose for a key."""

        _LOGGER.debug(f"Setting dose for key:{key} to pulses:{pulses}")
        await self.call_service(self._lm.set_dose, key=key, pulses=pulses)
        return True

    async def set_dose_tea(self, seconds=None):
        """Service call to set the tea dose."""

        _LOGGER.debug(f"Setting tea dose to seconds:{seconds}")
        await self.call_service(self._lm.set_dose_tea, seconds=seconds)
        return True

    async def set_prebrew_times(self, key=None, time_on=None, time_off=None):
        """Service call to set prebrew on time."""

        _LOGGER.debug(
            f"Setting prebrew on time for key:{key} to time_on:{time_on} and off_time:{time_off}"
        )
        await self.call_service(
            self._lm.set_prebrew_times,
            key=key,
            time_on=time_on,
            time_off=time_off,
        )
        _LOGGER.debug("Returning True")
        return True
