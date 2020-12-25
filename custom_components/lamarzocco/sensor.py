"""Sensor platform for the Corona virus."""
import logging

from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import *
from .entity_common import EntityCommon

_LOGGER = logging.getLogger(__name__)

SENSORS = {
    "coffee_temp": (
        TEMP_COFFEE,
        "Coffee Temp",
        ATTR_STATUS_MAP_COFFEE_TEMP,
        ENTITY_COFFEE_TEMP,
    ),
    "boiler_temp": (
        TEMP_STEAM,
        "Steam Temp",
        ATTR_STATUS_MAP_STEAM_TEMP,
        ENTITY_STEAM_TEMP,
    ),
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Defer sensor setup to the shared sensor module."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoSensor(coordinator, sensor_type, hass.config.units.is_metric)
        for sensor_type in SENSORS
    )


class LaMarzoccoSensor(CoordinatorEntity, EntityCommon):
    """Sensor representing corona virus data."""

    def __init__(self, coordinator, sensor_type, is_metric):
        """Initialize coronavirus sensor."""
        super().__init__(coordinator)
        self._name = sensor_type
        self._coordinator = coordinator
        self._is_metric = is_metric
        self._entity = SENSORS[self._name][3]

        self.coordinator._device.register_callback(self.update_callback)

    @property
    def available(self):
        """Return if sensor is available."""
        return (
            self.coordinator._device.current_status.get(SENSORS[self._name][0])
            is not None
        )

    @property
    def state(self):
        """State of the sensor."""
        return self.coordinator._device.current_status.get(SENSORS[self._name][0])

    @property
    def name(self):
        """Return the name of the switch."""
        return super().name_base + SENSORS[self._name][1]

    @property
    def icon(self):
        """Return the icon."""
        return "mdi:water-boiler"

    @property
    def unit_of_measurement(self):
        """Return unit of measurement."""

        """Machine returns temperature in C, but HA will convert to the right locale"""
        return "°C"

    @property
    def device_class(self):
        """Device class for sensor"""
        return "temperature"

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return self.generate_attrs(
            self.coordinator._device._current_status, SENSORS[self._name][2]
        )

    @property
    def unique_id(self):
        """Return unique ID."""
        return super().unique_id_base + self._name

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
