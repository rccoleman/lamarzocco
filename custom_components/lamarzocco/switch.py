"""Switch platform for La Marzocco espresso machines."""

import logging

import voluptuous as vol
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers import entity_platform
from lmdirect.msgs import GLOBAL_AUTO, POWER

from .const import (
    ATTR_MAP_AUTO_ON_OFF,
    ATTR_MAP_MAIN_GS3_AV,
    ATTR_MAP_MAIN_GS3_MP_LM,
    ATTR_MAP_PREBREW_GS3_AV,
    ATTR_MAP_PREBREW_LM,
    DAYS,
    DOMAIN,
    ENABLE_PREBREWING,
    ENTITY_FUNC,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_SERVICES,
    ENTITY_TAG,
    ENTITY_TYPE,
    FUNC_BASE,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    MODELS_SUPPORTED,
    SCHEMA,
    SERVICE_DISABLE_AUTO_ON_OFF,
    SERVICE_ENABLE_AUTO_ON_OFF,
    SERVICE_SET_AUTO_ON_OFF_HOURS,
    SERVICE_SET_DOSE,
    SERVICE_SET_DOSE_HOT_WATER,
    SERVICE_SET_PREBREW_TIMES,
    TYPE_AUTO_ON_OFF,
    TYPE_MAIN,
    TYPE_STEAM_TEMP,
)
from .entity_base import EntityBase

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "main": {
        ENTITY_TAG: POWER,
        ENTITY_NAME: "Main",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_MAIN_GS3_AV,
            MODEL_GS3_MP: ATTR_MAP_MAIN_GS3_MP_LM,
            MODEL_LM: ATTR_MAP_MAIN_GS3_MP_LM,
        },
        ENTITY_TYPE: TYPE_MAIN,
        ENTITY_ICON: "mdi:coffee-maker",
        ENTITY_FUNC: "set_power",
        ENTITY_SERVICES: {
            SERVICE_SET_DOSE: {
                SCHEMA: {
                    vol.Required("key"): vol.All(
                        vol.Coerce(int), vol.Range(min=1, max=5)
                    ),
                    vol.Required("pulses"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=1000)
                    ),
                },
                MODELS_SUPPORTED: [MODEL_GS3_AV],
            },
            SERVICE_SET_DOSE_HOT_WATER: {
                SCHEMA: {
                    vol.Required("seconds"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=30)
                    ),
                },
                MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP],
            },
        },
    },
    "auto_on_off": {
        ENTITY_TAG: GLOBAL_AUTO,
        ENTITY_NAME: "Auto On Off",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_AUTO_ON_OFF,
            MODEL_GS3_MP: ATTR_MAP_AUTO_ON_OFF,
            MODEL_LM: ATTR_MAP_AUTO_ON_OFF,
        },
        ENTITY_TYPE: TYPE_AUTO_ON_OFF,
        ENTITY_ICON: "mdi:alarm",
        ENTITY_FUNC: "set_auto_on_off_global",
        ENTITY_SERVICES: {
            SERVICE_ENABLE_AUTO_ON_OFF: {
                SCHEMA: {
                    vol.Required("day_of_week"): vol.In(DAYS),
                },
                MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM],
            },
            SERVICE_DISABLE_AUTO_ON_OFF: {
                SCHEMA: {
                    vol.Required("day_of_week"): vol.In(DAYS),
                },
                MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM],
            },
            SERVICE_SET_AUTO_ON_OFF_HOURS: {
                SCHEMA: {
                    vol.Required("day_of_week"): vol.In(DAYS),
                    vol.Required("hour_on"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=23)
                    ),
                    vol.Required("hour_off"): vol.All(
                        vol.Coerce(int), vol.Range(min=0, max=23)
                    ),
                },
                MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM],
            },
        },
    },
    "prebrew": {
        ENTITY_TAG: ENABLE_PREBREWING,
        ENTITY_NAME: "Prebrew",
        ENTITY_MAP: {
            MODEL_GS3_AV: ATTR_MAP_PREBREW_GS3_AV,
            MODEL_LM: ATTR_MAP_PREBREW_LM,
        },
        ENTITY_TYPE: TYPE_STEAM_TEMP,
        ENTITY_ICON: "mdi:location-enter",
        ENTITY_FUNC: "set_prebrewing_enable",
        ENTITY_SERVICES: {
            SERVICE_SET_PREBREW_TIMES: {
                SCHEMA: {
                    vol.Required("time_on"): vol.All(
                        vol.Coerce(float), vol.Range(min=0, max=5)
                    ),
                    vol.Required("time_off"): vol.All(
                        vol.Coerce(float), vol.Range(min=0, max=5)
                    ),
                },
                MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_LM],
            },
        },
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up switch entities and services."""

    lm = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        LaMarzoccoSwitch(lm, switch_type, hass.config.units.is_metric, config_entry)
        for switch_type in ENTITIES
        if lm.model_name in ENTITIES[switch_type][ENTITY_MAP]
    )

    """Set the max prebrew button based on model"""
    if lm.model_name in [MODEL_GS3_AV, MODEL_LM]:
        max_button_number = 4 if lm.model_name == MODEL_GS3_AV else 1
        ENTITIES["prebrew"][ENTITY_SERVICES][SERVICE_SET_PREBREW_TIMES][SCHEMA].update(
            {
                vol.Required("key"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=max_button_number)
                )
            },
        )

    platform = entity_platform.current_platform.get()

    [
        [
            platform.async_register_entity_service(
                service, entity[ENTITY_SERVICES][service][SCHEMA], service
            )
            for service in entity[ENTITY_SERVICES]
            if lm.model_name in entity[ENTITY_SERVICES][service][MODELS_SUPPORTED]
        ]
        for entity in ENTITIES.values()
    ]


class LaMarzoccoSwitch(EntityBase, SwitchEntity):
    """Switches representing espresso machine power, prebrew, and auto on/off."""

    def __init__(self, lm, switch_type, is_metric, config_entry):
        """Initialise switches."""
        self._object_id = switch_type
        self._temp_state = None
        self._is_metric = is_metric
        self._lm = lm
        self._entities = ENTITIES
        self._entity_type = self._entities[self._object_id][ENTITY_TYPE]
        self._config_entry = config_entry

        self._lm.register_callback(self.update_callback)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        await eval(FUNC_BASE + self._entities[self._object_id][ENTITY_FUNC] + "(True)")
        self._temp_state = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        await eval(FUNC_BASE + self._entities[self._object_id][ENTITY_FUNC] + "(False)")
        self._temp_state = False

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        reported_state = self._lm.current_status.get(
            self._entities[self._object_id][ENTITY_TAG]
        )
        if self._temp_state == reported_state:
            self._temp_state = None

        return self._temp_state if self._temp_state is not None else reported_state

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

    async def set_dose_hot_water(self, seconds=None):
        """Service call to set the hot water dose."""

        _LOGGER.debug(f"Setting hot water dose to seconds:{seconds}")
        await self.call_service(self._lm.set_dose_hot_water, seconds=seconds)
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
        return True

    async def set_coffee_temp(self, temperature=None):
        """Service call to set coffee temp."""

        """Machine expects Celcius, so convert if needed."""
        if not self._is_metric:
            temperature = round((temperature - 32) / 9 * 5, 1)

        _LOGGER.debug(f"Setting coffee temp to {temperature}")
        await self.call_service(self._lm.set_coffee_temp, temp=temperature)
        return True
