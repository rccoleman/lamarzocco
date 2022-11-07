"""Button platform for La Marzocco espresso machines."""

import logging

from homeassistant.components.button import ButtonEntity

from .const import (
    DOMAIN,
    ENTITY_FUNC,
    ENTITY_ICON,
    ENTITY_MAP,
    ENTITY_NAME,
    ENTITY_TYPE,
    TYPE_START_BACKFLUSH,
    MODEL_GS3_AV,
    MODEL_LM,
)
from .entity_base import EntityBase
from .services import async_setup_entity_services, call_service

_LOGGER = logging.getLogger(__name__)

ENTITIES = {
    "start_backflush": {
        ENTITY_NAME: "Start Backflush",
        ENTITY_MAP: {
            MODEL_GS3_AV: None,
            MODEL_LM: None,
        },
        ENTITY_TYPE: TYPE_START_BACKFLUSH,
        ENTITY_ICON: "mdi:coffee-maker",
        ENTITY_FUNC: "set_start_backflush",
    },
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up button entities and services."""

    lm = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        LaMarzoccoButton(lm, button_type, hass)
        for button_type in ENTITIES
        if lm.model_name in ENTITIES[button_type][ENTITY_MAP]
    )

    await async_setup_entity_services(lm)


class LaMarzoccoButton(EntityBase, ButtonEntity):
    """Button supporting backflush."""

    def __init__(self, lm, button_type, hass):
        """Initialise buttons."""
        self._object_id = button_type
        self._hass = hass
        self._lm = lm
        self._entities = ENTITIES
        self._entity_type = self._entities[self._object_id][ENTITY_TYPE]

    async def async_press(self, **kwargs) -> None:
        """Press button."""
        await call_service(
            getattr(self._lm, self._entities[self._object_id][ENTITY_FUNC])
        )
