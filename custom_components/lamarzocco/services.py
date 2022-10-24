"""Global services for the La Marzocco integration."""

import logging

import voluptuous as vol
from homeassistant.helpers import entity_platform
from lmdirect import InvalidInput
from lmdirect.msgs import Msg

from .const import (
    DAYS,
    DOMAIN,
    FUNC,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    MODELS_SUPPORTED,
    PLATFORM,
    SCHEMA,
)

_LOGGER = logging.getLogger(__name__)


async def call_service(func, *args, **kwargs):
    try:
        await func(*args, **kwargs)
    except InvalidInput as err:
        _LOGGER.error(f"{err}, returning FALSE")
        return False


async def async_setup_services(hass, config_entry):
    """Create and register services for the La Marzocco integration."""

    async def set_auto_on_off_enable(service):
        """Service call to enable auto on/off."""
        day_of_week = service.data.get("day_of_week", None)
        enable = service.data.get("enable", None)

        _LOGGER.debug(f"Setting auto on/off for {day_of_week} to {enable}")
        await call_service(lm.set_auto_on_off_enable, day_of_week=day_of_week, enable=enable)
        return True

    async def set_auto_on_off_times(service):
        """Service call to configure auto on/off hours for a day."""
        day_of_week = service.data.get("day_of_week", None)
        hour_on = service.data.get("hour_on", None)
        minute_on = service.data.get("minute_on", None)
        hour_off = service.data.get("hour_off", None)
        minute_off = service.data.get("minute_off", None)

        _LOGGER.debug(
            f"Setting auto on/off hours for {day_of_week} from {hour_on}:{minute_on} to {hour_off}:{minute_off}"
        )
        await call_service(
            lm.set_auto_on_off_times,
            day_of_week=day_of_week,
            hour_on=hour_on,
            minute_on=minute_on,
            hour_off=hour_off,
            minute_off=minute_off,
        )
        return True

    async def set_dose(service):
        """Service call to set the dose for a key."""
        key = service.data.get("key", None)
        pulses = service.data.get("pulses", None)

        _LOGGER.debug(f"Setting dose for key:{key} to pulses:{pulses}")
        await call_service(lm.set_dose, key=key, pulses=pulses)
        return True

    async def set_dose_hot_water(service):
        """Service call to set the hot water dose."""
        seconds = service.data.get("seconds", None)

        _LOGGER.debug(f"Setting hot water dose to seconds:{seconds}")
        await call_service(lm.set_dose_hot_water, seconds=seconds)
        return True

    async def set_prebrew_times(service):
        """Service call to set prebrew on time."""
        key = service.data.get("key", None)
        seconds_on = service.data.get("seconds_on", None)
        seconds_off = service.data.get("seconds_off", None)

        _LOGGER.debug(
            f"Setting prebrew on time for {key=} to {seconds_on=} and {seconds_off=}"
        )
        await call_service(
            lm.set_prebrew_times,
            key=key,
            seconds_on=seconds_on,
            seconds_off=seconds_off,
        )
        return True

    async def set_preinfusion_time(service):
        """Service call to set preinfusion time."""
        key = service.data.get("key", None)
        seconds = service.data.get("seconds", None)

        _LOGGER.debug(
            f"Setting prebrew on time for {key=} to {seconds=}"
        )
        await call_service(
            lm.set_preinfusion_times,
            key=key,
            seconds=seconds,
        )
        return True

    INTEGRATION_SERVICES = {
        Msg.SET_DOSE: {
            SCHEMA: {
                vol.Required("key"): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
                vol.Required("pulses"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=1000)
                ),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV],
            FUNC: set_dose,
        },
        Msg.SET_DOSE_HOT_WATER: {
            SCHEMA: {
                vol.Required("seconds"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=30)
                ),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP],
            FUNC: set_dose_hot_water,
        },
        Msg.SET_AUTO_ON_OFF_ENABLE: {
            SCHEMA: {
                vol.Required("day_of_week"): vol.In(DAYS),
                vol.Required("enable"): vol.Boolean(),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM],
            FUNC: set_auto_on_off_enable,
        },
        Msg.SET_AUTO_ON_OFF_TIMES: {
            SCHEMA: {
                vol.Required("day_of_week"): vol.In(DAYS),
                vol.Required("hour_on"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=23)
                ),
                vol.Optional("minute_on", default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=59)
                ),
                vol.Required("hour_off"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=23)
                ),
                vol.Optional("minute_off", default=0): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=59)
                ),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM],
            FUNC: set_auto_on_off_times,
        },
        Msg.SET_PREBREW_TIMES: {
            SCHEMA: {
                vol.Required("seconds_on"): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=5)
                ),
                vol.Required("seconds_off"): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=5)
                ),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_LM],
            FUNC: set_prebrew_times,
        },
        Msg.SET_PREINFUSION_TIME: {
            SCHEMA: {
                vol.Required("seconds"): vol.All(
                    vol.Coerce(float), vol.Range(min=0, max=5)
                ),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_LM],
            FUNC: set_preinfusion_time,
        },
    }

    existing_services = hass.services.async_services().get(DOMAIN)
    if existing_services and any(
        service in INTEGRATION_SERVICES for service in existing_services
    ):
        # Integration-level services have already been added. Return.
        return

    lm = hass.data[DOMAIN][config_entry.entry_id]

    """Set the max prebrew button based on model"""
    if lm.model_name in [MODEL_GS3_AV, MODEL_LM]:
        max_button_number = 4 if lm.model_name == MODEL_GS3_AV else 1
        INTEGRATION_SERVICES[Msg.SET_PREBREW_TIMES][SCHEMA].update(
            {
                vol.Required("key"): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=max_button_number)
                )
            },
        )

    """Register the services."""
    [
        hass.services.async_register(
            domain=DOMAIN,
            service=service,
            schema=vol.Schema(INTEGRATION_SERVICES[service][SCHEMA]),
            service_func=INTEGRATION_SERVICES[service][FUNC],
        )
        for service in INTEGRATION_SERVICES
        if lm.model_name in INTEGRATION_SERVICES[service][MODELS_SUPPORTED]
    ]


ENTITY_SERVICES = {}


async def async_setup_entity_services(lm):
    """Create and register entity services for the La Marzocco integration."""
    platform = entity_platform.current_platform.get()

    [
        platform.async_register_entity_service(
            service, ENTITY_SERVICES[service][SCHEMA], service
        )
        for service in ENTITY_SERVICES
        if lm.model_name in ENTITY_SERVICES[service][MODELS_SUPPORTED]
        and ENTITY_SERVICES[service][PLATFORM] == platform.domain
    ]
