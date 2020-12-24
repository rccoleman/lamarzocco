import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import *
from .entity_common import EntityCommon

_LOGGER = logging.getLogger(__name__)


class LaMarzoccoPrebrewEntity(
    CoordinatorEntity, SwitchEntity, RestoreEntity, EntityCommon
):
    """Implementation of a La Marzocco integration"""

    def __init__(self, coordinator, config, is_metric):
        """Initialise the platform with a data instance and site."""
        super().__init__(coordinator)
        self._config = config
        self._temp_state = None
        self._is_metric = is_metric

        self.coordinator._device.register_callback(self.update_callback)

    async def async_turn_on(self, **kwargs) -> None:
        """Turn device on."""
        await self.coordinator._device.set_prebrewing_enable(True)
        self._temp_state = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn device off."""
        await self.coordinator._device.set_prebrewing_enable(False)
        self._temp_state = False

    @property
    def unique_id(self):
        """Return unique ID."""
        return super().unique_id_base + "prebrew"

    @property
    def is_on(self) -> bool:
        """Return true if device is on."""
        reported_state = self.coordinator._device.current_status.get(ENABLE_PREBREWING)
        if self._temp_state == reported_state:
            self._temp_state = None

        return self._temp_state if self._temp_state is not None else reported_state

    @property
    def name(self):
        """Return the name of the switch."""
        return super().name_base + "Prebrew"

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend, if any."""
        return "mdi:location-enter"

    @property
    def state_attributes(self):
        """Return the state attributes."""
        return self.generate_attrs(
            self.coordinator._device._current_status, ATTR_STATUS_MAP_PREBREW
        )
