"""Base class for the La Marzocco entities."""

import logging

from homeassistant.const import PRECISION_TENTHS, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.temperature import display_temp as show_temp
from lmdirect.msgs import TEMP_KEYS, TSET_KEYS

from .const import DOMAIN, ENTITY_ICON, ENTITY_MAP, ENTITY_NAME, TEMPERATURE

_LOGGER = logging.getLogger(__name__)


class EntityBase(RestoreEntity):
    """Common elements for all switches."""

    _attr_assumed_state = False
    _attr_entity_registry_enabled_default = True

    @property
    def name(self):
        """Return the name of the switch."""
        return (
            f"{self._lm.machine_name} " + self._entities[self._object_id][ENTITY_NAME]
        )

    @property
    def unique_id(self):
        """Return unique ID."""
        return f"{self._lm.serial_number}_" + self._object_id

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        return self._entities[self._object_id][ENTITY_ICON]

    @callback
    def update_callback(self, **kwargs):
        """Update the state machine when new data arrives."""
        entity_type = kwargs.get("entity_type")
        if entity_type in [None, self._entity_type]:
            self.schedule_update_ha_state(force_refresh=False)

    @property
    def device_info(self):
        """Device info."""
        return {
            "identifiers": {(DOMAIN, self._lm.serial_number)},
            "name": self._lm.machine_name,
            "manufacturer": "La Marzocco",
            "model": self._lm.true_model_name,
            "default_name": "La Marzocco " + self._lm.true_model_name,
            "sw_version": self._lm.firmware_version,
        }

    def _get_key(self, k):
        """Construct tag name if needed."""
        if isinstance(k, tuple):
            k = "_".join(k)
        return k

    @property
    def state_attributes(self):
        """Return the state attributes."""

        def convert_value(k, v):
            """Convert boolean values to strings to improve display in Lovelace."""
            if isinstance(v, bool):
                v = str(v)

            """Convert temps to Fahrenheit if needed."""
            if k in TEMP_KEYS:
                v = show_temp(
                    self._hass,
                    v,
                    TEMP_CELSIUS,
                    PRECISION_TENTHS,
                )
            return v

        def convert_key(k):
            return TEMPERATURE if k in TSET_KEYS else k

        data = self._lm._current_status
        map = [
            self._get_key(k)
            for k in self._entities[self._object_id][ENTITY_MAP][self._lm.model_name]
        ]

        return {convert_key(k): convert_value(k, data[k]) for k in map if k in data}
