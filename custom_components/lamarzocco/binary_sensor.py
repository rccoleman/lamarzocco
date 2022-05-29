"""Binary Sensor platform for La Marzocco espresso machines."""

import logging

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_PROBLEM,
    BinarySensorEntity,
)

from .const import (
    ATTR_MAP_WATER_RESERVOIR,
    DOMAIN,
    ENTITY_CLASS,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TAG,
    ENTITY_TYPE,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    TYPE_WATER_RESERVOIR_CONTACT,
    WATER_RESERVOIR_CONTACT,
)
from .entity_base import EntityBase
from .services import async_setup_entity_services

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "water_reservoir": {
        ENTITY_TAG: WATER_RESERVOIR_CONTACT,
        ENTITY_NAME: "Water Reservoir",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_WATER_RESERVOIR,
            MODEL_GS3_MP: ATTR_MAP_WATER_RESERVOIR,
            MODEL_LM: ATTR_MAP_WATER_RESERVOIR,
        },
        ENTITY_TYPE: TYPE_WATER_RESERVOIR_CONTACT,
        ENTITY_ICON: "mdi:water-well",
        ENTITY_CLASS: DEVICE_CLASS_PROBLEM,
    }
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up binary sensor entities."""
    lm = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoBinarySensor(lm, sensor_type, hass, config_entry)
        for sensor_type in ENTITIES
        if lm.model_name in ENTITIES[sensor_type][ENTITY_MAP]
    )

    await async_setup_entity_services(lm)


class LaMarzoccoBinarySensor(EntityBase, BinarySensorEntity):
    """Binary Sensor representing espresso machine water reservoir status."""

    def __init__(self, lm, sensor_type, hass, config_entry):
        """Initialize binary sensors"""
        self._object_id = sensor_type
        self._lm = lm
        self._entities = ENTITIES
        self._hass = hass
        self._entity_type = self._entities[self._object_id][ENTITY_TYPE]

        self._lm.register_callback(self.update_callback)

    @property
    def available(self):
        """Return if binary sensor is available."""
        entity = self._entities[self._object_id][ENTITY_TAG]
        return self._lm.current_status.get(self._get_key(entity)) is not None

    @property
    def is_on(self) -> bool:
        """Return true if the binary sensor is on."""
        return not self._lm.current_status.get(
            self._get_key(self._entities[self._object_id][ENTITY_TAG])
        )

    @property
    def device_class(self):
        """Device class for binary sensor"""
        return self._entities[self._object_id][ENTITY_CLASS]
