"""Sensor platform for the Corona virus."""
import logging

from lmdirect.msgs import (
    CONTINUOUS,
    DRINKS_K1,
    DRINKS_K2,
    DRINKS_K3,
    DRINKS_K4,
    HOT_WATER,
)

from .const import (
    ATTR_MAP_COFFEE_TEMP,
    ATTR_MAP_DRINK_STATS,
    ATTR_MAP_STEAM_TEMP,
    DOMAIN,
    ENTITY_CLASS,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TAG,
    ENTITY_TYPE,
    ENTITY_UNITS,
    TEMP_COFFEE,
    TEMP_STEAM,
    TYPE_COFFEE_TEMP,
    TYPE_DRINK_STATS,
    TYPE_STEAM_TEMP,
)
from .entity_base import EntityBase

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "coffee_temp": {
        ENTITY_TAG: [TEMP_COFFEE],
        ENTITY_NAME: "Coffee Temp",
        ENTITY_MAP: ATTR_MAP_COFFEE_TEMP,
        ENTITY_TYPE: TYPE_COFFEE_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
        ENTITY_CLASS: "temperature",
        ENTITY_UNITS: "°C",
    },
    "boiler_temp": {
        ENTITY_TAG: [TEMP_STEAM],
        ENTITY_NAME: "Steam Temp",
        ENTITY_MAP: ATTR_MAP_STEAM_TEMP,
        ENTITY_TYPE: TYPE_STEAM_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
        ENTITY_CLASS: "temperature",
        ENTITY_UNITS: "°C",
    },
    "drink_stats": {
        ENTITY_TAG: [
            HOT_WATER,
            DRINKS_K1,
            DRINKS_K2,
            DRINKS_K3,
            DRINKS_K4,
            CONTINUOUS,
        ],
        ENTITY_NAME: "Total Drinks",
        ENTITY_MAP: ATTR_MAP_DRINK_STATS,
        ENTITY_TYPE: TYPE_DRINK_STATS,
        ENTITY_ICON: "mdi:coffee",
        ENTITY_CLASS: None,
        ENTITY_UNITS: "drinks",
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    lm = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoSensor(lm, sensor_type, hass.config.units.is_metric, config_entry)
        for sensor_type in ENTITIES
    )


class LaMarzoccoSensor(EntityBase):
    """Sensor representing corona virus data."""

    def __init__(self, lm, sensor_type, is_metric, config_entry):
        """Initialize sensors"""
        self._object_id = sensor_type
        self._lm = lm
        self._entities = ENTITIES
        self._is_metric = is_metric
        self._entity_type = self._entities[self._object_id][ENTITY_TYPE]
        self._config_entry = config_entry

        self._lm.register_callback(self.update_callback)

    @property
    def available(self):
        """Return if sensor is available."""
        return all(
            self._lm.current_status.get(x) is not None
            for x in self._entities[self._object_id][ENTITY_TAG]
        )

    @property
    def state(self):
        """State of the sensor."""
        entities = self._entities[self._object_id][ENTITY_TAG]
        return sum([self._lm.current_status.get(x, 0) for x in entities])

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""
        return self._entities[self._object_id][ENTITY_UNITS]

    @property
    def device_class(self):
        """Device class for sensor"""
        return self._entities[self._object_id][ENTITY_CLASS]
