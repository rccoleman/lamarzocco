"""Sensor platform for La Marzocco espresso machines."""

import logging

from lmdirect.msgs import (
    CONTINUOUS,
    DRINKS_K1,
    DRINKS_K2,
    DRINKS_K3,
    DRINKS_K4,
    TOTAL_FLUSHING,
)

from .const import (
    ATTR_MAP_DRINK_STATS_GS3_AV,
    ATTR_MAP_DRINK_STATS_GS3_MP_LM,
    DOMAIN,
    ENTITY_CLASS,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TAG,
    ENTITY_TYPE,
    ENTITY_UNITS,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    TYPE_DRINK_STATS,
)
from .entity_base import EntityBase
from .services import async_setup_entity_services

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "drink_stats": {
        ENTITY_TAG: [
            DRINKS_K1,
            DRINKS_K2,
            DRINKS_K3,
            DRINKS_K4,
            CONTINUOUS,
            TOTAL_FLUSHING,
        ],
        ENTITY_NAME: "Total Drinks",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_DRINK_STATS_GS3_AV,
            MODEL_GS3_MP: ATTR_MAP_DRINK_STATS_GS3_MP_LM,
            MODEL_LM: ATTR_MAP_DRINK_STATS_GS3_MP_LM,
        },
        ENTITY_TYPE: TYPE_DRINK_STATS,
        ENTITY_ICON: "mdi:coffee",
        ENTITY_CLASS: None,
        ENTITY_UNITS: "drinks",
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up sensor entities."""
    lm = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoSensor(lm, sensor_type, hass, config_entry)
        for sensor_type in ENTITIES
        if lm.model_name in ENTITIES[sensor_type][ENTITY_MAP]
    )

    await async_setup_entity_services(lm)


class LaMarzoccoSensor(EntityBase):
    """Sensor representing espresso machine temperature data."""

    def __init__(self, lm, sensor_type, hass, config_entry):
        """Initialize sensors"""
        self._object_id = sensor_type
        self._lm = lm
        self._entities = ENTITIES
        self._hass = hass
        self._entity_type = self._entities[self._object_id][ENTITY_TYPE]

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
        """Unit of measurement."""
        return self._entities[self._object_id][ENTITY_UNITS]

    @property
    def device_class(self):
        """Device class for sensor"""
        return self._entities[self._object_id][ENTITY_CLASS]
