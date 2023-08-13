"""Water heater platform for La Marzocco espresso machines."""

import logging

from homeassistant.components.water_heater import (
    STATE_ELECTRIC,
    STATE_OFF,
    WaterHeaterEntity,
    WaterHeaterEntityFeature
)
from homeassistant.const import PRECISION_TENTHS, UnitOfTemperature

from .const import (
    ATTR_MAP_COFFEE,
    ATTR_MAP_STEAM,
    COFFEE_BOILER_STATE,
    DOMAIN,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TOPERATION_TAG,
    ENTITY_TEMP_TAG,
    ENTITY_TSET_TAG,
    ENTITY_TSTATE_TAG,
    ENTITY_TYPE,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    MODEL_LMU,
    POWER,
    STEAM_BOILER_ENABLE,
    STEAM_BOILER_STATE,
    TEMP_COFFEE,
    TSET_COFFEE,
    TEMP_STEAM,
    TSET_STEAM,
    TYPE_COFFEE_TEMP,
    TYPE_STEAM_TEMP
)
from .entity_base import EntityBase
from .services import async_setup_entity_services, call_service

"""Min/Max coffee and team temps."""
COFFEE_MIN_TEMP = 85
COFFEE_MAX_TEMP = 104

STEAM_STEPS = [126, 128, 131]

MODE_ENABLED = "Enabled"
MODE_DISABLED = "Disabled"
OPERATION_MODES = [MODE_ENABLED, MODE_DISABLED]

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "coffee": {
        ENTITY_TEMP_TAG: TEMP_COFFEE,
        ENTITY_TSET_TAG: TSET_COFFEE,
        ENTITY_TOPERATION_TAG: POWER,
        ENTITY_TSTATE_TAG: COFFEE_BOILER_STATE,
        ENTITY_NAME: "Coffee",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_COFFEE,
            MODEL_GS3_MP: ATTR_MAP_COFFEE,
            MODEL_LM: ATTR_MAP_COFFEE,
            MODEL_LMU: ATTR_MAP_COFFEE
        },
        ENTITY_TYPE: TYPE_COFFEE_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
    },
    "steam": {
        ENTITY_TEMP_TAG: TEMP_STEAM,
        ENTITY_TSET_TAG: TSET_STEAM,
        ENTITY_TOPERATION_TAG: STEAM_BOILER_ENABLE,
        ENTITY_TSTATE_TAG: STEAM_BOILER_STATE,
        ENTITY_NAME: "Steam",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_STEAM,
            MODEL_GS3_MP: ATTR_MAP_STEAM,
            MODEL_LM: ATTR_MAP_COFFEE,
            MODEL_LMU: ATTR_MAP_STEAM
        },
        ENTITY_TYPE: TYPE_STEAM_TEMP,
        ENTITY_ICON: "mdi:water-boiler",
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up water heater type entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    async_add_entities(
        LaMarzoccoWaterHeater(coordinator, water_heater_type, hass, config_entry)
        for water_heater_type in ENTITIES
        if coordinator.lm.model_name in ENTITIES[water_heater_type][ENTITY_MAP]
    )

    await async_setup_entity_services(coordinator.lm)


class LaMarzoccoWaterHeater(EntityBase, WaterHeaterEntity):
    """Water heater representing espresso machine temperature data."""

    def __init__(self, coordinator, water_heater_type, hass, config_entry):
        """Initialize water heater."""
        super().__init__(coordinator, hass, water_heater_type, ENTITIES, ENTITY_TYPE)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return WaterHeaterEntityFeature.TARGET_TEMPERATURE | WaterHeaterEntityFeature.ON_OFF | WaterHeaterEntityFeature.OPERATION_MODE

    @property
    def temperature_unit(self):
        """Return the unit of measurement used by the platform."""
        return UnitOfTemperature.CELSIUS

    @property
    def precision(self):
        """Return the precision of the platform."""
        return PRECISION_TENTHS

    @property
    def state(self):
        """State of the water heater."""
        is_on = self._lm.current_status.get(
            self._entities[self._object_id][ENTITY_TSTATE_TAG], False
        )
        return STATE_ELECTRIC if is_on else STATE_OFF

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._lm.current_status.get(
            self._entities[self._object_id][ENTITY_TEMP_TAG], 0
        )

    @property
    def target_temperature(self):
        """Return the target temperature."""
        return self._lm.current_status.get(
            self._entities[self._object_id][ENTITY_TSET_TAG], 0
        )

    @property
    def min_temp(self):
        return COFFEE_MIN_TEMP if self._object_id == "coffee" else min(STEAM_STEPS)

    @property
    def max_temp(self):
        return COFFEE_MAX_TEMP if self._object_id == "coffee" else max(STEAM_STEPS)

    @property
    def operation_list(self):
        return OPERATION_MODES

    @property
    def current_operation(self):
        is_on = self._lm.current_status.get(
            self._entities[self._object_id][ENTITY_TOPERATION_TAG], False
        )
        return MODE_ENABLED if is_on else MODE_DISABLED

    async def async_set_temperature(self, **kwargs):
        """Service call to set the temp of either the coffee or steam boilers."""
        temperature = kwargs.get("temperature", None)
        func = getattr(self._lm, "set_" + self._object_id + "_temp")

        _LOGGER.debug(f"Setting {self._object_id} to {temperature}")
        await call_service(func, temp=round(temperature, 1))
        await self._update_ha_state()
        return True

    async def async_turn_on(self):
        _LOGGER.debug(f"Turning {self._object_id} on")
        func = getattr(self._lm, f"set_{self._entities[self._object_id][ENTITY_TSTATE_TAG]}")
        await call_service(func, state=True)

    async def async_turn_off(self):
        _LOGGER.debug(f"Turning {self._object_id} on")
        func = getattr(self._lm, f"set_{self._entities[self._object_id][ENTITY_TSTATE_TAG]}")
        await call_service(func, state=False)

    async def async_set_operation_mode(self, operation_mode):
        if operation_mode == MODE_ENABLED:
            await self.async_turn_on()
        else:
            await self.async_turn_off()
