"""Sensor platform for the Corona virus."""
import logging

from .const import (
    ATTR_STATUS_MAP_COFFEE_TEMP,
    ATTR_STATUS_MAP_STEAM_TEMP,
    DOMAIN,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TAG,
    ENTITY_TYPE,
    TEMP_COFFEE,
    TEMP_STEAM,
    TYPE_COFFEE_TEMP,
    TYPE_STEAM_TEMP,
)

# from .const import *
from .entity_base import EntityBase

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "coffee_temp": {
        ENTITY_TAG: TEMP_COFFEE,
        ENTITY_NAME: "Coffee Temp",
        ENTITY_MAP: ATTR_STATUS_MAP_COFFEE_TEMP,
        ENTITY_TYPE: TYPE_COFFEE_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
    },
    "boiler_temp": {
        ENTITY_TAG: TEMP_STEAM,
        ENTITY_NAME: "Steam Temp",
        ENTITY_MAP: ATTR_STATUS_MAP_STEAM_TEMP,
        ENTITY_TYPE: TYPE_STEAM_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    lm = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoSensor(lm, sensor_type, hass.config.units.is_metric)
        for sensor_type in ENTITIES
    )


class LaMarzoccoSensor(EntityBase):
    """Sensor representing corona virus data."""

    def __init__(self, lm, sensor_type, is_metric):
        """Initialize sensors"""
        self._object_id = sensor_type
        self._lm = lm
        self._is_metric = is_metric
        self.ENTITIES = ENTITIES
        self._entity_type = self.ENTITIES[self._object_id][ENTITY_TYPE]

        self._lm.register_callback(self.update_callback)

    @property
    def available(self):
        """Return if sensor is available."""
        return (
            self._lm.current_status.get(self.ENTITIES[self._object_id][ENTITY_TAG])
            is not None
        )

    @property
    def state(self):
        """State of the sensor."""
        return self._lm.current_status.get(self.ENTITIES[self._object_id][ENTITY_TAG])

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""

        """Machine returns temperature in C, but HA will convert to the right locale"""
        return "°C"

    @property
    def device_class(self):
        """Device class for sensor"""
        return "temperature"
