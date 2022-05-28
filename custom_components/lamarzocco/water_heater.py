"""Water heater platform for La Marzocco espresso machines."""

import logging

from homeassistant.components.water_heater import (
    SUPPORT_TARGET_TEMPERATURE,
    ATTR_CURRENT_TEMPERATURE,
    ATTR_TEMPERATURE,
    WaterHeaterEntity,
)
from homeassistant.const import PRECISION_TENTHS, TEMP_CELSIUS
from homeassistant.helpers.temperature import display_temp as show_temp

from .const import (
    ATTR_MAP_COFFEE,
    ATTR_MAP_STEAM,
    DOMAIN,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TEMP_TAG,
    ENTITY_TSET_TAG,
    ENTITY_TYPE,
    ENTITY_UNITS,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    TEMP_COFFEE,
    TSET_COFFEE,
    TEMP_STEAM,
    TSET_STEAM,
    TYPE_COFFEE_TEMP,
    TYPE_STEAM_TEMP,
)
from .entity_base import EntityBase
from .services import async_setup_entity_services, call_service

"""Min/Max coffee and team temps."""
COFFEE_MIN_TEMP = 87
COFFEE_MAX_TEMP = 100

STEAM_MIN_TEMP = 110
STEAM_MAX_TEMP = 132

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "coffee": {
        ENTITY_TEMP_TAG: TEMP_COFFEE,
        ENTITY_TSET_TAG: TSET_COFFEE,
        ENTITY_NAME: "Coffee",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_COFFEE,
            MODEL_GS3_MP: ATTR_MAP_COFFEE,
            MODEL_LM: ATTR_MAP_COFFEE,
        },
        ENTITY_TYPE: TYPE_COFFEE_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
        ENTITY_UNITS: TEMP_CELSIUS,
    },
    "steam": {
        ENTITY_TEMP_TAG: TEMP_STEAM,
        ENTITY_TSET_TAG: TSET_STEAM,
        ENTITY_NAME: "Steam",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_STEAM,
            MODEL_GS3_MP: ATTR_MAP_STEAM,
        },
        ENTITY_TYPE: TYPE_STEAM_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
        ENTITY_UNITS: TEMP_CELSIUS,
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up water heater type entities."""
    lm = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoWaterHeater(lm, water_heater_type, hass, config_entry)
        for water_heater_type in ENTITIES
        if lm.model_name in ENTITIES[water_heater_type][ENTITY_MAP]
    )

    await async_setup_entity_services(lm)


class LaMarzoccoWaterHeater(EntityBase, WaterHeaterEntity):
    """Water heater representing espresso machine temperature data."""

    """Set static properties."""
    _attr_supported_features = SUPPORT_TARGET_TEMPERATURE
    _attr_precision = PRECISION_TENTHS

    def __init__(self, lm, water_heater_type, hass, config_entry):
        """Initialize water heater."""
        self._object_id = water_heater_type
        self._lm = lm
        self._entities = ENTITIES
        self._hass = hass
        self._entity_type = self._entities[self._object_id][ENTITY_TYPE]

        """Set dynamic properties."""
        self._attr_min_temp = COFFEE_MIN_TEMP if self._object_id == "coffee" else STEAM_MIN_TEMP
        self._attr_max_temp = COFFEE_MAX_TEMP if self._object_id == "coffee" else STEAM_MAX_TEMP

        self._lm.register_callback(self.update_callback)

    @property
    def state(self):
        """State of the water heater."""
        return self.current_temperature

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return show_temp(
            self.hass,
            self._lm.current_status.get(
                self._entities[self._object_id][ENTITY_TEMP_TAG], 0
            ),
            self.temperature_unit,
            self.precision,
        )

    @property
    def target_temperature(self):
        """Return the target temperature."""
        return show_temp(
            self.hass,
            self._lm.current_status.get(
                self._entities[self._object_id][ENTITY_TSET_TAG], 0
            ),
            self.temperature_unit,
            self.precision,
        )

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return self._entities[self._object_id][ENTITY_UNITS]

    @property
    def state_attributes(self):
        temps = {
            ATTR_CURRENT_TEMPERATURE: self.current_temperature,
            ATTR_TEMPERATURE: self.target_temperature
        }
        return {**EntityBase.state_attributes.fget(self), **temps}

    async def async_set_temperature(self, **kwargs):
        """Service call to set the temp of either the coffee or steam boilers."""
        temperature = kwargs.get("temperature", None)
        func = getattr(self._lm, "set_" + self._object_id + "_temp")

        _LOGGER.debug(f"Setting {self._object_id} to {temperature}")
        await call_service(func, temp=round(temperature, 1))
        return True
