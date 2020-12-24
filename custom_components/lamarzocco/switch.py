import logging
import voluptuous as vol
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import *
from .switch_auto_on_off import LaMarzoccoAutoOnOffEntity
from .switch_main import LaMarzoccoMainEntity
from .switch_prebrew import LaMarzoccoPrebrewEntity

_LOGGER = logging.getLogger(__name__)


class Service:
    def __init__(self, name, params):
        self._name = name
        self._params = params
        self._platform = entity_platform.current_platform.get()

    def register(self):
        self._platform.async_register_entity_service(
            self._name, self._params, self._name
        )


SWITCHES = [LaMarzoccoMainEntity, LaMarzoccoPrebrewEntity, LaMarzoccoAutoOnOffEntity]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add a switch entity from a config_entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        switch_entity(coordinator, config_entry.data, hass.config.units.is_metric)
        for switch_entity in SWITCHES
    )

    SERVICES = [
        Service(
            SERVICE_SET_COFFEE_TEMP,
            {
                vol.Required("entity_id"): cv.string,
                vol.Required("temperature"): cv.string,
            },
        ),
        Service(
            SERVICE_SET_STEAM_TEMP,
            {
                vol.Required("entity_id"): cv.string,
                vol.Required("temperature"): cv.string,
            },
        ),
        Service(
            SERVICE_ENABLE_AUTO_ON_OFF,
            {
                vol.Required("entity_id"): cv.string,
                vol.Required("day_of_week"): cv.string,
            },
        ),
        Service(
            SERVICE_DISABLE_AUTO_ON_OFF,
            {
                vol.Required("entity_id"): cv.string,
                vol.Required("day_of_week"): cv.string,
            },
        ),
        Service(
            SERVICE_SET_AUTO_ON_OFF_HOURS,
            {
                vol.Required("entity_id"): cv.string,
                vol.Required("day_of_week"): cv.string,
                vol.Required("hour_on"): cv.string,
                vol.Required("hour_off"): cv.string,
            },
        ),
    ]

    for service in SERVICES:
        service.register()
