"""Sensor platform for the Corona virus."""
import logging

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import *
from .entity_base import EntityCommon

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
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoSensor(coordinator, sensor_type, hass.config.units.is_metric)
        for sensor_type in ENTITIES
    )


class LaMarzoccoSensor(EntityCommon):
    """Sensor representing corona virus data."""

    def __init__(self, coordinator, sensor_type, is_metric):
        """Initialize coronavirus sensor."""
        super().__init__(coordinator)
        self._object_id = sensor_type
        self._coordinator = coordinator
        self._is_metric = is_metric
        self.ENTITIES = ENTITIES
        self._entity_type = self.ENTITIES[self._object_id][ENTITY_TYPE]

        self.coordinator._device.register_callback(self.update_callback)

    @property
    def available(self):
        """Return if sensor is available."""
        return (
            self.coordinator._device.current_status.get(
                self.ENTITIES[self._object_id][ENTITY_TAG]
            )
            is not None
        )

    @property
    def state(self):
        """State of the sensor."""
        return self.coordinator._device.current_status.get(
            self.ENTITIES[self._object_id][ENTITY_TAG]
        )

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""

        """Machine returns temperature in C, but HA will convert to the right locale"""
        return "°C"

    @property
    def device_class(self):
        """Device class for sensor"""
        return "temperature"
