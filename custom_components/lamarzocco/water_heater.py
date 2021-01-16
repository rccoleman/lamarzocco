"""Water heater platform for La Marzocco espresso machines."""

import logging

from lmdirect.msgs import TSET_COFFEE, TSET_STEAM

from .const import (
    ATTR_MAP_COFFEE,
    ATTR_MAP_STEAM,
    DOMAIN,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TAG,
    ENTITY_TYPE,
    ENTITY_UNITS,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    TEMP_COFFEE,
    TEMP_STEAM,
    TYPE_COFFEE_TEMP,
    TYPE_STEAM_TEMP,
)
from .entity_base import EntityBase
from .services import call_service, async_setup_entity_services

from homeassistant.components.water_heater import (
    SUPPORT_TARGET_TEMPERATURE,
    WaterHeaterEntity,
)
from homeassistant.const import PRECISION_TENTHS, TEMP_CELSIUS
from homeassistant.helpers.temperature import display_temp as show_temp

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "coffee": {
        ENTITY_TAG: TEMP_COFFEE,
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
        ENTITY_TAG: TEMP_STEAM,
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

    def __init__(self, lm, water_heater_type, hass, config_entry):
        """Initialize water heater."""
        self._object_id = water_heater_type
        self._lm = lm
        self._entities = ENTITIES
        self._support_flags = SUPPORT_TARGET_TEMPERATURE
        self._hass = hass
        self._entity_type = self._entities[self._object_id][ENTITY_TYPE]

        self._lm.register_callback(self.update_callback)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return self._support_flags

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._entities[self._object_id][ENTITY_TAG]

    @property
    def state(self):
        """Current temperature of the water heater."""
        return self.current_temperature

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._lm.current_status.get(
            self._entities[self._object_id][ENTITY_TAG], 0
        )

    @property
    def state_attributes(self):
        """Return the state attributes."""
        tag = (
            TSET_COFFEE
            if self._entities[self._object_id][ENTITY_TYPE] == TYPE_COFFEE_TEMP
            else TSET_STEAM
        )
        value = self._lm.current_status.get(tag, 0)
        return {
            **super().state_attributes,
            "temperature": show_temp(
                self._hass,
                value,
                TEMP_CELSIUS,
                PRECISION_TENTHS,
            ),
        }

    @property
    def unit_of_measurement(self):
        """Unit of measurement."""
        return self._entities[self._object_id][ENTITY_UNITS]

    @property
    def precision(self):
        """Return the precision of the system."""
        return PRECISION_TENTHS

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def capability_attributes(self):
        """Return capability attributes."""
        return None

    async def async_set_temperature(self, **kwargs):
        """Service call to set the temp of either the coffee or steam boilers."""
        temperature = kwargs.get("temperature", None)
        func = getattr(self._lm, "set_" + self._object_id + "_temp")

        _LOGGER.debug(f"Setting {self._object_id} to {temperature}")
        await call_service(func, temp=round(temperature, 1))
        return True
