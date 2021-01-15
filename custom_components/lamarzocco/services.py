"""Global services for the La Marzocco integration."""

import voluptuous as vol
from lmdirect import InvalidInput
import logging
from .const import (
    DAYS,
    DOMAIN,
    MODEL_GS3_AV,
    MODEL_GS3_MP,
    MODEL_LM,
    MODELS_SUPPORTED,
    SCHEMA,
    SERVICE_SET_AUTO_ON_OFF_ENABLE,
    SERVICE_SET_AUTO_ON_OFF_HOURS,
    SERVICE_SET_DOSE,
    SERVICE_SET_DOSE_HOT_WATER,
    SERVICE_SET_PREBREW_TIMES,
    FUNC,
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
        await call_service(lm.set_auto_on_off, day_of_week=day_of_week, enable=enable)
        return True

    async def set_auto_on_off_hours(service):
        """Service call to configure auto on/off hours for a day."""
        day_of_week = service.data.get("day_of_week", None)
        hour_on = service.data.get("hour_on", None)
        hour_off = service.data.get("hour_off", None)

        _LOGGER.debug(
            f"Setting auto on/off hours for {day_of_week} from {hour_on} to {hour_off}"
        )
        await call_service(
            lm.set_auto_on_off_hours,
            day_of_week=day_of_week,
            hour_on=hour_on,
            hour_off=hour_off,
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
        time_on = service.data.get("time_on", None)
        time_off = service.data.get("time_off", None)

        _LOGGER.debug(
            f"Setting prebrew on time for key:{key} to time_on:{time_on} and off_time:{time_off}"
        )
        await call_service(
            lm.set_prebrew_times,
            key=key,
            time_on=time_on,
            time_off=time_off,
        )
        return True

    INTEGRATION_SERVICES = {
        SERVICE_SET_DOSE: {
            SCHEMA: {
                vol.Required("key"): vol.All(vol.Coerce(int), vol.Range(min=1, max=5)),
                vol.Required("pulses"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=1000)
                ),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV],
            FUNC: set_dose,
        },
        SERVICE_SET_DOSE_HOT_WATER: {
            SCHEMA: {
                vol.Required("seconds"): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=30)
                ),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP],
            FUNC: set_dose_hot_water,
        },
        SERVICE_SET_AUTO_ON_OFF_ENABLE: {
            SCHEMA: {
                vol.Required("day_of_week"): vol.In(DAYS),
                vol.Required("enable"): vol.Boolean(),
            },
            MODELS_SUPPORTED: [MODEL_GS3_AV, MODEL_GS3_MP, MODEL_LM],
            FUNC: set_auto_on_off_enable,
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
            FUNC: set_auto_on_off_hours,
        },
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
            FUNC: set_prebrew_times,
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
        INTEGRATION_SERVICES[SERVICE_SET_PREBREW_TIMES][SCHEMA].update(
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
